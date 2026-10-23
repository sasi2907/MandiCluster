import { Layers3, ArrowUpRight } from "lucide-react";
import { formatPrice } from "../utils/formatPrice";

function ClusterBreakdown({
  profiles,
  cluster,
  loading,
  onClusterChange,
}) {
  return (
    <article className="panel cluster-panel">
      <div className="panel-heading">
        <div>
          <h3>Cluster breakdown</h3>
          <p>Explore each group's characteristics</p>
        </div>

        <Layers3 size={20} className="muted-icon" />
      </div>

      <div className="cluster-list">
        {profiles.map((profile) => {
          const clusterValue = String(profile.cluster);
          const isSelected = clusterValue === cluster;

          return (
            <button
              key={profile.cluster}
              type="button"
              className={`cluster-row ${isSelected ? "selected" : ""}`}
              onClick={() =>
                onClusterChange(
                  isSelected ? "all" : clusterValue
                )
              }
            >
              <span
                className={`cluster-number cluster-color-${profile.cluster % 4}`}
              >
                {profile.cluster}
              </span>

              <span className="cluster-info">
                <strong>Cluster {profile.cluster}</strong>
                <small>{profile.market_count} market records</small>
              </span>

              <span className="cluster-price">
                {formatPrice(profile.avg_modal_price)}
                <small>Avg. modal price</small>
              </span>

              <ArrowUpRight size={16} className="muted-icon" />
            </button>
          );
        })}

        {!loading && !profiles.length && (
          <div className="empty-state">
            No clusters found for this crop.
          </div>
        )}
      </div>

      <p className="chart-note">
        Click a cluster to filter the market table below.
      </p>
    </article>
  );
}

export default ClusterBreakdown;
