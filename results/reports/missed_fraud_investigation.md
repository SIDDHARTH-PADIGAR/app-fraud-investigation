# Missed-fraud investigation

Diagnostic analysis of missed events in the held-out test set. This analysis is not used to retune test thresholds.

Total missed transactions: 39

## Misses by stage

| stage          |   missed |
|:---------------|---------:|
| victim_to_mule |       32 |
| cashout        |        6 |
| mule_layering  |        1 |

## Misses by campaign and stage

|                            |   missed |
|:---------------------------|---------:|
| ('C005', 'cashout')        |        3 |
| ('C005', 'mule_layering')  |        1 |
| ('C005', 'victim_to_mule') |        4 |
| ('C006', 'cashout')        |        3 |
| ('C006', 'victim_to_mule') |        7 |
| ('C007', 'victim_to_mule') |       12 |
| ('C008', 'victim_to_mule') |        9 |

## Interpretation

- Victim-to-mule: 32 misses. The current rule depends on prior receiver inflow and a ₹10,000 floor; early receipts and smaller split payments can fail one or both conditions.
- Cashout: 6 misses. Multiple payouts from a mule account are not well represented by a single-transaction onward-flow ratio.
- Layering: 1 miss. The event's forwarding ratio was 0.774519, below the frozen 0.80 threshold.
- These findings motivate future account-level cumulative-flow and payout-sequence features, developed using training/validation data only.