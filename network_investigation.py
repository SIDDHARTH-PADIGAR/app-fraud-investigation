
import networkx as nx
import pandas as pd

from config import RESULTS_DIR


def main():
    alert_path = RESULTS_DIR / "fraud_alerts.parquet"
    alerts = pd.read_parquet(alert_path)

    if alerts.empty:
        print("No alerts available. Nothing to investigate.")
        return

    required = {
        "transaction_id",
        "timestamp_s",
        "sender_id",
        "receiver_id",
        "amount_inr",
        "risk_score",
        "alert_reasons",
        "victim_mule_alert",
        "layering_alert",
    }

    missing = required - set(alerts.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    # Build an account network from detected transactions.
    graph = nx.Graph()

    for row in alerts.itertuples(index=False):
        graph.add_edge(
            row.sender_id,
            row.receiver_id,
            transaction_id=row.transaction_id
        )

    # Identify connected account networks.
    components = list(nx.connected_components(graph))

    # Rank networks by total alert risk and network size.
    components.sort(
        key=lambda nodes: (
            -sum(
                alerts.loc[
                    alerts.sender_id.isin(nodes)
                    & alerts.receiver_id.isin(nodes),
                    "risk_score"
                ]
            ),
            -len(nodes),
            min(nodes)
        )
    )

    case_rows = []
    transaction_frames = []
    account_frames = []

    for number, nodes in enumerate(components, start=1):
        case_id = f"CASE-{number:04d}"

        case_tx = alerts[
            alerts.sender_id.isin(nodes)
            & alerts.receiver_id.isin(nodes)
        ].copy()

        case_tx["case_id"] = case_id

        incoming = case_tx.groupby("receiver_id").agg(
            incoming_transactions=("transaction_id", "count"),
            incoming_amount=("amount_inr", "sum")
        )

        outgoing = case_tx.groupby("sender_id").agg(
            outgoing_transactions=("transaction_id", "count"),
            outgoing_amount=("amount_inr", "sum")
        )

        accounts = pd.DataFrame(
            {"account_id": sorted(nodes)}
        )

        accounts["case_id"] = case_id

        accounts["incoming_transactions"] = (
            accounts.account_id.map(
                incoming.incoming_transactions
            ).fillna(0).astype(int)
        )

        accounts["incoming_amount"] = (
            accounts.account_id.map(
                incoming.incoming_amount
            ).fillna(0)
        )

        accounts["outgoing_transactions"] = (
            accounts.account_id.map(
                outgoing.outgoing_transactions
            ).fillna(0).astype(int)
        )

        accounts["outgoing_amount"] = (
            accounts.account_id.map(
                outgoing.outgoing_amount
            ).fillna(0)
        )

        accounts["net_alerted_flow"] = (
            accounts.incoming_amount - accounts.outgoing_amount
        )

        # Summarise the investigation case.
        case_rows.append({
            "case_id": case_id,
            "account_count": len(nodes),
            "alert_transaction_count": len(case_tx),
            "total_alerted_amount": case_tx.amount_inr.sum(),
            "max_risk_score": case_tx.risk_score.max(),
            "total_risk_score": case_tx.risk_score.sum(),
            "victim_mule_alerts": int(
                case_tx.victim_mule_alert.sum()
            ),
            "layering_alerts": int(
                case_tx.layering_alert.sum()
            ),
            "first_seen": case_tx.timestamp_s.min(),
            "last_seen": case_tx.timestamp_s.max(),
            "account_ids": ",".join(map(str, sorted(nodes)))
        })

        transaction_frames.append(case_tx)
        account_frames.append(accounts)

    # Assemble outputs.
    cases = pd.DataFrame(case_rows).sort_values(
        ["total_risk_score", "account_count"],
        ascending=False
    )

    case_transactions = pd.concat(
        transaction_frames,
        ignore_index=True
    )

    case_accounts = pd.concat(
        account_frames,
        ignore_index=True
    )

    # Save investigation outputs.
    cases.to_csv(
        RESULTS_DIR / "investigation_cases.csv",
        index=False
    )

    case_transactions.to_parquet(
        RESULTS_DIR / "case_transactions.parquet",
        index=False
    )

    case_accounts.to_csv(
        RESULTS_DIR / "case_accounts.csv",
        index=False
    )

    # Report.
    print("\nNETWORK INVESTIGATION RESULTS")
    print(f"Alert transactions: {len(alerts):,}")
    print(f"Connected account networks: {len(cases):,}")
    print(f"Accounts involved: {graph.number_of_nodes():,}")
    print(f"Network connections: {graph.number_of_edges():,}")

    print("\nTOP 10 INVESTIGATION CASES")
    print(
        cases[
            [
                "case_id",
                "account_count",
                "alert_transaction_count",
                "total_alerted_amount",
                "total_risk_score"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nSAVED OUTPUTS")
    print("results/investigation_cases.csv")
    print("results/case_transactions.parquet")
    print("results/case_accounts.csv")


if __name__ == "__main__":
    main()
