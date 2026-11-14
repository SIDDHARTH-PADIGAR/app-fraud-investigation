
import pandas as pd
from config import DATA_DIR, RESULTS_DIR


def metrics(name, predicted, actual):
    tp = int((predicted & actual).sum())
    fp = int((predicted & ~actual).sum())
    fn = int((~predicted & actual).sum())
    tn = int((~predicted & ~actual).sum())

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    return {
        "detector": name,
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "F1": round(f1, 4),
    }


def main():
    test = pd.read_parquet(DATA_DIR / "splits" / "test.parquet")
    alerts = pd.read_parquet(RESULTS_DIR / "fraud_alerts.parquet")
    truth = pd.read_parquet(DATA_DIR / "transaction_ground_truth.parquet")

    # Keep only transactions belonging to the untouched test period.
    df = test[["transaction_id", "label"]].merge(
        alerts[[
            "transaction_id",
            "victim_mule_alert",
            "layering_alert",
        ]],
        on="transaction_id",
        how="left",
        validate="one_to_one"
    )

    df = df.merge(
        truth[["transaction_id", "stage", "campaign_id"]],
        on="transaction_id",
        validate="one_to_one"
    )

    for col in ["victim_mule_alert", "layering_alert"]:
        df[col] = df[col].fillna(False).astype(bool)

    actual = df["label"].eq(1)
    combined = df["victim_mule_alert"] | df["layering_alert"]

    results = [
        metrics("Victim-to-mule", df["victim_mule_alert"], actual),
        metrics("Layering", df["layering_alert"], actual),
        metrics("Combined engine", combined, actual),
    ]

    report = pd.DataFrame(results)

    print("UNTOUCHED TEST SET")
    print(f"Transactions: {len(df):,}")
    print(f"Fraud transactions: {int(actual.sum()):,}")
    print(f"Legitimate transactions: {int((~actual).sum()):,}")

    print("\nDETECTOR PERFORMANCE")
    print(report.to_string(index=False))

    print("\nCOMBINED DETECTIONS BY STAGE")
    print(
        df[combined]
        .groupby("stage")
        .size()
        .to_string()
    )

    print("\nDETECTIONS BY CAMPAIGN")
    print(
        df[combined]
        .groupby("campaign_id")
        .size()
        .to_string()
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(
        RESULTS_DIR / "test_evaluation.csv",
        index=False
    )

    df.to_parquet(
        RESULTS_DIR / "test_predictions.parquet",
        index=False
    )

    print("\nSaved results/test_evaluation.csv")
    print("Saved results/test_predictions.parquet")


if __name__ == "__main__":
    main()
