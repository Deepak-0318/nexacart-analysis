import json
from pathlib import Path

import pandas as pd

from config.settings import (
    SCHEMA_DIR,
    PRIMARY_KEY_DIR,
)


class PrimaryKeyDetector:

    IDENTIFIER_KEYWORDS = (
        "_id",
        "id",
        "key",
        "uuid",
        "code",
    )

    def __init__(self):

        PRIMARY_KEY_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def _confidence(score: int):

        if score >= 90:
            return "Very High"

        if score >= 75:
            return "High"

        if score >= 50:
            return "Medium"

        return "Low"

    def detect(self):

        candidates = []

        schema_files = sorted(
            SCHEMA_DIR.glob("*_schema.csv")
        )

        for schema_file in schema_files:

            schema = pd.read_csv(schema_file)

            for _, row in schema.iterrows():

                score = 0

                if row["missing_count"] == 0:
                    score += 30

                if row["unique_percentage"] >= 98:
                    score += 40

                column = row["column_name"].lower()

                if any(
                    keyword in column
                    for keyword in self.IDENTIFIER_KEYWORDS
                ):
                    score += 20

                if row["duplicate_count"] <= 0.02 * max(row["unique_count"], 1):
                    score += 10

                candidates.append({

                    "dataset_name": row["dataset_name"],

                    "column_name": row["column_name"],

                    "score": score,

                    "confidence": self._confidence(score),

                    "missing_percentage": row["missing_percentage"],

                    "unique_percentage": row["unique_percentage"],

                })

        candidates_df = pd.DataFrame(candidates)

        candidates_df = candidates_df.sort_values(
            by=[
                "dataset_name",
                "score",
            ],
            ascending=[
                True,
                False,
            ],
        )

        candidates_df.to_csv(
            PRIMARY_KEY_DIR /
            "primary_key_candidates.csv",
            index=False,
        )

        with open(
            PRIMARY_KEY_DIR /
            "primary_key_summary.json",
            "w",
        ) as f:

            json.dump(
                candidates_df.to_dict(
                    orient="records"
                ),
                f,
                indent=4,
            )

        print(
            "Generated primary key candidates."
        )