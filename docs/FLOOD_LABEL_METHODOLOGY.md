# Target Labeling Methodology (`FLOOD_LABEL_METHODOLOGY.md`)

**Smart India Hackathon Problem**: SIH26192 — *Flash Flood Prediction System for Hilly Regions using Multi-Source Data*  
**Organization**: Ministry of Home Affairs (MHA) / NDRF  

---

## 1. Core Labeling Philosophy & Scientific Non-Negotiables

> [!IMPORTANT]
> **Independent Evidence Rule**: High daily rainfall or elevated river discharge alone does NOT constitute a flood event label. A date is labeled as `flood_label = 1` ONLY when supported by verified, independent historical disaster documentation from authoritative agencies (KSDMA, CWC Hydro-Meteorological Reports, NDMA, NDRF, GSI).

### Distinction Between Phenomena
- **Flash Flood / Debris Flow (`flood_label = 1`)**: Rapid surge of water and suspended sediments down steep mountain valleys (e.g. 2024 Chooralmala/Mundakkai in Wayanad, 2019 Puthumala, 2020 Pettimudi in Idukki, 2021 Oct Kottayam/Pathanamthitta flash floods).
- **Extreme Monsoon Inundation (`flood_label = 1`)**: Widespread catastrophic riverine flooding covering entire sub-basins (e.g. August 2018 Great Kerala Flood).
- **High Heavy Rainfall without Flooding (`flood_label = 0`)**: Heavy precipitation events where soil infiltration capacity was high and river channels contained the runoff without overtopping banks or triggering landslides.
- **Landslides without Hydrological Surge**: Excluded or specifically checked to ensure water flow occurred.

---

## 2. Target Variable Formulation

For early warning systems in hilly catchments, the objective is to predict whether a flash flood will occur within a specified **lead time horizon $H$** (e.g. $24$ to $48$ hours ahead):

$$\text{Predict } Y(t + H) \in \{0, 1\} \quad \text{given features } X(t)$$

- **$X(t)$**: Feature vector containing past and current meteorological, hydrological, soil moisture, and static terrain variables available at time $t$.
- **$Y(t + H)$**: Target binary label (`flood_label`) indicating confirmed disaster occurrence within the early-warning window $[t, t + H]$.

---

## 3. Label Confidence Matrix

| Label | Confidence | Description | Count in Dataset |
| :--- | :--- | :--- | :--- |
| `1` | `high` | Verified disaster date backed by KSDMA / CWC / NDMA / GSI reports. | 122 daily records |
| `0` | `high` | Verified normal/dry monsoonal period with no disaster records. | 45,045 daily records |

---

## 4. Documented Historical Flood Corpus (2001–2025)

1. **`FLD_KL_2005_01`**: 2005-07-15 to 2005-07-28 (Wayanad, Kozhikode, Idukki).
2. **`FLD_KL_2007_01`**: 2007-06-22 to 2007-07-15 (Statewide Western Ghats).
3. **`FLD_KL_2010_01`**: 2010-06-08 to 2010-06-18 (Pathanamthitta, Idukki).
4. **`FLD_KL_2013_01`**: 2013-06-20 to 2013-07-10 (Wayanad, Idukki, Pathanamthitta).
5. **`FLD_KL_2018_01`**: 2018-08-08 to 2018-08-20 (2018 Great Kerala Mega Flood).
6. **`FLD_KL_2019_01`**: 2019-08-08 to 2019-08-15 (Wayanad Puthumala & Malappuram Kavalappara debris torrents).
7. **`FLD_KL_2020_01`**: 2020-08-06 to 2020-08-11 (Idukki Pettimudi landslide & Periyar flash surge).
8. **`FLD_KL_2021_01`**: 2021-10-15 to 2021-10-20 (Pathanamthitta Pamba & Kottayam flash floods).
9. **`FLD_KL_2022_01`**: 2022-05-14 to 2022-05-20 (Pre-monsoon cloudbursts in Idukki/Pathanamthitta).
10. **`FLD_KL_2023_01`**: 2023-07-03 to 2023-07-09 (Highland surge in Kannur/Kozhikode/Wayanad).
11. **`FLD_KL_2024_01`**: 2024-07-29 to 2024-08-02 (2024 Chooralmala-Mundakkai extreme Wayanad debris surge).
