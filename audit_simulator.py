
"""Audit synthetic-data shortcuts and potential label leakage."""
import pandas as pd

from config import DATA_DIR


def section(title):
    print(f"\n{'=' * 75}\n{title}\n{'=' * 75}")


def main():
    tx = pd.read_parquet(DATA_DIR / "transactions.parquet")
    truth = pd.read_parquet(DATA_DIR / "transaction_ground_truth.parquet")
    accounts = pd.read_parquet(DATA_DIR / "accounts.parquet")
    account_truth = pd.read_parquet(DATA_DIR / "account_ground_truth.parquet")

    df = tx.merge(
        truth, on="transaction_id", validate="one_to_one"
    )

    # Account metadata is included for audit only, never as model features.
    sender_meta = accounts.rename(columns={
        "account_id": "sender_id",
        "segment": "sender_segment_actual",
        "account_created_day": "sender_created_day",
    })

    receiver_meta = accounts.rename(columns={
        "account_id": "receiver_id",
        "segment": "receiver_segment_actual",
        "account_created_day": "receiver_created_day",
    })

    df = df.merge(sender_meta, on="sender_id", validate="many_to_one")
    df = df.merge(receiver_meta, on="receiver_id", validate="many_to_one")

    roles = account_truth.rename(columns={
        "account_id": "sender_id",
        "true_role": "sender_true_role",
    })

    df = df.merge(roles, on="sender_id", validate="many_to_one")

    df["sender_age_days"] = df["day"] - df["sender_created_day"]
    df["receiver_age_days"] = df["day"] - df["receiver_created_day"]

    # 1. Dataset and label integrity.
    section("1. DATASET INTEGRITY")
    print("Transactions:", len(df))
    print("Unique transaction IDs:", df.transaction_id.nunique())
    print("Duplicate transaction IDs:", df.transaction_id.duplicated().sum())
    print("Missing transaction truth:", df.stage.isna().sum())
    print("Fraud-stage rows:", df.is_fraud_stage.sum())
    print("\nStage counts:")
    print(df.stage.value_counts(dropna=False).to_string())

    # 2. Numeric distributions by stage.
    section("2. NUMERIC DISTRIBUTIONS BY STAGE")
    numeric = [
        "amount_inr",
        "day",
        "sender_id",
        "receiver_id",
        "sender_age_days",
        "receiver_age_days",
    ]

    for col in numeric:
        print(f"\n{col}")
        print(
            df.groupby("stage", dropna=False)[col]
            .agg(["count", "median", "mean", "min", "max"])
            .round(2).to_string()
        )

    # 3. Categorical shortcuts.
    for col in ["payment_type", "channel", "sender_segment_actual",
                "receiver_segment_actual", "sender_true_role"]:
        section(f"3. {col.upper()} BY STAGE")
        counts = pd.crosstab(df[col], df.stage)
        print("Counts:")
        print(counts.to_string())
        print("\nRow percentages:")
        print(
            pd.crosstab(df[col], df.stage, normalize="index")
            .mul(100).round(1).to_string()
        )

    # 4. Account ID allocation and campaign structure.
    section("4. ACCOUNT ID AND CAMPAIGN STRUCTURE")
    for col in ["sender_id", "receiver_id"]:
        print(f"\n{col} by stage:")
        print(
            df.groupby("stage", dropna=False)[col]
            .agg(["min", "median", "max", "nunique"])
            .to_string()
        )

    print("\nCampaigns by stage:")
    print(
        df.groupby(["campaign_id", "stage"], dropna=False)
        .size().to_string()
    )

    # 5. Daily fraud prevalence and campaign timing.
    section("5. DAILY ACTIVITY")
    daily = df.groupby("day").agg(
        transactions=("transaction_id", "count"),
        fraud_stages=("is_fraud_stage", "sum"),
        campaigns=("campaign_id", "nunique"),
    )
    daily["fraud_stage_rate_pct"] = (
        daily.fraud_stages / daily.transactions * 100
    )
    print(daily.to_string())

    # 6. Does account role reveal future fraud?
    section("6. SENDER ROLE VS TRANSACTION STAGE")
    print(
        pd.crosstab(df.sender_true_role, df.stage)
        .to_string()
    )

    # 7. Label association with obvious fields.
    section("7. FRAUD-STAGE RATE BY CATEGORICAL FIELD")
    for col in ["payment_type", "channel", "sender_segment_actual",
                "receiver_segment_actual"]:
        summary = df.groupby(col).agg(
            transactions=("transaction_id", "count"),
            fraud_stages=("is_fraud_stage", "sum"),
        )
        summary["fraud_rate_pct"] = (
            summary.fraud_stages / summary.transactions * 100
        )
        print(f"\n{col}")
        print(summary.round(3).to_string())

    # 8. Check whether campaign labels align with synthetic account ranges.
    section("8. CAMPAIGN ACCOUNT ID RANGES")
    campaign_rows = df[df.campaign_id.notna()]
    print(
        campaign_rows.groupby("campaign_id").agg(
            first_day=("day", "min"),
            last_day=("day", "max"),
            sender_min=("sender_id", "min"),
            sender_max=("sender_id", "max"),
            receiver_min=("receiver_id", "min"),
            receiver_max=("receiver_id", "max"),
            accounts=("sender_id", "nunique"),
        ).to_string()
    )

    print("\nAudit complete. Ground-truth fields above are for diagnosis only.")


if __name__ == "__main__":
    main()
