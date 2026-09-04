# Ground-Gauge Rainfall Merge — Notes & Caveats

This documents how `rainfall_kerala_cleaned_primary.csv` and
`rainfall_backup_candidate_stations.csv` were merged into
`FINAL_FLASH_FLOOD_DATASET.csv`, and why the result looks the way it does.

## Why this couldn't be a normal station-name join

Neither file contains a station that matches one of the 5 target CWC gauges
(VANDIPERIYAR, MUTHANKERA, THUMPAMON, KUTTYADI, PERUMANNU). So the join had
to be done spatially — nearest ground station to each target gauge — rather
than by matching station names.

## `rainfall_kerala_cleaned_primary.csv` (has real rainfall_mm values)

| Ground station | District | Nearest target gauge | Distance | Coverage |
|---|---|---|---|---|
| BOYCE ESTATE | Idukki | **VANDIPERIYAR** | 19.8 km | 2000-02-04 → 2020-12-31 |
| Vannapuram | Idukki | **VANDIPERIYAR** | 79.7 km | 2002-02-02 → 2020-12-31 |

Both nearest-matched to **VANDIPERIYAR** — no ground station in this file is
anywhere close to MUTHANKERA, THUMPAMON, KUTTYADI, or PERUMANNU (next-closest
is 200+ km away). So three new columns were added, populated **only** for
VANDIPERIYAR rows and only within each gauge's date coverage (all other
rows/stations are `NaN`):

- `ground_rainfall_mm_boyce_estate` — 3,493 non-null rows (19.8 km away; within the 50 km proxy threshold — reasonable regional proxy)
- `ground_rainfall_mm_vannapuram` — 3,255 non-null rows (79.7 km away; **beyond** the 50 km threshold — informational only, rainfall in Western Ghats terrain is highly localized so treat with caution)
- `ground_rainfall_mm_nearest_available` — 4,156 non-null rows (convenience column: whichever of the two has data for that date, preferring the closer BOYCE ESTATE)

These are **additive** columns for cross-checking the existing NASA POWER
`rainfall_1d` satellite estimate at VANDIPERIYAR against real gauge readings.
They do not replace `rainfall_1d`, and ~92% of rows are still `NaN` since
coverage is limited to one station and to 2000–2020 (the dataset's flood
target period extends to 2025-11-30, and 4 of 5 stations have no proxy at
all).

**Not recommended as a direct model feature** given the sparse, single-station
coverage — better used as a QA/validation signal or as an input to a
"trust weight" for the satellite rainfall column at VANDIPERIYAR specifically.

## `rainfall_backup_candidate_stations.csv` (no rainfall values — metadata only)

This file has **no rainfall measurements at all** — it's a shortlist of 24
candidate IMD-style gauges with only name/district/coordinates and how many
days they reported data during the 2018 Jul–Aug monsoon window. There is
nothing numeric to attach to a date, so it was **not merged into the main
dataset**.

Instead, `GROUND_RAINFALL_BACKUP_REFERENCE_LOG.csv` computes the nearest
target gauge and distance for all 24 candidates, for reference if you later
obtain the actual rainfall values for any of them. Notably:
- `F.C.S. Kurudamannil` and `Pathanamthitta` are the closest candidates to **THUMPAMON** (13.5 km and 9.8 km) — worth prioritizing if you can source their historical daily rainfall.
- `Mundakayam-rh`, `Nilackal`, `Vadasserikkara` etc. are all within ~20–30 km of VANDIPERIYAR/THUMPAMON.
- Nothing in this list is within reasonable range of MUTHANKERA, KUTTYADI, or PERUMANNU (all in northern Kerala; this candidate list is concentrated in central Kerala — Idukki/Kottayam/Pathanamthitta/Thrissur).

## Output files

- `FINAL_FLASH_FLOOD_DATASET_WITH_GROUND_RAINFALL.csv` — the original 35-column dataset + 3 new ground-rainfall columns (45,167 rows, unchanged).
- `GROUND_RAINFALL_PRIMARY_MERGE_LOG.csv` — exact distances/coverage for the 2 stations that were merged.
- `GROUND_RAINFALL_BACKUP_REFERENCE_LOG.csv` — nearest-target lookup for the 24 candidate stations (no data merged, reference only).
- Updated `DATA_DICTIONARY.csv` and `DATA_QUALITY_REPORT.csv` with entries for the 3 new columns.
