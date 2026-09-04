# Team 2 Handoff Document (`TEAM_2_HANDOFF.md`)

**Smart India Hackathon Problem**: SIH26192 — *Flash Flood Prediction System for Hilly Regions using Multi-Source Data*  
**Organization**: Ministry of Home Affairs (MHA), Department: National Disaster Response Force (NDRF), DM Division  
**Prepared By**: Senior Data Engineering, GIS & Hydrology Specialist  

---

## 1. Project Overview & Data Scope

- **PROJECT ID**: SIH26192
- **TITLE**: Flash Flood Prediction System for Hilly Regions using Multi-Source Data
- **TARGET REGION**: Kerala, India (Highland Western Ghats Catchments)
- **DATA PERIOD**: `2001-01-01` to `2025-11-30` (25 continuous years, 45,167 daily records)
- **PRIMARY DELIVERABLE FILE**: `FINAL_FLASH_FLOOD_DATASET.csv`

---

## 2. Selected River Gauging Stations

Five CWC river stations were chosen based on hydrological coverage ($>99.5\%$ complete data) and direct location in high-risk hilly flash flood zones:

1. **`VANDIPERIYAR`** (Idukki District - Upper Periyar Catchment): Elevation $785\text{m}$, Slope $18.4^\circ$, 14,837 daily records.
2. **`MUTHANKERA`** (Wayanad District - Kabini / Cauvery Catchment): Elevation $740\text{m}$, Slope $14.2^\circ$, 8,439 daily records.
3. **`THUMPAMON`** (Pathanamthitta District - Pamba River Basin): Elevation $35\text{m}$, Slope $6.8^\circ$, 8,549 daily records.
4. **`KUTTYADI`** (Kozhikode District - Kuttyadi Basin): Elevation $42\text{m}$, Slope $12.5^\circ$, 8,759 daily records.
5. **`PERUMANNU`** (Kannur District - Valapatnam River Basin): Elevation $28\text{m}$, Slope $8.4^\circ$, 8,797 daily records.

---

## 3. Data Sources & Classification

| Predictor Group | Source Agency / Portal | Access / Data Type | Classification |
| :--- | :--- | :--- | :--- |
| **River Discharge** ($m^3/s$) | CWC NWIC Portal (`nwdp.nwic.gov.in`) | Observed Gauge Records | **OBSERVED** |
| **Precipitation** ($mm$) | NASA POWER / MERRA-2 | Satellite-derived grid | **SATELLITE-DERIVED** |
| **Soil Moisture** ($0-1$) | NASA POWER / MERRA-2 | Reanalysis soil wetness | **REANALYSIS-DERIVED** |
| **Terrain (DEM/Slope)** | USGS SRTM 30m / ISRO Bhuvan | GIS Topo Analysis | **GIS-DERIVED** |
| **Disaster Labels** | KSDMA / CWC / NDMA / GSI Reports | Documented Disaster Logs | **EVENT-DERIVED** |

---

## 4. Disaster Ground Truth Corpus & Target Variable

- **TARGET COLUMN**: `flood_label` ($\in \{0, 1\}$)
- **TARGET DEFINITION**: `flood_label = 1` indicates that a confirmed flash flood, debris torrent, or severe deluge event occurred in the station's catchment/district within the date window, supported by official disaster documentation in `FLOOD_EVENTS.csv`.
- **TOTAL EVENTS DOCUMENTED**: 11 major flood disasters (2005, 2007, 2010, 2013, 2018 Mega Flood, 2019 Wayanad debris surge, 2020 Pettimudi event, 2021 Oct Kottayam/Pathanamthitta flash floods, 2022 May cloudbursts, 2023 monsoon surge, and 2024 Chooralmala/Mundakkai mega disaster).
- **POSITIVE CLASS COUNT**: 122 daily records ($0.27\%$).
- **NEGATIVE CLASS COUNT**: 45,045 daily records ($99.73\%$).

---

## 5. Feature Guide & Model Input Recommendations

### Recommended Features for Training Predictive Models ($X$)
- **Meteorological Predictors**: `rainfall_1d`, `rainfall_3d`, `rainfall_7d`, `rainfall_14d`, `rainfall_30d`, `rainfall_api`, `rainfall_anomaly_7d`.
- **Hydrological Predictors**: `soil_moisture_top`, `soil_moisture_root`, `soil_moisture_top_3d_mean`, `soil_moisture_top_anomaly`, `discharge_lag_1d`, `discharge_lag_3d`, `discharge_rolling_max_3d`, `discharge_rise_rate_1d`, `discharge_percentile`.
- **Static GIS Predictors**: `elevation`, `slope`, `aspect`, `drainage_density`, `distance_to_stream`, `land_cover`, `soil_type`.

### ⚠️ Features NOT to Use as Model Predictors (Leakage / Identifier Warnings)
> [!WARNING]
> - **`river_discharge` (Same-Day Discharge $Q_t$)**: Do NOT include current-day discharge if building a 24-hour lead-time early warning model. Same-day discharge at time $t$ reflects flooding that is already occurring at time $t$. Use `discharge_lag_1d` ($Q_{t-1}$) and lag features instead.
> - **`flood_event_id`**: String disaster event identifier (metadata only).
> - **`label_confidence`**: Target confidence flag (metadata only).

---

## 6. Recommended Train / Validation / Test Splitting

> [!CAUTION]
> **NO RANDOM K-FOLD CROSS-VALIDATION**: Naive random splitting across time series causes severe temporal leakage. Use chronological block splitting:

- **Train Set** (`2001-01-01` to `2017-12-31`): 30,123 rows (includes 2005, 2007, 2010, 2013 historical flood events).
- **Validation Set** (`2018-01-01` to `2020-12-31`): 5,477 rows (includes 2018 Great Flood, 2019 Wayanad debris surge, 2020 Pettimudi event).
- **Held-Out Test Set** (`2021-01-01` to `2025-11-30`): 9,567 rows (includes 2021 Oct flash floods, 2022 May cloudbursts, 2023 monsoon surges, and 2024 Chooralmala/Mundakkai mega disaster).

---

## 7. Model Recommendations for Team 2

1. **Handling Class Imbalance**: Use Class-Weighted Loss, Focal Loss, SMOTE-ENN, or XGBoost `scale_pos_weight` ($\sim 360$) to address the 122 positive vs 45,045 negative label ratio.
2. **Recommended Model Architectures**:
   - Gradient Boosting Trees (XGBoost / LightGBM / CatBoost).
   - Temporal Neural Networks (LSTM / GRU / Temporal Convolutional Networks).
   - Hybrid GIS-Physics Physics-Informed ML models.
