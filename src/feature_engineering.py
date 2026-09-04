"""
PRAHARI - SIH26192 Flash Flood Early Warning System (Kerala)
Feature Engineering Pipeline (Team 2: Backend, Role 2A)

This script:
1. Loads raw dataset from data/FINAL_FLASH_FLOOD_DATASET.csv and data/FLOOD_EVENTS.csv.
2. Constructs dual target labels:
   - flood_label_primary: original 122 historical primary-gauge labels.
   - flood_label_extended: 411 labels derived via Rule 4 Full Concordance (matching regional
     basin/district boundaries & statewide deluges documented in FLOOD_EVENTS.csv).
3. Engineers client-side browser-compatible features:
   - rainfall_mm: Same-day precipitation.
   - rainfall_3d_cum_mm: 3-day cumulative precipitation per station.
   - discharge_sensor_outage: Binary flag (1 for sensor failure/missing, 0 otherwise).
   - river_discharge: Physical discharge with missing outage periods imputed with station median.
   - river_discharge_roc: Clean rate-of-change (rolling daily difference river_discharge.diff() per station).
   - slope: Static catchment terrain slope in degrees.
   - drainage_density: Static catchment drainage density in km/km2.
4. Drops buggy columns (discharge_rise_rate_1d, discharge_percentile, discharge_rolling_max_3d).
5. Splits dataset into 80/20 train/test stratified by flood_label_extended.
6. Computes z-score scaling parameters strictly on train data and applies them.
7. Saves outputs into 'data/train model yaha se/':
   - features_engineered.csv (full feature table with metadata and train/test flag)
   - train_features.csv (80% stratified train partition)
   - test_features.csv (20% stratified test partition)
   - scaling_parameters.json (scaling constants for browser inference)
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def build_features(
    data_dir="data",
    output_dir=os.path.join("data", "train model yaha se"),
    random_state=42
):
    print("=" * 60)
    print("PRAHARI - ROLE 2A: FEATURE ENGINEERING & DATASET SPLIT")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)
    src_dir = "src"
    os.makedirs(src_dir, exist_ok=True)

    # 1. Load data
    dataset_path = os.path.join(data_dir, "FINAL_FLASH_FLOOD_DATASET.csv")
    events_path = os.path.join(data_dir, "FLOOD_EVENTS.csv")

    print(f"[1/7] Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"      Loaded {len(df):,} records across {df['station'].nunique()} stations.")

    print(f"[2/7] Loading flood event records from: {events_path}")
    df_events = pd.read_csv(events_path)

    # 2. Construct Dual Labels (Rule 4 Full Concordance)
    print("[3/7] Generating dual target labels (flood_label_primary & flood_label_extended)...")
    df["flood_label_primary"] = df["flood_label"].astype(int)
    df["flood_label_extended"] = 0
    df["flood_event_id"] = "NONE"

    # Match each event across dates and geographic footprint
    for _, ev in df_events.iterrows():
        e_id = ev["event_id"]
        s_date = ev["start_date"]
        e_date = ev["end_date"]
        p_stn = ev["primary_affected_station"]
        d_list = [x.strip().upper() for x in str(ev["district"]).split(",")]
        r_list = [x.strip().upper() for x in str(ev["river_basin"]).split(",")]
        is_statewide = ("STATEWIDE" in d_list)

        date_mask = (df["date"] >= s_date) & (df["date"] <= e_date)

        for stn in df["station"].unique():
            stn_rows = df[df["station"] == stn]
            stn_d = stn_rows["district"].iloc[0].upper()
            stn_r = stn_rows["river"].iloc[0].upper()

            d_hit = (stn_d in d_list)
            r_hit = any(stn_r in x or x in stn_r for x in r_list)
            is_primary = (stn == p_stn)

            # Rule 4: Match if primary station, statewide deluge, or basin/district overlap
            if is_primary or is_statewide or (d_hit and r_hit):
                match_mask = date_mask & (df["station"] == stn)
                df.loc[match_mask, "flood_label_extended"] = 1
                df.loc[match_mask, "flood_event_id"] = e_id

    n_prim = df["flood_label_primary"].sum()
    n_ext = df["flood_label_extended"].sum()
    print(f"      flood_label_primary:  {n_prim:,} positives ({n_prim/len(df)*100:.2f}%)")
    print(f"      flood_label_extended: {n_ext:,} positives ({n_ext/len(df)*100:.2f}%)")

    # 3. Dynamic and Static Feature Engineering
    print("[4/7] Engineering lightweight browser-compatible features...")

    # Rainfall features
    df["rainfall_mm"] = df["rainfall_1d"].astype(float)
    df["rainfall_3d_cum_mm"] = df["rainfall_3d"].astype(float)

    # Sensor outage flag (1 for missing or flag 9.0, 0 otherwise)
    outage_mask = df["river_discharge"].isna() | (df["data_quality_flag"] == 9.0)
    df["discharge_sensor_outage"] = outage_mask.astype(int)
    n_outages = df["discharge_sensor_outage"].sum()
    print(f"      Identified {n_outages:,} discharge sensor outage days (flagged in discharge_sensor_outage).")

    # Impute missing river discharge with station-level median (neutral baseline flow)
    stn_medians = df.groupby("station")["river_discharge"].median()
    df["river_discharge_raw"] = df["river_discharge"]
    df["river_discharge"] = df["river_discharge"].fillna(df["station"].map(stn_medians))

    # Compute clean rate of change (river_discharge_roc) per station
    # Ensure chronological sort per station before rolling difference
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["station", "date"]).reset_index(drop=True)

    df["river_discharge_roc"] = 0.0
    for stn in df["station"].unique():
        idx = df[df["station"] == stn].index
        stn_discharge = df.loc[idx, "river_discharge"]
        stn_outage = df.loc[idx, "discharge_sensor_outage"]

        # Daily rolling difference
        roc = stn_discharge.diff().fillna(0.0)

        # On outage boundaries (today or yesterday in outage), clamp ROC to 0.0 to prevent false spikes
        outage_boundary = (stn_outage == 1) | (stn_outage.shift(1).fillna(0) == 1)
        roc[outage_boundary] = 0.0

        df.loc[idx, "river_discharge_roc"] = roc

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Static features
    df["slope"] = df["slope"].astype(float)
    df["drainage_density"] = df["drainage_density"].astype(float)

    # 4. Define Feature Sets & Stratified Train/Test Split
    print("[5/7] Creating 80/20 stratified train/test split on flood_label_extended...")

    feature_cols_continuous = [
        "rainfall_mm",
        "rainfall_3d_cum_mm",
        "river_discharge",
        "river_discharge_roc",
        "slope",
        "drainage_density"
    ]
    feature_cols_binary = ["discharge_sensor_outage"]
    all_model_features = feature_cols_continuous + feature_cols_binary

    train_idx, test_idx = train_test_split(
        df.index,
        test_size=0.20,
        random_state=random_state,
        stratify=df["flood_label_extended"]
    )

    df["is_train"] = 0
    df.loc[train_idx, "is_train"] = 1

    df_train = df.loc[train_idx].copy().sort_values(["station", "date"]).reset_index(drop=True)
    df_test = df.loc[test_idx].copy().sort_values(["station", "date"]).reset_index(drop=True)

    print(f"      Train set size: {len(df_train):,} rows ({df_train['flood_label_extended'].sum()} floods, {df_train['flood_label_extended'].mean()*100:.2f}%)")
    print(f"      Test set size:  {len(df_test):,} rows ({df_test['flood_label_extended'].sum()} floods, {df_test['flood_label_extended'].mean()*100:.2f}%)")

    # 5. Fit Scaler strictly on train set and compute z-score scaling parameters
    print("[6/7] Computing standardization (z-score) constants on training partition...")
    scaling_params = {
        "scaling_method": "z-score (standardization: (x - mean) / std)",
        "fit_dataset": f"train_features (80% stratified split, n={len(df_train)})",
        "random_state": random_state,
        "features": {},
        "binary_features": feature_cols_binary,
        "model_feature_order": [f"{c}_scaled" for c in feature_cols_continuous] + feature_cols_binary,
        "target_column": "flood_label_extended",
        "benchmark_target_column": "flood_label_primary"
    }

    for col in feature_cols_continuous:
        mean_val = float(df_train[col].mean())
        std_val = float(df_train[col].std())
        if std_val == 0.0 or np.isnan(std_val):
            std_val = 1.0

        scaling_params["features"][col] = {
            "mean": round(mean_val, 6),
            "std": round(std_val, 6)
        }

        # Apply z-score transform to train, test, and full dataframe
        scaled_col_name = f"{col}_scaled"
        df_train[scaled_col_name] = (df_train[col] - mean_val) / std_val
        df_test[scaled_col_name] = (df_test[col] - mean_val) / std_val
        df[scaled_col_name] = (df[col] - mean_val) / std_val

    # 6. Save Output Files
    print(f"[7/7] Saving clean outputs to: {output_dir}")

    # A. Full engineered table (drops buggy columns, keeps full metadata)
    cols_to_drop = [
        "discharge_rise_rate_1d",
        "discharge_percentile",
        "discharge_rolling_max_3d",
        "river_discharge_raw"
    ]
    df_full_clean = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # Reorder columns logically
    metadata_cols = ["date", "station", "district", "river", "basin", "latitude", "longitude", "elevation"]
    target_cols = ["flood_label_extended", "flood_label_primary", "flood_event_id"]
    feature_cols_raw = feature_cols_continuous + feature_cols_binary
    feature_cols_scaled = [f"{c}_scaled" for c in feature_cols_continuous]

    ordered_cols = metadata_cols + target_cols + ["is_train"] + feature_cols_raw + feature_cols_scaled
    # Include any remaining non-buggy auxiliary columns at the end
    remaining_cols = [c for c in df_full_clean.columns if c not in ordered_cols]
    df_full_clean = df_full_clean[ordered_cols + remaining_cols]

    full_csv_path = os.path.join(output_dir, "features_engineered.csv")
    df_full_clean.to_csv(full_csv_path, index=False)
    print(f"      Saved full feature table: {full_csv_path} ({len(df_full_clean):,} rows, {len(df_full_clean.columns)} cols)")

    # B. Train features partition
    train_model_cols = (
        ["date", "station", "flood_label_extended", "flood_label_primary", "flood_event_id"] +
        feature_cols_scaled +
        feature_cols_binary +
        [f"raw_{c}" for c in feature_cols_continuous]
    )

    # Prepare train dataframe with raw_ prefixes for unscaled columns
    for c in feature_cols_continuous:
        df_train[f"raw_{c}"] = df_train[c]
        df_test[f"raw_{c}"] = df_test[c]

    df_train_model = df_train[[c for c in train_model_cols if c in df_train.columns]]
    df_test_model = df_test[[c for c in train_model_cols if c in df_test.columns]]

    train_csv_path = os.path.join(output_dir, "train_features.csv")
    test_csv_path = os.path.join(output_dir, "test_features.csv")

    df_train_model.to_csv(train_csv_path, index=False)
    df_test_model.to_csv(test_csv_path, index=False)
    print(f"      Saved train features:     {train_csv_path} ({len(df_train_model):,} rows)")
    print(f"      Saved test features:      {test_csv_path} ({len(df_test_model):,} rows)")

    # C. Save scaling parameters JSON
    json_path_data = os.path.join(output_dir, "scaling_parameters.json")
    json_path_src = os.path.join(src_dir, "scaling_parameters.json")

    with open(json_path_data, "w", encoding="utf-8") as f:
        json.dump(scaling_params, f, indent=2)
    with open(json_path_src, "w", encoding="utf-8") as f:
        json.dump(scaling_params, f, indent=2)

    print(f"      Saved scaling constants:  {json_path_data}")
    print(f"      Saved mirror in src:      {json_path_src}")

    print("\nFeature engineering completed successfully!")
    return df_full_clean, df_train_model, df_test_model, scaling_params


if __name__ == "__main__":
    build_features()
