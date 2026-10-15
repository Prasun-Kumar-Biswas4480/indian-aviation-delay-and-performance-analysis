import os
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# Constants
CORE_CARRIERS = ['IndiGo', 'Air India', 'Vistara', 'AIX Connect', 'Akasa Air', 'SpiceJet']
TATA_GROUP = ['Air India', 'Vistara', 'AIX Connect']
REGIONAL_CARRIERS = ['Alliance Air', 'Star Air', 'Fly91', 'Flybig', 'IndiaOne Air']
EXCLUDE_CARRIERS = ['Blue Dart Aviation', 'Quikjet Cargo']

# ==========================================
# ETL (EXTRACT, TRANSFORM, LOAD) PIPELINE
# ==========================================
# This module handles reading the raw CSV files, standardizing names, 
# and mathematically simulating missing data points (like precise delays).

def standardize_airline_name(name):
    """
    Cleans up messy airline names from raw datasets (e.g., 'AIR INDIA EXPRESS' -> 'AIX Connect').
    Groups smaller airlines into a unified 'Regional Carriers' bucket.
    """
    if not isinstance(name, str): return name
    name_upper = name.upper().strip().replace('_', ' ')
    
    if 'AIR ASIA' in name_upper or 'AIRASIA' in name_upper or 'AIR INDIA EXPRESS' in name_upper or 'AIX' in name_upper:
        return 'AIX Connect'
    if 'AIR INDIA' in name_upper:
        return 'Air India'
    if 'INDIGO' in name_upper:
        return 'IndiGo'
    if 'VISTARA' in name_upper:
        return 'Vistara'
    if 'AKASA' in name_upper:
        return 'Akasa Air'
    if 'SPICE' in name_upper or 'SPICEJET' in name_upper:
        return 'SpiceJet'
    
    for rc in REGIONAL_CARRIERS:
        if rc.upper() in name_upper:
            return 'Regional Carriers'
    
    for ex in EXCLUDE_CARRIERS:
        if ex.upper() in name_upper:
            return ex
            
    return 'Unknown' 

def consolidate_tata(df, airline_col='airline', apply_consolidation=False):
    """
    If the user toggles 'Tata Group Consolidation' in the UI, this dynamically 
    merges Air India, Vistara, and AIX Connect into a single 'Air India Group' entity.
    """
    if apply_consolidation and airline_col in df.columns:
        df[airline_col] = df[airline_col].apply(lambda x: 'Air India Group' if x in TATA_GROUP else x)
    return df

def clean_flights_data(base_path, tata_consolidation=False):
    """
    Reads and sanitizes the micro-level tactical flight data (economy.csv & business.csv).
    It synthesizes realistic arrival/departure delay distributions using numpy to 
    demonstrate the dashboard's capabilities since the raw dataset only has scheduled times.
    """
    economy_file = os.path.join(base_path, 'economy.csv')
    business_file = os.path.join(base_path, 'business.csv')
    flights_file = os.path.join(base_path, 'flights.csv')
    indian_airlines_file = os.path.join(base_path, 'Indian Airlines.csv')
    
    df_list = []
    
    if os.path.exists(economy_file) and os.path.exists(business_file):
        df_eco = pd.read_csv(economy_file)
        df_eco['fare_class'] = 'Economy'
        df_bus = pd.read_csv(business_file)
        df_bus['fare_class'] = 'Business'
        df = pd.concat([df_eco, df_bus], ignore_index=True)
        
        # Format mapping
        df.rename(columns={'from': 'origin_airport', 'to': 'destination_airport'}, inplace=True)
        df['flight_number'] = df['ch_code'].astype(str) + '-' + df['num_code'].astype(str)
        df['air_fare'] = pd.to_numeric(df['price'].astype(str).str.replace(',', ''), errors='coerce')
        
        # Real Date parsing
        date_obj = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        df['year'] = date_obj.dt.year.fillna(2022).astype(int)
        df['day_of_week'] = date_obj.dt.day_name().str[:3]
        
        # Time parsing
        df['departure_time_parsed'] = pd.to_datetime(df['dep_time'], format='%H:%M', errors='coerce').dt.time
        
    elif os.path.exists(indian_airlines_file):
        df = pd.read_csv(indian_airlines_file)
        df.rename(columns={'flight': 'flight_number', 'source_city': 'origin_airport', 
                           'destination_city': 'destination_airport', 'price': 'air_fare'}, inplace=True)
        df['year'] = np.random.choice([2018, 2019, 2020, 2021, 2022, 2023, 2024], len(df))
        df['day_of_week'] = np.random.choice(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], len(df))
        df['departure_time_parsed'] = pd.to_datetime('08:00', format='%H:%M').time() 
        if 'departure_time' in df.columns:
            df['diurnal_window'] = df['departure_time'].apply(lambda x: 'Morning (05:00-11:59)' if 'Morning' in str(x) else ('Evening (17:00-21:59)' if 'Evening' in str(x) else ('Afternoon (12:00-16:59)' if 'Afternoon' in str(x) else 'Red-Eye (22:00-04:59)')))
    else:
        # Fallback Mock data
        df = pd.DataFrame({'airline': ['IndiGo'] * 100, 'year': [2021]*100, 'diurnal_window': ['Morning (05:00-11:59)']*100, 'air_fare': [5000]*100})
        df['day_of_week'] = 'Mon'

    # Bin time if missing diurnal_window
    if 'diurnal_window' not in df.columns and 'departure_time_parsed' in df.columns:
        def bin_time(t):
            if pd.isna(t): return 'Unknown'
            h = t.hour
            if 5 <= h < 12: return 'Morning (05:00-11:59)'
            if 12 <= h < 17: return 'Afternoon (12:00-16:59)'
            if 17 <= h < 22: return 'Evening (17:00-21:59)'
            return 'Red-Eye (22:00-04:59)'
        df['diurnal_window'] = df['departure_time_parsed'].apply(bin_time)

    # Standardize columns required
    str_cols = {'flight_number', 'airline', 'origin_airport', 'destination_airport', 'diurnal_window', 'day_of_week'}
    num_cols = {'air_fare', 'year'}
    req_cols = list(str_cols | num_cols)
    for col in req_cols:
        if col not in df.columns:
            df[col] = 'Unknown' if col in str_cols else np.nan
            
    # Mock delay metrics since the raw datasets do not contain actual scheduled vs arrival timestamps
    np.random.seed(42)
    # Assign higher delays to some to make it interesting
    df['arrival_delay'] = np.random.normal(10, 15, len(df))
    # Make vistara slightly early on average as before
    df.loc[df['airline'].str.contains('Vistara', case=False, na=False), 'arrival_delay'] -= 15
    df['departure_delay'] = df['arrival_delay'] - np.random.uniform(0, 5, len(df))
            
    df['airline'] = df['airline'].apply(standardize_airline_name)
    df = df[~df['airline'].isin(EXCLUDE_CARRIERS)]
    
    # Inject some mock Akasa Air flights since it's a new airline missing from older raw data
    if 'Akasa Air' not in df['airline'].values:
        akasa_mock = df.sample(frac=0.05, random_state=42).copy()
        akasa_mock['airline'] = 'Akasa Air'
        akasa_mock['year'] = np.random.choice([2022, 2023, 2024], len(akasa_mock))
        df = pd.concat([df, akasa_mock], ignore_index=True)

    df = consolidate_tata(df, apply_consolidation=tata_consolidation)
    
    df['is_delayed'] = (df['arrival_delay'] > 15).astype(int)
    
    return df

def clean_macro_tables(base_path, tata_consolidation=False):
    """
    Reads the macro-level operational data (e.g., RPK, ASK, Load Factors) from the cleaned CSV.
    If the CSV hasn't been generated yet, it falls back to a simulated dataset.
    Also generates a simulated dataset for City-Pair O&D (Origin & Destination) traffic
    because the raw data files didn't include the required network density tables.
    """
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    airlines = CORE_CARRIERS + ['Regional Carriers']
    
    clean_macro_file = os.path.join(base_path, 'macro_data_clean.csv')
    if os.path.exists(clean_macro_file):
        df = pd.read_csv(clean_macro_file)
        if 'airline' in df.columns:
            df['airline'] = df['airline'].apply(standardize_airline_name)
        if 'plf' in df.columns:
            df['plf'] = df['plf'].clip(upper=100.0)
        df = consolidate_tata(df, apply_consolidation=tata_consolidation)
    else:
        records = []
        for y in years:
            for a in airlines:
                base_pax = 1e6 if a == 'IndiGo' else 500000
                if y in [2020, 2021]: base_pax *= 0.4
                if y >= 2022: base_pax *= 1.2
                
                ask = base_pax * 1200 / 0.8 
                
                records.append({
                    'year': y,
                    'airline': a,
                    'departures': base_pax / 150,
                    'hours_flown': (base_pax / 150) * 2,
                    'kilometers_flown': (base_pax / 150) * 1200,
                    'passengers_carried': base_pax,
                    'ask': ask,
                    'rpk': base_pax * 1200,
                    'plf': np.random.uniform(70, 90) if y not in [2020, 2021] else np.random.uniform(40, 60),
                    'freight_tonnes': base_pax * 0.01,
                    'mail_tonnes': base_pax * 0.001
                })
                
        df = pd.DataFrame(records)
        df = consolidate_tata(df, apply_consolidation=tata_consolidation)
    
    # --- City-Pair O&D Traffic from real Table 5.01 ---
    city_pairs = _parse_table_501(base_path, years)
    
    # --- Validated Market Share from real Table 4.01 ---
    df_market_share = _parse_table_401(base_path)
    if df_market_share.empty:
        # Fallback to calculated market share if table 4.01 is completely unavailable
        df_market_share = df.groupby('airline')['passengers_carried'].sum().reset_index()
    
    return df, city_pairs, df_market_share

def _parse_table_401(base_path):
    """
    Parses Table 4.01 for validated domestic market share data.
    """
    table_401_path = os.path.join(base_path, 'yearly statistics', 'TABLE 4.01 (AIRLINES WISE DOMESTIC TRAFFIC STATISTICS).xlsx')
    if os.path.exists(table_401_path):
        try:
            import warnings as _w
            with _w.catch_warnings():
                _w.simplefilter('ignore', UserWarning)
                raw = pd.read_excel(table_401_path, engine='openpyxl')
            
            # Extract airline names (Col 0) and passengers carried (Col 4)
            # Skip the first 4 rows which contain headers/titles
            data = raw.iloc[4:].copy()
            data = data.rename(columns={data.columns[0]: 'airline', data.columns[4]: 'passengers_carried'})
            
            data['passengers_carried'] = pd.to_numeric(data['passengers_carried'], errors='coerce')
            data = data.dropna(subset=['airline', 'passengers_carried'])
            
            # Filter out totals/cargo carriers
            data = data[~data['airline'].astype(str).str.upper().isin(['TOTAL', 'SUB TOTAL', 'YEAR TOTAL', 'BLUEDART', 'QUIKJET CARGO', 'PRADHAAN AIR EXPRESS'])]
            
            data['airline'] = data['airline'].apply(standardize_airline_name)
            
            return data[['airline', 'passengers_carried']].reset_index(drop=True)
            
        except Exception as e:
            print(f"Warning: Could not parse Table 4.01: {e}")
            
    return pd.DataFrame(columns=['airline', 'passengers_carried'])


def _parse_table_501(base_path, years):
    """
    Attempts to parse the real DGCA Table 5.01 city-pair traffic XLSX.
    Falls back to simulated data only if the file is missing or unreadable.
    """
    yearly_dir = os.path.join(base_path, 'yearly statistics')
    table_501_path = os.path.join(yearly_dir, 'TABLE 5.01 (INDIAN CITY-WISE PASSENGER TRAFFIC).xlsx')
    
    if os.path.exists(table_501_path):
        try:
            import warnings as _w
            with _w.catch_warnings():
                _w.simplefilter('ignore', UserWarning)
                raw = pd.read_excel(table_501_path, engine='openpyxl')
            
            # The real file layout (2024-25):
            #   Row 0: "PASSENGERS ( IN NUMBER )"
            #   Row 1: column headers -> S.No., CITY 1, CITY 2, PASSENGERS TO CITY 2, PASSENGERS FROM CITY 2
            #   Row 2+: actual data
            #   Last rows: SUB TOTAL / TOTAL (filter out)
            
            # Assign proper column names from the header row (row index 1)
            raw.columns = ['serial', 'city_1', 'city_2', 'passengers_to_city2', 'passengers_from_city2']
            
            # Drop the header rows and footer rows
            data = raw.iloc[2:].copy()  # skip first 2 rows (title + header)
            
            # Convert passenger columns to numeric, coerce non-numeric ('-', 'NaN', text) to NaN
            data['passengers_to_city2'] = pd.to_numeric(
                data['passengers_to_city2'].astype(str).str.replace(',', '').str.strip(), errors='coerce'
            )
            data['passengers_from_city2'] = pd.to_numeric(
                data['passengers_from_city2'].astype(str).str.replace(',', '').str.strip(), errors='coerce'
            )
            
            # Drop footer rows (SUB TOTAL, TOTAL, or rows with NaN cities)
            data = data.dropna(subset=['city_1', 'city_2'])
            data = data[~data['city_1'].astype(str).str.upper().isin(['SUB TOTAL', 'TOTAL', 'NAN'])]
            data = data[~data['city_2'].astype(str).str.upper().isin(['SUB TOTAL', 'TOTAL', 'NAN'])]
            
            # Fill NaN passenger values with 0 (routes with '-' in the original)
            data['passengers_to_city2'] = data['passengers_to_city2'].fillna(0).astype(int)
            data['passengers_from_city2'] = data['passengers_from_city2'].fillna(0).astype(int)
            
            # Build the city_pairs dataframe
            city_pairs = pd.DataFrame({
                'year': 2024,  # Table 5.01 covers 2024-25 fiscal year
                'origin_city': data['city_1'].str.strip().str.title(),
                'destination_city': data['city_2'].str.strip().str.title(),
                'passengers_outbound': data['passengers_to_city2'].values,
                'passengers_inbound': data['passengers_from_city2'].values
            })
            city_pairs['total_two_way_traffic'] = city_pairs['passengers_outbound'] + city_pairs['passengers_inbound']
            
            return city_pairs.reset_index(drop=True)
        
        except Exception as e:
            # If parsing fails, fall through to simulated data
            print(f"Warning: Could not parse Table 5.01, falling back to simulated data. Error: {e}")
    
    # Fallback: simulated city-pair data
    city_records = []
    routes = [('DEL', 'BOM'), ('BLR', 'DEL'), ('BOM', 'BLR'), ('DEL', 'HYD'), ('CCU', 'DEL'),
              ('BOM', 'GOI'), ('DEL', 'PNQ'), ('BOM', 'MAA'), ('BLR', 'HYD'), ('MAA', 'DEL'),
              ('DEL', 'AMD'), ('BOM', 'HYD'), ('DEL', 'GOI'), ('CCU', 'BOM'), ('BLR', 'BOM'),
              ('HYD', 'BLR'), ('PNQ', 'DEL'), ('DEL', 'LKO'), ('BOM', 'AMD'), ('CCU', 'BLR')]
    
    for y in years:
        for i, (orig, dest) in enumerate(routes):
            base = (20 - i) * 10000
            if y in [2020, 2021]: base *= 0.4
            if y >= 2022: base *= 1.2
            city_records.append({
                'year': y,
                'origin_city': orig,
                'destination_city': dest,
                'passengers_outbound': base + np.random.randint(-1000, 1000),
                'passengers_inbound': base + np.random.randint(-1000, 1000)
            })
            
    city_pairs = pd.DataFrame(city_records)
    city_pairs['total_two_way_traffic'] = city_pairs['passengers_outbound'] + city_pairs['passengers_inbound']
    
    return city_pairs

def clean_statutory_data(base_path, tata_consolidation=False):
    """
    Generates simulated financial statutory data (revenues, expenses, fleet count).
    This simulates the mandatory Form EF financial filings required by the DGCA.
    """
    clean_statutory_file = os.path.join(base_path, 'statutory_data_clean.csv')
    if os.path.exists(clean_statutory_file):
        df = pd.read_csv(clean_statutory_file)
        if 'airline' in df.columns:
            df['airline'] = df['airline'].apply(standardize_airline_name)
        df = consolidate_tata(df, apply_consolidation=tata_consolidation)
        return df
        
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    airlines = CORE_CARRIERS + ['Regional Carriers']
    
    records = []
    for y in years:
        for a in airlines:
            records.append({
                'year': y,
                'airline': a,
                'operating_revenues': np.random.uniform(5000, 20000),
                'operating_expenses_fuel': np.random.uniform(2000, 8000),
                'operating_expenses_maint': np.random.uniform(1000, 3000),
                'operating_expenses_user': np.random.uniform(500, 1500),
                'operating_expenses_admin': np.random.uniform(1000, 4000),
                'operating_expenses_total': np.random.uniform(4500, 21000),
                'net_profit': np.random.uniform(-2000, 1000),
                'active_fleet_count': np.random.randint(10, 300),
                'block_hours_flown': np.random.uniform(50000, 500000),
                'workforce_headcount': np.random.randint(500, 10000),
                'pkp': np.random.uniform(1e8, 1e9),
                'ask': np.random.uniform(1e8, 1.5e9)
            })
            
    df = pd.DataFrame(records)
    df = consolidate_tata(df, apply_consolidation=tata_consolidation)
    return df

def clean_moca_daily_data(base_path, tata_consolidation=False):
    """
    Ingests and parses official daily operational statistics published by the
    Ministry of Civil Aviation (MoCA) and DGCA (from india-aviation-traffic-main/aggregated/daily.csv).
    
    Extracts:
    1. Daily On-Time Performance (OTP %) for domestic carriers (2021-2026).
    2. AirSewa Passenger Grievance breakdown by category (refunds, baggage, check-in, etc.).
    3. Passenger Grievances lodged per airline.
    4. Macro operational KPIs (National average OTP, total complaints processed).
    """
    daily_path = os.path.join(base_path, 'india-aviation-traffic-main', 'aggregated', 'daily.csv')
    if not os.path.exists(daily_path):
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
    
    df = pd.read_csv(daily_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)
    
    # 1. Daily OTP parsing
    otp_mapping = {
        'On Time Performance (Indigo)': 'IndiGo',
        'On Time Performance (Air India)': 'Air India',
        'On Time Performance (Akasa Air)': 'Akasa Air',
        'On Time Performance (Spicejet)': 'SpiceJet',
        'On Time Performance (Vistara)': 'Vistara',
        'On Time Performance (Air Asia)': 'AIX Connect',
        'On Time Performance (Alliance Air)': 'Alliance Air',
        'On Time Performance (GoAir)': 'GoAir'
    }
    
    otp_dfs = []
    for col, airline in otp_mapping.items():
        if col in df.columns:
            s = pd.to_numeric(df[col].astype(str).str.rstrip('%').str.strip(), errors='coerce')
            sub = pd.DataFrame({'Date': df['Date'], 'airline': airline, 'otp': s}).dropna()
            otp_dfs.append(sub)
    
    df_otp = pd.concat(otp_dfs, ignore_index=True) if otp_dfs else pd.DataFrame(columns=['Date', 'airline', 'otp'])
    df_otp['year'] = df_otp['Date'].dt.year
    
    # 2. Grievance categories
    griev_cat_mapping = {
        'Grievances (Refunds)': 'Ticket Refunds',
        'Grievances (Baggage)': 'Baggage Handling',
        'Grievances (Check-In)': 'Check-In & Boarding',
        'Grievances (Security Check)': 'Airport Security',
        'Grievances (Meals)': 'Flight Catering / Meals',
        'Grievances (Others)': 'Customer Service & Others'
    }
    cat_records = []
    for col, cat_name in griev_cat_mapping.items():
        if col in df.columns:
            val = pd.to_numeric(df[col], errors='coerce').sum()
            cat_records.append({'Category': cat_name, 'Count': val})
    df_griev_cat = pd.DataFrame(cat_records)
    
    # 3. Grievances per airline
    airline_griev_cols = {
        'Grievances (IndiGo)': 'IndiGo',
        'Grievances (Air India)': 'Air India',
        'Grievances (Akasa Air)': 'Akasa Air',
        'Grievances (Spicejet)': 'SpiceJet',
        'Grievances (Vistara)': 'Vistara',
        'Grievances (Air India Express)': 'Air India Express',
        'Grievances (Alliance Air)': 'Alliance Air',
        'Grievances (GoAir)': 'GoAir',
        'Grievances (Star Air)': 'Star Air',
        'Grievances (Flybig)': 'Flybig'
    }
    air_records = []
    for col, air_name in airline_griev_cols.items():
        if col in df.columns:
            cnt = pd.to_numeric(df[col], errors='coerce').sum()
            air_records.append({'airline': air_name, 'Grievances': cnt})
    df_griev_airline = pd.DataFrame(air_records)
    
    # Handle Tata Group consolidation if active
    if tata_consolidation:
        tata_members = ['Air India', 'Vistara', 'AIX Connect', 'Air India Express']
        df_otp['airline'] = df_otp['airline'].apply(lambda x: 'Air India Group' if x in tata_members else x)
        df_otp = df_otp.groupby(['Date', 'airline', 'year'])['otp'].mean().reset_index()
        
        df_griev_airline['airline'] = df_griev_airline['airline'].apply(lambda x: 'Air India Group' if x in tata_members else x)
        df_griev_airline = df_griev_airline.groupby('airline')['Grievances'].sum().reset_index()
    
    df_griev_airline = df_griev_airline.sort_values('Grievances', ascending=False).reset_index(drop=True)
    
    summary = {
        'national_otp_mean': df_otp['otp'].mean() if not df_otp.empty else 0,
        'total_grievances': df_griev_cat['Count'].sum() if not df_griev_cat.empty else 0,
        'total_resolved': pd.to_numeric(df.get('Grievances (Resolved)', pd.Series()), errors='coerce').sum(),
        'date_min': df_otp['Date'].min() if not df_otp.empty else None,
        'date_max': df_otp['Date'].max() if not df_otp.empty else None
    }
    
    return df_otp, df_griev_cat, df_griev_airline, summary
