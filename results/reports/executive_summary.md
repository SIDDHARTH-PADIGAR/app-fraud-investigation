# Executive summary

## Objective

Build a reproducible synthetic APP-fraud investigation benchmark to detect victim-to-mule receipts and mule-layering transfers, then group alerts into connected account investigations.

## What was built

- Synthetic campaign-based transaction dataset and audit.
- Point-in-time transaction and fund-flow features.
- Delayed-label temporal train, validation and test splits.
- Explainable receiving-account and rapid-fund-forwarding rules.
- Connected-account cases with transaction and account evidence.

## Untouched test results

- Transactions: 21,668
- TP: 17; FP: 0; FN: 39
- Precision: 100.00%; recall: 30.36%; F1: 0.4658

## Interpretation

The detector is conservative on this synthetic holdout: it recorded no false positives but detected only a subset of fraud-stage transactions. This is not a production performance claim.
The miss analysis contains 39 missed events. The main gaps are victim-to-mule receipts and multi-payout cashout sequences.

## Limitations

All records are simulated, positive examples are limited, and the simulator has known shortcuts. Real-world validation is required before operational use.