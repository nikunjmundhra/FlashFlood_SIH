"""
PRAHARI - Role 2B: Model Training & Evaluation
Trains Logistic Regression (deployed model) + Random Forest (comparison)
on real Kerala flash-flood data prepared by Team 2A.
"""
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)
import joblib

RANDOM_STATE = 42

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
train = pd.read_csv("train_features.csv", parse_dates=["date"])
test = pd.read_csv("test_features.csv", parse_dates=["date"])

with open("scaling_parameters.json") as f:
    scaling = json.load(f)

FEATURES = scaling["model_feature_order"]
TARGET = scaling["target_column"]          # flood_label_extended
BENCHMARK_TARGET = scaling["benchmark_target_column"]  # flood_label_primary

print("=" * 70)
print("1. DATA CHECK")
print("=" * 70)
print(f"Train shape: {train.shape}   Test shape: {test.shape}")
print(f"Feature order: {FEATURES}")
print()
print("Class balance (train) -", TARGET, ":")
print(train[TARGET].value_counts(normalize=False))
print(f"  -> positive rate: {train[TARGET].mean()*100:.3f}%")
print()
print("Class balance (train) -", BENCHMARK_TARGET, ":")
print(train[BENCHMARK_TARGET].value_counts(normalize=False))
print(f"  -> positive rate: {train[BENCHMARK_TARGET].mean()*100:.3f}%")

X_train, y_train = train[FEATURES], train[TARGET]
X_test, y_test = test[FEATURES], test[TARGET]
y_test_benchmark = test[BENCHMARK_TARGET]

# ---------------------------------------------------------------------------
# 2. Train Logistic Regression (deployed model)
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("2. TRAINING: Logistic Regression (deployed model)")
print("=" * 70)
log_reg = LogisticRegression(
    class_weight="balanced",
    max_iter=1000,
    random_state=RANDOM_STATE,
)
log_reg.fit(X_train, y_train)
print("Done. Coefficients:")
for feat, coef in zip(FEATURES, log_reg.coef_[0]):
    print(f"  {feat:30s} {coef:+.4f}")
print(f"  intercept: {log_reg.intercept_[0]:+.4f}")

# ---------------------------------------------------------------------------
# 3. Train Random Forest (comparison model)
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("3. TRAINING: Random Forest (comparison model)")
print("=" * 70)
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
rf.fit(X_train, y_train)
print("Done. Feature importances:")
for feat, imp in sorted(zip(FEATURES, rf.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat:30s} {imp:.4f}")

# ---------------------------------------------------------------------------
# 4. Evaluate both models on held-out test set
# ---------------------------------------------------------------------------
def evaluate(name, model, X_test, y_true_extended, y_true_primary, threshold=0.5):
    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= threshold).astype(int)

    print()
    print("-" * 70)
    print(f"EVALUATION: {name}  (threshold={threshold})")
    print("-" * 70)

    for label_name, y_true in [(TARGET, y_true_extended), (BENCHMARK_TARGET, y_true_primary)]:
        print(f"\n  Against {label_name}:")
        print(f"    Precision: {precision_score(y_true, preds, zero_division=0):.4f}")
        print(f"    Recall:    {recall_score(y_true, preds, zero_division=0):.4f}")
        print(f"    F1:        {f1_score(y_true, preds, zero_division=0):.4f}")
        try:
            print(f"    ROC-AUC:   {roc_auc_score(y_true, proba):.4f}")
        except ValueError:
            print("    ROC-AUC:   n/a (only one class present)")
        cm = confusion_matrix(y_true, preds)
        print(f"    Confusion matrix [ [TN FP] [FN TP] ]:\n{cm}")

    return proba, preds

print()
print("=" * 70)
print("4. TEST SET EVALUATION")
print("=" * 70)
lr_proba, lr_preds = evaluate("Logistic Regression", log_reg, X_test, y_test, y_test_benchmark)
rf_proba, rf_preds = evaluate("Random Forest", rf, X_test, y_test, y_test_benchmark)

# ---------------------------------------------------------------------------
# 5. August 2018 Kerala flood check (plausibility check, not clean holdout)
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("5. AUGUST 2018 KERALA FLOOD CHECK")
print("=" * 70)

full = pd.concat([
    train.assign(split="train"),
    test.assign(split="test"),
], ignore_index=True)
aug2018 = full[(full["date"] >= "2018-08-01") & (full["date"] <= "2018-08-31")].copy()

print(f"Total Aug-2018 rows: {len(aug2018)}  "
      f"(train: {(aug2018['split']=='train').sum()}, test: {(aug2018['split']=='test').sum()})")
print(f"Rows flagged {BENCHMARK_TARGET}=1 (confirmed flood days): {(aug2018[BENCHMARK_TARGET]==1).sum()}")
print("NOTE: most of these rows were in the TRAIN split (stratified random split, not time-based),")
print("      so this is a plausibility check on the model's behavior, not a clean generalization test.")

aug2018["lr_proba"] = log_reg.predict_proba(aug2018[FEATURES])[:, 1]
aug2018["rf_proba"] = rf.predict_proba(aug2018[FEATURES])[:, 1]

flood_days = aug2018[aug2018[BENCHMARK_TARGET] == 1].sort_values("date")
print(f"\nModel-predicted flood probability on the {len(flood_days)} confirmed flood days:")
print(flood_days[["date", "station", "split", "lr_proba", "rf_proba"]].to_string(index=False))

print(f"\nMean LR probability on flood days:     {flood_days['lr_proba'].mean():.4f}")
print(f"Mean RF probability on flood days:     {flood_days['rf_proba'].mean():.4f}")
non_flood_aug = aug2018[aug2018[BENCHMARK_TARGET] == 0]
print(f"Mean LR probability on non-flood Aug18 days: {non_flood_aug['lr_proba'].mean():.4f}")
print(f"Mean RF probability on non-flood Aug18 days: {non_flood_aug['rf_proba'].mean():.4f}")

# ---------------------------------------------------------------------------
# Save artifacts for later steps (model export, report)
# ---------------------------------------------------------------------------
joblib.dump(log_reg, "logistic_regression_model.joblib")
joblib.dump(rf, "random_forest_model.joblib")
aug2018.to_csv("aug2018_check_results.csv", index=False)

print()
print("=" * 70)
print("Saved: logistic_regression_model.joblib, random_forest_model.joblib, aug2018_check_results.csv")
print("=" * 70)
