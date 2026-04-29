"""
powerbi_export.py
=================
Starlink Collision Risk Analysis — Power BI Data Export Pipeline
Author: Writick Parui | M.Tech CSE, Thapar University

This script reads the raw project datasets and generates structured,
Power BI-ready CSV tables. Import these CSVs into Power BI Desktop
to build the collision risk dashboard described in POWERBI_DASHBOARD.md.

Usage:
    python powerbi_export.py

Output folder: ./powerbi_data/
    ├── pbi_satellite_master.csv
    ├── pbi_collision_events.csv
    ├── pbi_risk_summary.csv
    ├── pbi_orbital_density.csv
    ├── pbi_launch_timeline.csv
    └── pbi_kpi_summary.csv
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.spatial import cKDTree

# ── Output directory ──────────────────────────────────────────────────────────
OUT_DIR = "powerbi_data"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Input files ───────────────────────────────────────────────────────────────
SPACEX_CSV   = "SpaceX Satellite Dataset.csv"
MULTI_CSV    = "multi_satellite_collision_dataset.csv"

print("=" * 60)
print("  Starlink Collision Risk — Power BI Export Pipeline")
print("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 1 — Satellite Master (from SpaceX dataset)
# Fields: satellite_id, name, orbit_type, perigee_km, apogee_km,
#         inclination_deg, period_min, launch_mass_kg, launch_date,
#         expected_lifetime_yrs, launch_site, launch_vehicle,
#         altitude_mean_km, eccentricity, orbit_shell
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1/6] Building pbi_satellite_master.csv ...")

df_spacex = pd.read_csv(SPACEX_CSV, index_col=0)
df_spacex.columns = df_spacex.columns.str.strip()

master = pd.DataFrame()
master["satellite_id"]        = df_spacex.get("Satellite ID(Fake)", df_spacex.index + 1)
master["name"]                = df_spacex.get("Current Official Name of Satellite", "Unknown")
master["country_operator"]    = df_spacex.get("Country of Operator/Owner", "Unknown")
master["orbit_class"]         = df_spacex.get("Class of Orbit", "Unknown")
master["orbit_type"]          = df_spacex.get("Type of Orbit", "Unknown")
master["perigee_km"]          = pd.to_numeric(df_spacex.get("Perigee (km)"), errors="coerce")
master["apogee_km"]           = pd.to_numeric(df_spacex.get("Apogee (km)"),  errors="coerce")
master["altitude_mean_km"]    = (master["perigee_km"] + master["apogee_km"]) / 2
master["eccentricity"]        = pd.to_numeric(df_spacex.get("Eccentricity"), errors="coerce")
master["inclination_deg"]     = pd.to_numeric(df_spacex.get("Inclination (degrees)"), errors="coerce")
master["period_min"]          = pd.to_numeric(df_spacex.get("Period (minutes)"), errors="coerce")
master["launch_mass_kg"]      = pd.to_numeric(df_spacex.get("Launch Mass (kg.)"), errors="coerce")
master["launch_date"]         = pd.to_datetime(df_spacex.get("Date of Launch"), errors="coerce")
master["expected_lifetime_yrs"] = pd.to_numeric(df_spacex.get("Expected Lifetime (yrs.)"), errors="coerce")
master["launch_site"]         = df_spacex.get("Launch Site", "Unknown")
master["launch_vehicle"]      = df_spacex.get("Launch Vehicle", "Unknown")
master["norad_number"]        = pd.to_numeric(df_spacex.get("NORAD Number"), errors="coerce")
master["cospar_number"]       = df_spacex.get("COSPAR Number", "Unknown")

# Orbit shell classification based on altitude
def classify_shell(alt):
    if pd.isna(alt):    return "Unknown"
    if alt < 400:       return "VLEO (<400 km)"
    elif alt < 600:     return "Shell-1 (400–600 km)"
    elif alt < 800:     return "Shell-2 (600–800 km)"
    elif alt < 1200:    return "Shell-3 (800–1200 km)"
    else:               return "MEO (>1200 km)"

master["orbit_shell"] = master["altitude_mean_km"].apply(classify_shell)

# Launch year for time-series
master["launch_year"] = master["launch_date"].dt.year

out_path = os.path.join(OUT_DIR, "pbi_satellite_master.csv")
master.to_csv(out_path, index=False)
print(f"    ✔ Saved {len(master)} rows → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 2 — Collision Events (from multi-satellite dataset)
# Fields: event_id, timestamp, satellite_id, x_km, y_km, z_km,
#         distance_km, relative_speed, range_rate,
#         hist_close_count, collision_probability, risk_tier
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/6] Building pbi_collision_events.csv ...")

df_multi = pd.read_csv(MULTI_CSV)
df_multi.columns = df_multi.columns.str.strip().str.lower().str.replace(" ", "_")

events = pd.DataFrame()
events["timestamp"]            = pd.to_datetime(df_multi.get("timestamp"), errors="coerce")
events["satellite_id"]         = df_multi.get("satellite_id", "Unknown")
events["x_km"]                 = pd.to_numeric(df_multi.get("x_km"), errors="coerce")
events["y_km"]                 = pd.to_numeric(df_multi.get("y_km"), errors="coerce")
events["z_km"]                 = pd.to_numeric(df_multi.get("z_km"), errors="coerce")
events["distance_km"]          = pd.to_numeric(df_multi.get("distance_km"), errors="coerce")
events["relative_speed"]       = pd.to_numeric(df_multi.get("relative_speed"), errors="coerce")
events["range_rate"]           = pd.to_numeric(df_multi.get("range_rate"), errors="coerce")
events["hist_close_count"]     = pd.to_numeric(df_multi.get("hist_close_count"), errors="coerce").fillna(0).astype(int)
events["collision_probability"] = pd.to_numeric(df_multi.get("collision_probability"), errors="coerce")

# Risk tier classification
def risk_tier(prob):
    if pd.isna(prob):   return "Unknown"
    if prob < 0.001:    return "Low"
    elif prob < 0.005:  return "Medium"
    elif prob < 0.01:   return "High"
    else:               return "Critical"

events["risk_tier"] = events["collision_probability"].apply(risk_tier)

# Time features for Power BI time intelligence
events["date"]       = events["timestamp"].dt.date
events["hour"]       = events["timestamp"].dt.hour
events["day_of_week"] = events["timestamp"].dt.day_name()
events["week_number"] = events["timestamp"].dt.isocalendar().week.astype(int)
events["month"]       = events["timestamp"].dt.month_name()

# Event ID
events.insert(0, "event_id", range(1, len(events) + 1))

out_path = os.path.join(OUT_DIR, "pbi_collision_events.csv")
events.to_csv(out_path, index=False)
print(f"    ✔ Saved {len(events)} rows → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 3 — Risk Summary per Satellite (aggregated)
# Fields: satellite_id, total_events, avg_collision_probability,
#         max_collision_probability, min_distance_km, avg_distance_km,
#         critical_events, high_events, medium_events, low_events,
#         avg_relative_speed, risk_score_composite
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3/6] Building pbi_risk_summary.csv ...")

risk_summary = events.groupby("satellite_id").agg(
    total_events          = ("event_id",              "count"),
    avg_collision_prob    = ("collision_probability",  "mean"),
    max_collision_prob    = ("collision_probability",  "max"),
    min_distance_km       = ("distance_km",            "min"),
    avg_distance_km       = ("distance_km",            "mean"),
    avg_relative_speed    = ("relative_speed",         "mean"),
    total_hist_encounters = ("hist_close_count",       "sum"),
).reset_index()

# Per-tier counts
tier_counts = events.groupby(["satellite_id", "risk_tier"]).size().unstack(fill_value=0).reset_index()
for tier in ["Low", "Medium", "High", "Critical"]:
    if tier not in tier_counts.columns:
        tier_counts[tier] = 0

risk_summary = risk_summary.merge(
    tier_counts[["satellite_id", "Low", "Medium", "High", "Critical"]],
    on="satellite_id", how="left"
)
risk_summary.rename(columns={
    "Low": "low_events", "Medium": "medium_events",
    "High": "high_events", "Critical": "critical_events"
}, inplace=True)

# Composite risk score (0–100): weighted average of normalised signals
max_prob  = risk_summary["max_collision_prob"].max() or 1
max_hist  = risk_summary["total_hist_encounters"].max() or 1
risk_summary["risk_score_composite"] = (
    0.5 * (risk_summary["avg_collision_prob"] / max_prob) * 100 +
    0.3 * (risk_summary["critical_events"] / (risk_summary["total_events"] + 1)) * 100 +
    0.2 * (risk_summary["total_hist_encounters"] / max_hist) * 100
).round(2)

# Overall risk label
def overall_risk(score):
    if score >= 60: return "Critical"
    elif score >= 35: return "High"
    elif score >= 15: return "Medium"
    else: return "Low"

risk_summary["overall_risk_label"] = risk_summary["risk_score_composite"].apply(overall_risk)

out_path = os.path.join(OUT_DIR, "pbi_risk_summary.csv")
risk_summary.to_csv(out_path, index=False)
print(f"    ✔ Saved {len(risk_summary)} rows → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 4 — Orbital Density (KD-Tree based proximity analysis)
# Shows how many satellites fall within 10km / 50km shells per altitude band
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/6] Building pbi_orbital_density.csv ...")

# Use mean satellite positions (one snapshot per satellite for density)
sat_positions = events.groupby("satellite_id")[["x_km", "y_km", "z_km"]].mean().dropna()

R_EARTH = 6371.0
coords = sat_positions.values
altitude = np.sqrt((coords**2).sum(axis=1)) - R_EARTH

# KD-Tree proximity search
tree = cKDTree(coords)
close_10km  = [len(tree.query_ball_point(p, r=10))  - 1 for p in coords]  # -1 to exclude self
close_50km  = [len(tree.query_ball_point(p, r=50))  - 1 for p in coords]
close_100km = [len(tree.query_ball_point(p, r=100)) - 1 for p in coords]

density_df = pd.DataFrame({
    "satellite_id":       sat_positions.index,
    "x_km":               coords[:, 0],
    "y_km":               coords[:, 1],
    "z_km":               coords[:, 2],
    "altitude_km":        altitude,
    "neighbors_10km":     close_10km,
    "neighbors_50km":     close_50km,
    "neighbors_100km":    close_100km,
})

# Altitude bin for grouping
bins = list(range(0, 2001, 50))
density_df["altitude_band_km"] = pd.cut(
    density_df["altitude_km"], bins=bins,
    labels=[f"{b}-{b+50}" for b in bins[:-1]]
)

density_df["density_risk"] = density_df["neighbors_10km"].apply(
    lambda n: "Critical" if n >= 5 else ("High" if n >= 3 else ("Medium" if n >= 1 else "Low"))
)

out_path = os.path.join(OUT_DIR, "pbi_orbital_density.csv")
density_df.to_csv(out_path, index=False)
print(f"    ✔ Saved {len(density_df)} rows → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 5 — Launch Timeline (for trend analysis in Power BI)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5/6] Building pbi_launch_timeline.csv ...")

timeline = master.dropna(subset=["launch_date"]).copy()
timeline["launch_year"]    = timeline["launch_date"].dt.year
timeline["launch_month"]   = timeline["launch_date"].dt.month
timeline["launch_quarter"] = timeline["launch_date"].dt.quarter
timeline["launch_yearmonth"] = timeline["launch_date"].dt.to_period("M").astype(str)

# Cumulative launches over time
timeline_agg = (
    timeline.groupby("launch_yearmonth")
    .agg(launches_in_period=("satellite_id", "count"))
    .reset_index()
)
timeline_agg["launch_yearmonth_dt"] = pd.to_datetime(timeline_agg["launch_yearmonth"])
timeline_agg = timeline_agg.sort_values("launch_yearmonth_dt")
timeline_agg["cumulative_launches"] = timeline_agg["launches_in_period"].cumsum()

out_path = os.path.join(OUT_DIR, "pbi_launch_timeline.csv")
timeline_agg.to_csv(out_path, index=False)
print(f"    ✔ Saved {len(timeline_agg)} rows → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 6 — KPI Summary (single-row card table for Power BI KPI cards)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[6/6] Building pbi_kpi_summary.csv ...")

total_sats            = len(master)
total_events          = len(events)
critical_events       = (events["risk_tier"] == "Critical").sum()
high_events           = (events["risk_tier"] == "High").sum()
avg_prob              = events["collision_probability"].mean()
max_prob_val          = events["collision_probability"].max()
min_distance          = events["distance_km"].min()
avg_distance          = events["distance_km"].mean()
sats_with_critical    = (risk_summary["critical_events"] > 0).sum()
pct_critical_sats     = round(sats_with_critical / len(risk_summary) * 100, 2) if len(risk_summary) > 0 else 0
kdtree_close_pairs_10 = sum(close_10km) // 2  # each pair counted twice
avg_neighbors_50km    = round(np.mean(close_50km), 2)

kpi = pd.DataFrame([{
    "total_satellites":          total_sats,
    "total_collision_events":    total_events,
    "critical_risk_events":      int(critical_events),
    "high_risk_events":          int(high_events),
    "avg_collision_probability": round(float(avg_prob), 6),
    "max_collision_probability": round(float(max_prob_val), 6),
    "min_observed_distance_km":  round(float(min_distance), 4),
    "avg_observed_distance_km":  round(float(avg_distance), 4),
    "satellites_with_critical_events": int(sats_with_critical),
    "pct_critical_satellites":   pct_critical_sats,
    "kdtree_close_pairs_10km":   kdtree_close_pairs_10,
    "avg_neighbors_within_50km": avg_neighbors_50km,
    "export_timestamp":          datetime.utcnow().isoformat(),
}])

out_path = os.path.join(OUT_DIR, "pbi_kpi_summary.csv")
kpi.to_csv(out_path, index=False)
print(f"    ✔ Saved → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Final summary
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  Export Complete! Files saved to ./powerbi_data/")
print("=" * 60)

print(f"""
  Tables Generated:
  ┌─────────────────────────────────┬──────────┐
  │ File                            │ Rows     │
  ├─────────────────────────────────┼──────────┤
  │ pbi_satellite_master.csv        │ {len(master):>8} │
  │ pbi_collision_events.csv        │ {len(events):>8} │
  │ pbi_risk_summary.csv            │ {len(risk_summary):>8} │
  │ pbi_orbital_density.csv         │ {len(density_df):>8} │
  │ pbi_launch_timeline.csv         │ {len(timeline_agg):>8} │
  │ pbi_kpi_summary.csv             │        1 │
  └─────────────────────────────────┴──────────┘

  Next step: Open POWERBI_DASHBOARD.md for dashboard setup.
""")
