# Technical report: APP fraud and mule-network investigation

## 1. Problem definition and threat model

APP fraud involves a payer being manipulated into authorising a payment to a fraudster-controlled or fraudster-benefiting account. Mule accounts receive and move proceeds through onward transfers and cashout.

## 2. Objective

Identify suspicious victim-to-mule receipts and rapid onward fund movement, then group alerted transactions into connected investigation cases.

## 3. Data and simulation

The project uses synthetic transaction, account and campaign records. See `dataset_profile.md`, `data_dictionary.md` and `simulator_and_temporal_methodology.md`.

## 4. Feature engineering

Features describe strictly prior rolling inbound/outbound activity, account age and amount-to-history ratios. Flow features compare an outgoing transfer with the sender's prior 72-hour inflow.

## 5. Temporal methodology

Time-based splits use delayed label maturity. Training controls derive thresholds; validation is used for selection; the test set is reserved for final evaluation.

## 6. Detection

The victim-to-mule rule uses receiver age, payment amount and prior receiver inflow. The layering rule uses prior sender inflow and an outgoing-to-inflow ratio. Repeated outgoing activity is context only, not an independent alert.

## 7. Network investigation

Directed sender-to-receiver alert edges are grouped into connected components. A connected component is an investigative lead, not proof of common control.

## 8. Evaluation

Untouched test performance: precision 100.00%, recall 30.36%, F1 0.4658; TP 17, FP 0, FN 39.

## 9. Error analysis

39 test fraud-stage events were missed. See `missed_fraud_investigation.md` for stage and campaign breakdowns.

## 10. Limitations and next steps

- Expand independent campaign and legitimate-behaviour diversity.
- Remove simulator shortcuts and test adversarial variations.
- Develop cumulative account-flow and multi-payout sequence features using training/validation only.
- Evaluate at transaction, account, campaign and case levels.
- Validate with appropriate real-world data before operational claims.

## 11. Reproducibility

See the project README for environment setup and execution order. Generated reports and figures are under `results/reports/` and `results/evidence/`.