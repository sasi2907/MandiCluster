from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs"

EVALUATION_FILE = OUTPUT_DIR / "cluster_evaluation.csv"
ASSIGNMENTS_FILE = OUTPUT_DIR / "cluster_assignments.csv"


def analyze_quality():
    if not EVALUATION_FILE.exists():
        raise FileNotFoundError(
            "Run python src/models/train_clusters.py first."
        )

    evaluation = pd.read_csv(EVALUATION_FILE)
    assignments = pd.read_csv(ASSIGNMENTS_FILE)

    # Use the current training evaluation, not an old quality report.
    report = evaluation.rename(
        columns={"status": "quality_flag"}
    ).copy()

    cluster_sizes = (
        assignments.groupby(["commodity", "cluster"])
        .size()
        .reset_index(name="market_count")
    )

    if cluster_sizes.empty:
        tiny_clusters = cluster_sizes.copy()
    else:
        tiny_clusters = cluster_sizes[
            cluster_sizes["market_count"] < 5
        ].copy()

    report.to_csv(
        OUTPUT_DIR / "cluster_quality_report.csv",
        index=False,
    )

    tiny_clusters.to_csv(
        OUTPUT_DIR / "tiny_clusters.csv",
        index=False,
    )

    print("\n========== UPDATED CLUSTER QUALITY ==========")
    print("Commodities clustered:", len(report))
    print(
        "Promising:",
        (report["quality_flag"] == "Promising").sum(),
    )
    print(
        "Weak separation:",
        (report["quality_flag"] == "Weak separation").sum(),
    )
    print(
        "Needs review:",
        (report["quality_flag"] == "Review").sum(),
    )
    print("Clusters with fewer than 5 markets:", len(tiny_clusters))

    print("\n========== LOWEST SILHOUETTE SCORES ==========")
    columns = [
        "commodity",
        "records",
        "selected_k",
        "silhouette_score",
        "smallest_cluster",
        "largest_cluster",
        "quality_flag",
    ]

    print(
        report.sort_values("silhouette_score")[columns]
        .head(15)
        .to_string(index=False)
    )

    print("\nSaved:", OUTPUT_DIR / "cluster_quality_report.csv")
    print("Saved:", OUTPUT_DIR / "tiny_clusters.csv")


if __name__ == "__main__":
    analyze_quality()
