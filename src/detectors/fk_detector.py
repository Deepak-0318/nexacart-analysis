import json

import pandas as pd

from config.settings import (
    RAW_DATA_DIR,
    SCHEMA_DIR,
    PRIMARY_KEY_DIR,
    FOREIGN_KEY_DIR,
)

from src.loaders.csv_loader import CSVLoader
from src.loaders.excel_loader import ExcelLoader


class ForeignKeyDetector:

    def __init__(self):

        FOREIGN_KEY_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.loaders = {
            ".csv": CSVLoader(),
            ".xlsx": ExcelLoader(),
            ".xls": ExcelLoader(),
        }

    @staticmethod
    def _confidence(score):

        if score >= 90:
            return "Very High"

        if score >= 75:
            return "High"

        if score >= 50:
            return "Medium"

        return "Low"

    def detect(self):

        pk = pd.read_csv(
            PRIMARY_KEY_DIR /
            "primary_key_candidates.csv"
        )

        schema_files = list(
            SCHEMA_DIR.glob("*_schema.csv")
        )

        datasets = {}

        for extension in self.loaders.keys():

            for file in RAW_DATA_DIR.rglob(f"*{extension}"):

                datasets.update(
                    self.loaders[
                        file.suffix
                    ].load(file)
                )

        schema = pd.concat(

            [
                pd.read_csv(file)
                for file in schema_files
            ],

            ignore_index=True,

        )

        candidates = []

        pk_candidates = pk[
            pk["confidence"] == "Very High"
        ]

        for _, parent in pk_candidates.iterrows():

            parent_dataset = parent["dataset_name"]

            parent_column = parent["column_name"]

            parent_values = set(

                datasets[parent_dataset][
                    parent_column
                ].dropna()

            )

            parent_dtype = schema[
                (schema.dataset_name == parent_dataset)
                &
                (schema.column_name == parent_column)
            ]["pandas_dtype"].iloc[0]

            for dataset_name, dataframe in datasets.items():

                if dataset_name == parent_dataset:
                    continue

                for column in dataframe.columns:

                    score = 0

                    if column == parent_column:
                        score += 30

                    dtype = str(
                        dataframe[column].dtype
                    )

                    if dtype == parent_dtype:
                        score += 20

                    score += 30

                    child_values = set(
                        dataframe[column]
                        .dropna()
                    )

                    if len(parent_values):

                        overlap = len(

                            child_values &
                            parent_values

                        ) / len(child_values)

                    else:

                        overlap = 0

                    if overlap >= 0.9:
                        score += 20

                    candidates.append({

                        "parent_dataset":
                            parent_dataset,

                        "parent_column":
                            parent_column,

                        "child_dataset":
                            dataset_name,

                        "child_column":
                            column,

                        "overlap":
                            round(
                                overlap,
                                3,
                            ),

                        "score":
                            score,

                        "confidence":
                            self._confidence(
                                score
                            ),

                    })

        df = pd.DataFrame(
            candidates
        ).sort_values(

            by="score",

            ascending=False,

        )

        if not df.empty:
            filtered_df = df[
                df["confidence"].isin(["High", "Very High"])
            ].copy()
            debug_df = df[
                df["confidence"].isin(["Medium", "Low"])
            ].copy()
        else:
            filtered_df = df.copy()
            debug_df = df.copy()

        filtered_df.to_csv(

            FOREIGN_KEY_DIR /
            "foreign_key_candidates.csv",

            index=False,

        )

        debug_df.to_csv(

            FOREIGN_KEY_DIR /
            "foreign_key_candidates_debug.csv",

            index=False,

        )

        with open(

            FOREIGN_KEY_DIR /
            "foreign_key_summary.json",

            "w",

        ) as f:

            json.dump(

                filtered_df.to_dict(
                    orient="records"
                ),

                f,

                indent=4,

            )

        print(
            "Generated foreign key candidates."
        )