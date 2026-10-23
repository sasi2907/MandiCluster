from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Commodity, Market, MarketObservation
from app.db.session import SessionLocal, engine


DATA_FILE = Path("data/raw/mandi_prices.csv")


def clean_text(value):
    """Convert empty or missing text values to None."""
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value or value.lower() in {"nan", "none", "null"}:
        return None

    return value


def import_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade",
        "Arrival_Date",
        "Min_x0020_Price",
        "Max_x0020_Price",
        "Modal_x0020_Price",
    ]

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing CSV columns: {sorted(missing_columns)}")

    df = df[required_columns].copy()

    # Normalize text fields without changing the source CSV.
    text_columns = [
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade",
    ]

    for column in text_columns:
        df[column] = df[column].map(clean_text)

    # Parse dates using the source format.
    df["Arrival_Date"] = pd.to_datetime(
        df["Arrival_Date"],
        format="%d/%m/%Y",
        errors="raise",
    ).dt.date

    price_columns = [
        "Min_x0020_Price",
        "Max_x0020_Price",
        "Modal_x0020_Price",
    ]

    for column in price_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    # Reject incomplete keys and invalid price records.
    key_columns = [
        "State",
        "District",
        "Market",
        "Commodity",
        "Arrival_Date",
    ]

    if df[key_columns].isna().any().any():
        raise ValueError("Some rows have missing market, commodity, or date keys.")

    if df[price_columns].isna().any().any():
        raise ValueError("Some rows have missing prices.")

    if (df[price_columns] < 0).any().any():
        raise ValueError("Negative prices were found.")

    # The source may contain exact repeated records.
    # Keep one copy of each identical source observation.
    df = df.drop_duplicates(
        subset=required_columns,
        keep="first",
    )

    # The database constraint treats NULLs as distinct. Normalize missing
    # variety/grade to empty strings for consistent uniqueness handling.
    df["Variety"] = df["Variety"].fillna("")
    df["Grade"] = df["Grade"].fillna("")

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        with session.begin():
            # Avoid silently mixing a second import with existing observations.
            existing_count = session.scalar(
                select(MarketObservation.id).limit(1)
            )

            if existing_count is not None:
                raise RuntimeError(
                    "market_observations is not empty. "
                    "Import cancelled to avoid duplicate or mixed data."
                )

            # Create or reuse commodity records.
            commodity_names = sorted(df["Commodity"].unique())

            commodities = {}
            for name in commodity_names:
                commodity = Commodity(name=name)
                session.add(commodity)
                commodities[name] = commodity

            session.flush()

            # Create unique market records.
            market_keys = (
                df[["State", "District", "Market"]]
                .drop_duplicates()
                .sort_values(["State", "District", "Market"])
            )

            markets = {}
            for row in market_keys.itertuples(index=False, name=None):
                state, district, name = row
                market = Market(
                    state=state,
                    district=district,
                    name=name,
                )
                session.add(market)
                markets[(state, district, name)] = market

            session.flush()

            # Insert observations with their foreign keys.
            observations = []

            for row in df.itertuples(index=False, name=None):
                (
                    state,
                    district,
                    market_name,
                    commodity_name,
                    variety,
                    grade,
                    observation_date,
                    min_price,
                    max_price,
                    modal_price,
                ) = row

                observations.append(
                    MarketObservation(
                        market=markets[(state, district, market_name)],
                        commodity=commodities[commodity_name],
                        observation_date=observation_date,
                        variety=variety,
                        grade=grade,
                        min_price=float(min_price),
                        max_price=float(max_price),
                        modal_price=float(modal_price),
                    )
                )

            session.add_all(observations)

        # The transaction commits only after all inserts succeed.

    print("Dataset import completed successfully.")
    print(f"Source rows: {len(pd.read_csv(DATA_FILE))}")
    print(f"Unique commodities imported: {len(commodity_names)}")
    print(f"Unique markets imported: {len(markets)}")
    print(f"Observations imported: {len(observations)}")


if __name__ == "__main__":
    import_data()
