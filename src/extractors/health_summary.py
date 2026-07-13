import json
from typing import Any

import pandas as pd

from config.settings import (
    HEALTH_DIR,
    INVENTORY_DIR,
    SCHEMA_DIR,
    RELATIONSHIP_DIR,
)


class HealthSummary:

    def __init__(self) -> None:

        HEALTH_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _grade(health_score: float) -> str:

        if health_score >= 90:
            return "A"
        if health_score >= 80:
            return "B"
        if health_score >= 70:
            return "C"
        if health_score >= 60:
            return "D"
        return "F"

    def summarize(self) -> pd.DataFrame:

        inventory_df = pd.read_csv(INVENTORY_DIR / "inventory.csv") if (INVENTORY_DIR / "inventory.csv").exists() else pd.DataFrame(columns=["dataset_name", "rows"])
        inventory_lookup = inventory_df[["dataset_name", "rows"]].copy()
        inventory_lookup["dataset_name"] = inventory_lookup["dataset_name"].astype(str)

        relationship_path = RELATIONSHIP_DIR / "relationship_graph.csv"
        relationship_df = pd.read_csv(relationship_path) if relationship_path.exists() else pd.DataFrame(columns=["parent_dataset", "child_dataset"])

        rows: list[dict[str, Any]] = []

        for schema_file in sorted(SCHEMA_DIR.glob("*_schema.csv")):
            schema_df = pd.read_csv(schema_file)
            dataset_name = str(schema_df.iloc[0]["dataset_name"]) if not schema_df.empty else schema_file.stem.replace("_schema", "")

            total_rows = int(
                inventory_lookup.loc[inventory_lookup["dataset_name"] == dataset_name, "rows"].iloc[0]
            ) if not inventory_lookup.empty and dataset_name in inventory_lookup["dataset_name"].values else 1

            missing_percentage = float(schema_df["missing_percentage"].mean()) if not schema_df.empty else 0.0
            duplicate_percentage = float(
                (schema_df["duplicate_count"] / max(total_rows, 1)).mean() * 100
            ) if not schema_df.empty else 0.0

            missing_score = max(0.0, 100.0 - missing_percentage)
            duplicate_score = max(0.0, 100.0 - duplicate_percentage)
            schema_score = max(0.0, 100.0 - missing_percentage / 2.0)

            relationship_count = 0
            if not relationship_df.empty:
                relationship_count = int(
                    ((relationship_df["parent_dataset"] == dataset_name).sum())
                    + ((relationship_df["child_dataset"] == dataset_name).sum())
                )

            relationship_score = 100.0 if relationship_count > 0 else 60.0
            health_score = round((missing_score + duplicate_score + schema_score + relationship_score) / 4.0, 2)
            grade = self._grade(health_score)

            if health_score < 70:
                recommendation = "Investigate quality issues and enrich metadata"
            elif health_score < 85:
                recommendation = "Monitor for drift and missingness"
            else:
                recommendation = "Dataset is in good health"

            rows.append({
                "Dataset": dataset_name,
                "Health Score": health_score,
                "Missing Score": round(missing_score, 2),
                "Duplicate Score": round(duplicate_score, 2),
                "Schema Score": round(schema_score, 2),
                "Relationship Score": round(relationship_score, 2),
                "Overall Grade": grade,
                "Recommendation": recommendation,
            })

        health_df = pd.DataFrame(rows)
        health_df.to_csv(HEALTH_DIR / "dataset_health.csv", index=False)

        markdown_summary = self._build_markdown_summary(health_df)
        with open(HEALTH_DIR / "dataset_health.md", "w", encoding="utf-8") as file_handle:
            file_handle.write(markdown_summary)

        print("Generated dataset health summary.")

        return health_df

    @staticmethod
    def _build_markdown_summary(health_df: pd.DataFrame) -> str:

        lines = ["# Dataset Health Summary", ""]

        for _, row in health_df.iterrows():
            lines.append(
                f"- {row['Dataset']}: score {row['Health Score']} ({row['Overall Grade']}) - {row['Recommendation']}"
            )

        return "\n".join(lines) + "\n"
