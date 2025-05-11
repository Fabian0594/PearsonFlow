from abc import ABC, abstractmethod
import pandas as pd

class DataLoader(ABC):
    """ Clase base para cargar datos """

    def __init__(self, path: str):
        self.path = path
        self._dataframe = None
    
    @abstractmethod
    def load(self) -> pd.DataFrame:
        """ Metodo abstracto para cargar datos """
        pass

    def get_data(self) -> pd.DataFrame:
        """ Metodo para obtener el dataframe cargado """
        
        if self._dataframe is None:
            raise ValueError("No se han cargado datos aun.")
        return self._dataframe

