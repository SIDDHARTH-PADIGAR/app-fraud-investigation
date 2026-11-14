
import numpy as np
import pandas as pd
from config import DATA_DIR

tx = pd.read_parquet(DATA_DIR / "transactions.parquet")

count_24h = np.zeros(len(tx), dtype=np.int64)
amount_24h = np.zeros(len(tx), dtype=float)

for _, group in tx.groupby("sender_id", sort=False):
    group = group.sort_values("timestamp_s", kind="stable")
    positions = group.index.to_numpy()
    times = group.timestamp_s.to_numpy(dtype=np.int64)
    amounts = group.amount_inr.to_numpy(dtype=float)

    prefix = np.concatenate(([0.0], np.cumsum(amounts)))

    left = np.searchsorted(times, times - 86400, side="left")
    right = np.searchsorted(times, times, side="left")

    count_24h[positions] = right - left
    amount_24h[positions] = prefix[right] - prefix[left]

result = tx[["transaction_id"]].copy()
result["sender_prior_outgoing_count_24h"] = count_24h
result["sender_prior_outgoing_amount_24h"] = amount_24h

result.to_parquet(DATA_DIR / "cashout_features.parquet", index=False)

truth = pd.read_parquet(DATA_DIR / "transaction_ground_truth.parquet")
df = result.merge(truth, on="transaction_id", validate="one_to_one")
df = df.merge(tx[["transaction_id", "amount_inr"]], on="transaction_id")

metrics = [
    "amount_inr",
    "sender_prior_outgoing_count_24h",
    "sender_prior_outgoing_amount_24h",
]

for stage in ["cashout", "legitimate", "mule_layering"]:
    subset = df[df.stage == stage]
    print(f"\n{stage.upper()} ({len(subset)} transactions)")
    print(subset[metrics].describe(
        percentiles=[.5, .75, .9, .95, .99]
    ).round(2).to_string())

print("\nSaved data/cashout_features.parquet")
