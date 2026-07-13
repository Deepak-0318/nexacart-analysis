from pathlib import Path
import pandas as pd
import numpy as np

from config.settings import (
    RAW_DATA_DIR,
    STATISTICS_DIR,
)

from src.loaders.csv_loader import CSVLoader
from src.loaders.excel_loader import ExcelLoader


class StatisticsExtractor:

    def __init__(self):

        STATISTICS_DIR.mkdir(parents=True, exist_ok=True)

        self.loaders = {
            ".csv": CSVLoader(),
            ".xlsx": ExcelLoader(),
            ".xls": ExcelLoader(),
        }

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

                self._numeric_statistics(
                    dataset_name,
                    dataframe
                )

                self._categorical_statistics(
                    dataset_name,
                    dataframe
                )

                print(
                    f"Generated statistics for {dataset_name}"
                )

    def _numeric_statistics(
        self,
        dataset_name,
        dataframe,
    ):

        numeric_columns = dataframe.select_dtypes(
            include=np.number
        )

        if numeric_columns.empty:
            return

        statistics = []

        for column in numeric_columns.columns:

            series = numeric_columns[column]

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            statistics.append({

                "column_name": column,

                "count": int(series.count()),

                "min": series.min(),

                "max": series.max(),

                "mean": round(series.mean(), 4),

                "median": round(series.median(), 4),

                "std": round(series.std(), 4),

                "variance": round(series.var(), 4),

                "q1": round(q1, 4),

                "q3": round(q3, 4),

                "iqr": round(q3 - q1, 4),

                "skewness": round(series.skew(), 4),

                "kurtosis": round(series.kurt(), 4),

                "zero_count": int((series == 0).sum()),

                "negative_count": int((series < 0).sum()),

            })

        pd.DataFrame(statistics).to_csv(

            STATISTICS_DIR /
            f"{dataset_name}_numeric.csv",

            index=False,
        )

    def _categorical_statistics(
        self,
        dataset_name,
        dataframe,
    ):

        categorical_columns = dataframe.select_dtypes(
            exclude=np.number
        )

        if categorical_columns.empty:
            return

        statistics = []

        for column in categorical_columns.columns:

            series = categorical_columns[column]

            mode = series.mode()

            statistics.append({

                "column_name": column,

                "count": int(series.count()),

                "unique_values": int(series.nunique()),

                "mode": (
                    mode.iloc[0]
                    if not mode.empty
                    else None
                ),

                "mode_frequency": (
                    int(series.value_counts().iloc[0])
                    if not series.value_counts().empty
                    else 0
                ),

                "avg_length": round(
                    series.astype(str)
                    .str.len()
                    .mean(),
                    2,
                ),

                "min_length": int(
                    series.astype(str)
                    .str.len()
                    .min()
                ),

                "max_length": int(
                    series.astype(str)
                    .str.len()
                    .max()
                ),

                "top_10_values": (
                    series.value_counts()
                    .head(10)
                    .to_dict()
                ),

            })

        pd.DataFrame(statistics).to_csv(

            STATISTICS_DIR /
            f"{dataset_name}_categorical.csv",

            index=False,
        )