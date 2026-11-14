import pandas as pd

from config import DAY, LABEL_DELAY_DAYS, TRAIN, VAL, TEST, N_DAYS
from pathlib import Path

DATA = Path("data")
SPLITS = DATA / "splits"


def load_split(name):
    return pd.read_parquet(SPLITS / f"{name}.parquet")


def test_split_ids_are_unique_and_disjoint():
    train = load_split("train")
    val = load_split("validation")
    test = load_split("test")

    for df in (train, val, test):
        assert df["transaction_id"].is_unique

    train_ids = set(train.transaction_id)
    val_ids = set(val.transaction_id)
    test_ids = set(test.transaction_id)

    assert not train_ids & val_ids
    assert not train_ids & test_ids
    assert not val_ids & test_ids


def test_event_time_boundaries():
    boundaries = {
        "train": TRAIN,
        "validation": VAL,
        "test": TEST,
    }

    for name, (start, end) in boundaries.items():
        df = load_split(name)

        assert (df.timestamp_s >= start * DAY).all()
        assert (df.timestamp_s < end * DAY).all()


def test_all_labels_are_mature():
    cutoffs = {
        "train": (TRAIN[1] + LABEL_DELAY_DAYS) * DAY,
        "validation": (VAL[1] + LABEL_DELAY_DAYS) * DAY,
        "test": N_DAYS * DAY,
    }

    for name, cutoff in cutoffs.items():
        df = load_split(name)

        assert (
            df.label_available_timestamp_s <= cutoff
        ).all()


def test_label_maturity_timestamp_is_correct():
    for name in ("train", "validation", "test"):
        df = load_split(name)

        expected = (
            df.timestamp_s + LABEL_DELAY_DAYS * DAY
        )

        assert (
            df.label_available_timestamp_s == expected
        ).all()


def test_labels_match_hidden_ground_truth():
    truth = pd.read_parquet(
        DATA / "transaction_ground_truth.parquet"
    )

    truth = truth.rename(
        columns={"is_fraud_stage": "expected_label"}
    )

    for name in ("train", "validation", "test"):
        df = load_split(name)

        checked = df[
            ["transaction_id", "label"]
        ].merge(
            truth[["transaction_id", "expected_label"]],
            on="transaction_id",
            validate="one_to_one",
        )

        assert len(checked) == len(df)
        assert (
            checked.label == checked.expected_label
        ).all()


def test_no_ground_truth_metadata_in_features():
    forbidden = {
        "campaign_id",
        "stage",
        "true_role",
        "is_fraud_stage",
    }

    for name in ("train", "validation", "test"):
        df = load_split(name)

        assert not forbidden.intersection(df.columns)


def test_split_column_matches_file():
    for name in ("train", "validation", "test"):
        df = load_split(name)
        assert set(df.split) == {name}
