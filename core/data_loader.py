from abc import ABC, abstractmethod
import pandas as pd

class DataLoader(ABC):

    def __init__(self, path: str):
        self.path = path
        self._dataframe = None
    
    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass

    def get_data(self) -> pd.DataFrame:
        if self._dataframe is None:
            raise ValueError("No se han cargado datos aún.")
        return self._dataframe


