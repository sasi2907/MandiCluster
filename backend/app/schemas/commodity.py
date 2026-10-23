from pydantic import BaseModel


class CommodityListResponse(BaseModel):
    commodities: list[str]


class ClusterProfile(BaseModel):
    cluster: int
    market_count: int
    avg_modal_price: float
    avg_price_range: float
    commodity: str
    selected_k: int
    silhouette_score: float
    cluster_label: str


class CommodityClustersResponse(BaseModel):
    commodity: str
    clusters: list[ClusterProfile]


class MarketRecord(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    avg_modal_price: float
    avg_price_range: float
    cluster: int
    silhouette_score: float
    cluster_label: str


class CommodityMarketsResponse(BaseModel):
    commodity: str
    cluster: int | None
    count: int
    markets: list[MarketRecord]
