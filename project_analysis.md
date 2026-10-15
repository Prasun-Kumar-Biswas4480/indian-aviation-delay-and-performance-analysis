# 📊 Full Project Analysis: Indian Domestic Aviation Performance (2018–Present)

> **Comprehensive Student Project Report**  
> **Prepared by:** Prasun Kumar Biswas, Ipsita Priyadarshini, Omm Shree Hota  
> **Faculty Guide:** Dr. Amit Kumar Sahoo  
> **Academic Department:** Computer Science & Data Engineering, Centurion University of Technology and Management  

---

## 1. Project Overview

| Project Detail | Description |
|---|---|
| **Project Title** | Indian Domestic Aviation Delay and Performance Analysis (2018–Present) |
| **Objective** | Build an interactive, visual data analytics platform to study how Indian airlines perform, handle delays, deploy flight capacity, resolve consumer grievances, and manage their finances before, during, and after the COVID-19 pandemic. |
| **Student Researchers** | **Prasun Kumar Biswas**, **Ipsita Priyadarshini**, **Omm Shree Hota** |
| **Faculty Guide** | **Dr. Amit Kumar Sahoo** |
| **University** | Centurion University of Technology and Management |
| **Technologies Used** | Python 3.12, Streamlit 1.64.0, Plotly 7.1.0, Pandas 3.0.6, NumPy 2.5.3, OpenPyXL 3.1.5 |
| **Data Sources** | • **Ministry of Civil Aviation (MoCA) Daily Reports:** 1,265 consecutive daily records of On-Time Performance (OTP %) and AirSewa passenger complaints<br>• **DGCA Table 1 Series (1.01–1.08):** Individual airline annual & monthly operational stats (RPK, ASK, PLF, departures, hours flown)<br>• **DGCA Table 2 Series (2.01–2.08):** All Scheduled Indian Airlines combined (national industry benchmark)<br>• **DGCA Table 3 Series (3.01–3.08):** All Scheduled Private Airlines combined (private sector benchmark)<br>• **DGCA Table 4.01:** Official airline domestic passenger market shares<br>• **DGCA Table 5.01:** 835 city-to-city route records<br>• **DGCA Statutory Forms D & EF (1A–1G):** Corporate financial filings (fuel, maintenance, revenue, fleet, employees)<br>• **Individual Flight Bookings:** 315,274 flight rows (`economy.csv` & `business.csv`) |

---

## 2. Platform Architecture & Data Integration Flow

```text
========================================================================================
                                 STEP 1: RAW DATA SOURCES
========================================================================================
  1. Ministry of Civil Aviation (MoCA) Daily Operational Reports (daily.csv - 1,299 days)
     • Official carrier-wise On-Time Performance (OTP %)
     • AirSewa consumer complaints (Refunds, Baggage, Check-In, Security)
  2. Individual Flight Bookings (economy.csv & business.csv - 315,274 rows)
  3. DGCA Table 1 Series (1.01 to 1.08): Individual Airline Operational Stats
  4. DGCA Table 2 Series (2.01 to 2.08): All Scheduled Indian Airlines Combined
  5. DGCA Table 3 Series (3.01 to 3.08): All Scheduled Private Airlines Combined
  6. DGCA Table 4.01: Annual Domestic Passenger Traffic & Validated Market Shares
  7. DGCA Table 5.01: 835 City-to-City Flight Corridors (Delhi–Mumbai, etc.)
  8. DGCA Forms D & EF / Forms 1A–1G: Corporate Financial & Fleet Reports
                                      │
                                      ▼
========================================================================================
                            STEP 2: PREPROCESSING SCRIPT
========================================================================================
  [ preprocess_dgca.py ] scans the 1,300+ government Excel files offline (Tables 1, 2, 3,
  and Forms D & EF) and extracts them into three clean summary CSV files:
  1. macro_data_clean.csv (78 rows of annual operational stats from Table 1.01)
  2. monthly_macro_data_clean.csv (120 rows of monthly stats from Tables 1.02–1.08, 2.xx, 3.xx)
  3. statutory_data_clean.csv (59 rows of corporate airline financials from Forms D & EF)
                                      │
                                      ▼
========================================================================================
                            STEP 3: CLEANING & ETL PIPELINE
========================================================================================
  [ pipeline/etl.py ]
  • Parses daily MoCA On-Time Performance (OTP %) and AirSewa consumer complaint counts.
  • Cleans airline names (standardizing variants to IndiGo, Air India, SpiceJet, Akasa Air, etc.).
  • Groups smaller regional airlines into 'Regional Carriers'.
  • Dynamically combines Air India, Vistara, and AIX Connect if the user turns on the
    'Tata Group Consolidation' toggle.
                                      │
                                      ▼
========================================================================================
                            STEP 4: AVIATION MATH CALCULATOR
========================================================================================
  [ pipeline/metrics.py ]
  • On-Time Performance (OTP %) using DGCA's 15-minute standard.
  • Weighted Passenger Load Factor (sum of RPK / sum of ASK * 100).
  • True CASK & RASK (with 1,000,000 scaling for Form EF financial numbers).
  • Labor Productivity (Passengers handled per airline employee).
                                      │
                                      ▼
========================================================================================
                         STEP 5: INTERACTIVE STREAMLIT WEBSITE
========================================================================================
  [ app.py ] renders 6 interactive tabs with Plotly charts, animated races,
  elevated metric cards with hover micro-animations, and responsive sidebar filters!
========================================================================================
```

---

## 3. Tour of the Dashboard (Tabs 0 to 5)

### 🛫 Tab 0: Flight Operations, Punctuality & Consumer Grievances

* **Section 1: Official Ministry of Civil Aviation Daily Monitoring**
  * **Top Metrics:** Official National OTP % (~76.6%), Most Punctual Airline (IndiGo / Tata Group depending on toggle), Total AirSewa Complaints Processed (232,000+), and Resolution Rate (99.2%).
  * **Official On-Time Performance (OTP %) by Carrier (Bar Chart):** Ranks verified punctuality percentages from daily government logs:
    1. **IndiGo:** 81.9%
    2. **Vistara:** 80.8%
    3. **Akasa Air:** 79.6%
    4. **AIX Connect:** 79.0%
    5. **Air India:** 76.8%
    6. **Alliance Air:** 67.2%
    7. **SpiceJet:** 66.0%
  * **AirSewa Consumer Grievances by Issue (Donut Chart):** Breaks down consumer complaints filed with the Ministry of Civil Aviation:
    * **Ticket Refunds:** ~30.8% (71,635 complaints) — the #1 source of passenger dissatisfaction.
    * **Baggage Handling:** ~15.1% (35,102 complaints).
    * **Check-In & Boarding:** ~6.3% (14,707 complaints).
    * **Airport Security Check:** ~3.2% (7,519 complaints).
    * **Flight Catering:** <1% (1,999 complaints).
    * **General Service & Other Inquiries:** ~43.6%.
  * **Monthly Punctuality Trend Trajectory (Line Chart):** Multi-line time series tracking monthly carrier punctuality from July 2021 through September 2026.
  * **Consumer Complaints Lodged by Airline (Bar Chart):** Displays total AirSewa complaints received per carrier (IndiGo: 33,504; Air India: 20,376; Akasa Air: 9,786; SpiceJet: 3,882; Vistara: 582).

* **Section 2: Route Dynamics & Fare Sensitivity (Flight Bookings)**
  * **Diurnal Average Delay Heatmap:** A 7-day $\times$ 4-time-window grid highlighting that **Friday and Sunday evenings** suffer the highest congestion because business and weekend travelers pack metro airports.
  * **Fare vs. Arrival Delay Scatter Plot:** Compares ticket prices against delay distributions to analyze fare sensitivity.

---

### 🗺️ Tab 1: Network Density & Busiest Routes in India (Table 5.01)

* **Top 15 Busiest Domestic Corridors (Horizontal Bar Chart):** Ranks the top domestic corridors in India based on annual passenger volume from DGCA Table 5.01 (835 city-pairs):
  1. **Delhi – Mumbai (DEL–BOM):** Undisputed #1 corridor in India, carrying over **6.85 Million passengers** annually.
  2. **Bengaluru – Delhi (BLR–DEL):** #2 route with ~4.32 Million passengers.
  3. **Bengaluru – Mumbai (BLR–BOM):** #3 route with ~3.89 Million passengers.
  4. **Delhi – Kolkata (DEL–CCU):** #4 route with ~3.15 Million passengers.
  5. **Delhi – Hyderabad (DEL–HYD):** #5 route with ~2.98 Million passengers.
* **Directional Flow Balance (Scatter Plot):** Plots outbound passengers ($x$-axis) against inbound passengers ($y$-axis). Corridors align along the 45-degree diagonal line, demonstrating symmetric bidirectional travel flows.

---

### 💺 Tab 2: Fleet Productivity & Capacity Economics

* **Passenger Load Factor Benchmark (Box Plot):** Compares how full each airline's planes fly across quarters.
* **Carrier Domestic Market Share (Pie Chart):** Uses official DGCA Table 4.01 data to reveal market concentration. **IndiGo dominates with over 60% of the entire Indian domestic market**, followed by the Air India Group (~26–28%), SpiceJet, and Akasa Air.
* **✨ Animated Bubble Chart (Airline Evolution):**  
  * **X-axis:** Passenger Load Factor (% filled seats).
  * **Y-axis:** Average Flight Distance (km).
  * **Bubble Size:** Total annual passenger volume.
  * Users can press **▶ Play** to watch bubbles evolve year by year from 2018 to 2024.

---

### 📈 Tab 3: Pre- vs. Post-COVID Resilience & Trajectory

* **Longitudinal Passenger Growth Curve (Line Chart):** Tracks domestic passengers from 2018 to 2024, displaying the sharp 60% pandemic crash in 2020 followed by a robust V-shaped recovery reaching record heights by 2024.
* **✨ Animated Racing Bar Chart (Passenger Volume Race 2018 $\rightarrow$ 2024):**  
  A horizontal racing bar chart where users press **▶ Play Race** to watch IndiGo pull ahead, all airlines shrink in 2020 during lockdowns, and competition intensify post-2022.
* **Capacity (ASK) vs. Demand (RPK) Tracking (Dual-Line Overlay):** Illustrates that in early 2022, carriers deployed capacity faster than demand recovered, creating temporary seat overhangs before full passenger return in 2023.

---

### 💰 Tab 4: Corporate Financial Health & Unit Economics

* **CASK vs. RASK Grouped Bar Chart:** Compares unit cost (red bar) against unit revenue (green bar) for each airline under DGCA Form EF filings.
* **Total Earning vs Total Spending by Airline (Bar Chart):** Compares absolute revenues against total expenses in Millions of Rupees.
* **Operating Cost Breakdown (Donut Chart):**
  * **Aviation Turbine Fuel (Jet Fuel):** The single largest expense, consuming **35% to 42%** of all airline operational spending.
  * **Aircraft Maintenance & Overhaul:** ~15% to 20%.
  * **Airport & User Charges:** ~12% to 16%.
  * **Administrative Overhead:** Balance of operating budget.

---

### 🎓 Tab 5: Empirical Conclusions & Answers to Research Questions

#### Question 1 (The Tata Group Takeover & Consolidation)
* **Finding:** Combining Air India, Vistara, and AIX Connect delivers fleet and engineering synergies. Enabling the **Tata Group Consolidation** toggle demonstrates that the unified *Air India Group* commands ~28% domestic market share, establishing the only counterweight to IndiGo's 60% sector dominance.

#### Question 2 (Airline Efficiency: Budget vs. Full-Service)
* **Finding:** Low-cost carriers (LCCs) achieve substantially higher labor productivity, handling over **8,000 passengers per employee per year** compared to **3,500 to 5,000** for legacy full-service models. This is driven by fleet commonality (Airbus A320 family), rapid 25–30 minute gate turnarounds, and outsourced ground handling.

#### Question 3 (Pandemic Recovery Dynamics)
* **Finding:** Following the lifting of domestic capacity restrictions in early 2022, airlines aggressively added flight frequencies to protect airport slots and gain market share, temporarily exceeding passenger demand before load factors normalized at 85%+ in 2023–2024.
