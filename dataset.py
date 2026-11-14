"""Build leakage-aware, time-based transaction datasets."""

import pandas as pd

from config import (
    DATA_DIR,
    DAY,
    LABEL_DELAY_DAYS,
    TRAIN,
    VAL,
    TEST,
    N_DAYS,
    WARMUP_END_DAY,
)
from common import setup_directories


def build_datasets():
    setup_directories()

    feature_file = DATA_DIR / "transaction_features.parquet"
    truth_file = DATA_DIR / "transaction_ground_truth.parquet"
    output_dir = DATA_DIR / "splits"

    if not feature_file.exists() or not truth_file.exists():
        raise FileNotFoundError("Generate features and ground truth first.")

    output_dir.mkdir(parents=True, exist_ok=True)

    features = pd.read_parquet(feature_file)
    truth = pd.read_parquet(truth_file)

    # Validate source keys before joining hidden labels.
    if features["transaction_id"].duplicated().any():
        raise AssertionError("Duplicate feature transaction IDs.")

    if truth["transaction_id"].duplicated().any():
        raise AssertionError("Duplicate ground-truth transaction IDs.")

    if set(features["transaction_id"]) != set(truth["transaction_id"]):
        raise AssertionError("Feature and ground-truth transaction IDs differ.")

    # Labels are joined only in this dataset-building layer.
    df = features.merge(
        truth[["transaction_id", "is_fraud_stage"]],
        on="transaction_id",
        how="left",
        validate="one_to_one",
    )

    if df["is_fraud_stage"].isna().any():
        raise AssertionError("Missing transaction labels.")

    df["label"] = df["is_fraud_stage"].astype("int8")
    df = df.drop(columns=["is_fraud_stage"])

    if not df["label"].isin([0, 1]).all():
        raise AssertionError("Unexpected transaction label values.")

    # Every label, positive or negative, matures after the configured delay.
    df["label_available_timestamp_s"] = (
        df["timestamp_s"] + LABEL_DELAY_DAYS * DAY
    )

    # Assign event-time periods. End boundaries are exclusive.
    df["split"] = "excluded"
    df["exclusion_reason"] = "outside_defined_periods"

    train_start, train_end = TRAIN
    val_start, val_end = VAL
    test_start, test_end = TEST

    train_mask = (
        (df["timestamp_s"] >= train_start * DAY)
        & (df["timestamp_s"] < train_end * DAY)
    )

    val_mask = (
        (df["timestamp_s"] >= val_start * DAY)
        & (df["timestamp_s"] < val_end * DAY)
    )

    test_period_mask = (
        (df["timestamp_s"] >= test_start * DAY)
        & (df["timestamp_s"] < test_end * DAY)
    )

    # Labels must be observable by the end of each evaluation period.
    train_mature = (
        df["label_available_timestamp_s"]
        <= (train_end + LABEL_DELAY_DAYS) * DAY
    )

    val_mature = (
        df["label_available_timestamp_s"]
        <= (val_end + LABEL_DELAY_DAYS) * DAY
    )

    evaluation_horizon = N_DAYS * DAY
    test_mature = (
        df["label_available_timestamp_s"] <= evaluation_horizon
    )

    if not train_mature[train_mask].all():
        raise AssertionError("Immature labels found in training period.")

    if not val_mature[val_mask].all():
        raise AssertionError("Immature labels found in validation period.")

    df.loc[train_mask, "split"] = "train"
    df.loc[val_mask, "split"] = "validation"

    df.loc[test_period_mask & test_mature, "split"] = "test"

    # Record why rows were not selected.
    df.loc[
        (df["timestamp_s"] < WARMUP_END_DAY * DAY),
        "exclusion_reason",
    ] = "warmup"

    df.loc[
        test_period_mask & ~test_mature,
        "exclusion_reason",
    ] = "test_labels_not_mature"

    # Only retain selected rows in the three modelling datasets.
    splits = {
        "train": df[df["split"] == "train"].copy(),
        "validation": df[df["split"] == "validation"].copy(),
        "test": df[df["split"] == "test"].copy(),
    }

    if any(part.empty for part in splits.values()):
        raise AssertionError("One or more temporal datasets are empty.")

    # Verify split boundaries and label maturity.
    cutoffs = {
        "train": (train_end + LABEL_DELAY_DAYS) * DAY,
        "validation": (val_end + LABEL_DELAY_DAYS) * DAY,
        "test": evaluation_horizon,
    }

    for name, part in splits.items():
        if (part["label_available_timestamp_s"] > cutoffs[name]).any():
            raise AssertionError(f"Immature labels found in {name}.")

        if part["transaction_id"].duplicated().any():
            raise AssertionError(f"Duplicate IDs in {name}.")

        part.to_parquet(output_dir / f"{name}.parquet", index=False)

    # No transaction may appear in more than one split.
    ids = [
        set(part["transaction_id"])
        for part in splits.values()
    ]

    if ids[0] & ids[1] or ids[0] & ids[2] or ids[1] & ids[2]:
        raise AssertionError("Transaction overlap between datasets.")

    print("Temporal dataset construction successful.")

    for name, part in splits.items():
        print(
            f"{name.title():12} | "
            f"rows: {len(part):,} | "
            f"fraud stages: {int(part['label'].sum()):,} | "
            f"fraud rate: {part['label'].mean():.4%} | "
            f"event days: {part['day'].min()}-{part['day'].max()}"
        )

    print(
        "\nTest rows excluded for immature labels:",
        int((test_period_mask & ~test_mature).sum()),
    )

    print(f"Output directory: {output_dir}")

    return splits


if __name__ == "__main__":
    build_datasets()
