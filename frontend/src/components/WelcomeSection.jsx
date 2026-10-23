import { Sprout, Leaf, ChevronDown } from "lucide-react";

function WelcomeSection({
  commodities,
  commodity,
  onCommodityChange,
}) {
  return (
    <section className="welcome-section">
      <div>
        <div className="eyebrow">
          <Sprout size={15} />
          AGRICULTURAL ANALYTICS
        </div>

        <h2>Understand your market landscape.</h2>

        <p>
          Explore discovered market-price groups and compare reported prices
          for individual crops.
        </p>
      </div>

      <div className="crop-picker">
        <label htmlFor="commodity">SELECT COMMODITY</label>

        <div className="select-wrap">
          <Leaf size={18} />

          <select
            id="commodity"
            value={commodity}
            onChange={(event) =>
              onCommodityChange(event.target.value)
            }
          >
            {commodities.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>

          <ChevronDown size={16} />
        </div>
      </div>
    </section>
  );
}

export default WelcomeSection;
