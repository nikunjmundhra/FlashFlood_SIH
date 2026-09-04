# Spatial & Temporal Data Merge Methodology (`DATA_MERGE_METHODOLOGY.md`)

**Smart India Hackathon Problem**: SIH26192 — *Flash Flood Prediction System for Hilly Regions using Multi-Source Data*  
**Organization**: Ministry of Home Affairs (MHA) / NDRF  

---

## 1. Primary Integration Challenge

Building a unified ML training table requires joining multi-source data across different spatial and temporal scales:

- **Point-Based River Discharge**: CWC manual daily gauge readings ($m^3/s$) at specific station coordinates.
- **Gridded Precipitation**: NASA POWER / MERRA-2 daily precipitation ($mm/day$) on a $0.5^\circ \times 0.625^\circ$ spatial grid.
- **Gridded Soil Moisture**: NASA POWER surface ($0-5\text{ cm}$) and root-zone soil wetness fractions.
- **High-Resolution GIS Terrain**: USGS SRTM 30m DEM metrics (elevation, slope, aspect, drainage density, distance to stream).
- **Temporal Event Logs**: Historical disaster start/end dates from KSDMA / CWC.

---

## 2. Spatial Matching Strategy

- **Primary Spatial Unit**: **River Gauging Station Catchment** (`station_id`).
- **Spatial Alignment Procedure**:
  1. For each selected CWC river gauge station (`VANDIPERIYAR`, `MUTHANKERA`, `THUMPAMON`, `KUTTYADI`, `PERUMANNU`), the exact latitude and longitude were extracted from official CWC survey records.
  2. NASA POWER gridded precipitation and soil moisture time series were extracted at the exact grid cell centroid covering each gauge's geographical coordinates.
  3. GIS terrain predictors (slope, aspect, elevation, drainage density, stream distance) were extracted for each station's upstream catchment boundary using 30m SRTM DEM hydro-processing.

---

## 3. Temporal Standardization & Feature Engineering

- **Timezone**: All timestamps are standardized to **Asia/Kolkata (IST)** in ISO-8601 `YYYY-MM-DD` date format.
- **Strict Anti-Leakage Constraints**:
  - No future information is included in any row at time $t$.
  - All rolling features ($3$-day, $7$-day, $14$-day, $30$-day sums and means) use backward-looking rolling windows:
    $$\text{Rainfall}_{7d, t} = \sum_{i=0}^{6} \text{Rainfall}_{t-i}$$
  - Antecedent Precipitation Index (API) is computed using exponential daily decay ($k=0.85$):
    $$API_t = P_t + 0.85 \cdot API_{t-1}$$
  - Discharge lag metrics ($Q_{t-1}$, $Q_{t-3}$, $3$-day max, $1$-day relative rise rate) are calculated strictly on past observations.

---

## 4. Final Join Schema

All sub-tables (`RIVER_DATA_CLEANED.csv`, `RAINFALL_DATA_CLEANED.csv`, `SOIL_MOISTURE_DATA.csv`, `TERRAIN_DATA.csv`, `FLOOD_EVENTS.csv`) are joined on the primary compound key:

$$\text{Primary Key} = (\text{date}, \text{station})$$
