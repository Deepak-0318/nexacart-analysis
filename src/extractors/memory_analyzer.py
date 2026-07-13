import json
from typing import Any

import numpy as np
import pandas as pd

from config.settings import (
    MEMORY_DIR,
    RAW_DATA_DIR,
)

from src.loaders.csv_loader import CSVLoader
from src.loaders.excel_loader import ExcelLoader


class MemoryAnalyzer:

    def __init__(self) -> None:

        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

        self.loaders = {
            ".csv": CSVLoader(),
            ".xlsx": ExcelLoader(),
            ".xls": ExcelLoader(),
        }

    @staticmethod
    def _memory_mb(series: pd.Series) -> float:

        return round(series.memory_usage(deep=True) / 1024 / 1024, 4)

    def analyze(self) -> pd.DataFrame:

        rows: list[dict[str, Any]] = []
        dataset_memories: list[float] = []

        files: list[Any] = []
        for extension in self.loaders.keys():
            files.extend(RAW_DATA_DIR.rglob(f"*{extension}"))

        for file_path in sorted(files):
            loader = self.loaders[file_path.suffix]
            datasets = loader.load(file_path)

            for dataset_name, dataframe in datasets.items():
                dataset_memory = round(dataframe.memory_usage(deep=True).sum() / 1024 / 1024, 4)
                dataset_memories.append(dataset_memory)

                column_memories = {
                    column: self._memory_mb(dataframe[column])
                    for column in dataframe.columns
                }
                largest_columns = sorted(column_memories.items(), key=lambda item: item[1], reverse=True)[:5]
                largest_columns_str = ", ".join(
                    f"{name} ({round(size, 2)} MB)" for name, size in largest_columns
                )

                object_memory = round(
                    dataframe.select_dtypes(include=[object]).memory_usage(deep=True).sum() / 1024 / 1024,
                    4,
                )
                numeric_memory = round(
                    dataframe.select_dtypes(include=np.number).memory_usage(deep=True).sum() / 1024 / 1024,
                    4,
                )
                memory_percent = round(dataset_memory / sum(dataset_memories) * 100, 2) if dataset_memories else 0.0

                suggestions: list[str] = []
                if object_memory > 0:
                    suggestions.append("Reduce object-dtype memory with categorical encoding")
                if dataset_memory > 50:
                    suggestions.append("Consider parquet or optimized dtypes for large tables")
                if not suggestions:
                    suggestions.append("No optimization required")

                rows.append({
                    "Dataset": dataset_name,
                    "Dataset Memory (MB)": dataset_memory,
                    "Column Memory (MB)": round(max(column_memories.values(), default=0.0), 4),
                    "Largest Columns": largest_columns_str,
                    "Object Memory (MB)": object_memory,
                    "Numeric Memory (MB)": numeric_memory,
                    "Memory %": memory_percent,
                    "Memory Optimization Suggestions": "; ".join(suggestions),
                })

        memory_df = pd.DataFrame(rows)
        memory_df.to_csv(MEMORY_DIR / "memory_analysis.csv", index=False)

        with open(MEMORY_DIR / "memory_summary.json", "w", encoding="utf-8") as file_handle:
            json.dump(memory_df.to_dict(orient="records"), file_handle, indent=4)

        print("Generated memory analysis.")

        return memory_df
