from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.db.models import (
    ClusterRun,
    Commodity,
    Market,
    MarketClusterAssignment,
)
from app.db.session import SessionLocal


ASSIGNMENTS_FILE = Path("outputs/cluster_assignments.csv")
EVALUATION_FILE = Path("outputs/cluster_evaluation.csv")


def import_clusters():
    assignments_df = pd.read_csv(ASSIGNMENTS_FILE)
    evaluation_df = pd.read_csv(EVALUATION_FILE)

    required_columns = {
        "state",
        "district",
        "market",
        "commodity",
        "avg_modal_price",
        "avg_price_range",
        "cluster",
        "selected_k",
        "silhouette_score",
    }

    missing = required_columns - set(assignments_df.columns)
    if missing:
        raise ValueError(f"Missing assignment columns: {sorted(missing)}")

    if not {"commodity", "records", "selected_k", "silhouette_score"}.issubset(
        evaluation_df.columns
    ):
        raise ValueError("The evaluation CSV is missing required columns.")

    if assignments_df.empty:
        raise ValueError("The assignments file contains no records.")

    if evaluation_df["commodity"].duplicated().any():
        raise ValueError("Evaluation file has duplicate commodity rows.")

    with SessionLocal() as session:
        with session.begin():
            existing_runs = session.scalar(
                select(ClusterRun.id).limit(1)
            )

            if existing_runs is not None:
                raise RuntimeError(
                    "Cluster runs already exist. Import cancelled "
                    "to avoid duplicate results."
                )

            markets = session.scalars(select(Market)).all()
            commodities = session.scalars(select(Commodity)).all()

            market_map = {
                (market.state, market.district, market.name): market.id
                for market in markets
            }
            commodity_map = {
                commodity.name: commodity.id
                for commodity in commodities
            }

            evaluation_map = evaluation_df.set_index("commodity").to_dict(
                orient="index"
            )

            # Validate every assignment before writing any cluster results.
            for row in assignments_df.itertuples(index=False):
                key = (row.state, row.district, row.market)

                if key not in market_map:
                    raise ValueError(f"Unknown market: {key}")

                if row.commodity not in commodity_map:
                    raise ValueError(f"Unknown commodity: {row.commodity}")

                if row.commodity not in evaluation_map:
                    raise ValueError(
                        f"No evaluation record for {row.commodity}"
                    )

            run_count = 0
            assignment_count = 0

            for commodity_name, group in assignments_df.groupby(
                "commodity",
                sort=True,
            ):
                evaluation = evaluation_map[commodity_name]

                selected_k_values = group["selected_k"].unique()
                silhouette_values = group["silhouette_score"].unique()

                if len(selected_k_values) != 1 or len(silhouette_values) != 1:
                    raise ValueError(
                        f"Inconsistent model metrics for {commodity_name}"
                    )

                selected_k = int(selected_k_values[0])
                silhouette = float(silhouette_values[0])

                parameters = {
                    "commodity": commodity_name,
                    "selected_k": selected_k,
                    "silhouette_score": silhouette,
                    "evaluation_status": str(evaluation.get("status", "Unknown")),
                }

                cluster_run = ClusterRun(
                    algorithm="KMeans",
                    parameters=parameters,
                    feature_columns=[
                        "avg_modal_price",
                        "avg_price_range",
                    ],
                    dataset_description=(
                        f"Mandi price clusters for {commodity_name}; "
                        "source date 2026-10-16"
                    ),
                )

                session.add(cluster_run)
                session.flush()

                records = []

                for row in group.itertuples(index=False):
                    market_id = market_map[
                        (row.state, row.district, row.market)
                    ]
                    commodity_id = commodity_map[commodity_name]

                    records.append(
                        MarketClusterAssignment(
                            cluster_run_id=cluster_run.id,
                            market_id=market_id,
                            commodity_id=commodity_id,
                            cluster=int(row.cluster),
                            avg_modal_price=float(row.avg_modal_price),
                            avg_price_range=float(row.avg_price_range),
                            silhouette_score=float(row.silhouette_score),
                        )
                    )

                session.add_all(records)

                run_count += 1
                assignment_count += len(records)

            print(f"Cluster runs imported: {run_count}")
            print(f"Cluster assignments imported: {assignment_count}")


if __name__ == "__main__":
    import_clusters()
