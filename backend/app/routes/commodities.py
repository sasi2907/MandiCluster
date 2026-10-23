from fastapi import APIRouter, HTTPException, Query

from app.schemas.commodity import (
    CommodityClustersResponse,
    CommodityListResponse,
    CommodityMarketsResponse,
)
from app.services.market_service import (
    get_cluster_profiles,
    get_markets,
    list_commodities,
)

router = APIRouter(
    prefix="/api/commodities",
    tags=["Commodities"],
)


@router.get("", response_model=CommodityListResponse)
def commodities():
    return {"commodities": list_commodities()}


@router.get(
    "/{commodity}/clusters",
    response_model=CommodityClustersResponse,
)
def commodity_clusters(commodity: str):
    profiles = get_cluster_profiles(commodity)

    if not profiles:
        raise HTTPException(
            status_code=404,
            detail="Commodity not found or no clusters available.",
        )

    return {
        "commodity": commodity,
        "clusters": profiles,
    }


@router.get(
    "/{commodity}/markets",
    response_model=CommodityMarketsResponse,
)
def commodity_markets(
    commodity: str,
    cluster: int | None = Query(default=None, ge=0),
):
    markets = get_markets(commodity, cluster)

    if not markets:
        raise HTTPException(
            status_code=404,
            detail="No matching market records found.",
        )

    return {
        "commodity": commodity,
        "cluster": cluster,
        "count": len(markets),
        "markets": markets,
    }
