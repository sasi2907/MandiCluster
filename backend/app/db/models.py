from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Commodity(Base):
    __tablename__ = "commodities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)

    observations: Mapped[list["MarketObservation"]] = relationship(
        back_populates="commodity"
    )


class Market(Base):
    __tablename__ = "markets"

    __table_args__ = (
        UniqueConstraint(
            "state",
            "district",
            "name",
            name="uq_market_location",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(100), index=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)

    observations: Mapped[list["MarketObservation"]] = relationship(
        back_populates="market"
    )


class MarketObservation(Base):
    __tablename__ = "market_observations"

    __table_args__ = (
        UniqueConstraint(
            "market_id",
            "commodity_id",
            "observation_date",
            "variety",
            "grade",
            name="uq_market_commodity_date_variety_grade",
        ),
        Index("ix_observation_date", "observation_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id"),
        index=True,
    )
    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id"),
        index=True,
    )

    observation_date: Mapped[date] = mapped_column(Date, index=True)
    variety: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="",
    )

    grade: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="",
    )

    min_price: Mapped[float] = mapped_column(Float)
    max_price: Mapped[float] = mapped_column(Float)
    modal_price: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    market: Mapped["Market"] = relationship(
        back_populates="observations"
    )
    commodity: Mapped["Commodity"] = relationship(
        back_populates="observations"
    )


class ClusterRun(Base):
    __tablename__ = "cluster_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    algorithm: Mapped[str] = mapped_column(
        String(100),
        default="KMeans",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    feature_columns: Mapped[list] = mapped_column(JSON, default=list)
    dataset_description: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    assignments: Mapped[list["MarketClusterAssignment"]] = relationship(
        back_populates="cluster_run"
    )


class MarketClusterAssignment(Base):
    __tablename__ = "market_cluster_assignments"

    __table_args__ = (
        UniqueConstraint(
            "cluster_run_id",
            "market_id",
            "commodity_id",
            name="uq_run_market_commodity",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    cluster_run_id: Mapped[int] = mapped_column(
        ForeignKey("cluster_runs.id"),
        index=True,
    )
    market_id: Mapped[int] = mapped_column(
        ForeignKey("markets.id"),
        index=True,
    )
    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id"),
        index=True,
    )

    cluster: Mapped[int] = mapped_column(Integer)
    avg_modal_price: Mapped[float] = mapped_column(Float)
    avg_price_range: Mapped[float] = mapped_column(Float)
    silhouette_score: Mapped[float] = mapped_column(Float)

    cluster_run: Mapped["ClusterRun"] = relationship(
        back_populates="assignments"
    )
