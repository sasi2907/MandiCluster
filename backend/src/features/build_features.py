from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_mandi_prices.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "market_features.csv"


def build_features():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    # Ensure price columns are numeric
    price_columns = ["min_price", "max_price", "modal_price"]

    for column in price_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Calculate the reported price range for each record
    df["price_range"] = df["max_price"] - df["min_price"]

    # Aggregate records by market and commodity.
    # State and district identify the market's location.
    group_columns = [
        "state",
        "district",
        "market",
        "commodity"
    ]

    features = (
        df.groupby(group_columns, as_index=False)
        .agg(
            avg_modal_price=("modal_price", "mean"),
            min_modal_price=("modal_price", "min"),
            max_modal_price=("modal_price", "max"),
            avg_price_range=("price_range", "mean"),
            observation_count=("modal_price", "count")
        )
    )

    # Remove invalid numerical feature rows
    numeric_columns = [
        "avg_modal_price",
        "min_modal_price",
        "max_modal_price",
        "avg_price_range",
        "observation_count"
    ]

    features = features.dropna(subset=numeric_columns)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    features.to_csv(OUTPUT_FILE, index=False)

    print("Feature engineering completed.")
    print(f"Original cleaned records: {len(df)}")
    print(f"Market-commodity combinations: {len(features)}")
    print("\nFeature columns:")
    print(features.columns.tolist())
    print("\nFirst 5 feature records:")
    print(features.head().to_string(index=False))
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_features()
