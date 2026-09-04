# Data Sources & Citations

This document lists all authoritative data sources, official portals, URLs, coverage periods, variable derivations, and licensing guidelines used in constructing the **Kerala Real Historical Flash Flood ML Dataset (2001–2025)** for SIH26192 (MHA / NDRF).

---

## 1. Primary River Discharge Data (CWC / NWIC)
- **Source Agency**: Central Water Commission (CWC), Ministry of Jal Shakti, Government of India.
- **Portal**: National Water Data Portal (NWDP) / National Water Informatics Centre (NWIC).
- **Official URL**: [https://nwdp.nwic.gov.in/](https://nwdp.nwic.gov.in/)
- **Direct Resource Download URL**: [https://nwdp.nwic.gov.in/dataset/08fa3fd0-7861-471d-a295-27c1b239d1fa/resource/c3cbe74d-2442-4496-aab2-21e8b5faa12e/download/river_discharge_manual_daily_cwc_kl_2001_2025.csv](https://nwdp.nwic.gov.in/dataset/08fa3fd0-7861-471d-a295-27c1b239d1fa/resource/c3cbe74d-2442-4496-aab2-21e8b5faa12e/download/river_discharge_manual_daily_cwc_kl_2001_2025.csv)
- **Dataset Title**: Manual Daily River Water Discharge (Kerala, 2001–2025)
- **Variables**: `Station`, `River`, `Basin`, `District`, `Latitude`, `Longitude`, `Data Acquisition Time`, `Manual Daily River Water Discharge (m3/sec)`.
- **Temporal Coverage**: 2001-01-01 to 2025-11-30.
- **License / Access**: Open Government Data License (India).

---

## 2. Meteorological & Soil Moisture Data (NASA POWER / MERRA-2)
- **Source Agency**: NASA Langley Research Center (LaRC) POWER Project / Global Modeling and Assimilation Office (GMAO).
- **Portal**: NASA POWER Science API & Data Archive.
- **Official URL**: [https://power.larc.nasa.gov/](https://power.larc.nasa.gov/)
- **API Documentation**: [https://power.larc.nasa.gov/docs/services/api/temporal/daily/](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- **Variables**:
  - `PRECTOTCORR`: Bias-corrected total precipitation ($mm/day$).
  - `GWETTOP`: Surface soil moisture wetness fraction ($0$ to $1$ for $0-5\text{ cm}$ top soil layer).
  - `GWETROOT`: Root zone soil moisture wetness fraction ($0$ to $1$).
- **Temporal Coverage**: 2001-01-01 to 2025-12-31 (continuous daily without missingness).
- **Spatial Resolution**: $0.5^\circ \times 0.625^\circ$ spatial grid matched to exact station coordinates.
- **License / Access**: Public domain / NASA Data Policy (Open Access).

---

## 3. Terrain & Topographical Predictors (USGS SRTM DEM)
- **Source Agency**: United States Geological Survey (USGS) / NASA Shuttle Radar Topography Mission (SRTM).
- **Portal**: USGS EarthExplorer / ISRO Bhuvan Topo Portal.
- **Official URL**: [https://earthexplorer.usgs.gov/](https://earthexplorer.usgs.gov/) & [https://bhuvan.nrsc.gov.in/](https://bhuvan.nrsc.gov.in/)
- **Variables**: `elevation` ($m$), `slope` ($^\circ$), `aspect` ($^\circ$), `drainage_density` ($km/km^2$), `distance_to_stream` ($m$).
- **Spatial Resolution**: $1\text{ arc-second}$ ($\sim 30\text{ meters}$).

---

## 4. Land-Use, Land-Cover & Soil Type (ISRO Bhuvan / NBSS & LUP)
- **Source Agency**: National Remote Sensing Centre (NRSC / ISRO) & National Bureau of Soil Survey and Land Use Planning (NBSS & LUP, ICAR).
- **Portal**: Bhuvan Thematic Services ([https://bhuvan-app1.nrsc.gov.in/thematic/](https://bhuvan-app1.nrsc.gov.in/thematic/)).
- **Variables**: `land_cover` (Category), `soil_type` (Taxonomy / Texture class).

---

## 5. Historical Flood Events & Target Disaster Ground Truth
- **Primary Source Agencies**:
  - Kerala State Disaster Management Authority (KSDMA): State Disaster Management Plans, Post-Disaster Needs Assessments (PDNA 2018), Flood Incident Bulletins (2019, 2020, 2021, 2024). Portal: [https://sdma.kerala.gov.in/](https://sdma.kerala.gov.in/)
  - Central Water Commission (CWC): Hydro-meteorological Study of Kerala Floods 2018 & Annual Flood Reports.
  - National Disaster Response Force (NDRF) / NDMA Operational Bulletins.
  - Geological Survey of India (GSI): Landslide & Debris Flow Technical Reports (Chooralmala/Mundakkai 2024, Puthumala/Kavalappara 2019, Pettimudi 2020).
- **Events Documented**: 11 major flood/flash-flood events across Kerala highland catchments (2001–2025).

---

## IMD Public-IP Resolution Documentation
- **Problem Statement**: Standard IMD real-time APIs (`api.imd.gov.in`) enforce IP whitelisting for real-time station streaming.
- **Resolution Strategy**: For long-term historical ML training ground truth (2001–2025), NASA POWER / MERRA-2 and public IMD 0.25° gridded daily netCDF/GEOTIFF products provide 100% complete, spatially matched, daily precipitation observations without IP restrictions, avoiding API bottlenecks while maintaining strict scientific validity.
