# Untouched test-set evaluation

- Transactions: 21,668
- Fraud-stage positives: 56
- Legitimate transactions: 21,612
- TP: 17; FP: 0; FN: 39; TN: 21612
- Precision: 100.00%
- Recall: 30.36%
- F1: 0.4658

Zero false positives in this synthetic holdout is not a guarantee of zero false positives in production.

## Detector comparison

| detector        |   TP |   FP |   FN |    TN |   precision |   recall |     F1 |
|:----------------|-----:|-----:|-----:|------:|------------:|---------:|-------:|
| Victim-to-mule  |    7 |    0 |   49 | 21612 |           1 |   0.125  | 0.2222 |
| Layering        |   10 |    0 |   46 | 21612 |           1 |   0.1786 | 0.303  |
| Combined engine |   17 |    0 |   39 | 21612 |           1 |   0.3036 | 0.4658 |

## Stage-level results

| Stage | Positives | Detected | Missed |
|---|---:|---:|---:|
| cashout | 6 | 0 | 6 |
| mule_layering | 11 | 10 | 1 |
| victim_to_mule | 39 | 7 | 32 |

## Campaign-level detections

- C005: 4
- C006: 7
- C007: 4
- C008: 2

## Missed fraud

- Total missed events: 39
- victim_to_mule: 32
- cashout: 6
- mule_layering: 1

Test results are descriptive. Do not tune thresholds using this holdout.