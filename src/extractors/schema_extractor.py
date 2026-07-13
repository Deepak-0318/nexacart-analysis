from pathlib import Path
import pandas as pd

from config.settings import (
    RAW_DATA_DIR,
    SCHEMA_DIR,
)

from src.loaders.csv_loader import CSVLoader
from src.loaders.excel_loader import ExcelLoader


class SchemaExtractor:

    def __init__(self):

        SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

        self.loaders = {
            ".csv": CSVLoader(),
            ".xlsx": ExcelLoader(),
            ".xls": ExcelLoader(),
        }

    @staticmethod
    def _memory(series: pd.Series) -> float:

        return round(
            series.memory_usage(deep=True) / 1024 / 1024,
            2,
        )

    def extract(self):

        files = []

        for extension in self.loaders.keys():
            files.extend(
                RAW_DATA_DIR.rglob(f"*{extension}")
            )

        for file_path in sorted(files):

            loader = self.loaders[file_path.suffix]

            datasets = loader.load(file_path)

            for dataset_name, dataframe in datasets.items():

                schema = []

                total_rows = len(dataframe)

                for column in dataframe.columns:

                    series = dataframe[column]

                    unique_count = series.nunique(dropna=True)

                    missing_count = series.isna().sum()

                    sample_values = (
                        series.dropna()
                        .head(5)
                        .tolist()
                    )

                    schema.append({

                        "dataset_name": dataset_name,

                        "column_name": column,

                        "pandas_dtype": str(series.dtype),

                        "nullable": missing_count > 0,

                        "missing_count": int(missing_count),

                        "missing_percentage":
                            round(
                                missing_count
                                / total_rows
                                * 100,
                                2,
                            ),

                        "unique_count": int(unique_count),

                        "unique_percentage":
                            round(
                                unique_count
                                / total_rows
                                * 100,
                                2,
                            ),

                        "duplicate_count":
                            int(
                                total_rows
                                - unique_count
                            ),

                        "memory_usage_mb":
                            self._memory(series),

                        "sample_values":
                            sample_values,
                    })

                schema_df = pd.DataFrame(schema)

                schema_df.to_csv(

                    SCHEMA_DIR /
                    f"{dataset_name}_schema.csv",

                    index=False,
                )

                print(
                    f"Generated schema for {dataset_name}"
                )