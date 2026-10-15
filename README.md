# ✈️ Indian Domestic Aviation Delay and Performance Analysis (2018–Present)

> **A Comprehensive Academic Data Analytics & Aviation Intelligence Platform**  
> **Institution:** Centurion University of Technology and Management  
> **Student Team:** Prasun Kumar Biswas, Ipsita Priyadarshini, Omm Shree Hota  
> **Project Guide:** Dr. Amit Kumar Sahoo  

---

## 📌 Project Overview

Welcome to the **Indian Domestic Aviation Delay and Performance Analysis Platform**. Developed as a capstone data intelligence project, this platform examines airline operational punctuality, fleet capacity dynamics, domestic network topology, and airline financial sustainability in India from 2018 through 2026.

Our platform unifies four multi-tiered aviation datasets:
1. **Ministry of Civil Aviation (MoCA) Daily Operational Reports (2020–2026):**
   * Over 1,260 consecutive daily reports tracking official **On-Time Performance (OTP %)** for major scheduled carriers.
   * Real consumer complaint filings lodged through the Government of India's **AirSewa Grievance Portal** (covering ticket refunds, baggage losses, check-in delays, and airport security).
2. **Official Directorate General of Civil Aviation (DGCA) Annual & Monthly Abstracts:**
   * **Table 1 Series (1.01 to 1.08):** Individual carrier operational records (aircraft hours, departures, ASK, RPK, passenger load factors).
   * **Table 2 & 3 Series:** Aggregate scheduled domestic and private sector benchmarks.
   * **Table 4.01:** Audited annual passenger volumes and domestic market shares.
   * **Table 5.01:** Point-to-point passenger and freight volume across **835 domestic flight corridors**.
   * **Statutory Form EF / Form 1A–1G Filings:** Corporate financial filings detailing airline operating revenues, jet fuel bills, maintenance expenses, active fleet sizes, and employee headcount.
3. **Micro-Level Flight Operations Horizon (315,000+ Flight Bookings):**
   * Real flight schedules, fare classes, cabin types, and route corridors from domestic commercial aviation records (`economy.csv` and `business.csv`).

---

## 🌟 Dashboard Architecture & Navigation

The Streamlit web application is organized into **6 cohesive analytical modules**:

* **Tab 0: Flight Operations, Punctuality & Grievances**  
  * **Section 1 (MoCA Daily Monitoring):** Official daily On-Time Performance (OTP %) by airline, monthly punctuality trajectories (2021–2026), and a categorical breakdown of 230,000+ AirSewa passenger complaints (Refunds, Baggage, Check-In, Catering).
  * **Section 2 (Flight Booking Dynamics):** Weekly diurnal delay heatmaps (identifying bottleneck periods such as Friday and Sunday evenings) and ticket fare vs. arrival delay scatter plots.
* **Tab 1: Network Density & Corridor Bottlenecks**  
  * Evaluates India's top 15 busiest domestic corridors (proving that **Delhi–Mumbai** is the #1 corridor with 6.85M+ annual passengers) and analyzes directional inbound/outbound flow balance across city pairs.
* **Tab 2: Fleet Productivity & Capacity Economics**  
  * Box plots benchmarking Passenger Load Factors (PLF %) across carriers, domestic passenger market share distribution (highlighting IndiGo's 60%+ sector dominance), and an **interactive animated bubble chart** tracking carrier evolution across PLF vs. stage length from 2018 to 2024.
* **Tab 3: Pre- vs. Post-COVID Resilience Trajectory**  
  * Quantifies the pandemic shock (-60% volume contraction in 2020) and subsequent recovery velocity against the 2019 pre-COVID baseline. Features an **interactive animated racing bar chart** visualizing passenger volume expansion by airline over time.
* **Tab 4: Corporate Financial Health & Unit Economics**  
  * Compares Cost per Available Seat-Kilometer (CASK) against Revenue per Available Seat-Kilometer (RASK) under Form EF filings, examines total revenues vs. expenditures, and breaks down operating cost drivers (highlighting that Aviation Turbine Fuel accounts for ~38–42% of total operational expenditure).
* **Tab 5: Empirical Conclusions & Research Hypotheses**  
  * Evaluates three core research questions: the financial impact of the Tata Group consolidation, labor productivity differentials between LCCs and full-service carriers, and post-lockdown capacity deployment versus passenger demand.

---

## 👥 Airlines Evaluated

* **Core Scheduled Airlines:** IndiGo, Air India, Vistara, AIX Connect (formerly AirAsia India), Akasa Air, and SpiceJet.
* **Regional & Commuter Airlines:** Alliance Air, Star Air, Fly91, Flybig, and IndiaOne Air (benchmarked in regional groupings to maintain visual clarity).
* **Tata Group Consolidation Engine:** Includes a dynamic sidebar toggle that consolidates Air India, Vistara, and AIX Connect into a unified **Air India Group** entity across punctuality, market share, load factor, and financial metrics.

---

## 🛠️ Pipeline Architecture

```text
[ Raw DGCA Excel Files (1,300+) & MoCA Daily CSVs ]
                         │
                         ▼
             [ preprocess_dgca.py ]   ──> Extracts government tabular reports into validated CSVs
                         │
                         ▼
              [ pipeline/etl.py ]     ──> Cleans airline naming anomalies, parses MoCA OTP & AirSewa grievances
                         │
                         ▼
            [ pipeline/metrics.py ]   ──> Computes weighted PLF (ΣRPK/ΣASK), CASK, RASK, OTP %, CAGR
                         │
                         ▼
                   [ app.py ]         ──> Modern Streamlit interface with interactive Plotly visual analytics
```

---

## 🚀 Execution Instructions

### 1. Clone or Open the Repository:
```bash
cd "Indian aviation delay and performance analysis"
```

### 2. Activate Virtual Environment:
* **Windows (PowerShell):**
  ```powershell
  .\venv2\Scripts\Activate.ps1
  ```
* **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Required Dependencies:
```bash
pip install -r requirements.txt
```

### 4. Launch the Streamlit Web Application:
```bash
streamlit run app.py
```
*(If the system shell reports `streamlit: command not found`, launch directly via Python module:)*
```bash
python -m streamlit run app.py
```

The application will launch locally at `http://localhost:8501` (or `http://localhost:8502`).

---

## 💡 Methodological Standards & Transparency

To uphold strict academic defensibility for review panels:
1. **Weighted PLF Calculations:**  
   National Passenger Load Factor is calculated using industry-standard passenger-kilometers divided by available seat-kilometers ($\frac{\sum \text{RPK}}{\sum \text{ASK}} \times 100$). This prevents arithmetic bias (Simpson's Paradox) inherent in averaging percentage values of disparate fleet sizes.
2. **Form EF Financial Unit Normalization:**  
   DGCA Form EF entries reported in millions of INR are multiplied by $10^6$ during CASK/RASK calculation to accurately compute per-seat-kilometer cost and revenue figures.
3. **Arrival Delay Zero-Clipping:**  
   In operational delay summaries and heatmaps, arrival delays are clipped at zero ($\ge 0$ minutes) so that flights touching down ahead of schedule do not mathematically conceal the severity of delayed flights.
4. **AirSewa Grievance Tracking:**  
   Consumer complaints reflect verified Ministry of Civil Aviation AirSewa portal records, providing empirical insight into service delivery bottlenecks across the Indian domestic market.

---

## 📁 Repository File Guide

| File / Folder | Role & Description |
| :--- | :--- |
| `app.py` | Main Streamlit web application with modern CSS styling, interactive filters, and Plotly visual analytics. |
| `pipeline/etl.py` | Ingestion, naming standardization, MoCA daily OTP parsing, and Tata Group consolidation logic. |
| `pipeline/metrics.py` | Aviation mathematical functions (CASK, RASK, weighted PLF, stage length, labor productivity). |
| `preprocess_dgca.py` | Automated extractor processing 1,300+ government DGCA Excel files into clean tabular CSVs. |
| `project_objectives.md` | Traceability matrix linking all 18 project objectives directly to their corresponding dashboard charts. |
| `methodology.md` | Academic methodology documentation containing mathematical proofs, hypotheses, and analytical procedures. |
| `libraries_and_logic.md` | Comprehensive technical guide explaining package dependencies, caching protocols, and script structures. |
| `project_analysis.md` | Detailed analytical findings, corridor rankings, and industry conclusions. |
| `project_execution_summary.txt` | Complete execution log chronicling bug fixes, architectural upgrades, and validation steps. |
