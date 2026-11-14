
import pandas as pd
from config import DATA_DIR, RESULTS_DIR


def main():
    predictions = pd.read_parquet(
        RESULTS_DIR / "test_predictions.parquet"
    )

    tx = pd.read_parquet(DATA_DIR / "transactions.parquet")
    features = pd.read_parquet(DATA_DIR / "transaction_features.parquet")
    flow = pd.read_parquet(DATA_DIR / "flow_features.parquet")
    cashout = pd.read_parquet(DATA_DIR / "cashout_features.parquet")

    # Identify missed fraud.
    missed = predictions[
        predictions["label"].eq(1)
        & ~predictions["victim_mule_alert"].fillna(False)
        & ~predictions["layering_alert"].fillna(False)
    ].copy()

    # Keep transaction metadata in one controlled merge.
    missed = missed.merge(
        tx[[
            "transaction_id", "timestamp_s", "sender_id",
            "receiver_id", "amount_inr", "payment_type", "channel"
        ]],
        on="transaction_id",
        validate="one_to_one"
    )

    # Attach selected transaction features.
    feature_cols = [
        "transaction_id",
        "receiver_account_age_days",
        "receiver_incoming_count_24h",
        "receiver_incoming_amount_24h",
        "receiver_incoming_count_30d",
        "receiver_incoming_amount_30d",
        "sender_account_age_days",
    ]

    missed = missed.merge(
        features[feature_cols],
        on="transaction_id",
        validate="one_to_one"
    )

    missed = missed.merge(
        flow[[
            "transaction_id",
            "sender_incoming_amount_72h",
            "sender_incoming_count_72h",
            "outgoing_to_recent_inflow_ratio"
        ]],
        on="transaction_id",
        validate="one_to_one"
    )

    missed = missed.merge(
        cashout,
        on="transaction_id",
        validate="one_to_one"
    )

    # Verify that all expected evidence is available.
    assert missed["timestamp_s"].notna().all()
    assert missed["stage"].notna().all()

    print("MISSED FRAUD INVESTIGATION")
    print(f"Missed transactions: {len(missed)}")

    print("\nBY STAGE")
    print(missed["stage"].value_counts().to_string())

    print("\nBY CAMPAIGN AND STAGE")
    print(
        missed.groupby(["campaign_id", "stage"])
        .size().to_string()
    )

    columns = [
        "transaction_id", "timestamp_s", "campaign_id", "stage",
        "sender_id", "receiver_id", "amount_inr",
        "receiver_account_age_days",
        "receiver_incoming_amount_30d",
        "sender_incoming_amount_72h",
        "outgoing_to_recent_inflow_ratio",
        "sender_prior_outgoing_count_24h",
        "sender_prior_outgoing_amount_24h",
    ]

    missed = missed.sort_values(
        ["stage", "campaign_id", "timestamp_s"]
    )

    print("\nMISSED TRANSACTION EVIDENCE")
    print(missed[columns].to_string(index=False))

    output = RESULTS_DIR / "missed_fraud_analysis.csv"
    missed.to_csv(output, index=False)

    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
