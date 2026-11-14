# Detection methodology

## Victim-to-mule rule

- Receiver account age <= 15 days.
- Transaction amount >= ₹10,000.
- Prior 30-day receiver inflow >= training-control P99.

## Mule-layering rule

- Prior 72-hour sender inflow >= training-control P99.
- Outgoing amount / prior 72-hour inflow >= 0.80.

## Cashout investigation

- Prior 24-hour outgoing count and amount are retained as contextual evidence.
- The repeated-outgoing signal does not independently create alerts because it produced excessive legitimate alerts.
- Cashout detection remains a known gap.

## Explainable score

- Victim-to-mule rule: 50 points.
- Layering rule: 50 points.
- Score is a prioritisation weight, not a calibrated fraud probability.
- An alert is an investigative lead, not proof of fraud.