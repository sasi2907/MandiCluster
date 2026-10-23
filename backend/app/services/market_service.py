from sqlalchemy import func, select

from app.db.models import (
    ClusterRun,
    Commodity,
    Market,
    MarketClusterAssignment,
)
from app.db.session import SessionLocal


def get_price_label(rank, total_clusters):
    """Create a readable label based on relative cluster price rank."""

    if total_clusters <= 1:
        return "Single price group"

    if total_clusters == 2:
        return (
            "Lower-price markets"
            if rank == 0
            else "Higher-price markets"
        )

    if total_clusters == 3:
        labels = [
            "Lower-price markets",
            "Middle-price markets",
            "Higher-price markets",
        ]
        return labels[rank]

    if rank == 0:
        return "Lowest-price markets"

    if rank == total_clusters - 1:
        return "Highest-price markets"

    if rank < total_clusters / 2:
        return "Lower-middle-price markets"

    return "Upper-middle-price markets"


def list_commodities():
    """Return commodities that have clustering results in PostgreSQL."""

    with SessionLocal() as session:
        statement = (
            select(Commodity.name)
            .join(
                MarketClusterAssignment,
                MarketClusterAssignment.commodity_id == Commodity.id,
            )
            .distinct()
            .order_by(Commodity.name)
        )

        return list(session.scalars(statement).all())


def get_cluster_label_map(commodity):
    """Map each cluster ID to its price-rank label."""

    profiles = get_cluster_profiles(commodity)

    return {
        int(profile["cluster"]): profile["cluster_label"]
        for profile in profiles
    }


def get_cluster_profiles(commodity):
    """Return aggregated cluster profiles from PostgreSQL."""

    commodity_name = commodity.strip()

    with SessionLocal() as session:
        commodity_id = session.scalar(
            select(Commodity.id).where(
                func.lower(Commodity.name) == commodity_name.casefold()
            )
        )

        if commodity_id is None:
            return []

        run = session.scalar(
            select(ClusterRun)
            .join(
                MarketClusterAssignment,
                MarketClusterAssignment.cluster_run_id == ClusterRun.id,
            )
            .where(
                MarketClusterAssignment.commodity_id == commodity_id
            )
            .limit(1)
        )

        if run is None:
            return []

        statement = (
            select(
                MarketClusterAssignment.cluster.label("cluster"),
                func.count(
                    MarketClusterAssignment.id
                ).label("market_count"),
                func.avg(
                    MarketClusterAssignment.avg_modal_price
                ).label("avg_modal_price"),
                func.avg(
                    MarketClusterAssignment.avg_price_range
                ).label("avg_price_range"),
                func.avg(
                    MarketClusterAssignment.silhouette_score
                ).label("silhouette_score"),
            )
            .where(
                MarketClusterAssignment.cluster_run_id == run.id,
                MarketClusterAssignment.commodity_id == commodity_id,
            )
            .group_by(MarketClusterAssignment.cluster)
            .order_by(
                func.avg(MarketClusterAssignment.avg_modal_price),
                MarketClusterAssignment.cluster,
            )
        )

        rows = session.execute(statement).mappings().all()

        if not rows:
            return []

        parameters = run.parameters or {}
        selected_k = parameters.get("selected_k", len(rows))

        profiles = []

        for rank, row in enumerate(rows):
            profiles.append(
                {
                    "cluster": int(row["cluster"]),
                    "market_count": int(row["market_count"]),
                    "avg_modal_price": float(row["avg_modal_price"]),
                    "avg_price_range": float(row["avg_price_range"]),
                    "commodity": commodity_name,
                    "selected_k": int(selected_k),
                    "silhouette_score": float(row["silhouette_score"]),
                    "cluster_label": get_price_label(rank, len(rows)),
                }
            )

        return profiles


def get_markets(commodity, cluster=None):
    """Return clustered markets, optionally filtered by cluster ID."""

    commodity_name = commodity.strip()

    with SessionLocal() as session:
        commodity_id = session.scalar(
            select(Commodity.id).where(
                func.lower(Commodity.name) == commodity_name.casefold()
            )
        )

        if commodity_id is None:
            return []

        run = session.scalar(
            select(ClusterRun)
            .join(
                MarketClusterAssignment,
                MarketClusterAssignment.cluster_run_id == ClusterRun.id,
            )
            .where(
                MarketClusterAssignment.commodity_id == commodity_id
            )
            .limit(1)
        )

        if run is None:
            return []

        statement = (
            select(
                Market.state.label("state"),
                Market.district.label("district"),
                Market.name.label("market"),
                Commodity.name.label("commodity"),
                MarketClusterAssignment.avg_modal_price.label(
                    "avg_modal_price"
                ),
                MarketClusterAssignment.avg_price_range.label(
                    "avg_price_range"
                ),
                MarketClusterAssignment.cluster.label("cluster"),
                MarketClusterAssignment.silhouette_score.label(
                    "silhouette_score"
                ),
            )
            .join(
                Market,
                Market.id == MarketClusterAssignment.market_id,
            )
            .join(
                Commodity,
                Commodity.id == MarketClusterAssignment.commodity_id,
            )
            .where(
                MarketClusterAssignment.cluster_run_id == run.id,
                MarketClusterAssignment.commodity_id == commodity_id,
            )
        )

        if cluster is not None:
            statement = statement.where(
                MarketClusterAssignment.cluster == cluster
            )

        statement = statement.order_by(
            MarketClusterAssignment.avg_modal_price.desc()
        )

        rows = session.execute(statement).mappings().all()

        if not rows:
            return []

        label_map = get_cluster_label_map(commodity_name)

        return [
            {
                "state": row["state"],
                "district": row["district"],
                "market": row["market"],
                "commodity": row["commodity"],
                "avg_modal_price": float(row["avg_modal_price"]),
                "avg_price_range": float(row["avg_price_range"]),
                "cluster": int(row["cluster"]),
                "silhouette_score": float(row["silhouette_score"]),
                "cluster_label": label_map.get(
                    int(row["cluster"]),
                    "Unclassified",
                ),
            }
            for row in rows
        ]
