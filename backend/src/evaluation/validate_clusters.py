from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs"

ASSIGNMENTS_FILE = OUTPUT_DIR / "cluster_assignments.csv"
PROFILES_FILE = OUTPUT_DIR / "cluster_profiles.csv"


def validate_clusters():
    assignments = pd.read_csv(ASSIGNMENTS_FILE)
    profiles = pd.read_csv(PROFILES_FILE)

    # One evaluation row per commodity
    evaluations = (
        assignments.groupby("commodity")
        .agg(
            records=("cluster", "size"),
            clusters=("cluster", "nunique"),
            silhouette=("silhouette_score", "first"),
        )
        .reset_index()
    )

    # Calculate the size of each discovered cluster
    sizes = (
        assignments.groupby(["commodity", "cluster"])
        .size()
        .rename("cluster_size")
        .reset_index()
    )

    # Count clusters containing fewer than 5 records
    tiny_clusters = sizes[sizes["cluster_size"] < 5]

    # Identify commodities with weak silhouette scores
    weak_results = evaluations[
        evaluations["silhouette"] < 0.25
    ].sort_values("silhouette")

    # Summarize the cluster sizes for each commodity
    size_summary = (
        sizes.groupby("commodity")["cluster_size"]
        .agg(["min", "median", "max"])
        .reset_index()
    )

    evaluations = evaluations.merge(
        size_summary,
        on="commodity",
        how="left",
    )

    evaluations["has_tiny_cluster"] = (
        evaluations["min"] < 5
    )

    evaluations.to_csv(
        OUTPUT_DIR / "validation_by_commodity.csv",
        index=False,
    )

    tiny_clusters.to_csv(
        OUTPUT_DIR / "tiny_clusters.csv",
        index=False,
    )

    weak_results.to_csv(
        OUTPUT_DIR / "weak_clustering.csv",
        index=False,
    )

    print("\n========== VALIDATION SUMMARY ==========")
    print("Commodities evaluated:", len(evaluations))
    print("Records assigned:", len(assignments))
    print(
        "Commodities with silhouette below 0.25:",
        len(weak_results),
    )
    print(
        "Clusters with fewer than 5 records:",
        len(tiny_clusters),
    )
    print(
        "Commodities containing tiny clusters:",
        evaluations["has_tiny_cluster"].sum(),
    )

    print("\n========== LOWEST SILHOUETTE SCORES ==========")
    print(
        evaluations.nsmallest(10, "silhouette")[
            ["commodity", "records", "clusters", "silhouette"]
        ].to_string(index=False)
    )

    print("\n========== SMALLEST CLUSTERS ==========")
    print(
        tiny_clusters.sort_values("cluster_size")
        .head(15)
        .to_string(index=False)
    )

    print("\nValidation reports saved in:", OUTPUT_DIR)


if __name__ == "__main__":
    validate_clusters()
