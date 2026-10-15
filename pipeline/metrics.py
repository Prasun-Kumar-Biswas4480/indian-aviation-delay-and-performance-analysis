import pandas as pd
import numpy as np

# ==========================================
# AVIATION KPI CALCULATOR
# ==========================================
# This module contains all the mathematical formulas used to calculate 
# industry-standard aviation Key Performance Indicators (KPIs).

# ------------------------------------------
# MICRO-OPERATIONAL METRICS
# ------------------------------------------

def calc_otp(df_flights):
    """Calculates On-Time Performance (OTP) percentage."""
    if len(df_flights) == 0: return 0
    ontime = df_flights[df_flights['is_delayed'] == 0]
    return (len(ontime) / len(df_flights)) * 100

def route_congestion_index(df_flights):
    """Calculates average arrival delays grouped by specific Origin-Destination routes."""
    if len(df_flights) == 0: return pd.DataFrame()
    return df_flights.assign(arrival_delay=df_flights['arrival_delay'].clip(lower=0)).groupby(['origin_airport', 'destination_airport', 'diurnal_window'])['arrival_delay'].mean().reset_index()

# ------------------------------------------
# MACRO-CAPACITY & PRODUCTIVITY METRICS
# ------------------------------------------

def calc_plf(df_macro):
    """
    Calculates system-wide Passenger Load Factor (PLF).
    Properly aggregates Total Revenue Passenger Kilometers (RPK) / Total Available Seat Kilometers (ASK)
    to avoid Simpson's Paradox (taking the flat average of percentages).
    """
    if 'rpk' in df_macro.columns and 'ask' in df_macro.columns:
        if df_macro['ask'].sum() == 0: return 0
        return (df_macro['rpk'].sum() / df_macro['ask'].sum()) * 100
    if 'pkp' in df_macro.columns and 'ask' in df_macro.columns:
        if df_macro['ask'].sum() == 0: return 0
        return (df_macro['pkp'].sum() / df_macro['ask'].sum()) * 100
    if 'plf' in df_macro.columns:
        return df_macro['plf'].mean()
    return 0

def calc_average_stage_length(df_macro):
    """Calculates the average flight distance per departure."""
    return df_macro['kilometers_flown'].sum() / df_macro['departures'].sum()

def calc_daily_utilization(df_stat):
    """Calculates aircraft utilization in block hours per day per aircraft."""
    return df_stat['block_hours_flown'].sum() / (df_stat['active_fleet_count'].sum() * 365)

# ------------------------------------------
# FINANCIAL & UNIT ECONOMICS METRICS
# ------------------------------------------

def calc_cask(df_stat):
    """Calculates Cost per Available Seat Kilometer (Operating Expenses / ASK)."""
    if df_stat['ask'].sum() == 0: return 0
    return (df_stat['operating_expenses_total'].sum() * 1e6) / df_stat['ask'].sum()

def calc_rask(df_stat):
    """Calculates Revenue per Available Seat Kilometer (Operating Revenues / ASK)."""
    if df_stat['ask'].sum() == 0: return 0
    return (df_stat['operating_revenues'].sum() * 1e6) / df_stat['ask'].sum()

def calc_labor_productivity(df_stat, df_macro):
    """Calculates average passengers handled per airline employee."""
    headcount = df_stat['workforce_headcount'].sum()
    if headcount == 0: return 0
    return df_macro['passengers_carried'].sum() / headcount

# ------------------------------------------
# LONGITUDINAL TRAJECTORY METRICS
# ------------------------------------------

def calc_recovery_velocity(df_macro, metric_col, current_year=2024):
    """Measures how much a metric (like passengers) has recovered compared to 2019 baseline (100%)."""
    baseline_2019 = df_macro[df_macro['year'] == 2019][metric_col].sum()
    current = df_macro[df_macro['year'] == current_year][metric_col].sum()
    if baseline_2019 == 0: return 0
    return (current / baseline_2019) * 100

def calc_cagr(df_macro, metric_col, start_year=2018, end_year=2024):
    """Calculates the Compound Annual Growth Rate (CAGR) for a given metric."""
    start_val = df_macro[df_macro['year'] == start_year][metric_col].sum()
    end_val = df_macro[df_macro['year'] == end_year][metric_col].sum()
    if start_val == 0: return 0
    n = end_year - start_year
    if end_val / start_val < 0: return 0
    return ((end_val / start_val) ** (1/n)) - 1
