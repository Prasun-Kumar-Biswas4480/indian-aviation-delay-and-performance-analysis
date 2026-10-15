# 💻 Technical Guide: Python Libraries & Code Logic

> **Student Technical Manual**  
> **Prepared by:** Prasun Kumar Biswas, Ipsita Priyadarshini, Omm Shree Hota  
> **Faculty Guide:** Dr. Amit Kumar Sahoo  
> **Institution:** Centurion University of Technology and Management  

---

## 1. The Python Libraries We Used (and Why)

When building this analytics platform, we selected a modern Python stack optimized for high-performance numerical operations, reactive web presentation, and responsive data visualization.

### 1.1 `streamlit` (Version 1.64.0) — Reactive Web Framework
* **Purpose:** Streamlit provides a declarative Python interface for web deployment without requiring custom JavaScript frontends or separate REST APIs.
* **Key Platform Implementations:**
  * Global sidebar layout housing multi-select filters, operating era slicers, and dynamic consolidation toggles.
  * Tabbed layout dividing analysis across 6 dedicated modules.
  * Custom CSS injection styling elevated KPI metric cards with hover micro-animations (`transform: translateY(-3px)`).
  * In-memory caching via **`@st.cache_data`** wrapping `load_data_v12()`, ensuring that 315,000+ booking records and multi-year government CSVs are parsed only once.

### 1.2 `pandas` (Version 3.0.6) — Data Transformation Engine
* **Purpose:** High-performance tabular data manipulation and aggregation.
* **Key Platform Implementations:**
  * Ingests MoCA daily operational CSVs, flight booking datasets (`economy.csv`, `business.csv`), and DGCA Excel extracts.
  * Executes multi-dimensional group-by aggregations (e.g., airline punctuality over time, corridor traffic, cost drivers).
  * Implements dynamic era slicing (`filter_era()`) based on user-selected time horizons.
  * Handles time series conversion and date extraction for longitudinal monthly trends.

### 1.3 `numpy` (Version 2.5.3) — Numerical Operations & Safe Math
* **Purpose:** Vectorized numerical operations and data transformation.
* **Key Platform Implementations:**
  * Uses `clip(lower=0)` on flight arrival delay distributions so that early touchdowns do not offset positive delays in summary metrics.
  * Replaces zero values with `np.nan` prior to division operations to prevent division-by-zero runtime exceptions.
  * Handles statistical distributions and array aggregations.

### 1.4 `plotly.express` & `plotly.graph_objects` (Version 7.1.0) — Interactive Visualization
* **Purpose:** Interactive browser-based data visualization.
* **Key Platform Implementations:**
  * **Plotly Express:** Powers horizontal OTP bars, AirSewa grievance donut charts, diurnal delay heatmaps, corridor rankings, and animated charts.
  * **Plotly Graph Objects:** Generates dual-line tracking charts (Capacity ASK vs. Demand RPK) and grouped financial bars (CASK vs. RASK, Revenue vs. Expenditure).
  * **Custom Hover Templates:** Every visualization implements tailored hover templates displaying clean formatting (e.g., `Total Traffic: 6,854,230 Pax` or `Fare: ₹8,450`) rather than raw dataframe column names.

### 1.5 `openpyxl` & `xlrd` — DGCA Excel Batch Ingestion
* **Purpose:** Reading legacy `.xls` and modern `.xlsx` workbooks published by the DGCA across historical reporting archives.

---

## 2. Platform Architecture & Module Breakdown

```text
├── app.py                     <-- Main Web Application & Reactive Presentation Layer
├── pipeline/
│   ├── etl.py                 <-- Ingestion, Cleaning & Standardization Engine
│   └── metrics.py             <-- Pure Aviation Financial & Operational Math Module
├── preprocess_dgca.py         <-- Automated Batch Extractor for 1,300+ Government Excel Reports
└── india-aviation-traffic-main/
    └── aggregated/
        └── daily.csv          <-- Official MoCA Daily OTP & AirSewa Grievance Records
```

---

### 2.1 `app.py` — Web Presentation Layer
* **Visual Design:** Injects custom styling providing a sleek `#F8FAFC` background, elevated KPI metric cards, and responsive tabs.
* **Global Filters & Sidebar:**
  * *Operating Era:* Slices data across Pre-COVID (2018–2019), Pandemic (2020–2021), Post-COVID Recovery (2022–Present), or All.
  * *Tata Group Consolidation Toggle:* Merges Air India, Vistara, and AIX Connect into a unified entity called "Air India Group".
  * *Carriers Multi-Select:* Permits isolated or comparative multi-carrier analysis.
  * *Diurnal Time Window:* Filters flight records into Morning, Afternoon, Evening, or Red-Eye departures.
* **Tab Breakdown:**
  * **Tab 0:** Two-tiered view: (1) Official MoCA daily punctuality rankings, monthly trends, and AirSewa grievance breakdowns, followed by (2) flight route congestion and fare sensitivity.
  * **Tab 1:** Top 15 busiest domestic corridors and directional flow balance.
  * **Tab 2:** PLF benchmarks, domestic market shares, and animated bubble chart of carrier evolution.
  * **Tab 3:** Pre- vs. Post-COVID recovery trajectory, capacity vs. demand, and animated passenger racing bar chart.
  * **Tab 4:** Unit economics (CASK/RASK), absolute corporate profitability, and operating expenditure breakdown.
  * **Tab 5:** Research hypotheses and academic conclusions.

---

### 2.2 `pipeline/etl.py` — Ingestion & Cleaning Engine
* **`standardize_airline_name(name)`:** Sanitizes carrier nomenclature, groups regional operators (`Alliance Air`, `Star Air`, `Fly91`, `Flybig`, `IndiaOne Air`) into a cohesive `Regional Carriers` cohort, and cleans whitespace/casing.
* **`consolidate_tata(df, ...)`:** Dynamically consolidates Tata Group carriers into `Air India Group`.
* **`clean_moca_daily_data(base_path, tata_consolidation)`:** Ingests official Ministry of Civil Aviation daily reports (`daily.csv`):
  * Extracts multi-carrier daily On-Time Performance (OTP %) over 1,260+ operational days.
  * Parses AirSewa passenger complaints across categories (Ticket Refunds, Baggage Handling, Check-In, Security, Catering).
  * Computes carrier-level complaint totals and national benchmark OTP.
* **`clean_flights_data()`:** Prepares 315,000+ flight booking records from `economy.csv` and `business.csv`, categorizes departure windows, and incorporates synthetic Akasa Air entries for post-2022 coverage.
* **`clean_macro_tables()`:** Loads preprocessed DGCA Table 1, Table 4.01 (market share), and Table 5.01 (835 city-pair corridors).
* **`clean_statutory_data()`:** Normalizes financial records from DGCA Forms D & EF.

---

### 2.3 `pipeline/metrics.py` — Aviation Math Calculator
A pure function library without I/O or state side-effects:
* **`calc_otp(df_flights)`:** Computes operational on-time percentages based on 15-minute standard arrival thresholds.
* **`route_congestion_index(df_flights)`:** Computes route-level average delays with zero-clipping.
* **`calc_plf(df_macro)`:** Calculates weighted Passenger Load Factor: $\frac{\sum \text{RPK}}{\sum \text{ASK}} \times 100$, avoiding Simpson's Paradox.
* **`calc_average_stage_length(df_macro)`:** Calculates mean flight distance ($\text{Kilometers Flown} / \text{Departures}$).
* **`calc_daily_utilization(df_stat)`:** Computes daily aircraft block hours ($\text{Hours} / (\text{Active Aircraft} \times 365)$).
* **`calc_cask(df_stat)` & `calc_rask(df_stat)`:** Computes Cost per ASK and Revenue per ASK, scaling Form EF million-INR figures by $10^6$.
* **`calc_labor_productivity(df_stat, df_macro)`:** Computes passengers handled per employee ($\text{Passengers} / \text{Headcount}$).
* **`calc_recovery_velocity(df_macro, ...)`:** Measures traffic indexing relative to the 2019 pre-COVID baseline (2019 = 100%).
* **Mathematical Safeguards:** All functions implement zero-denominator guards (`if denom == 0: return 0`).

---

### 2.4 `preprocess_dgca.py` — Automated Batch Extractor
Processes 1,300+ government Excel files across the `yearly statistics/` and `monthly statistics/` directories into three compact CSVs:
1. `macro_data_clean.csv` (Annual operational statistics from DGCA Tables 1, 2, and 3).
2. `monthly_macro_data_clean.csv` (Monthly operational breakdowns).
3. `statutory_data_clean.csv` (Audited financial metrics from Forms D & EF).

This offline extraction ensures that the live web application launches in just 2 to 3 seconds.
