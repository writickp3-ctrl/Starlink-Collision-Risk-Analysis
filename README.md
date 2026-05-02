# Starlink Constellation Collision Risk Analysis 🛰️

> End-to-end Python data engineering and ML pipeline for orbital proximity detection, collision risk scoring, brightness modeling, and Power BI dashboard visualization across Starlink megaconstellation datasets.

---

## Tech Stack

`Python` `Pandas` `NumPy` `SciPy` `KD-Tree` `SGP4` `Skyfield` `Scikit-learn` `Plotly` `Power BI`

---

## Project Overview

This project builds a complete analysis pipeline to detect and prioritize satellite collision risks in dense Low Earth Orbit (LEO) constellations. It fetches live TLE orbital data, propagates satellite trajectories using SGP4, applies KD-Tree spatial indexing for fast proximity detection, trains ML classifiers for collision prediction and brightness calibration, and exports everything into a three-page interactive Power BI dashboard.

---

## Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              Starlink_Optimized_Pipeline.py                   │
│                   ── Run this FIRST ──                        │
│                                                               │
│  Section 1  →  Setup & Imports                                │
│  Section 2  →  TLE Fetch from CelesTrak                       │
│  Section 3  →  SGP4 Orbital Propagation                       │
│  Section 4  →  Altitude Density Analysis                      │
│  Section 5  →  KD-Tree Proximity Detection  [O(n log n)]      │
│  Section 6  →  Satellite Brightness Modeling                  │
│  Section 7  →  SatNOGS Fetch & Calibration                    │
│  Section 8  →  ML Brightness Predictor (Gradient Boosting)    │
│  Section 9  →  Collision Risk Scoring & ML Classifier         │
│  Section 10 →  Synthetic Constellation (100 sats × 300 frames)│
│  Section 11 →  Plotly Interactive Dashboard (HTML)            │
│  Section 12 →  Power BI Export (6 structured CSVs)            │
│  Section 13 →  Summary & ZIP Export                           │
└───────────────────────┬──────────────────────────────────────┘
                        │ generates
                        ▼
     multi_satellite_dataset.csv
     collision_risk.csv
     passes_calibrated.csv
     calibration_data.csv
     collision_features.csv
     pbi_satellite_master.csv
     pbi_collision_events.csv
     pbi_risk_summary.csv
     pbi_orbital_density.csv
     pbi_launch_timeline.csv
     pbi_kpi_summary.csv
     starlink_dashboard.html
     roc_pr_curves.png
     altitude_density.png
                        │
          ┌─────────────┘
          ▼
┌──────────────────────────────────────────────────────────────┐
│                   powerbi_export.py                           │
│          ── OPTIONAL: standalone re-export only ──            │
│                                                               │
│  Use this ONLY when you want to regenerate the 6 Power BI    │
│  CSVs from the 2 raw input CSVs without re-running the full  │
│  pipeline above (e.g. to refresh the dashboard quickly).      │
│                                                               │
│  Reads:                                                       │
│    SpaceX Satellite Dataset.csv                               │
│    multi_satellite_collision_dataset.csv                      │
│                                                               │
│  Generates → same 6 pbi_*.csv files                          │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                   Power BI Desktop                            │
│                                                               │
│  Import the 6 pbi_*.csv files → build relational model       │
│  OR open Starlink_Dashboard.pbix directly                     │
│                                                               │
│  Page 1 → Collision Risk Overview                            │
│  Page 2 → Temporal Trends                                    │
│  Page 3 → Orbital Density & KD-Tree Analysis                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
Starlink-Collision-Risk-Analysis/
│
├── Starlink_Optimized_Pipeline.py         ← Full pipeline (run first)
├── powerbi_export.py                      ← Standalone PBI export (optional)
├── Starlink_project_data_science.ipynb    ← Original notebook (EDA + Plotly)
├── Starlink_Dashboard.pbix                ← Power BI Desktop dashboard
│
├── SpaceX Satellite Dataset.csv           ← Raw input (902 satellites)
├── multi_satellite_collision_dataset.csv  ← Raw input (800 events)
│
├── powerbi_data/
│   ├── pbi_satellite_master.csv           ← Satellite dimension table
│   ├── pbi_collision_events.csv           ← Encounter fact table
│   ├── pbi_risk_summary.csv               ← Per-satellite risk scores
│   ├── pbi_orbital_density.csv            ← KD-Tree density by altitude
│   ├── pbi_launch_timeline.csv            ← Cumulative launch trend
│   └── pbi_kpi_summary.csv                ← Single-row KPI summary
│
├── Dashboard Screenshots/
│   ├── page1_collision_risk_overview.png
│   ├── page2_temporal_trends.png
│   └── page3_orbital_density.png
│
├── collision_model.pkl                    ← Trained collision classifier
├── brightness_gb_model.joblib             ← Trained brightness predictor
├── run_summary.json                       ← Pipeline run metadata
└── README.md
```

---

## How to Run

### Step 0 — Install Dependencies

```bash
pip install sgp4 skyfield pandas numpy matplotlib scipy requests tqdm scikit-learn plotly python-dateutil joblib seaborn
```

In Google Colab:

```python
!pip install -q sgp4 skyfield pandas numpy matplotlib scipy requests tqdm scikit-learn plotly python-dateutil joblib seaborn
```

---

### Step 1 — Run the Full Pipeline

```bash
python Starlink_Optimized_Pipeline.py
```

This runs all 13 sections end to end and generates every output file automatically. All 6 Power BI CSVs are produced here — **you do not need to run `powerbi_export.py` after this.**

What each section produces:

| Section | Output |
|---|---|
| TLE Fetch | `starlink_latest.txt` |
| SGP4 Propagation | In-memory position DataFrame |
| Altitude Density | `altitude_density.png` |
| KD-Tree Detection | `collision_features.csv` |
| Brightness Modeling | Skyfield pass objects |
| SatNOGS Calibration | `calibration_data.csv` |
| ML Brightness | `brightness_gb_model.joblib` + `passes_calibrated.csv` |
| Collision Scoring | `collision_risk.csv` + `roc_pr_curves.png` + `collision_model.pkl` |
| Synthetic Dataset | `multi_satellite_dataset.csv` |
| Plotly Dashboard | `starlink_dashboard.html` |
| Power BI Export | All 6 `pbi_*.csv` files |
| Summary | `run_summary.json` + `starlink_export_all.zip` |

---

### Step 2 — Power BI Export (Optional)

Only run this if you want to **regenerate the 6 Power BI tables from the 2 raw CSVs** without running the full pipeline:

```bash
python powerbi_export.py
```

**When to use `powerbi_export.py`:**
- You updated the raw CSVs and only need fresh PBI tables
- You want to demo the dashboard without running ML/SGP4
- You are on a machine without SGP4 or Skyfield installed

**Reads:**
```
SpaceX Satellite Dataset.csv
multi_satellite_collision_dataset.csv
```

**Generates in `./powerbi_data/`:**

| File | Description | Rows |
|---|---|---|
| `pbi_satellite_master.csv` | Orbital params, orbit shell classification | 902 |
| `pbi_collision_events.csv` | Events with risk tiers, timestamps, positions | 800 |
| `pbi_risk_summary.csv` | Composite risk scores per satellite | 4 |
| `pbi_orbital_density.csv` | KD-Tree neighbor counts at 10/50/100 km | 4 |
| `pbi_launch_timeline.csv` | Cumulative satellite launches over time | 11 |
| `pbi_kpi_summary.csv` | Single-row headline KPIs for cards | 1 |

---

### Step 3 — Open the Power BI Dashboard

1. Download [Power BI Desktop](https://powerbi.microsoft.com/desktop) — free
2. Open `Starlink_Dashboard.pbix` — data loads automatically
3. Or import fresh: **Home → Get Data → Text/CSV** → load all 6 files from `powerbi_data/`

**Dashboard Pages:**

| Page | Visuals |
|---|---|
| Page 1 — Collision Risk Overview | 4 KPI cards, bar chart of max Pc per satellite, donut chart of risk tier distribution, ranked risk table |
| Page 2 — Temporal Trends | Collision probability over time, event frequency by hour of day, cumulative launch timeline |
| Page 3 — Orbital Density & KD-Tree | Scatter of altitude vs neighbor count, crowded altitude band bar chart, density risk donut, KD-Tree KPI cards |

---

## Key Technical Contributions

### KD-Tree Spatial Indexing
Replaces O(n²) brute-force pairwise comparison with O(n log n) `cKDTree` proximity search. At 4,000-satellite Starlink scale this is approximately **166× faster** than brute force.

```python
tree  = cKDTree(coords)          # Build: O(n log n)
pairs = tree.query_pairs(r=5.0)  # Query: O(n log n)
```

### Composite Risk Score (0–100)
```
Score = 50% × avg_collision_probability (normalised)
      + 30% × fraction of critical-tier events
      + 20% × historical close encounter count (normalised)
```

### Risk Tier Classification

| Tier | Collision Probability |
|---|---|
| Low | < 0.001 |
| Medium | 0.001 – 0.005 |
| High | 0.005 – 0.01 |
| Critical | ≥ 0.01 |

### ML Collision Classifier
Gradient Boosting Classifier trained on `distance_km`, `rel_speed`, `range_rate`, `hist_close_count`. Acts as a rapid triage layer — reserves expensive covariance-based Pc computation only for the top flagged pairs.

### Calibrated Brightness Model
Gradient Boosting Regressor calibrated against SatNOGS observational records. Predicts apparent visual magnitude per pass using elevation angle and Sun–satellite–observer phase geometry.

---

## Datasets

| File | Description | Records |
|---|---|---|
| `SpaceX Satellite Dataset.csv` | Real Starlink orbital parameters, launch info, NORAD numbers | 902 |
| `multi_satellite_collision_dataset.csv` | Simulated multi-satellite encounter events with 3D ECI positions | 800 |

---

## Results Summary

| Metric | Value |
|---|---|
| Min observed distance | 0.12 km |
| Total collision events | 800 |
| Avg observed distance | 9.57 km |
| Risk distribution | 48.5% Medium, 40.73% Low, 10.76% High |
| KD-Tree complexity | O(n log n) vs O(n²) brute-force |
| Complexity improvement | ~166× faster at 4,000-satellite scale |

---

## Interview Statement

> *"I built a Python pipeline using SGP4 propagation and KD-Tree spatial indexing to process orbital datasets and compute satellite proximity at O(n log n) complexity — approximately 166× faster than brute force at Starlink scale. I trained a Gradient Boosting classifier for collision triage and a calibrated photometric model for brightness prediction using SatNOGS observations. I then exported six structured tables into Power BI, built a relational star-schema data model, and designed a three-page dashboard covering collision risk distribution, temporal trends, and orbital density analysis by altitude band."*

---

## Author

**Writick Parui**
M.E. CSE @ Thapar Institute of Engineering & Technology (TIET), Patiala
CGPA: 9.72 | GATE 2025 Qualified | Ex-TCS iON Intern

GitHub: [@writickp3-ctrl](https://github.com/writickp3-ctrl)

---

## License

For educational and research purposes only.
