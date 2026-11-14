
# 3. Create APP fraud campaigns and mule networks.

import numpy as np
import pandas as pd

from config import (
    DATA_DIR,
    N_DAYS,
    DAY,
    SEED,
    SCOPE_THRESHOLD,
    BROAD_THRESHOLD,
)
from common import setup_directories, set_seed


def generate_world():
    rng = np.random.default_rng(SEED)
    setup_directories()

    # ---------------------------------------------------------
    # 1. Create accounts. Roles are kept out of observable data.
    # ---------------------------------------------------------
    accounts = []
    account_truth = []
    next_id = 1

    def add_account(segment, role="customer", created_day=0):
        nonlocal next_id
        account_id = next_id
        next_id += 1

        accounts.append({
            "account_id": account_id,
            "segment": segment,
            "account_created_day": created_day,
        })
        account_truth.append({
            "account_id": account_id,
            "true_role": role,
        })
        return account_id

    customers = []
    for segment, count in [
        ("salaried", 1000),
        ("student", 250),
        ("senior", 150),
        ("sole_prop", 100),
    ]:
        customers.extend(
            add_account(segment) for _ in range(count)
        )

    merchants = [
        add_account("merchant", "merchant")
        for _ in range(100)
    ]

    # ---------------------------------------------------------
    # 2. Generate ordinary background transactions.
    # ---------------------------------------------------------
    transactions = []
    ground_truth = []
    tx_id = 1

    def add_transaction(
        day, sender, receiver, amount, payment_type,
        campaign_id=None, stage="legitimate",
        fraud=False,
    ):
        nonlocal tx_id

        timestamp = int(day * DAY + rng.integers(0, DAY))

        transactions.append({
            "transaction_id": tx_id,
            "timestamp_s": timestamp,
            "day": day,
            "sender_id": sender,
            "receiver_id": receiver,
            "amount_inr": round(float(amount), 2),
            "payment_type": payment_type,
            "channel": rng.choice(["upi", "mobile_app", "internet"]),
        })

        ground_truth.append({
            "transaction_id": tx_id,
            "is_fraud_stage": int(fraud),
            "campaign_id": campaign_id,
            "stage": stage,
        })

        tx_id += 1

    for day in range(N_DAYS):
        # Ordinary peer-to-peer payments.
        for _ in range(700):
            sender, receiver = rng.choice(customers, 2, replace=False)
            amount = rng.lognormal(mean=6.0, sigma=1.0)

            add_transaction(
                day, sender, receiver, amount, "P2P"
            )

        # Merchant payments, including high-volume legitimate payees.
        for _ in range(450):
            sender = int(rng.choice(customers))
            receiver = int(rng.choice(merchants))
            amount = rng.lognormal(mean=6.5, sigma=0.9)

            add_transaction(
                day, sender, receiver, amount, "MERCHANT"
            )

        # Salary, rent and other recurring transfers.
        if day % 30 == 0:
            for _ in range(300):
                sender = int(rng.choice(merchants))
                receiver = int(rng.choice(customers))
                amount = rng.uniform(12000, 65000)

                add_transaction(
                    day, sender, receiver, amount, "PAYROLL"
                )

        if day % 7 == 0:
            for _ in range(120):
                sender, receiver = rng.choice(customers, 2, replace=False)
                amount = rng.uniform(5000, 25000)

                add_transaction(
                    day, sender, receiver, amount, "RECURRING"
                )

        # Group collections and event payments.
        for _ in range(80):
            sender = int(rng.choice(customers))
            receiver = int(rng.choice(customers))
            amount = rng.uniform(100, 5000)

            add_transaction(
                day, sender, receiver, amount, "GROUP_PAYMENT"
            )


    # ---------------------------------------------------------
    # 3. Create APP fraud campaigns and mule networks.
    # ---------------------------------------------------------
    campaign_summaries = []
    campaign_days = [20, 30, 40, 50, 58, 64, 68, 70]

    for campaign_number, start_day in enumerate(campaign_days, 1):
        campaign_id = f"C{campaign_number:03d}"

        mule_count = int(rng.integers(4, 7))
        mules = [
            add_account(
                "salaried",
                role="mule",
                created_day=max(0, start_day - 10),
            )
            for _ in range(mule_count)
        ]

        victims = rng.choice(customers, size=5, replace=False)

        # Seasoning transactions are legitimate and are not
        # included in the campaign's fraud proceeds.
        for mule in mules:
            for _ in range(3):
                sender = int(rng.choice(customers))
                amount = rng.uniform(200, 2500)

                add_transaction(
                    max(0, start_day - 5),
                    sender,
                    mule,
                    amount,
                    "P2P",
                    campaign_id=campaign_id,
                    stage="seasoning",
                    fraud=False,
                )

        campaign_total = 0.0
        first_mule = mules[0]
        split_victim_count = 0

        # Victims authorise payments into the first mule account.
        for victim in victims:
            split_attack = bool(rng.random() < 0.35)
            if split_attack:
                split_victim_count += 1
            total_amount = float(rng.uniform(18000, 75000))

            if split_attack:
                pieces = int(rng.integers(3, 7))
                amounts = rng.dirichlet(np.ones(pieces)) * total_amount
            else:
                amounts = [total_amount]

            for amount in amounts:
                transfer_day = min(
                    N_DAYS - 1,
                    start_day + int(rng.integers(0, 2)),
                )

                add_transaction(
                    transfer_day,
                    int(victim),
                    first_mule,
                    float(amount),
                    "APP_TRANSFER",
                    campaign_id=campaign_id,
                    stage="victim_to_mule",
                    fraud=True,
                )
                campaign_total += float(amount)

        # Maintain an explicit balance for every mule.
        # Only money actually received can be forwarded.
        mule_balances = {mule: 0.0 for mule in mules}
        mule_balances[first_mule] = campaign_total

        total_forwarded = 0.0

        # Layer proceeds through the mule chain.
        for index in range(len(mules) - 1):
            sender = mules[index]
            receiver = mules[index + 1]

            available = mule_balances[sender]

            # The mule retains a portion instead of forwarding
            # the entire balance.
            forwarding_fraction = float(rng.uniform(0.75, 0.95))
            forwarded = available * forwarding_fraction

            if forwarded > available + 1e-8:
                raise AssertionError("Mule forwarded more money than received.")

            transfer_day = min(
                N_DAYS - 1,
                start_day + 1 + index,
            )

            add_transaction(
                transfer_day,
                sender,
                receiver,
                forwarded,
                "P2P",
                campaign_id=campaign_id,
                stage="mule_layering",
                fraud=True,
            )

            mule_balances[sender] -= forwarded
            mule_balances[receiver] += forwarded
            total_forwarded += forwarded

        # The final mule disperses only its actual available balance.
        final_mule = mules[-1]
        final_balance = mule_balances[final_mule]

        cashout_fraction = float(rng.uniform(0.80, 0.95))
        total_cashout = final_balance * cashout_fraction

        cashout_destinations = rng.choice(
            merchants,
            size=min(3, len(merchants)),
            replace=False,
        )

        cashout_weights = rng.dirichlet(
            np.ones(len(cashout_destinations))
        )

        for destination, weight in zip(
            cashout_destinations, cashout_weights
        ):
            amount = total_cashout * float(weight)

            transfer_day = min(
                N_DAYS - 1,
                start_day + mule_count,
            )

            add_transaction(
                transfer_day,
                final_mule,
                int(destination),
                amount,
                "MERCHANT",
                campaign_id=campaign_id,
                stage="cashout",
                fraud=True,
            )

        mule_balances[final_mule] -= total_cashout

        # Sum all retained balances across the mule network.
        total_retained = sum(mule_balances.values())

        # Campaign-level conservation check.
        conservation_error = (
            campaign_total - total_cashout - total_retained
        )

        if abs(conservation_error) > 0.01:
            raise AssertionError(
                f"{campaign_id}: money-flow imbalance "
                f"of INR {conservation_error:.4f}"
            )

        campaign_summaries.append({
            "campaign_id": campaign_id,
            "start_day": start_day,
            "victim_count": len(victims),
            "mule_count": len(mules),
            "split_attack": split_victim_count > 0,
            "split_victim_count": split_victim_count,
            "victim_funds_inr": round(campaign_total, 2),
            "cumulative_inter_mule_transfers_inr": round(total_forwarded, 2),
            "cashout_inr": round(total_cashout, 2),
            "retained_inr": round(total_retained, 2),
            "conservation_error_inr": round(conservation_error, 8),
        })

    # ---------------------------------------------------------
    # 4. Save observable data and hidden ground truth separately.
    # ---------------------------------------------------------
    tx_df = pd.DataFrame(transactions).sort_values(
        ["timestamp_s", "transaction_id"]
    )
    truth_df = pd.DataFrame(ground_truth)
    accounts_df = pd.DataFrame(accounts)
    account_truth_df = pd.DataFrame(account_truth)
    campaigns_df = pd.DataFrame(campaign_summaries)

    tx_df.to_parquet(DATA_DIR / "transactions.parquet", index=False)
    accounts_df.to_parquet(DATA_DIR / "accounts.parquet", index=False)

    truth_df.to_parquet(DATA_DIR / "transaction_ground_truth.parquet", index=False)
    account_truth_df.to_parquet(DATA_DIR / "account_ground_truth.parquet", index=False)
    campaigns_df.to_csv(DATA_DIR / "campaign_ground_truth.csv", index=False)

    print("Synthetic payment world generated.")
    print(f"Transactions: {len(tx_df):,}")
    print(f"Accounts: {len(accounts_df):,}")
    print(f"Fraud-labelled transaction stages: {truth_df['is_fraud_stage'].sum():,}")
    print(f"Campaigns: {len(campaigns_df)}")
    print(f"₹10,000 scope threshold: {SCOPE_THRESHOLD:,}")
    print(f"₹2,000 broad threshold: {BROAD_THRESHOLD:,}")
    print("Observable data and hidden ground truth saved separately.")

    return tx_df, accounts_df, truth_df


if __name__ == "__main__":
    generate_world()
