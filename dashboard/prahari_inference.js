/**
 * PRAHARI - Flash Flood Risk Inference (Role 2B deployed model)
 *
 * Wraps the auto-generated Random Forest scoring function (prahari_rf_model.js)
 * with the feature scaling used at training time, so Team 3 can pass in RAW
 * sensor/API values and get back a flood-risk decision directly.
 *
 * Usage (Node):
 *   const { predictFloodRisk } = require('./prahari_inference.js');
 *   const result = predictFloodRisk({
 *     rainfall_mm: 42.5,
 *     rainfall_3d_cum_mm: 88.0,
 *     river_discharge: 120.3,
 *     river_discharge_roc: 15.2,
 *     slope: 12.5,
 *     drainage_density: 2.8,
 *     discharge_sensor_outage: 0   // 1 if the river discharge sensor is down
 *   });
 *   // result = { probability: 0.83, isHighRisk: true, threshold: 0.8 }
 *
 * Usage (browser, after <script src="prahari_rf_model.js"></script> and
 * <script src="prahari_inference.js"></script>): call `predictFloodRisk(...)`
 * directly as a global function.
 */

// Scaling parameters copied from model_export.json (mean/std computed on
// the training set only, per feature) — DO NOT change these without
// retraining the model.
const SCALING = {
  rainfall_mm: { mean: 6.395273, std: 11.011747 },
  rainfall_3d_cum_mm: { mean: 19.209031, std: 28.629555 },
  river_discharge: { mean: 55.561825, std: 157.275945 },
  river_discharge_roc: { mean: -0.340381, std: 97.906757 },
  slope: { mean: 12.053519, std: 4.154698 },
  drainage_density: { mean: 2.801709, std: 0.227898 },
};

// Order the trained model expects its 7 inputs in. Must match
// scaling_parameters.json -> model_feature_order exactly.
const FEATURE_ORDER = [
  "rainfall_mm_scaled",
  "rainfall_3d_cum_mm_scaled",
  "river_discharge_scaled",
  "river_discharge_roc_scaled",
  "slope_scaled",
  "drainage_density_scaled",
  "discharge_sensor_outage",
];

// Decision threshold chosen from the evaluation (best-F1 operating point
// for this specific small model — NOT 0.5, see eval report for why).
const DECISION_THRESHOLD = 0.8;

function zScore(value, feature) {
  const { mean, std } = SCALING[feature];
  return (value - mean) / std;
}

/**
 * @param {Object} raw - raw (unscaled) sensor readings
 * @param {number} raw.rainfall_mm
 * @param {number} raw.rainfall_3d_cum_mm
 * @param {number} raw.river_discharge
 * @param {number} raw.river_discharge_roc
 * @param {number} raw.slope
 * @param {number} raw.drainage_density
 * @param {number} raw.discharge_sensor_outage - 0 or 1
 * @returns {{probability: number, isHighRisk: boolean, threshold: number}}
 */
function predictFloodRisk(raw) {
  const required = [
    "rainfall_mm", "rainfall_3d_cum_mm", "river_discharge",
    "river_discharge_roc", "slope", "drainage_density",
    "discharge_sensor_outage",
  ];
  for (const key of required) {
    if (raw[key] === undefined || raw[key] === null) {
      throw new Error(`predictFloodRisk: missing required field "${key}"`);
    }
  }

  const scaledInput = [
    zScore(raw.rainfall_mm, "rainfall_mm"),
    zScore(raw.rainfall_3d_cum_mm, "rainfall_3d_cum_mm"),
    zScore(raw.river_discharge, "river_discharge"),
    zScore(raw.river_discharge_roc, "river_discharge_roc"),
    zScore(raw.slope, "slope"),
    zScore(raw.drainage_density, "drainage_density"),
    raw.discharge_sensor_outage, // binary, not scaled
  ];

  // `score` comes from prahari_rf_model.js — load it before this file
  // (Node: require it and pass in; browser: plain global works via <script> tags)
  const scoreFn = (typeof score !== "undefined") ? score
    : (typeof require !== "undefined") ? require("./prahari_rf_model.js")
    : null;
  if (!scoreFn) {
    throw new Error("predictFloodRisk: prahari_rf_model.js not loaded");
  }

  const [, probability] = scoreFn(scaledInput); // [P(class0), P(class1=flood)]

  return {
    probability,
    isHighRisk: probability >= DECISION_THRESHOLD,
    threshold: DECISION_THRESHOLD,
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { predictFloodRisk, DECISION_THRESHOLD, FEATURE_ORDER };
}
