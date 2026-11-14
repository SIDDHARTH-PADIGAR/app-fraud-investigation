"""Global constants. Times are integer seconds since simulation start (t=0)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
SQL_DIR = ROOT / "sql"

DAY = 86_400
N_DAYS = 75

# RBI discussion paper (Apr 9 2026), Option 1 scope: APP transactions of Rs 10,000 and above.
SCOPE_THRESHOLD = 10_000
# Broader scope used to test "structuring below the threshold" evasion.
BROAD_THRESHOLD = 2_000

# Fraud labels (victim complaint -> bank investigation) are not known instantly.
# A mule account only becomes "known" this many days after it first received fraud proceeds.
LABEL_DELAY_DAYS = 3

# Temporal windows in days. Chosen so that:
#  * train rows end LABEL_DELAY_DAYS before the model "training date" (day 40), so every
#    positive label used in training was already knowable on that date;
#  * validation labels (used only for threshold selection) are mature by day 55;
#  * test starts at day 55 and is never touched during model/threshold selection.
WARMUP_END_DAY = 14          # first 14 days only build history (left-censoring of pair history)
TRAIN = (14, 37)
VAL = (43, 52)
TEST = (55, 75)

INDIVIDUAL_SEGMENTS = ["salaried", "student", "senior", "sole_prop"]   # RBI Option 1/3 scope (individuals + proprietors)
SEED = 42