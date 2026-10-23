import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

import { ChartNoAxesCombined } from "lucide-react";
import { formatPrice } from "../utils/formatPrice";

function ClusterPriceChart({ loading, chartData }) {
  return (
    <article className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <h3>Cluster price comparison</h3>
          <p>Average modal price within each discovered group</p>
        </div>

        <span className="panel-icon">
          <ChartNoAxesCombined size={19} />
        </span>
      </div>

      {loading ? (
        <div className="empty-state">Loading chart data...</div>
      ) : chartData.length ? (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{
                top: 12,
                right: 12,
                left: 8,
                bottom: 4,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e7ece8"
              />

              <XAxis
                dataKey="name"
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) =>
                  `₹${Number(value).toLocaleString("en-IN")}`
                }
                width={78}
              />

              <Tooltip
                formatter={(value, name) => [
                  name === "price" ? formatPrice(value) : value,
                  name === "price"
                    ? "Average modal price"
                    : name,
                ]}
              />

              <Bar
                dataKey="price"
                fill="#19856b"
                radius={[7, 7, 0, 0]}
                maxBarSize={55}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="empty-state">
          No cluster data available.
        </div>
      )}

      <p className="chart-note">
        Prices describe the current dataset, not predicted future prices.
      </p>
    </article>
  );
}

export default ClusterPriceChart;
