from sqlalchemy import inspect, text

from app.db.session import engine


def update_observation_schema():
    inspector = inspect(engine)

    columns = {
        column["name"]: column
        for column in inspector.get_columns("market_observations")
    }

    # Verify the table is empty before changing its column definitions.
    with engine.connect() as connection:
        row_count = connection.execute(
            text("SELECT COUNT(*) FROM market_observations")
        ).scalar_one()

        if row_count != 0:
            raise RuntimeError(
                "market_observations is not empty. "
                "Schema update cancelled."
            )

        if "variety" not in columns or "grade" not in columns:
            raise RuntimeError("Expected variety and grade columns were not found.")

        # Remove the old uniqueness constraint before updating columns.
        connection.execute(
            text(
                """
                ALTER TABLE market_observations
                DROP CONSTRAINT IF EXISTS
                uq_market_commodity_date_variety_grade
                """
            )
        )

        # Normalize any existing NULL values, then enforce NOT NULL.
        connection.execute(
            text(
                """
                UPDATE market_observations
                SET variety = COALESCE(variety, ''),
                    grade = COALESCE(grade, '')
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE market_observations
                ALTER COLUMN variety SET DEFAULT '',
                ALTER COLUMN variety SET NOT NULL,
                ALTER COLUMN grade SET DEFAULT '',
                ALTER COLUMN grade SET NOT NULL
                """
            )
        )

        connection.execute(
            text(
                """
                ALTER TABLE market_observations
                ADD CONSTRAINT uq_market_commodity_date_variety_grade
                UNIQUE (
                    market_id,
                    commodity_id,
                    observation_date,
                    variety,
                    grade
                )
                """
            )
        )

        connection.commit()

    print("Observation table schema updated successfully.")


if __name__ == "__main__":
    update_observation_schema()
