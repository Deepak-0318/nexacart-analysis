from pathlib import Path
import pandas as pd

from src.loaders.base_loader import BaseLoader


class ExcelLoader(BaseLoader):

    def load(self, file_path: Path):

        excel = pd.ExcelFile(file_path, engine="openpyxl")

        datasets = {}

        for sheet_name in excel.sheet_names:

            datasets[sheet_name] = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                engine="openpyxl"
            )

        return datasets