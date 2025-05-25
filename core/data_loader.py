from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any, Union
import logging

class DataLoader(ABC):
    """
    Clase base abstracta para cargar datos desde diferentes fuentes usando patrón Template Method.
    
    Define la interfaz común para todos los cargadores de datos y proporciona
    funcionalidad básica compartida. Las clases derivadas deben implementar
    el método load() específico para cada tipo de fuente de datos.
    """

    def __init__(self, path: str = ""):
        """
        Inicializar el cargador de datos con configuración base.
        
        Args:
            path: Ruta o identificador de la fuente de datos
        """
        self.path = path
        self._dataframe: Optional[pd.DataFrame] = None  # Cache del DataFrame cargado
        self.metadata: Dict[str, Any] = {}              # Metadatos de la fuente de datos
    
    @abstractmethod
    def load(self) -> pd.DataFrame:
        """
        Método abstracto para cargar datos desde la fuente específica.
        
        Este método debe ser implementado por cada clase derivada
        para manejar el tipo específico de fuente de datos.
        
        Returns:
            pd.DataFrame: DataFrame con los datos cargados
            
        Raises:
            ValueError: Si hay un error al cargar los datos
        """
        pass

    def get_data(self) -> pd.DataFrame:
        """
        Obtener el DataFrame cargado con lazy loading automático.
        
        Si los datos aún no han sido cargados, se ejecuta el método load()
        automáticamente y se almacena el resultado en cache.
        
        Returns:
            pd.DataFrame: DataFrame con los datos
            
        Raises:
            ValueError: Si no se han podido cargar los datos
        """
        # Implementar lazy loading: cargar solo cuando se necesite
        if self._dataframe is None:
            try:
                logging.debug(f"Cargando datos desde: {self.path}")
                self._dataframe = self.load()
            except Exception as e:
                error_msg = f"Error al cargar los datos: {str(e)}"
                logging.error(error_msg)
                raise ValueError(error_msg)
                
        return self._dataframe
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Obtener metadatos de la fuente de datos.
        
        Returns:
            Dict[str, Any]: Diccionario con metadatos (tipo, tamaño, columnas, etc.)
        """
        return self.metadata
    
    def set_path(self, path: str) -> None:
        """
        Establecer nueva ruta o identificador de la fuente de datos.
        
        Args:
            path: Nueva ruta o identificador
        """
        self.path = path
        self._dataframe = None  # Invalidar cache para forzar recarga
        logging.debug(f"Ruta actualizada a: {path}")
        
    def get_path(self) -> str:
        """
        Obtener la ruta o identificador actual de la fuente de datos.
        
        Returns:
            str: Ruta o identificador actual
        """
        return self.path
    
    def validate_data(self) -> bool:
        """
        Validar que los datos cargados sean correctos y utilizables.
        
        Realiza validaciones básicas como verificar que el DataFrame
        no esté vacío y contenga datos válidos.
        
        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        try:
            df = self.get_data()
            # Validaciones básicas: DataFrame no vacío y con columnas
            return not df.empty and len(df.columns) > 0
        except Exception as e:
            logging.warning(f"Error en validación de datos: {str(e)}")
            return False
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocesar los datos aplicando transformaciones básicas.
        
        Este método puede ser sobrescrito por las clases derivadas
        para implementar preprocesamiento específico según el tipo de datos.
        
        Returns:
            pd.DataFrame: DataFrame con los datos preprocesados
        """
        df = self.get_data()
        
        # Implementación básica: eliminar filas completamente vacías
        cleaned_df = df.dropna(how='all')
        
        logging.debug(f"Preprocesamiento completado: {len(df)} -> {len(cleaned_df)} filas")
        return cleaned_df

