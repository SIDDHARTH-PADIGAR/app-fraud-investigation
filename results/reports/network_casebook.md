# Network investigation casebook

Cases are connected components of alerted sender-to-receiver transactions. Connectedness is an investigative lead, not proof of common control.

| Case | Accounts | Alert transfers | Alerted transaction volume (₹) | Risk points |
|---|---:|---:|---:|---:|
| CASE-0001 | 7 | 7 | 625,294.17 | 350 |
| CASE-0002 | 7 | 6 | 878,239.15 | 300 |
| CASE-0003 | 6 | 6 | 665,117.08 | 300 |
| CASE-0004 | 6 | 5 | 732,021.60 | 250 |
| CASE-0005 | 6 | 5 | 754,250.77 | 250 |
| CASE-0006 | 5 | 4 | 511,934.36 | 200 |
| CASE-0007 | 5 | 4 | 563,026.02 | 200 |
| CASE-0008 | 4 | 3 | 494,014.01 | 150 |

## Top case evidence

### CASE-0001

- Accounts: 7
- Alerted transfers: 7
- Alerted transaction volume: ₹625,294.17
- Victim-to-mule alerts: 4
- Layering alerts: 3
- Account IDs: 467,667,1169,1624,1625,1626,1627

|   transaction_id |   sender_id |   receiver_id |   amount_inr |   risk_score | alert_reasons                                             |
|-----------------:|------------:|--------------:|-------------:|-------------:|:----------------------------------------------------------|
|            94642 |        1169 |          1624 |      22624.9 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94650 |        1624 |          1625 |     208109   |           50 | Rapid onward fund movement;                               |
|            94649 |         467 |          1624 |      26651.5 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94646 |         667 |          1624 |      10273.4 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94640 |        1169 |          1624 |      12879   |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94651 |        1625 |          1626 |     189683   |           50 | Rapid onward fund movement;                               |
|            94652 |        1626 |          1627 |     155074   |           50 | Rapid onward fund movement;                               |

### CASE-0002

- Accounts: 7
- Alerted transfers: 6
- Alerted transaction volume: ₹878,239.15
- Victim-to-mule alerts: 2
- Layering alerts: 4
- Account IDs: 224,713,1606,1607,1608,1609,1610

|   transaction_id |   sender_id |   receiver_id |   amount_inr |   risk_score | alert_reasons                                             |
|-----------------:|------------:|--------------:|-------------:|-------------:|:----------------------------------------------------------|
|            94519 |         713 |          1606 |      68843.9 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94530 |        1606 |          1607 |     231289   |           50 | Rapid onward fund movement;                               |
|            94523 |         224 |          1606 |      13799.8 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94531 |        1607 |          1608 |     208999   |           50 | Rapid onward fund movement;                               |
|            94532 |        1608 |          1609 |     187736   |           50 | Rapid onward fund movement;                               |
|            94533 |        1609 |          1610 |     167572   |           50 | Rapid onward fund movement;                               |

### CASE-0003

- Accounts: 6
- Alerted transfers: 6
- Alerted transaction volume: ₹665,117.08
- Victim-to-mule alerts: 3
- Layering alerts: 3
- Account IDs: 511,1440,1611,1612,1613,1614

|   transaction_id |   sender_id |   receiver_id |   amount_inr |   risk_score | alert_reasons                                             |
|-----------------:|------------:|--------------:|-------------:|-------------:|:----------------------------------------------------------|
|            94549 |         511 |          1611 |      41995.8 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94559 |        1440 |          1611 |      16495.4 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94566 |        1611 |          1612 |     214839   |           50 | Rapid onward fund movement;                               |
|            94560 |        1440 |          1611 |      26385.9 |           50 | Suspicious receiving account; Repeated outgoing activity; |
|            94567 |        1612 |          1613 |     199316   |           50 | Rapid onward fund movement;                               |
|            94568 |        1613 |          1614 |     166085   |           50 | Rapid onward fund movement;                               |

### CASE-0004

- Accounts: 6
- Alerted transfers: 5
- Alerted transaction volume: ₹732,021.60
- Victim-to-mule alerts: 1
- Layering alerts: 4
- Account IDs: 399,1633,1634,1635,1636,1637

|   transaction_id |   sender_id |   receiver_id |   amount_inr |   risk_score | alert_reasons                 |
|-----------------:|------------:|--------------:|-------------:|-------------:|:------------------------------|
|            94716 |        1633 |          1634 |     214809   |           50 | Rapid onward fund movement;   |
|            94710 |         399 |          1633 |      74402.4 |           50 | Suspicious receiving account; |
|            94717 |        1634 |          1635 |     174633   |           50 | Rapid onward fund movement;   |
|            94718 |        1635 |          1636 |     139946   |           50 | Rapid onward fund movement;   |
|            94719 |        1636 |          1637 |     128231   |           50 | Rapid onward fund movement;   |

## Money-flow interpretation

Summed alerted transaction volume is not unique money moved, recovered funds or confirmed loss. The same funds may appear in multiple inter-account transfers.
Account-level incoming/outgoing summaries are in `results/case_accounts.csv`.