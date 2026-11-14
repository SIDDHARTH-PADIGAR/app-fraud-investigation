# Dataset profile

All records are synthetic. No real customer or bank data is used.

| File | Rows | Columns | Size MB |
|---|---:|---:|---:|
| data\account_ground_truth.parquet | 1,637 | 2 | 0.010 |
| data\accounts.parquet | 1,637 | 3 | 0.011 |
| data\campaign_ground_truth.csv | 8 | 11 | 0.001 |
| data\cashout_features.parquet | 94,722 | 3 | 1.003 |
| data\flow_features.parquet | 94,722 | 8 | 3.096 |
| data\splits\test.parquet | 21,668 | 30 | 1.964 |
| data\splits\train.parquet | 29,148 | 30 | 2.625 |
| data\splits\validation.parquet | 11,217 | 30 | 1.016 |
| data\transaction_features.parquet | 94,722 | 26 | 7.857 |
| data\transaction_ground_truth.parquet | 94,722 | 4 | 0.548 |
| data\transactions.parquet | 94,722 | 8 | 1.970 |

## Core data

- Transactions: 94,722
- Unique transaction IDs: 94,722
- Unique sender accounts: 1,637
- Unique receiver accounts: 1,637
- Amount range: ₹5.01 to ₹231,288.65
- Account records: 1,637

## Transaction labels

- legitimate: 94,470
- seasoning: 111
- victim_to_mule: 88
- mule_layering: 29
- cashout: 24