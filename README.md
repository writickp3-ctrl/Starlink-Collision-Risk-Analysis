# Starlink Constellation Collision Risk Analysis 🛰️

> Python data engineering pipeline for orbital proximity detection, risk scoring, and Power BI dashboard visualization across multi-satellite datasets.

---

## Tech Stack

`Python` `Pandas` `NumPy` `SciPy` `KD-Tree` `Power BI`

---

## Project Overview

This project builds an end-to-end data engineering and analytics pipeline to detect and prioritize satellite collision risks in dense Low Earth Orbit (LEO) constellations. It processes large orbital datasets, applies KD-Tree spatial indexing for fast proximity detection, generates composite risk scores per satellite, and visualizes insights through a multi-page Power BI dashboard.

---

## Pipeline Architecture

```
Raw Orbital Data (CSV)
        │
        ▼
 Python Data Pipeline (powerbi_export.py)
        │
        ├── KD-Tree Proximity Search (SciPy cKDTree)
        ├── Risk Scoring & Tier Classification
        ├── Orbital Density Analysis by Altitude Band
        └── Structured Export → 6 Power BI-ready CSVs
                │
                ▼
        Power BI Desktop
                │
                ├── Page 1: Collision Risk Overview
                ├── Page 2: Temporal Trends
                └── Page 3: Orbital Density & KD-Tree Analysis
```

---

## Key Features

**Data Engineering**
- Built Python pipelines to process raw orbital datasets (position vectors, timestamps, collision probabilities) using Pandas and NumPy
- Applied `scipy.spatial.cKDTree` for O(n log n) satellite proximity search — detecting close-approach pairs within 10km, 50km, and 100km radius shells
- Reduced brute-force O(n²) lookup complexity via KD-Tree spatial indexing

**Risk Scoring**
- Classified satellite encounters into Low / Medium / High / Critical risk tiers based on collision probability thresholds
- Computed a composite risk score (0–100) per satellite using weighted signals: average collision probability, critical event frequency, and historical close-encounter count
- Exported aggregated risk rankings as structured, analysis-ready datasets

**Power BI Dashboard**
- Designed a relational data model across 6 exported tables in Power BI Desktop
- Built 3 interactive dashboard pages covering collision risk distribution, temporal trends, and KD-Tree orbital density analysis
- Enabled drill-down filtering by satellite ID, risk tier, and time period

---

## Dashboard Pages

### Page 1 — Collision Risk Overview
KPI cards (total events, critical events, avg collision probability, min observed distance) + bar chart of max collision probability per satellite + donut chart of risk tier distribution + ranked risk summary table.

### Page 2 — Temporal Trends
Collision probability over time, event frequency by hour of day, cumulative satellite launch timeline.

### Page 3 — Orbital Density & KD-Tree Analysis
Scatter plot of altitude vs neighbor count (sized by 10km proximity), bar chart of crowded altitude bands, density risk donut chart, KPI cards for KD-Tree close pairs and average neighbors within 50km.

> **Screenshots:** See `/Dashboard Screenshots/` folder in this repo.

---

## Repository Structure

```
Starlink-Collision-Risk-Analysis/
│
├── Starlink_project_data_science.ipynb   # Main analysis notebook (EDA, ML, Plotly)
├── powerbi_export.py                     # Python pipeline → generates Power BI CSVs
├── Starlink_Dashboard.pbix               # Power BI Desktop dashboard file
│
├── SpaceX Satellite Dataset.csv          # Raw satellite master data (902 satellites)
├── multi_satellite_collision_dataset.csv # Multi-satellite collision event data (800 events)
│
├── pbi_satellite_master.csv             # Power BI Table 1 — satellite attributes
├── pbi_collision_events.csv             # Power BI Table 2 — event-level data
├── pbi_risk_summary.csv                 # Power BI Table 3 — per-satellite risk scores
├── pbi_orbital_density.csv              # Power BI Table 4 — KD-Tree density analysis
├── pbi_launch_timeline.csv              # Power BI Table 5 — launch trend data
├── pbi_kpi_summary.csv                  # Power BI Table 6 — KPI card values
│
└── Dashboard Screenshots/
    ├── page1_collision_risk_overview.png
    ├── page2_temporal_trends.png
    └── page3_orbital_density.png
```

---

## How to Run

**1. Generate Power BI datasets:**
```bash
pip install pandas numpy scipy
python powerbi_export.py
```
This produces all 6 `pbi_*.csv` files in a `powerbi_data/` folder.

**2. Open the dashboard:**
- Download [Power BI Desktop](https://powerbi.microsoft.com/desktop) (free)
- Open `Starlink_Dashboard.pbix`
- All data loads automatically from the embedded model

**3. Explore the notebook:**
- Open `Starlink_project_data_science.ipynb` in Jupyter or Google Colab
- Contains full EDA, Plotly visualizations, and ML-based brightness modeling

---

## Datasets

| File | Description | Rows |
|---|---|---|
| SpaceX Satellite Dataset.csv | Satellite orbital parameters, launch info | 902 |
| multi_satellite_collision_dataset.csv | Simulated multi-satellite encounter events | 800 |

---

## Author

**Writick Parui**
M.E. CSE @ Thapar Institute of Engineering & Technology (TIET), Patiala
CGPA: 9.72 | GATE 2025 Qualified | Ex-TCS iON Intern

GitHub: [@writickp3-ctrl](https://github.com/writickp3-ctrl)

---

## License

For educational and research purposes only.
