from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]

FEATURES_FILE = ROOT / "data" / "processed" / "market_features.csv"
OUTPUT_DIR = ROOT / "outputs"
MODEL_DIR = ROOT / "models"

ASSIGNMENTS_FILE = OUTPUT_DIR / "cluster_assignments.csv"
EVALUATION_FILE = OUTPUT_DIR / "cluster_evaluation.csv"
PROFILES_FILE = OUTPUT_DIR / "cluster_profiles.csv"
SKIPPED_FILE = OUTPUT_DIR / "skipped_commodities.csv"
MODEL_FILE = MODEL_DIR / "mandi_cluster_models.joblib"

KEY_COLUMNS = ["state", "district", "market", "commodity"]
FEATURE_COLUMNS = ["avg_modal_price", "avg_price_range"]

MIN_MARKET_RECORDS = 10
MIN_CLUSTER_SIZE = 5
MAX_CLUSTERS = 6
RANDOM_STATE = 42


def load_features():
    if not FEATURES_FILE.exists():
        raise FileNotFoundError(
            f"Feature file not found: {FEATURES_FILE}\n"
            "Run: python src/features/build_features.py"
        )

    df = pd.read_csv(FEATURES_FILE)

    required = KEY_COLUMNS + FEATURE_COLUMNS
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=required).copy()

    for column in FEATURE_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=FEATURE_COLUMNS)

    # Reject invalid price features.
    df = df[
        (df["avg_modal_price"] > 0)
        & (df["avg_price_range"] >= 0)
    ].copy()

    return df


def find_best_model(group):
    X = group[FEATURE_COLUMNS].to_numpy(dtype=float)

    if len(X) < MIN_MARKET_RECORDS:
        return None, "Fewer than 10 market records"

    # Clustering constant features does not provide useful separation.
    if np.any(np.std(X, axis=0) < 1e-9):
        varying_columns = [
            column
            for column in FEATURE_COLUMNS
            if group[column].nunique() > 1
        ]

        if len(varying_columns) == 0:
            return None, "All selected features are constant"

        feature_columns = varying_columns
    else:
        feature_columns = FEATURE_COLUMNS

    X = group[feature_columns].to_numpy(dtype=float)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Identical feature vectors cannot be meaningfully separated.
    unique_count = len(np.unique(X_scaled, axis=0))

    if unique_count < 2:
        return None, "Fewer than two distinct feature patterns"

    upper_k = min(MAX_CLUSTERS, len(group) // MIN_CLUSTER_SIZE, unique_count)

    if upper_k < 2:
        return None, "Not enough records for at least two valid clusters"

    candidates = []

    for k in range(2, upper_k + 1):
        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=20,
        )

        labels = model.fit_predict(X_scaled)

        # Silhouette is undefined if the model creates only one cluster
        # or one cluster per distinct observation.
        if len(np.unique(labels)) < 2:
            continue

        sizes = pd.Series(labels).value_counts()

        # Reject models that create clusters that are too small.
        if sizes.min() < MIN_CLUSTER_SIZE:
            continue

        if len(np.unique(labels)) >= len(group):
            continue

        score = silhouette_score(X_scaled, labels)

        candidates.append(
            {
                "model": model,
                "scaler": scaler,
                "labels": labels,
                "k": k,
                "silhouette": float(score),
                "feature_columns": feature_columns,
                "smallest_cluster": int(sizes.min()),
                "largest_cluster": int(sizes.max()),
            }
        )

    if not candidates:
        return None, "No candidate model met the minimum cluster-size rule"

    # Prefer the best silhouette among models that passed our size checks.
    best = max(candidates, key=lambda item: item["silhouette"])

    return best, None


def train():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = load_features()

    assignments = []
    evaluations = []
    profiles = []
    skipped = []
    saved_models = {}

    commodities = sorted(df["commodity"].dropna().unique())

    print("\n========== TRAINING CLUSTERS ==========")
    print("Eligible source records:", len(df))
    print("Commodities to examine:", len(commodities))

    for commodity in commodities:
        group = (
            df[df["commodity"] == commodity]
            .copy()
            .reset_index(drop=True)
        )

        result, reason = find_best_model(group)

        if result is None:
            skipped.append(
                {
                    "commodity": commodity,
                    "market_records": len(group),
                    "reason": reason,
                }
            )
            continue

        labels = result["labels"]

        group["cluster"] = labels
        group["selected_k"] = result["k"]
        group["silhouette_score"] = result["silhouette"]

        assignments.append(group)

        saved_models[commodity] = {
            "model": result["model"],
            "scaler": result["scaler"],
            "feature_columns": result["feature_columns"],
            "selected_k": result["k"],
            "silhouette_score": result["silhouette"],
        }

        evaluations.append(
            {
                "commodity": commodity,
                "records": len(group),
                "selected_k": result["k"],
                "silhouette_score": result["silhouette"],
                "smallest_cluster": result["smallest_cluster"],
                "largest_cluster": result["largest_cluster"],
                "status": (
                    "Promising"
                    if result["silhouette"] >= 0.50
                    else "Review"
                    if result["silhouette"] >= 0.25
                    else "Weak separation"
                ),
            }
        )

        profile = (
            group.groupby("cluster")
            .agg(
                market_count=("market", "size"),
                avg_modal_price=("avg_modal_price", "mean"),
                avg_price_range=("avg_price_range", "mean"),
            )
            .reset_index()
        )

        profile["commodity"] = commodity
        profile["selected_k"] = result["k"]
        profile["silhouette_score"] = result["silhouette"]

        profiles.append(profile)

    assignment_columns = (
        KEY_COLUMNS
        + FEATURE_COLUMNS
        + ["cluster", "selected_k", "silhouette_score"]
    )

    profile_columns = [
        "cluster",
        "market_count",
        "avg_modal_price",
        "avg_price_range",
        "commodity",
        "selected_k",
        "silhouette_score",
    ]

    evaluation_columns = [
        "commodity",
        "records",
        "selected_k",
        "silhouette_score",
        "smallest_cluster",
        "largest_cluster",
        "status",
    ]

    skipped_columns = ["commodity", "market_records", "reason"]

    assignment_df = (
        pd.concat(assignments, ignore_index=True)
        if assignments
        else pd.DataFrame(columns=assignment_columns)
    )

    profile_df = (
        pd.concat(profiles, ignore_index=True)
        if profiles
        else pd.DataFrame(columns=profile_columns)
    )

    evaluation_df = pd.DataFrame(
        evaluations,
        columns=evaluation_columns,
    )

    skipped_df = pd.DataFrame(
        skipped,
        columns=skipped_columns,
    )

    assignment_df.to_csv(ASSIGNMENTS_FILE, index=False)
    evaluation_df.to_csv(EVALUATION_FILE, index=False)
    profile_df.to_csv(PROFILES_FILE, index=False)
    skipped_df.to_csv(SKIPPED_FILE, index=False)

    joblib.dump(saved_models, MODEL_FILE)

    print("\n========== TRAINING COMPLETED ==========")
    print("Commodities examined:", len(commodities))
    print("Commodities clustered:", len(saved_models))
    print("Commodities skipped:", len(skipped_df))
    print("Market records assigned:", len(assignment_df))

    if not evaluation_df.empty:
        print("\n========== MODEL QUALITY ==========")
        print(evaluation_df["status"].value_counts().to_string())
        print(
            "\nAverage silhouette:",
            round(evaluation_df["silhouette_score"].mean(), 3),
        )

    print("\n========== OUTPUT FILES ==========")
    print("Assignments:", ASSIGNMENTS_FILE)
    print("Profiles:", PROFILES_FILE)
    print("Evaluation:", EVALUATION_FILE)
    print("Skipped commodities:", SKIPPED_FILE)
    print("Models:", MODEL_FILE)


if __name__ == "__main__":
    train()
