from pathlib import Path
import pandas as pd

# Locate the project root automatically
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = PROJECT_ROOT / "data" / "raw" / "mandi_prices.csv"


def inspect_dataset(file_path):
    if not file_path.exists():
        print(f"Dataset not found: {file_path}")
        print("Place mandi_prices.csv inside data/raw/")
        return

    df = pd.read_csv(file_path)

    # Normalize column names for easier processing
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"_x0020_", "_", regex=True)
        .str.replace(" ", "_")
    )

    print("\n========== DATASET OVERVIEW ==========")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column names: {df.columns.tolist()}")

    print("\n========== FIRST 5 RECORDS ==========")
    print(df.head().to_string(index=False))

    print("\n========== MISSING VALUES ==========")
    print(df.isnull().sum())

    print("\n========== DUPLICATE RECORDS ==========")
    print(df.duplicated().sum())

    if "arrival_date" in df.columns:
        df["arrival_date"] = pd.to_datetime(
            df["arrival_date"],
            dayfirst=True,
            errors="coerce"
        )

        print("\n========== DATE COVERAGE ==========")
        print("Earliest date:", df["arrival_date"].min())
        print("Latest date:", df["arrival_date"].max())
        print("Unique dates:", df["arrival_date"].nunique())

    for column in ["state", "district", "market", "commodity"]:
        if column in df.columns:
            print(
                f"Unique {column} values:",
                df[column].nunique()
            )

    print("\n========== PRICE SUMMARY ==========")
    price_columns = [
        col for col in [
            "min_price",
            "max_price",
            "modal_price"
        ]
        if col in df.columns
    ]

    if price_columns:
        print(df[price_columns].describe())

    print("\nInspection completed.")


if __name__ == "__main__":
    inspect_dataset(DATA_FILE)
