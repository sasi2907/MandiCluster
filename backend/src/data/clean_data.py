from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "mandi_prices.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "cleaned_mandi_prices.csv"


def clean_dataset():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}"
        )

    df = pd.read_csv(RAW_FILE)

    # Normalize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"_x0020_", "_", regex=True)
        .str.replace(" ", "_")
    )

    required_columns = [
        "state", "district", "market", "commodity",
        "arrival_date", "min_price", "max_price",
        "modal_price"
    ]

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove duplicate records
    df = df.drop_duplicates().copy()

    # Clean categorical fields
    categorical_columns = [
        "state", "district", "market", "commodity"
    ]

    for column in categorical_columns:
        df[column] = df[column].astype("string").str.strip()

    # Convert numeric fields
    price_columns = ["min_price", "max_price", "modal_price"]

    for column in price_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Parse dates
    df["arrival_date"] = pd.to_datetime(
        df["arrival_date"],
        dayfirst=True,
        errors="coerce"
    )

    # Remove rows missing essential information
    df = df.dropna(
        subset=required_columns
    ).copy()

    # Prices must be positive
    df = df[
        (df["min_price"] > 0)
        & (df["max_price"] > 0)
        & (df["modal_price"] > 0)
    ].copy()

    # Check price consistency
    df = df[
        (df["min_price"] <= df["max_price"])
        & (df["modal_price"] >= df["min_price"])
        & (df["modal_price"] <= df["max_price"])
    ].copy()

    # Remove empty identifiers
    for column in categorical_columns:
        df = df[df[column].str.len() > 0].copy()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("Data cleaning completed.")
    print(f"Original rows: {len(pd.read_csv(RAW_FILE))}")
    print(f"Cleaned rows: {len(df)}")
    print(f"Removed rows: {len(pd.read_csv(RAW_FILE)) - len(df)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_dataset()
