
"""Build point-in-time transaction features using DuckDB."""

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from config import DATA_DIR
from common import setup_directories


ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "features.sql"


def build_features():
    setup_directories()

    transaction_file = DATA_DIR / "transactions.parquet"
    account_file = DATA_DIR / "accounts.parquet"
    output_file = DATA_DIR / "transaction_features.parquet"

    for path in (transaction_file, account_file, SQL_FILE):
        if not path.exists():
            raise FileNotFoundError(f"Required input not found: {path}")

    con = duckdb.connect(database=":memory:")

    try:
        con.execute(
            f"""
            CREATE VIEW transactions AS
            SELECT * FROM read_parquet('{transaction_file.as_posix()}')
            """
        )
        

        con.execute(
            f"""
            CREATE VIEW accounts AS
            SELECT * FROM read_parquet('{account_file.as_posix()}')
            """
        )

        sql = SQL_FILE.read_text(encoding="utf-8")
        con.execute(sql)

        result = con.execute(
            "SELECT * FROM transaction_features"
        ).df()

        # Every source transaction must produce exactly one feature row.
        source_count = con.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        if len(result) != source_count:
            raise AssertionError(
                f"Feature row count mismatch: "
                f"{len(result)} features for {source_count} transactions"
            )

        if result["transaction_id"].duplicated().any():
            raise AssertionError("Duplicate transaction IDs in feature table")

        # Feature table must not contain hidden simulator labels.
        forbidden_columns = {
            "is_fraud_stage",
            "campaign_id",
            "stage",
            "true_role",
        }

        leaked_columns = forbidden_columns.intersection(result.columns)

        if leaked_columns:
            raise AssertionError(
                f"Ground-truth columns leaked into features: {leaked_columns}"
            )

        # Numerical feature values must be finite where present.
        numeric = result.select_dtypes(include=[np.number])

        if np.isinf(numeric.to_numpy()).any():
            raise AssertionError("Infinite numerical feature detected")

        # Missing ratios are allowed when no historical activity exists.
        result.to_parquet(output_file, index=False)

        print("Point-in-time feature generation successful.")
        print(f"Source transactions: {source_count:,}")
        print(f"Feature rows: {len(result):,}")
        print(f"Feature columns: {len(result.columns)}")
        print(f"Output: {output_file}")

        print("\nFeature preview:")
        print(result.head(5).to_string(index=False))

        return result

    finally:
        con.close()


if __name__ == "__main__":
    build_features()
