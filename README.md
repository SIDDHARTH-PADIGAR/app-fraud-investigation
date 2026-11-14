# APP Fraud Investigation Workbench

**A reproducible, rule-based investigation system for detecting Authorised Push Payment (APP) fraud patterns and tracing mule-account networks.**

This project simulates financial transaction activity, identifies suspicious victim-to-mule payments and mule-layering transfers, and groups alerts into connected account investigations.

It focuses on explainable detection, point-in-time feature engineering, temporal evaluation, and evidence-led investigation rather than treating fraud detection as a black-box classification problem.

---

## Key Results

Evaluated on an untouched synthetic test set:

| Metric | Result |
|---|---:|
| Transactions evaluated | 21,668 |
| Fraud-stage transactions | 56 |
| True positives | 17 |
| False positives | 0 |
| False negatives | 39 |
| Precision | 100% |
| Recall | 30.36% |
| F1 score | 0.4658 |

**Interpretation:** The detector was conservative on this synthetic holdout. It identified a subset of suspicious activity without false alerts in this sample, but missed 39 fraud-stage transactions. These results are not representative of production performance.

## What It Does

- **Transaction simulation:** Generates synthetic customers, mule accounts, transactions, and coordinated fraud campaigns.
- **Point-in-time features:** Calculates historical transaction activity and fund-flow behaviour without using future events.
- **Temporal evaluation:** Uses time-based train, validation, and test splits with delayed-label handling.
- **Explainable detection:** Applies transparent rules for suspicious receiving accounts and rapid fund forwarding.
- **Network investigation:** Groups connected alert accounts into investigation cases with supporting transaction evidence.
- **Miss analysis:** Examines undetected fraud patterns to identify weaknesses in the current detection approach.

## Detection Approach

| Investigation pattern | Signals |
|---|---|
| Victim-to-mule | New receiving account, transaction amount, historical incoming volume |
| Mule layering | Recent incoming funds and outgoing-to-incoming amount ratio |
| Cashout | Prior outgoing activity retained as contextual evidence |

The system uses rule-based prioritisation. Its scores are not calibrated fraud probabilities, and an alert is an investigative lead, not proof of fraud.

## Test Results by Fraud Stage

![Fraud stage detection](results/evidence/charts/fraud_stage_detection.png)

| Fraud stage | Detected | Missed |
|---|---:|---:|
| Victim-to-mule | 7 | 32 |
| Mule layering | 10 | 1 |
| Cashout | 0 | 6 |

Cashout detection remains an identified gap. Repeated outgoing activity generated too many legitimate alerts to be used as an independent detection rule.

## Investigation Evidence

The network investigation groups connected alert accounts into cases and preserves transaction-level evidence for review.

**Example investigation networks:**

![Investigation case 1](results/evidence/networks/case-0001_network.png)

![Investigation case 2](results/evidence/networks/case-0002_network.png)

Additional cases and evaluation charts are available in [`results/evidence/`](results/evidence/).

## Technical Overview

- **Language:** Python
- **Data processing:** Pandas, NumPy, DuckDB, PyArrow
- **Detection:** Explainable rule-based engine
- **Network analysis:** NetworkX
- **Visualisation:** Matplotlib
- **Testing:** Pytest

### Pipeline

1. Generate synthetic transaction and account data.
2. Engineer historical transaction and fund-flow features.
3. Construct delayed-label temporal datasets.
4. Evaluate detection rules and generate alerts.
5. Group connected accounts into investigation cases.
6. Evaluate performance and analyse missed fraud.
7. Generate reports, charts, and investigation evidence.

## Repository Outputs

| Location | Contents |
|---|---|
| `data/` | Synthetic accounts, transactions, features, labels, and temporal splits |
| `results/reports/` | Executive summary, methodology, evaluation, casebook, and technical report |
| `results/evidence/charts/` | Test metrics, confusion matrix, stage detection, and campaign results |
| `results/evidence/networks/` | Investigation network visualisations |
| `sql/` | Feature engineering queries |

Start with the [Executive Summary](results/reports/executive_summary.md), then review the [Technical Report](results/reports/technical_report.md).

## Limitations

- All data is synthetic. No real customer or banking records are used.
- Fraud examples are limited and generated from predefined campaign behaviours.
- The simulator contains known shortcuts and does not represent the full complexity of real financial fraud.
- Zero false positives on this test set does not establish production precision.
- Cashout detection is incomplete.
- The system has not been validated against real-world banking data.

**This is a research and investigation prototype, not a production fraud detection system.**

## Reproducibility

Install dependencies in a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The generated datasets and supporting reports are included in the repository. The individual pipeline scripts are available at the project root.

---

*Built as an applied investigation into transaction behaviour, mule-account networks, explainable detection, and evidence-driven fraud analysis.*
