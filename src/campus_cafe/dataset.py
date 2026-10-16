"""Load the bundled synthetic Kaggle sample for transparent UI exploration."""

from pathlib import Path

import pandas as pd


DATASET_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "student_spending.csv"
REQUIRED_COLUMNS = {
    "age",
    "year_in_school",
    "major",
    "food",
    "preferred_payment_method",
}


def load_student_spending(path: Path = DATASET_PATH) -> pd.DataFrame:
    """Load the CSV and fail clearly if its expected fields are missing."""
    dataset = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(dataset.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}")
    return dataset.rename(columns={"Unnamed: 0": "record_id"})