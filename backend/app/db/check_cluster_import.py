from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.db.models import Commodity, Market
from app.db.session import SessionLocal


ASSIGNMENTS_FILE = Path("outputs/cluster_assignments.csv")


def clean_text(value):
    if pd.isna(value):
        return None
    return str(value).strip()


def check_cluster_import():
    if not ASSIGNMENTS_FILE.exists():
        raise FileNotFoundError(
            f"Cluster assignments file not found: {ASSIGNMENTS_FILE}"
        )

    df = pd.read_csv(ASSIGNMENTS_FILE)

    required_columns = [
        "state",
        "district",
        "market",
        "commodity",
        "cluster",
        "selected_k",
        "avg_modal_price",
        "avg_price_range",
        "silhouette_score",
    ]

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")

    for column in ["state", "district", "market", "commodity"]:
        df[column] = df[column].map(clean_text)

    if df[["state", "district", "market", "commodity"]].isna().any().any():
        raise ValueError("Assignments contain missing market or commodity keys.")

    duplicate_mask = df.duplicated(
        subset=["state", "district", "market", "commodity"],
        keep=False,
    )

    with SessionLocal() as session:
        market_rows = session.execute(
            select(Market.state, Market.district, Market.name)
        ).all()

        commodity_names = set(
            session.scalars(select(Commodity.name)).all()
        )

    database_market_keys = {
        (state, district, name)
        for state, district, name in market_rows
    }

    csv_market_keys = set(
        zip(df["state"], df["district"], df["market"])
    )

    missing_markets = csv_market_keys - database_market_keys
    missing_commodities = set(df["commodity"]) - commodity_names

    print("=== Cluster Import Validation ===")
    print(f"Assignment rows: {len(df)}")
    print(f"Distinct market keys in assignments: {len(csv_market_keys)}")
    print(f"Duplicate market-commodity assignment rows: {int(duplicate_mask.sum())}")
    print(f"Market keys not found in database: {len(missing_markets)}")
    print(f"Commodities not found in database: {len(missing_commodities)}")

    if missing_markets:
        print("\nExamples of unmatched markets:")
        for key in sorted(missing_markets)[:10]:
            print(key)

    if missing_commodities:
        print("\nUnmatched commodities:")
        for name in sorted(missing_commodities)[:10]:
            print(name)

    if missing_markets or missing_commodities or duplicate_mask.any():
        print("\nValidation needs review before importing.")
    else:
        print("\nValidation passed. Ready to import cluster results.")


if __name__ == "__main__":
    check_cluster_import()
