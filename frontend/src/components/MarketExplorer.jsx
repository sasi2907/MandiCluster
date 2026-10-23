import { useEffect, useMemo, useState } from "react";
import {
  MapPin,
  Search,
  RefreshCw,
  Store,
} from "lucide-react";

import { formatPrice } from "../utils/formatPrice";

const PAGE_SIZE = 50;

function MarketExplorer({
  markets,
  profiles,
  cluster,
  search,
  loading,
  onClusterChange,
  onSearchChange,
  onRefresh,
}) {
  const [currentPage, setCurrentPage] = useState(1);

  const filteredMarkets = useMemo(() => {
    const query = search.trim().toLowerCase();

    return markets.filter((market) => {
      const matchesCluster =
        cluster === "all" ||
        market.cluster === Number(cluster);

      const matchesSearch =
        !query ||
        market.market?.toLowerCase().includes(query) ||
        market.district?.toLowerCase().includes(query) ||
        market.state?.toLowerCase().includes(query);

      return matchesCluster && matchesSearch;
    });
  }, [markets, cluster, search]);

  useEffect(() => {
    setCurrentPage(1);
  }, [cluster, search, markets]);

  const totalPages = Math.ceil(
    filteredMarkets.length / PAGE_SIZE
  );

  const safeCurrentPage = Math.min(
    currentPage,
    Math.max(totalPages, 1)
  );

  const startIndex = (safeCurrentPage - 1) * PAGE_SIZE;

  const endIndex = Math.min(
    startIndex + PAGE_SIZE,
    filteredMarkets.length
  );

  const paginatedMarkets = useMemo(
    () => filteredMarkets.slice(startIndex, endIndex),
    [filteredMarkets, startIndex, endIndex]
  );

  return (
    <section className="panel market-panel" id="markets">
      <div className="panel-heading market-heading">
        <div>
          <h3>Market explorer</h3>
          <p>Compare markets assigned to each cluster</p>
        </div>

        <div className="market-controls">
          <div className="search-box">
            <Search size={17} />

            <input
              value={search}
              onChange={(event) =>
                onSearchChange(event.target.value)
              }
              placeholder="Search market or district..."
              aria-label="Search market or district"
            />
          </div>

          <select
            className="cluster-filter"
            value={cluster}
            onChange={(event) =>
              onClusterChange(event.target.value)
            }
            aria-label="Filter by cluster"
          >
            <option value="all">All clusters</option>

            {profiles.map((profile) => (
              <option
                key={profile.cluster}
                value={profile.cluster}
              >
                Cluster {profile.cluster}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="table-meta">
        <span>
          <MapPin size={15} />
          {filteredMarkets.length.toLocaleString("en-IN")} matching records
        </span>

        <button
          type="button"
          className="refresh-button"
          onClick={onRefresh}
          disabled={loading}
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Market</th>
              <th>Location</th>
              <th>Avg. modal price</th>
              <th>Price range</th>
              <th>Cluster</th>
            </tr>
          </thead>

          <tbody>
            {paginatedMarkets.map((market, index) => (
              <tr
                key={`${market.market}-${market.district}-${market.state}-${startIndex + index}`}
              >
                <td>
                  <div className="market-name">
                    <span className="market-avatar">
                      <Store size={16} />
                    </span>

                    <strong>{market.market}</strong>
                  </div>
                </td>

                <td>
                  <div className="location-cell">
                    <span>{market.district}</span>
                    <small>{market.state}</small>
                  </div>
                </td>

                <td className="price-cell">
                  {formatPrice(market.avg_modal_price)}
                </td>

                <td>
                  {formatPrice(market.avg_price_range)}
                </td>

                <td>
                  <span
                    className={`cluster-badge cluster-color-${market.cluster % 4}`}
                  >
                    Cluster {market.cluster}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {!loading && filteredMarkets.length === 0 && (
          <div className="empty-state">
            No matching market records.
          </div>
        )}
      </div>

      
      <div className="table-footer">
        <div className="table-footer-info">
          {filteredMarkets.length === 0
            ? "Showing 0 records"
            : `Showing ${startIndex + 1}–${endIndex} of ${filteredMarkets.length.toLocaleString("en-IN")} records`}
        </div>

        <div className="pagination-controls">
          <button
            type="button"
            className="refresh-button"
            onClick={() =>
              setCurrentPage((page) => Math.max(1, page - 1))
            }
            disabled={safeCurrentPage <= 1}
          >
            Previous
          </button>

          <span className="pagination-page">
            Page {safeCurrentPage} of {Math.max(totalPages, 1)}
          </span>

          <button
            type="button"
            className="refresh-button"
            onClick={() =>
              setCurrentPage((page) =>
                Math.min(Math.max(totalPages, 1), page + 1)
              )
            }
            disabled={
              totalPages === 0 || safeCurrentPage >= totalPages
            }
          >
            Next
          </button>
        </div>

        <p className="table-footer-note">
          Cluster membership indicates similarity in model features,
          not guaranteed profitability.
        </p>
      </div>
    </section>
  );
}

export default MarketExplorer;
