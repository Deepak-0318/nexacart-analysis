import json
from pathlib import Path
from typing import Any

import pandas as pd

from config.settings import (
    FOREIGN_KEY_DIR,
    PRIMARY_KEY_DIR,
    RELATIONSHIP_DIR,
)


class RelationshipDetector:

    def __init__(self) -> None:

        RELATIONSHIP_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _confidence(score: int) -> str:

        if score >= 90:
            return "Very High"

        if score >= 75:
            return "High"

        if score >= 50:
            return "Medium"

        return "Low"

    @staticmethod
    def _build_adjacency_list(relationship_df: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:

        adjacency: dict[str, list[dict[str, Any]]] = {}

        for _, row in relationship_df.iterrows():

            parent_dataset = str(row["parent_dataset"])

            adjacency.setdefault(parent_dataset, []).append({
                "child_dataset": str(row["child_dataset"]),
                "child_column": str(row["child_column"]),
                "parent_column": str(row["parent_column"]),
                "score": int(row["score"]),
                "confidence": str(row["confidence"]),
            })

        return adjacency

    @staticmethod
    def _build_relationship_matrix(relationship_df: pd.DataFrame) -> pd.DataFrame:

        datasets = sorted(
            set(relationship_df["parent_dataset"].tolist())
            | set(relationship_df["child_dataset"].tolist())
        )

        matrix = pd.DataFrame(
            0,
            index=datasets,
            columns=datasets,
            dtype=int,
        )

        for _, row in relationship_df.iterrows():

            matrix.loc[str(row["parent_dataset"]), str(row["child_dataset"])] += 1

        return matrix

    def detect(self) -> pd.DataFrame:

        pk_df = pd.read_csv(PRIMARY_KEY_DIR / "primary_key_candidates.csv")
        fk_df = pd.read_csv(FOREIGN_KEY_DIR / "foreign_key_candidates.csv")

        filtered_df = fk_df[
            fk_df["confidence"].astype(str).str.lower() != "low"
        ].copy()

        relationship_rows: list[dict[str, Any]] = []

        for _, row in filtered_df.iterrows():

            parent_dataset = str(row["parent_dataset"])
            parent_column = str(row["parent_column"])
            child_dataset = str(row["child_dataset"])
            child_column = str(row["child_column"])
            score = int(row["score"])
            confidence = str(row["confidence"])

            relationship_rows.append({
                "parent_dataset": parent_dataset,
                "parent_column": parent_column,
                "child_dataset": child_dataset,
                "child_column": child_column,
                "score": score,
                "confidence": confidence,
            })

        relationship_df = pd.DataFrame(relationship_rows)

        if not relationship_df.empty:
            relationship_df = relationship_df.sort_values(
                by=["score", "parent_dataset", "child_dataset"],
                ascending=[False, True, True],
            )

        relationship_df.to_csv(
            RELATIONSHIP_DIR / "relationship_graph.csv",
            index=False,
        )

        adjacency_list = self._build_adjacency_list(relationship_df)
        relationship_matrix = self._build_relationship_matrix(relationship_df)

        graph_payload = {
            "relationships": relationship_df.to_dict(orient="records"),
            "adjacency_list": adjacency_list,
            "relationship_matrix": relationship_matrix.to_dict(orient="index"),
        }

        with open(
            RELATIONSHIP_DIR / "relationship_graph.json",
            "w",
            encoding="utf-8",
        ) as file_handle:
            json.dump(graph_payload, file_handle, indent=4)

        relationship_summary = self._build_markdown_summary(relationship_df)

        with open(
            RELATIONSHIP_DIR / "relationship_summary.md",
            "w",
            encoding="utf-8",
        ) as file_handle:
            file_handle.write(relationship_summary)

        print("Generated relationship suggestions.")

        return relationship_df

    @staticmethod
    def _build_markdown_summary(relationship_df: pd.DataFrame) -> str:

        if relationship_df.empty:
            return "# Relationship Summary\n\nNo high-confidence relationships were detected."

        lines = ["# Relationship Summary", ""]

        for _, row in relationship_df.iterrows():
            lines.append(
                f"- {row['parent_dataset']}.{row['parent_column']} -> {row['child_dataset']}.{row['child_column']} "
                f"(score: {row['score']}, confidence: {row['confidence']})"
            )

        return "\n".join(lines) + "\n"
