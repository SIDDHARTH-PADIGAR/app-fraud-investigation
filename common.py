"""Shared utilities for the fraud investigation pipeline."""

import json
import random
from pathlib import Path

import numpy as np

from config import DATA_DIR, RESULTS_DIR, SQL_DIR, SEED


def setup_directories():
    """Create project data and results directories."""
    for directory in (DATA_DIR, RESULTS_DIR, SQL_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def set_seed(seed=SEED):
    """Make experiments reproducible."""
    random.seed(seed)
    np.random.seed(seed)


def save_json(data, path):
    """Save results as readable JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, default=str)


def save_dataframe(df, path):
    """Save a dataframe as Parquet."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)