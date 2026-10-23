import {
  Store,
  Layers3,
  TrendingUp,
  ChartNoAxesCombined,
} from "lucide-react";

import { formatPrice } from "../utils/formatPrice";

function StatsGrid({
  loading,
  marketCount,
  clusterCount,
  averagePrice,
  averageSilhouette,
}) {
  const displayValue = loading ? "—" : null;

  return (
    <section className="stats-grid">
      <article className="stat-card">
        <div className="stat-top">
          <span>Markets &amp; records</span>
          <span className="stat-icon mint">
            <Store size={20} />
          </span>
        </div>

        <strong>
          {displayValue ?? marketCount.toLocaleString("en-IN")}
        </strong>

        <p>For the selected commodity</p>
      </article>

      <article className="stat-card">
        <div className="stat-top">
          <span>Discovered clusters</span>
          <span className="stat-icon violet">
            <Layers3 size={20} />
          </span>
        </div>

        <strong>{displayValue ?? clusterCount}</strong>

        <p>Groups identified by K-Means</p>
      </article>

      <article className="stat-card">
        <div className="stat-top">
          <span>Mean modal price</span>
          <span className="stat-icon amber">
            <TrendingUp size={20} />
          </span>
        </div>

        <strong className="price-stat">
          {displayValue ?? formatPrice(averagePrice)}
        </strong>

        <p>Average of market-level records</p>
      </article>

      <article className="stat-card">
        <div className="stat-top">
          <span>Silhouette score</span>
          <span className="stat-icon blue">
            <ChartNoAxesCombined size={20} />
          </span>
        </div>

        <strong>
          {displayValue ?? averageSilhouette.toFixed(3)}
        </strong>

        <p>Cluster separation diagnostic</p>
      </article>
    </section>
  );
}

export default StatsGrid;
