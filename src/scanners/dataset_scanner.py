from pathlib import Path
from datetime import datetime
import json
import pandas as pd

from config.settings import (
    RAW_DATA_DIR,
    INVENTORY_DIR,
    SUPPORTED_FILE_TYPES,
)

from src.loaders.csv_loader import CSVLoader
from src.loaders.excel_loader import ExcelLoader


class DatasetScanner:

    def __init__(self):

        INVENTORY_DIR.mkdir(parents=True, exist_ok=True)

        self.loaders = {
            ".csv": CSVLoader(),
            ".xlsx": ExcelLoader(),
            ".xls": ExcelLoader(),
        }

    @staticmethod
    def _file_size(file_path: Path):

        return round(file_path.stat().st_size / 1024 / 1024, 2)

    @staticmethod
    def _last_modified(file_path: Path):

        return datetime.fromtimestamp(
            file_path.stat().st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _memory(df):

        return round(
            df.memory_usage(deep=True).sum() / 1024 / 1024,
            2,
        )

    def scan(self):

        inventory = []

        files = []

        for extension in SUPPORTED_FILE_TYPES:
            files.extend(
                RAW_DATA_DIR.rglob(f"*{extension}")
            )

        for file_path in sorted(files):

            loader = self.loaders[file_path.suffix]

            datasets = loader.load(file_path)

            for dataset_name, dataframe in datasets.items():

                inventory.append({

                    "dataset_name": dataset_name,

                    "source_file": file_path.name,

                    "extension": file_path.suffix,

                    "rows": len(dataframe),

                    "columns": len(dataframe.columns),

                    "file_size_mb": self._file_size(file_path),

                    "memory_usage_mb": self._memory(dataframe),

                    "last_modified": self._last_modified(file_path),

                })

        inventory_df = pd.DataFrame(inventory)

        inventory_df.to_csv(
            INVENTORY_DIR / "inventory.csv",
            index=False,
        )

        inventory_df.to_json(
            INVENTORY_DIR / "inventory.json",
            orient="records",
            indent=4,
        )

        return inventory_df