const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api"
).replace(/\/+$/, "");

export async function getCommodities() {
  const response = await fetch(`${API_BASE_URL}/commodities`);

  if (!response.ok) {
    throw new Error("Failed to load commodities");
  }

  const data = await response.json();
  return data.commodities;
}

export async function getCommodityClusters(commodity) {
  const response = await fetch(
    `${API_BASE_URL}/commodities/${encodeURIComponent(commodity)}/clusters`
  );

  if (!response.ok) {
    throw new Error("Failed to load clusters");
  }

  return response.json();
}

export async function getCommodityMarkets(commodity, cluster) {
  const params = new URLSearchParams();

  if (cluster !== undefined && cluster !== null) {
    params.set("cluster", cluster);
  }

  const query = params.toString();

  const response = await fetch(
    `${API_BASE_URL}/commodities/${encodeURIComponent(commodity)}/markets${query ? `?${query}` : ""}`
  );

  if (!response.ok) {
    throw new Error("Failed to load markets");
  }

  return response.json();
}
