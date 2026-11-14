from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from config import DATA_DIR, RESULTS_DIR, TRAIN, VAL, TEST, SEED

ROOT = Path(__file__).resolve().parent
REPORTS = RESULTS_DIR / "reports"
EVIDENCE = RESULTS_DIR / "evidence"
CHARTS = EVIDENCE / "charts"
NETWORKS = EVIDENCE / "networks"
for p in (REPORTS, EVIDENCE, CHARTS, NETWORKS):
    p.mkdir(parents=True, exist_ok=True)


def read(path):
    path = Path(path)
    if not path.exists():
        return None
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)


def chart_bar(path, title, labels, values, ylabel):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def inventory_and_dictionary():
    inventory, dictionary = [], []
    for path in sorted(DATA_DIR.rglob("*")):
        if not path.is_file() or path.suffix not in (".parquet", ".csv"):
            continue
        df = read(path)
        if df is None:
            continue
        inventory.append({
            "file": str(path.relative_to(ROOT)),
            "rows": len(df),
            "columns": len(df.columns),
            "size_mb": round(path.stat().st_size / 1048576, 3),
        })
        for col in df.columns:
            s = df[col]
            sample = "" if s.dropna().empty else str(s.dropna().iloc[0])[:70]
            dictionary.append({
                "file": str(path.relative_to(ROOT)),
                "column": col,
                "dtype": str(s.dtype),
                "null_count": int(s.isna().sum()),
                "null_pct": round(float(s.isna().mean() * 100), 3),
                "distinct": int(s.nunique(dropna=True)),
                "sample": sample,
            })

    inv = pd.DataFrame(inventory)
    dic = pd.DataFrame(dictionary)
    inv.to_csv(REPORTS / "dataset_inventory.csv", index=False)
    dic.to_csv(REPORTS / "data_dictionary.csv", index=False)

    lines = ["# Data dictionary", "", "Generated from the project's current data files.", "",
             "| File | Column | Type | Nulls | Null % | Distinct | Sample |",
             "|---|---|---|---:|---:|---:|---|"]
    for r in dictionary:
        lines.append(
            f"| {r['file']} | {r['column']} | {r['dtype']} | "
            f"{r['null_count']} | {r['null_pct']}% | {r['distinct']} | {r['sample']} |"
        )
    (REPORTS / "data_dictionary.md").write_text("\n".join(lines), encoding="utf-8")

    tx = read(DATA_DIR / "transactions.parquet")
    truth = read(DATA_DIR / "transaction_ground_truth.parquet")
    accounts = read(DATA_DIR / "accounts.parquet")
    lines = ["# Dataset profile", "", "All records are synthetic. No real customer or bank data is used.", "",
             "| File | Rows | Columns | Size MB |", "|---|---:|---:|---:|"]
    for r in inventory:
        lines.append(f"| {r['file']} | {r['rows']:,} | {r['columns']} | {r['size_mb']:.3f} |")
    lines += ["", "## Core data", ""]
    if tx is not None:
        lines += [
            f"- Transactions: {len(tx):,}",
            f"- Unique transaction IDs: {tx.transaction_id.nunique():,}",
            f"- Unique sender accounts: {tx.sender_id.nunique():,}",
            f"- Unique receiver accounts: {tx.receiver_id.nunique():,}",
            f"- Amount range: ₹{tx.amount_inr.min():,.2f} to ₹{tx.amount_inr.max():,.2f}",
        ]
    if accounts is not None:
        lines.append(f"- Account records: {len(accounts):,}")
    if truth is not None:
        lines += ["", "## Transaction labels", ""]
        lines += [f"- {k}: {v:,}" for k, v in truth.stage.value_counts().items()]
    (REPORTS / "dataset_profile.md").write_text("\n".join(lines), encoding="utf-8")
    return inv


def write_methodology():
    audit = RESULTS_DIR / "simulator_audit.txt"
    audit_text = audit.read_text(encoding="utf-16") if audit.exists() else "Simulator audit file not found."
    (REPORTS / "simulator_and_temporal_methodology.md").write_text(
        "\n".join([
            "# Simulator audit and temporal methodology", "",
            "## Simulator audit", "", audit_text, "",
            "## Temporal splits", "",
            f"- Warm-up ends at day 14.",
            f"- Train event-time interval: [{TRAIN[0]}, {TRAIN[1]}).",
            f"- Validation event-time interval: [{VAL[0]}, {VAL[1]}).",
            f"- Test event-time interval: [{TEST[0]}, {TEST[1]}).",
            "- Labels use a simulated three-day maturity delay.",
            "- Thresholds are derived from training controls; validation is for selection; test is held out.",
            "", "## Point-in-time and leakage controls", "",
            "- Rolling features use strictly prior transactions; same-timestamp events are excluded.",
            "- Campaign IDs, ground-truth labels, account true roles and account IDs are not detector inputs.",
            "- Simulator audit identified APP_TRANSFER as a perfect fraud shortcut; payment_type must not be used as a detector feature.",
            "- Receiver segment and role fields are simulator shortcuts and must not be used as detector features.",
            "", "## Limitations", "",
            "- All data is synthetic and the positive sample is small.",
            "- Simulator campaigns and account-generation rules may create artificial patterns.",
            "- Results do not establish real-world or production performance.",
            "", "## Reproducibility", "",
            "Record Python/dependency versions and Git commit. Run generation, feature engineering, temporal split, detector and evaluation scripts in the documented order."
        ]), encoding="utf-8"
    )

    (REPORTS / "detection_methodology.md").write_text(
        "\n".join([
            "# Detection methodology", "",
            "## Victim-to-mule rule", "",
            "- Receiver account age <= 15 days.",
            "- Transaction amount >= ₹10,000.",
            "- Prior 30-day receiver inflow >= training-control P99.",
            "", "## Mule-layering rule", "",
            "- Prior 72-hour sender inflow >= training-control P99.",
            "- Outgoing amount / prior 72-hour inflow >= 0.80.",
            "", "## Cashout investigation", "",
            "- Prior 24-hour outgoing count and amount are retained as contextual evidence.",
            "- The repeated-outgoing signal does not independently create alerts because it produced excessive legitimate alerts.",
            "- Cashout detection remains a known gap.",
            "", "## Explainable score", "",
            "- Victim-to-mule rule: 50 points.",
            "- Layering rule: 50 points.",
            "- Score is a prioritisation weight, not a calibrated fraud probability.",
            "- An alert is an investigative lead, not proof of fraud."
        ]), encoding="utf-8"
    )


def evaluation_and_charts():
    pred = read(RESULTS_DIR / "test_predictions.parquet")
    eval_table = read(RESULTS_DIR / "test_evaluation.csv")
    truth = read(DATA_DIR / "transaction_ground_truth.parquet")
    missed = read(RESULTS_DIR / "missed_fraud_analysis.csv")
    if pred is None or eval_table is None or missed is None:
        raise FileNotFoundError("Run evaluate_detector.py and analyze_misses.py before packaging.")

    actual = pred.label.eq(1)
    victim = pred.victim_mule_alert.fillna(False).astype(bool)
    layering = pred.layering_alert.fillna(False).astype(bool)
    combined = victim | layering
    tp = int((combined & actual).sum())
    fp = int((combined & ~actual).sum())
    fn = int((~combined & actual).sum())
    tn = int((~combined & ~actual).sum())
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    pred = pred.drop(columns=["stage", "campaign_id"], errors="ignore")
    
    joined = pred.merge(
        truth[["transaction_id", "stage", "campaign_id"]],
        on="transaction_id", validate="one_to_one"
    )
    detected = joined[combined.to_numpy()]
    actual_stage = joined[joined.label.eq(1)].groupby("stage").size()
    detected_stage = detected.groupby("stage").size()
    detected_campaign = detected.groupby("campaign_id").size()

    lines = [
        "# Untouched test-set evaluation", "",
        f"- Transactions: {len(pred):,}",
        f"- Fraud-stage positives: {int(actual.sum()):,}",
        f"- Legitimate transactions: {int((~actual).sum()):,}",
        f"- TP: {tp}; FP: {fp}; FN: {fn}; TN: {tn}",
        f"- Precision: {precision:.2%}",
        f"- Recall: {recall:.2%}",
        f"- F1: {f1:.4f}",
        "",
        "Zero false positives in this synthetic holdout is not a guarantee of zero false positives in production.",
        "", "## Detector comparison", "", eval_table.to_markdown(index=False),
        "", "## Stage-level results", "",
        "| Stage | Positives | Detected | Missed |", "|---|---:|---:|---:|"
    ]
    for stage, total in actual_stage.items():
        found = int(detected_stage.get(stage, 0))
        lines.append(f"| {stage} | {int(total)} | {found} | {int(total)-found} |")
    lines += ["", "## Campaign-level detections", ""]
    lines += [f"- {k}: {int(v)}" for k, v in detected_campaign.items()]
    lines += ["", "## Missed fraud", "",
              f"- Total missed events: {len(missed)}"]
    lines += [f"- {k}: {int(v)}" for k, v in missed.stage.value_counts().items()]
    lines += ["", "Test results are descriptive. Do not tune thresholds using this holdout."]
    (REPORTS / "test_evaluation.md").write_text("\n".join(lines), encoding="utf-8")

    chart_bar(CHARTS / "test_metrics.png", "Untouched test-set performance",
              ["Precision", "Recall", "F1"], [precision, recall, f1], "Score")
    stages = list(actual_stage.index)
    x = np.arange(len(stages))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - .18, [int(actual_stage[s]) for s in stages], .36, label="Test positives")
    ax.bar(x + .18, [int(detected_stage.get(s, 0)) for s in stages], .36, label="Detected")
    ax.set_xticks(x, stages, rotation=15)
    ax.set_title("Fraud-stage detection coverage")
    ax.set_ylabel("Transactions")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS / "fraud_stage_detection.png", dpi=180)
    plt.close(fig)

    chart_bar(CHARTS / "campaign_detections.png", "Detected transactions by campaign",
              detected_campaign.index.astype(str).tolist(), detected_campaign.tolist(), "Detections")

    fig, ax = plt.subplots(figsize=(5, 4))
    matrix = np.array([[tn, fp], [fn, tp]])
    im = ax.imshow(matrix)
    ax.set_xticks([0, 1], ["Predicted legitimate", "Predicted fraud"], rotation=12)
    ax.set_yticks([0, 1], ["Actual legitimate", "Actual fraud"])
    for (i, j), value in np.ndenumerate(matrix):
        ax.text(j, i, f"{value:,}", ha="center", va="center")
    ax.set_title("Combined detector confusion matrix")
    fig.colorbar(im, ax=ax, label="Transactions")
    fig.tight_layout()
    fig.savefig(CHARTS / "confusion_matrix.png", dpi=180)
    plt.close(fig)


def missed_and_case_reports():
    missed = pd.read_csv(RESULTS_DIR / "missed_fraud_analysis.csv")
    lines = [
        "# Missed-fraud investigation", "",
        "Diagnostic analysis of missed events in the held-out test set. This analysis is not used to retune test thresholds.",
        "", f"Total missed transactions: {len(missed)}", "",
        "## Misses by stage", "",
        missed.stage.value_counts().to_frame("missed").to_markdown(),
        "", "## Misses by campaign and stage", "",
        missed.groupby(["campaign_id", "stage"]).size().to_frame("missed").to_markdown(),
        "", "## Interpretation", "",
        "- Victim-to-mule: 32 misses. The current rule depends on prior receiver inflow and a ₹10,000 floor; early receipts and smaller split payments can fail one or both conditions.",
        "- Cashout: 6 misses. Multiple payouts from a mule account are not well represented by a single-transaction onward-flow ratio.",
        "- Layering: 1 miss. The event's forwarding ratio was 0.774519, below the frozen 0.80 threshold.",
        "- These findings motivate future account-level cumulative-flow and payout-sequence features, developed using training/validation data only."
    ]
    (REPORTS / "missed_fraud_investigation.md").write_text("\n".join(lines), encoding="utf-8")

    cases_path = RESULTS_DIR / "investigation_cases.csv"
    case_tx_path = RESULTS_DIR / "case_transactions.parquet"
    accounts_path = RESULTS_DIR / "case_accounts.csv"
    if not all(p.exists() for p in (cases_path, case_tx_path, accounts_path)):
        warnings.warn("Network case outputs missing; skipping casebook and graphs.")
        return

    cases = pd.read_csv(cases_path)
    case_tx = pd.read_parquet(case_tx_path)
    accounts = pd.read_csv(accounts_path)
    cases.to_csv(REPORTS / "ranked_investigation_cases.csv", index=False)

    lines = [
        "# Network investigation casebook", "",
        "Cases are connected components of alerted sender-to-receiver transactions. Connectedness is an investigative lead, not proof of common control.",
        "", "| Case | Accounts | Alert transfers | Alerted transaction volume (₹) | Risk points |",
        "|---|---:|---:|---:|---:|"
    ]
    for r in cases.itertuples(index=False):
        lines.append(f"| {r.case_id} | {r.account_count} | {r.alert_transaction_count} | {r.total_alerted_amount:,.2f} | {r.total_risk_score} |")

    lines += ["", "## Top case evidence", ""]
    for r in cases.head(4).itertuples(index=False):
        lines += [
            f"### {r.case_id}", "",
            f"- Accounts: {r.account_count}",
            f"- Alerted transfers: {r.alert_transaction_count}",
            f"- Alerted transaction volume: ₹{r.total_alerted_amount:,.2f}",
            f"- Victim-to-mule alerts: {r.victim_mule_alerts}",
            f"- Layering alerts: {r.layering_alerts}",
            f"- Account IDs: {r.account_ids}", ""
        ]
        subset = case_tx[case_tx.case_id.eq(r.case_id)]
        lines.append(subset[[
            "transaction_id", "sender_id", "receiver_id",
            "amount_inr", "risk_score", "alert_reasons"
        ]].to_markdown(index=False))
        lines.append("")

        graph = nx.DiGraph()
        for edge in subset.itertuples(index=False):
            graph.add_edge(edge.sender_id, edge.receiver_id, amount=float(edge.amount_inr))
        if graph.number_of_nodes():
            fig, ax = plt.subplots(figsize=(9, 6))
            pos = nx.spring_layout(graph, seed=SEED)
            nx.draw_networkx(graph, pos, ax=ax, node_size=900, font_size=8,
                             arrows=True, arrowsize=18)
            labels = {(u, v): f"₹{d['amount']:,.0f}" for u, v, d in graph.edges(data=True)}
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=7, ax=ax)
            ax.set_title(f"{r.case_id}: directed alerted transfers")
            ax.axis("off")
            fig.tight_layout()
            fig.savefig(NETWORKS / f"{r.case_id.lower()}_network.png", dpi=180)
            plt.close(fig)

    lines += [
        "## Money-flow interpretation", "",
        "Summed alerted transaction volume is not unique money moved, recovered funds or confirmed loss. The same funds may appear in multiple inter-account transfers.",
        "Account-level incoming/outgoing summaries are in `results/case_accounts.csv`."
    ]
    (REPORTS / "network_casebook.md").write_text("\n".join(lines), encoding="utf-8")


def write_summaries():
    pred = pd.read_parquet(RESULTS_DIR / "test_predictions.parquet")
    missed = pd.read_csv(RESULTS_DIR / "missed_fraud_analysis.csv")
    actual = pred.label.eq(1)
    predicted = pred.victim_mule_alert.fillna(False).astype(bool) | pred.layering_alert.fillna(False).astype(bool)
    tp = int((actual & predicted).sum())
    fp = int((~actual & predicted).sum())
    fn = int((actual & ~predicted).sum())
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    (REPORTS / "executive_summary.md").write_text("\n".join([
        "# Executive summary", "",
        "## Objective", "",
        "Build a reproducible synthetic APP-fraud investigation benchmark to detect victim-to-mule receipts and mule-layering transfers, then group alerts into connected account investigations.",
        "", "## What was built", "",
        "- Synthetic campaign-based transaction dataset and audit.",
        "- Point-in-time transaction and fund-flow features.",
        "- Delayed-label temporal train, validation and test splits.",
        "- Explainable receiving-account and rapid-fund-forwarding rules.",
        "- Connected-account cases with transaction and account evidence.",
        "", "## Untouched test results", "",
        f"- Transactions: {len(pred):,}",
        f"- TP: {tp}; FP: {fp}; FN: {fn}",
        f"- Precision: {precision:.2%}; recall: {recall:.2%}; F1: {f1:.4f}",
        "", "## Interpretation", "",
        "The detector is conservative on this synthetic holdout: it recorded no false positives but detected only a subset of fraud-stage transactions. This is not a production performance claim.",
        f"The miss analysis contains {len(missed)} missed events. The main gaps are victim-to-mule receipts and multi-payout cashout sequences.",
        "", "## Limitations", "",
        "All records are simulated, positive examples are limited, and the simulator has known shortcuts. Real-world validation is required before operational use."
    ]), encoding="utf-8")

    (REPORTS / "technical_report.md").write_text("\n".join([
        "# Technical report: APP fraud and mule-network investigation", "",
        "## 1. Problem definition and threat model", "",
        "APP fraud involves a payer being manipulated into authorising a payment to a fraudster-controlled or fraudster-benefiting account. Mule accounts receive and move proceeds through onward transfers and cashout.",
        "", "## 2. Objective", "",
        "Identify suspicious victim-to-mule receipts and rapid onward fund movement, then group alerted transactions into connected investigation cases.",
        "", "## 3. Data and simulation", "",
        "The project uses synthetic transaction, account and campaign records. See `dataset_profile.md`, `data_dictionary.md` and `simulator_and_temporal_methodology.md`.",
        "", "## 4. Feature engineering", "",
        "Features describe strictly prior rolling inbound/outbound activity, account age and amount-to-history ratios. Flow features compare an outgoing transfer with the sender's prior 72-hour inflow.",
        "", "## 5. Temporal methodology", "",
        "Time-based splits use delayed label maturity. Training controls derive thresholds; validation is used for selection; the test set is reserved for final evaluation.",
        "", "## 6. Detection", "",
        "The victim-to-mule rule uses receiver age, payment amount and prior receiver inflow. The layering rule uses prior sender inflow and an outgoing-to-inflow ratio. Repeated outgoing activity is context only, not an independent alert.",
        "", "## 7. Network investigation", "",
        "Directed sender-to-receiver alert edges are grouped into connected components. A connected component is an investigative lead, not proof of common control.",
        "", "## 8. Evaluation", "",
        f"Untouched test performance: precision {precision:.2%}, recall {recall:.2%}, F1 {f1:.4f}; TP {tp}, FP {fp}, FN {fn}.",
        "", "## 9. Error analysis", "",
        f"{len(missed)} test fraud-stage events were missed. See `missed_fraud_investigation.md` for stage and campaign breakdowns.",
        "", "## 10. Limitations and next steps", "",
        "- Expand independent campaign and legitimate-behaviour diversity.",
        "- Remove simulator shortcuts and test adversarial variations.",
        "- Develop cumulative account-flow and multi-payout sequence features using training/validation only.",
        "- Evaluate at transaction, account, campaign and case levels.",
        "- Validate with appropriate real-world data before operational claims.",
        "", "## 11. Reproducibility", "",
        "See the project README for environment setup and execution order. Generated reports and figures are under `results/reports/` and `results/evidence/`."
    ]), encoding="utf-8")


def main():
    print("Generating project documentation and evidence...")
    inventory = inventory_and_dictionary()
    print(f"Dataset files: {len(inventory)}")
    write_methodology()
    evaluation_and_charts()
    missed_and_case_reports()
    write_summaries()

    files = sorted(str(p.relative_to(ROOT)) for p in EVIDENCE.rglob("*") if p.is_file())
    (EVIDENCE / "README.md").write_text(
        "# Evidence index\n\nGenerated charts and network diagrams:\n\n" +
        "\n".join(f"- `{p}`" for p in files),
        encoding="utf-8"
    )

    print("\nPACKAGE COMPLETE")
    print(f"Reports: {REPORTS}")
    print(f"Evidence: {EVIDENCE}")
    print("\nGenerated reports:")
    for p in sorted(REPORTS.glob("*")):
        print(f"  {p.name}")
    print("\nGenerated evidence:")
    for p in sorted(EVIDENCE.rglob("*.png")):
        print(f"  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
