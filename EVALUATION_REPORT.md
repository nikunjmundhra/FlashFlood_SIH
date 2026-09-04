# PRAHARI — Role 2B: Model Training & Evaluation Report

**Model:** Random Forest Classifier (30 trees, max depth 5)
**Target:** `flood_label_extended`
**Data:** Real Kerala flash-flood data, 2001–2025, 5 stations (KUTTYADI, MUTHANKERA, PERUMANNU, THUMPAMON, VANDIPERIYAR) — provided by Team 2A (`train_features.csv`, `test_features.csv`, 80/20 stratified split, random_state=42)
**Deployment format:** pure JavaScript (no backend required) — see `prahari_rf_model.js` + `prahari_inference.js`

---

## 1. Class balance

Both target columns are heavily imbalanced, as expected for a rare-event problem:

| Target | Positive rate (train) |
|---|---|
| `flood_label_extended` | 0.91% (329 / 36,133) |
| `flood_label_primary` (benchmark) | 0.25% (91 / 36,133) |

`class_weight="balanced"` was used during training to compensate.

## 2. Model comparison (why we ended up here)

Three models were evaluated on the held-out test set (9,034 rows):

| Model | ROC-AUC | Precision @ default | Recall @ default |
|---|---|---|---|
| Logistic Regression | 0.907 | 0.050 | 0.79 |
| Random Forest (full, 300 trees) | 0.918 | 0.111 | 0.26 |
| Random Forest (small, 30 trees — **deployed**) | 0.917 | — | — |

The full 300-tree Random Forest was selected over Logistic Regression for higher precision, but its JavaScript export (via m2cgen) came to **17.7 MB** — impractical for a frontend dashboard to load. A smaller Random Forest (30 trees, max depth 5) was retrained specifically for JS deployment. It preserves nearly all of the ranking power (ROC-AUC 0.917 vs 0.918) at **120 KB**.

**Important:** the smaller model's probability *calibration* is different from the full model — it produces much higher probabilities at every threshold (fewer trees averaged = less smoothing). Its best-F1 operating point is **threshold 0.8**, not 0.4/0.5. Do not reuse thresholds across model versions.

## 3. Final deployed model performance (threshold = 0.8, test set)

| Metric | Value |
|---|---|
| Precision | 0.110 |
| Recall | 0.378 |
| F1 | 0.170 |
| ROC-AUC | 0.917 |

This means: of all flood warnings the model raises, ~11% are real floods; of all real flood events, it catches ~38%. Given the extreme class imbalance (~1% positive), this is a reasonable early-warning operating point — but it should be communicated honestly in any pitch/demo: this is not a highly precise detector, it is a screening tool that meaningfully raises the odds of catching a flood versus chance.

## 4. August 2018 Kerala flood validation

| | Value |
|---|---|
| Confirmed flood days in Aug 2018 | 13 (station: VANDIPERIYAR) |
| Mean predicted probability on flood days | 0.82 |
| Mean predicted probability on non-flood days (same month) | 0.44 |
| Flood days correctly flagged @ threshold 0.8 | 9 / 13 (69%) |

**Caveat:** the train/test split is stratified-random, not time-based, so 10 of the 13 confirmed Aug-2018 flood days fell into the *training* set. This is a plausibility/sanity check confirming the model behaves sensibly around a real historical event — not a clean generalization test. A genuinely held-out validation would require a time-based split excluding known flood events from training, which could be a follow-up improvement if time allows.

## 5. Deliverables for Team 3

- `prahari_rf_model.js` — auto-generated (m2cgen) pure-JS decision function, no dependencies
- `prahari_inference.js` — wrapper exposing `predictFloodRisk(rawSensorValues)`, handles feature scaling and thresholding
- `model_export.json` — metadata: scaling parameters, feature order, threshold, model info
- Verified: JS output matches Python `predict_proba` to 6 decimal places on real data (Aug 16, 2018, VANDIPERIYAR)

## 6. Known limitations / honest caveats for the pitch

- Precision is low (~11%) — expect noticeable false-alarm rate; frame this as a screening/early-warning signal, not a certainty.
- August 2018 validation is not a clean holdout (see above).
- Only 5 stations, all with fairly limited historical labeled flood events (411 extended-label positives total) — model may not generalize well to basins with very different terrain/rainfall regimes.
- No time-series/sequence modeling (e.g. LSTM) was used — this is a same-day tabular classifier, which limits genuine "advance warning" lead time. Worth mentioning as future work.
