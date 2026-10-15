# 📖 Project Methodology & Analytical Framework

> **Academic Project Report**  
> **Prepared by:** Prasun Kumar Biswas, Ipsita Priyadarshini, Omm Shree Hota  
> **Faculty Guide:** Dr. Amit Kumar Sahoo  
> **Department:** Computer Science & Data Engineering, Centurion University of Technology and Management  

---

## 1. Research Motivation & Context

The Indian commercial aviation market is one of the fastest-growing civil aviation ecosystems globally. Yet, it operates under stringent structural challenges: acute fuel price volatility, foreign exchange sensitivity, high airport landing and parking tariffs, and dense airspace congestion across metro corridors like Delhi and Mumbai.

This research project conducts an empirical evaluation of the Indian domestic airline sector across three pivotal operational epochs:
1. **Pre-COVID Baseline (2018–2019):** Unconstrained passenger traffic growth and fleet expansion.
2. **Pandemic Disruption (2020–2021):** Total airspace shutdowns, phased capacity caps (33% to 80%), and severe carrier financial distress.
3. **Post-COVID Structural Realignment (2022–Present):** Strong passenger demand recovery, entry of new carriers (Akasa Air), and privatization/merger consolidation under the Tata Group.

---

## 2. Core Research Hypotheses & Evaluative Questions

Our analytical framework addresses three university capstone research questions:

* **Question 1: The Privatization & Consolidation Hypothesis (Tata Group)**  
  * *Did the acquisition and operational consolidation of Air India, Vistara, and AIX Connect yield immediate unit cost efficiencies or revenue synergies?*  
  * **Analytical Implementation:** We incorporated a dynamic multi-table toggle (*"Tata Group Consolidation"*) allowing evaluators to analyze the carriers either as discrete entities or unified as `Air India Group` across market share, load factor, and CASK/RASK metrics.
* **Question 2: Labor Productivity Differential (LCCs vs. FSCs)**  
  * *Do low-cost carriers (e.g., IndiGo) achieve structurally superior labor productivity (passengers carried per employee) relative to legacy full-service carrier models?*  
  * **Analytical Implementation:** Multi-source synthesis comparing regulatory workforce headcounts (Form EF filings) against annual passenger volumes.
* **Question 3: Capacity Recovery vs. Demand Velocity Post-Pandemic**  
  * *Did scheduled domestic carriers restore seat capacity (ASK) faster than real passenger demand (RPK) recovered post-lockdowns, creating transitory capacity overhangs?*  
  * **Analytical Implementation:** Longitudinal tracking of Available Seat-Kilometers against Revenue Passenger-Kilometers from 2018 through 2024.

---

## 3. Data Architecture & Ingestion Protocols

The platform harmonizes data across three complementary horizons:

### 3.1 Ministry of Civil Aviation (MoCA) Daily Monitoring Reports (2020–2026)
* Sourced from daily regulatory publications by the Ministry of Civil Aviation and historical snapshots preserved on Wayback Machine (`daily.csv`, 1,299 daily snapshots):
  * **Daily On-Time Performance (OTP %):** Over 1,260 consecutive days of verified punctuality percentages across scheduled carriers (IndiGo, Air India, Akasa Air, SpiceJet, Vistara, Alliance Air).
  * **AirSewa Consumer Grievance Monitoring:** Real-time customer dissatisfaction metrics categorizing over 230,000 complaints across Ticket Refunds, Baggage Mishandling, Check-In and Boarding Delays, and Security.

### 3.2 Directorate General of Civil Aviation (DGCA) Regulatory Publications
* **Table 1 Series (1.01 to 1.08):** Annual and monthly operational returns per airline (flight departures, block hours, aircraft-km, passengers, ASK, RPK, PLF).
* **Table 2 & 3 Series:** Aggregate benchmarks for All Scheduled Indian Airlines and All Private Scheduled Airlines.
* **Table 4.01:** Audited domestic passenger market share distributions.
* **Table 5.01:** Passenger and freight volumes across **835 domestic city-pair flight corridors**.
* **Statutory Forms D & EF / Forms 1A–1G:** Audited corporate financial statements (passenger revenue, jet fuel expenditure, maintenance, active fleet counts, workforce headcounts).
* **Historical Fiscal Year Crawl:** Automated extraction across fiscal directories (`17-18` to `23-24`) via `preprocess_dgca.py` utilizing recursive globbing and regex parsing.

### 3.3 Micro-Level Flight Operations Horizon
* Extensive commercial booking records (`economy.csv` and `business.csv`, 315,000+ flight records) capturing flight frequencies, scheduled departure windows, and fare pricing distributions.

---

## 4. Standardized Aviation Metrics & Mathematical Formulations

All mathematical derivations are encapsulated in `pipeline/metrics.py`:

### 4.1 Unit Cost: CASK (Cost per Available Seat Kilometer)
Because Form EF entries record expenditures in millions of INR, a $10^6$ multiplier is applied to derive per-unit Rupees:
$$\text{CASK} = \frac{\text{Operating Expenses (in Millions)} \times 10^6}{\text{Total ASK}}$$

### 4.2 Unit Revenue: RASK (Revenue per Available Seat Kilometer)
$$\text{RASK} = \frac{\text{Operating Revenue (in Millions)} \times 10^6}{\text{Total ASK}}$$

An airline achieves operating profitability when $\text{RASK} > \text{CASK}$.

### 4.3 Weighted Passenger Load Factor (Addressing Simpson's Paradox)
A simple arithmetic mean of load factor percentages introduces severe aggregation bias (*Simpson's Paradox*), as small regional aircraft routes would distort high-density trunk routes. We enforce true capacity weighting:
$$\text{PLF}\ (\%) = \left( \frac{\sum \text{RPK}}{\sum \text{ASK}} \right) \times 100$$

### 4.4 Labor Productivity Index
$$\text{Labor Productivity} = \frac{\text{Total Passengers Carried}}{\text{Total Airline Headcount}}$$

### 4.5 Average Stage Length
$$\text{Average Stage Length (km)} = \frac{\text{Total Kilometers Flown}}{\text{Total Flight Departures}}$$

### 4.6 Arrival Delay Zero-Clipping
In operational delay summaries, negative delay values (flights landing early) are bounded at zero:
$$\text{Delay}_{\text{clipped}} = \max(0, \text{Arrival Delay})$$
This prevents early touchdowns from artificially masking true flight delays.

---

## 5. Data Hygiene & Transformation Rules

Implemented in `pipeline/etl.py`:
1. **Dedicated Cargo Carrier Exclusion:** Dedicated freight operators (Blue Dart Aviation, Quikjet Cargo) are excluded from passenger PLF computations to avoid skewing commercial passenger metrics.
2. **Charter and Non-Scheduled Normalization:** Non-scheduled operators (Table 6) are isolated from scheduled passenger benchmarks.
3. **Nomenclature Harmonization:** Standardizes multi-format naming variants (`AIR_INDIA`, `AirAsia`, `AIX Express`) into unified keys and consolidates minor regional carriers into `Regional Carriers`.
4. **MoCA Daily Metric Ingestion:** Ingests percentage strings, cleans whitespace and headers, and aligns date ranges from July 2021 through September 2026.

---

## 6. Academic Disclaimers & Integrity Standards

1. **Dual-Horizon Grounding:** Punctuality metrics in Tab 0 combine verified **Ministry of Civil Aviation daily OTP reports** with micro-level booking delay heatmaps.
2. **Regulatory Reporting Latency:** In accordance with statutory audit timelines, audited Form EF filings follow government publication cycles.
