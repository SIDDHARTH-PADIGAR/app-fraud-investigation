
"""Causal transaction-flow features for mule-layering investigation."""
import numpy as np
import pandas as pd

from config import DATA_DIR

WINDOW_SECONDS = 3 * 86_400


def build_flow_features():
    tx = pd.read_parquet(DATA_DIR / "transactions.parquet")

    required = {
        "transaction_id", "timestamp_s", "sender_id",
        "receiver_id", "amount_inr",
    }
    missing = required - set(tx.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    # Index inbound transactions by receiving account.
    inbound_by_account = {}
    for account, group in tx.groupby("receiver_id", sort=False):
        group = group.sort_values("timestamp_s", kind="stable")
        times = group["timestamp_s"].to_numpy(dtype=np.int64)
        amounts = group["amount_inr"].to_numpy(dtype=np.float64)

        inbound_by_account[account] = (
            times,
            np.concatenate(([0.0], np.cumsum(amounts))),
        )

    recent_amount = np.zeros(len(tx), dtype=np.float64)
    recent_count = np.zeros(len(tx), dtype=np.int64)

    # For each outgoing transaction, inspect only strictly earlier inflows.
    for account, group in tx.groupby("sender_id", sort=False):
        inbound = inbound_by_account.get(account)
        if inbound is None:
            continue

        times, prefix = inbound
        positions = group.index.to_numpy()
        current_times = group["timestamp_s"].to_numpy(dtype=np.int64)

        left = np.searchsorted(
            times, current_times - WINDOW_SECONDS, side="left"
        )
        right = np.searchsorted(times, current_times, side="left")

        recent_amount[positions] = prefix[right] - prefix[left]
        recent_count[positions] = right - left

    result = tx[["transaction_id", "timestamp_s", "sender_id",
                 "receiver_id", "amount_inr"]].copy()

    result["sender_incoming_amount_72h"] = recent_amount
    result["sender_incoming_count_72h"] = recent_count

    result["outgoing_to_recent_inflow_ratio"] = np.divide(
        result["amount_inr"].to_numpy(),
        recent_amount,
        out=np.full(len(result), np.nan),
        where=recent_amount > 0,
    )

    output = DATA_DIR / "flow_features.parquet"
    result.to_parquet(output, index=False)

    print(f"Saved: {output}")
    print(f"Transactions: {len(result):,}")
    print(f"Transactions with prior inflows: {(recent_amount > 0).sum():,}")

    return result


def inspect_features(flow):
    truth = pd.read_parquet(DATA_DIR / "transaction_ground_truth.parquet")

    df = flow.merge(
        truth[["transaction_id", "is_fraud_stage", "campaign_id", "stage"]],
        on="transaction_id",
        validate="one_to_one",
    )

    metrics = [
        "amount_inr",
        "sender_incoming_amount_72h",
        "sender_incoming_count_72h",
        "outgoing_to_recent_inflow_ratio",
    ]

    print("\nSTAGE DISTRIBUTIONS")
    for stage in ["mule_layering", "cashout"]:
        subset = df[df["stage"] == stage]
        print(f"\n{stage}: {len(subset)} transactions")
        print(subset[metrics].median().round(2).to_string())

    legitimate = df[df["is_fraud_stage"].eq(False)]

    print("\nLEGITIMATE TRANSACTION QUANTILES")
    print(
        legitimate[metrics]
        .quantile([.50, .90, .95, .99])
        .round(2)
        .to_string()
    )

    print("\nLAYERING BY CAMPAIGN")
    print(
        df[df["stage"] == "mule_layering"]
        .groupby("campaign_id")[metrics]
        .median()
        .round(2)
        .to_string()
    )


if __name__ == "__main__":
    flow = build_flow_features()
    inspect_features(flow)
