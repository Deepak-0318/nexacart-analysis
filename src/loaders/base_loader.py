from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path


class BaseLoader(ABC):

    @abstractmethod
    def load(self, file_path: Path) -> dict[str, pd.DataFrame]:
        """
        Returns

        {
            dataset_name : dataframe
        }
        """
        pass