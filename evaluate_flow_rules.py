
"""Consolidated evaluation of the layering detection rule."""
import pandas as pd

from config import DATA_DIR

FLOW_COLUMNS = [
    "transaction_id",
    "sender_incoming_amount_72h",
    "sender_incoming_count_72h",
    "outgoing_to_recent_inflow_ratio",
]

TRUTH_COLUMNS = [
    "transaction_id", "campaign_id", "stage"
]

AMOUNT_THRESHOLD = None
INFLOW_THRESHOLD = None
RATIO_THRESHOLD = 0.80


def load_split(name, flow, truth):
    split = pd.read_parquet(DATA_DIR / "splits" / f"{name}.parquet")

    return (
        split.merge(flow[FLOW_COLUMNS], on="transaction_id",
                    validate="one_to_one")
        .merge(truth[TRUTH_COLUMNS], on="transaction_id",
               validate="one_to_one")
    )


def make_conditions(df):
    return {
        "amount": df.amount_inr.ge(AMOUNT_THRESHOLD),
        "inflow": df.sender_incoming_amount_72h.ge(INFLOW_THRESHOLD),
        "ratio": df.outgoing_to_recent_inflow_ratio.ge(RATIO_THRESHOLD),
    }


def evaluate(df, mask, name):
    layering = df.stage.eq("mule_layering")
    legitimate = df.stage.eq("legitimate")
    other_fraud = df.stage.isin(["victim_to_mule", "cashout"])

    tp = int((mask & layering).sum())
    missed = int((~mask & layering).sum())
    fp_legit = int((mask & legitimate).sum())
    other_flagged = int((mask & other_fraud).sum())
    total_alerts = int(mask.sum())

    print(
        f"{name:<22} "
        f"TP={tp:>3} Missed={missed:>3} "
        f"Legit_FP={fp_legit:>3} "
        f"Other_fraud={other_flagged:>3} "
        f"Alerts={total_alerts:>3} "
        f"Layering_precision={tp / max(total_alerts, 1):.2%} "
        f"Recall={tp / max(tp + missed, 1):.2%}"
    )


def main():
    global AMOUNT_THRESHOLD, INFLOW_THRESHOLD

    flow = pd.read_parquet(DATA_DIR / "flow_features.parquet")
    truth = pd.read_parquet(DATA_DIR / "transaction_ground_truth.parquet")

    train = load_split("train", flow, truth)
    val = load_split("validation", flow, truth)
    test = load_split("test", flow, truth)

    # Re-derive thresholds from training negatives only.
    train_controls = train[train.label.eq(0)]
    AMOUNT_THRESHOLD = train_controls.amount_inr.quantile(0.99)
    INFLOW_THRESHOLD = train_controls.sender_incoming_amount_72h.quantile(0.99)

    print("FROZEN TRAINING THRESHOLDS")
    print(f"Amount P99: Rs {AMOUNT_THRESHOLD:,.2f}")
    print(f"Prior inflow P99: Rs {INFLOW_THRESHOLD:,.2f}")
    print(f"Forwarding ratio: {RATIO_THRESHOLD:.2f}")

    print("\nDATA INTEGRITY")
    print("Train/validation/test rows:",
          len(train), len(val), len(test))
    print("Duplicate flow IDs:", flow.transaction_id.duplicated().sum())
    print("Missing flow ratios:", flow.outgoing_to_recent_inflow_ratio.isna().sum())
    print("Missing campaign/stage:",
          truth[["campaign_id", "stage"]].isna().sum().to_dict())

    # Every non-empty combination of the three conditions.
    combinations = [
        ("amount only", ["amount"]),
        ("inflow only", ["inflow"]),
        ("ratio only", ["ratio"]),
        ("amount + inflow", ["amount", "inflow"]),
        ("amount + ratio", ["amount", "ratio"]),
        ("inflow + ratio", ["inflow", "ratio"]),
        ("all three", ["amount", "inflow", "ratio"]),
    ]

    for split_name, df in [
        ("TRAIN", train), ("VALIDATION", val), ("TEST", test)
    ]:
        print(f"\n{'=' * 90}\n{split_name} ABLATION RESULTS")
        conditions = make_conditions(df)

        for label, keys in combinations:
            mask = pd.Series(True, index=df.index)
            for key in keys:
                mask &= conditions[key]
            evaluate(df, mask, label)

        print("\nFULL RULE: DETECTIONS BY CAMPAIGN AND STAGE")
        full_mask = (
            conditions["amount"]
            & conditions["inflow"]
            & conditions["ratio"]
        )

        detected = df[full_mask]
        if detected.empty:
            print("No detections")
        else:
            print(
                detected.groupby(["campaign_id", "stage"], dropna=False)
                .size().to_string()
            )

        print("\nFULL RULE: MISSED LAYERING BY CAMPAIGN")
        missed = df[df.stage.eq("mule_layering") & ~full_mask]
        if missed.empty:
            print("None")
        else:
            print(
                missed.groupby("campaign_id").size().to_string()
            )

    # Sensitivity analysis: change only the forwarding-ratio threshold.
    print("\n" + "=" * 90)
    print("TEST: FORWARDING-RATIO SENSITIVITY")
    print("Amount and inflow thresholds remain frozen.")

    base = (
        test.amount_inr.ge(AMOUNT_THRESHOLD)
        & test.sender_incoming_amount_72h.ge(INFLOW_THRESHOLD)
    )

    for ratio in [0.70, 0.75, 0.7745, 0.80, 0.85, 0.90]:
        mask = base & test.outgoing_to_recent_inflow_ratio.ge(ratio)
        evaluate(test, mask, f"ratio >= {ratio:.4f}")

    # Inspect legitimate transactions flagged by the frozen full rule.
    full_test = (
        base
        & test.outgoing_to_recent_inflow_ratio.ge(RATIO_THRESHOLD)
    )

    print("\n" + "=" * 90)
    print("TEST: FLAGGED LEGITIMATE TRANSACTIONS")
    flagged_legitimate = test[full_test & test.stage.eq("legitimate")]

    print("Count:", len(flagged_legitimate))
    if not flagged_legitimate.empty:
        print(
            flagged_legitimate[
                ["transaction_id", "sender_id", "receiver_id",
                 "amount_inr", "sender_incoming_amount_72h",
                 "outgoing_to_recent_inflow_ratio"]
            ].to_string(index=False)
        )

    print("\nTEST: ALL FRAUD STAGES")
    print(test.stage.value_counts().to_string())


if __name__ == "__main__":
    main()
