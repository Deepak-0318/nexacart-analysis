from pathlib import Path
import pandas as pd

from src.loaders.base_loader import BaseLoader


class CSVLoader(BaseLoader):

    def load(self, file_path: Path):

        dataframe = pd.read_csv(file_path)

        return {
            file_path.stem: dataframe
        }