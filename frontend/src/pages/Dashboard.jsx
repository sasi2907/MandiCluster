import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Leaf } from "lucide-react";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import WelcomeSection from "../components/WelcomeSection";
import StatsGrid from "../components/StatsGrid";
import ClusterPriceChart from "../components/ClusterPriceChart";
import ClusterBreakdown from "../components/ClusterBreakdown";
import MarketExplorer from "../components/MarketExplorer";

import {
  getCommodities,
  getCommodityClusters,
  getCommodityMarkets,
} from "../services/api";

import "../global.css";

function Dashboard() {
  const [commodities, setCommodities] = useState([]);
  const [commodity, setCommodity] = useState("");
  const [profiles, setProfiles] = useState([]);
  const [markets, setMarkets] = useState([]);
  const [cluster, setCluster] = useState("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshCounter, setRefreshCounter] = useState(0);

  // Load the available commodities once.
  useEffect(() => {
    let cancelled = false;

    getCommodities()
      .then((items) => {
        if (cancelled) return;

        setCommodities(items);

        if (items.length > 0) {
          setCommodity(
            items.includes("Tomato") ? "Tomato" : items[0]
          );
        } else {
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Cannot connect to the MandiCluster API.");
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Load cluster profiles and market records for the selected commodity.
  useEffect(() => {
    if (!commodity) return;

    let cancelled = false;

    setLoading(true);
    setError("");
    setCluster("all");
    setSearch("");

    Promise.all([
      getCommodityClusters(commodity),
      getCommodityMarkets(commodity),
    ])
      .then(([clusterData, marketData]) => {
        if (cancelled) return;

        setProfiles(clusterData.clusters);
        setMarkets(marketData.markets);
      })
      .catch(() => {
        if (cancelled) return;

        setProfiles([]);
        setMarkets([]);
        setError(`Unable to load data for ${commodity}.`);
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [commodity, refreshCounter]);

  // Calculate the mean modal price across returned market records.
  const averagePrice = useMemo(() => {
    if (!markets.length) return 0;

    const total = markets.reduce(
      (sum, market) =>
        sum + Number(market.avg_modal_price || 0),
      0
    );

    return total / markets.length;
  }, [markets]);

  // Prepare data for the cluster price chart.
  const chartData = useMemo(() => {
    return profiles
      .map((profile) => ({
        name: `Cluster ${profile.cluster}`,
        cluster: profile.cluster,
        price: Number(profile.avg_modal_price),
        markets: Number(profile.market_count),
      }))
      .sort((a, b) => a.cluster - b.cluster);
  }, [profiles]);

  const averageSilhouette = profiles.length
    ? Number(profiles[0].silhouette_score || 0)
    : 0;

  function handleRefresh() {
    setRefreshCounter((count) => count + 1);
  }

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-area" id="dashboard">
        <Topbar />

        <WelcomeSection
          commodities={commodities}
          commodity={commodity}
          onCommodityChange={setCommodity}
        />

        {error && (
          <div className="error-banner">
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        <StatsGrid
          loading={loading}
          marketCount={markets.length}
          clusterCount={profiles.length}
          averagePrice={averagePrice}
          averageSilhouette={averageSilhouette}
        />

        <section className="content-grid" id="clusters">
          <ClusterPriceChart
            loading={loading}
            chartData={chartData}
          />

          <ClusterBreakdown
            profiles={profiles}
            cluster={cluster}
            loading={loading}
            onClusterChange={setCluster}
          />
        </section>

        <MarketExplorer
          markets={markets}
          profiles={profiles}
          cluster={cluster}
          search={search}
          loading={loading}
          onClusterChange={setCluster}
          onSearchChange={setSearch}
          onRefresh={handleRefresh}
        />

        <footer className="page-footer">
          <span>
            MandiCluster · Unsupervised market segmentation
          </span>

          <span>
            Data-driven exploration <Leaf size={14} />
          </span>
        </footer>
      </main>
    </div>
  );
}

export default Dashboard;
