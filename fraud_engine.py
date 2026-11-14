
import pandas as pd

from config import DATA_DIR, RESULTS_DIR


def merge_features(base, extra):
    overlap = (set(base.columns) & set(extra.columns)) - {"transaction_id"}
    return base.merge(
        extra.drop(columns=list(overlap)),
        on="transaction_id",
        validate="one_to_one"
    )


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load source data
    tx = pd.read_parquet(DATA_DIR / "transactions.parquet")
    features = pd.read_parquet(DATA_DIR / "transaction_features.parquet")
    flow = pd.read_parquet(DATA_DIR / "flow_features.parquet")
    cashout = pd.read_parquet(DATA_DIR / "cashout_features.parquet")
    truth = pd.read_parquet(DATA_DIR / "transaction_ground_truth.parquet")

    # 2. Assemble point-in-time features
    df = merge_features(tx, features)

    df = merge_features(
        df,
        flow.drop(columns=[
            "timestamp_s", "sender_id", "receiver_id", "amount_inr"
        ])
    )

    df = merge_features(df, cashout)

    # Fail early if the expected schema is missing
    required = [
        "receiver_account_age_days",
        "receiver_incoming_amount_30d",
        "sender_incoming_amount_72h",
        "outgoing_to_recent_inflow_ratio",
        "sender_prior_outgoing_count_24h",
        "sender_prior_outgoing_amount_24h",
    ]

    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    # 3. Derive thresholds from training negatives only
    train = pd.read_parquet(DATA_DIR / "splits" / "train.parquet")
    train = merge_features(train, features)

    train = merge_features(
        train,
        flow[[
            "transaction_id",
            "sender_incoming_amount_72h",
            "outgoing_to_recent_inflow_ratio"
        ]]
    )

    controls = train[train["label"].eq(0)]

    inflow_threshold = controls[
        "sender_incoming_amount_72h"
    ].quantile(0.99)

    receiver_inflow_threshold = controls[
        "receiver_incoming_amount_30d"
    ].quantile(0.99)

    print("FROZEN TRAINING THRESHOLDS")
    print(f"Receiver 30d inflow P99: Rs {receiver_inflow_threshold:,.2f}")
    print(f"Sender 72h inflow P99: Rs {inflow_threshold:,.2f}")
    print("Forwarding ratio: 0.80")

    # 4. Detection rules

    # A: Newly active receiving account with unusually high inflows
    victim_rule = (
        df["receiver_account_age_days"].le(15)
        & df["amount_inr"].ge(10_000)
        & df["receiver_incoming_amount_30d"].ge(
            receiver_inflow_threshold
        )
    )

    # B: Rapid onward movement of recently received funds
    layering_rule = (
        df["sender_incoming_amount_72h"].ge(inflow_threshold)
        & df["outgoing_to_recent_inflow_ratio"].ge(0.80)
    )

    # C: Repeated outgoing activity, supporting evidence only
    cashout_signal = (
        df["sender_prior_outgoing_count_24h"].ge(1)
        & df["sender_prior_outgoing_amount_24h"].gt(0)
    )

    # 5. Explainable risk score
# Cashout activity remains supporting investigation evidence.
# It must not independently generate alerts.

    df["victim_mule_alert"] = victim_rule
    df["layering_alert"] = layering_rule
    df["cashout_activity_signal"] = cashout_signal

    df["risk_score"] = (
        victim_rule.astype(int) * 50
        + layering_rule.astype(int) * 50
    )

    # Cashout activity adds context only to an existing alert.
    df["alert_reasons"] = ""

    df.loc[victim_rule, "alert_reasons"] += (
        "Suspicious receiving account; "
    )
    df.loc[layering_rule, "alert_reasons"] += (
        "Rapid onward fund movement; "
    )

    df.loc[
        (victim_rule | layering_rule) & cashout_signal,
        "alert_reasons"
    ] += "Repeated outgoing activity; "

    # Only the two validated detection rules create alerts.
    alerts = df[victim_rule | layering_rule].copy()

    alerts = alerts.sort_values(
        ["risk_score", "timestamp_s"],
        ascending=[False, True]
    )

    # 6. Rank alerts
    alerts = df[df["risk_score"] > 0].copy()

    alerts = alerts.sort_values(
        ["risk_score", "timestamp_s"],
        ascending=[False, True]
    )

    # 7. Attach ground truth only for evaluation
    evaluation = alerts.merge(
        truth[["transaction_id", "stage", "campaign_id"]],
        on="transaction_id",
        validate="one_to_one"
    )

    # 8. Save investigation outputs
    alerts.to_parquet(
        RESULTS_DIR / "fraud_alerts.parquet",
        index=False
    )

    evaluation.to_csv(
        RESULTS_DIR / "fraud_alerts_evaluation.csv",
        index=False
    )

    # 9. Report
    print("\nFRAUD ENGINE RESULTS")
    print(f"Transactions processed: {len(df):,}")
    print(f"Alerts generated: {len(alerts):,}")
    print(f"Victim-to-mule alerts: {victim_rule.sum():,}")
    print(f"Layering alerts: {layering_rule.sum():,}")
    print(f"Cashout activity signals: {cashout_signal.sum():,}")

    print("\nALERTS BY FRAUD STAGE")
    print(evaluation["stage"].value_counts(dropna=False).to_string())

    print("\nTOP 15 ALERTS")
    columns = [
        "transaction_id",
        "sender_id",
        "receiver_id",
        "amount_inr",
        "risk_score",
        "alert_reasons"
    ]

    print(alerts[columns].head(15).to_string(index=False))

    print("\nSAVED OUTPUTS")
    print("results/fraud_alerts.parquet")
    print("results/fraud_alerts_evaluation.csv")


if __name__ == "__main__":
    main()
