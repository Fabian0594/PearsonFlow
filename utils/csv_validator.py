import pandas as pd
import numpy as np
from typing import List, Dict, Union, Optional
import logging

class ValidatorCSV:
    """Clase para validar archivos CSV y sus datos."""
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Inicializar el validador con un DataFrame.
        
        Args:
            dataframe (pd.DataFrame): DataFrame a validar
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Se requiere un DataFrame de pandas")
        self._dataframe = dataframe.copy()

    def validate_columns(self, required_columns: List[str]) -> bool:
        """
        Validar que el DataFrame contenga las columnas requeridas.
        
        Args:
            required_columns (List[str]): Lista de columnas requeridas
            
        Returns:
            bool: True si la validación es exitosa
            
        Raises:
            ValueError: Si faltan columnas requeridas
        """
        if not required_columns:
            return True
            
        missing_columns = [col for col in required_columns if col not in self._dataframe.columns]
        if missing_columns:
            raise ValueError(f"Faltan las siguientes columnas requeridas: {missing_columns}")
        return True

    def validate_no_nulls(self, columns: List[str] = None) -> Dict[str, int]:
        """
        Validar valores nulos en el DataFrame.
        
        Args:
            columns (List[str], optional): Lista de columnas específicas a validar
            
        Returns:
            Dict[str, int]: Diccionario con el conteo de nulos por columna
        """
        columns = columns or self._dataframe.columns
        null_counts = {col: int(self._dataframe[col].isnull().sum()) 
                      for col in columns if col in self._dataframe.columns}
        
        return null_counts

    def _safe_convert_column(self, column: str, target_type: str, fill_value: Optional[Union[int, float, str]] = None) -> pd.Series:
        """
        Convierte una columna a un tipo específico de manera segura.
        
        Args:
            column (str): Nombre de la columna
            target_type (str): Tipo de dato objetivo
            fill_value: Valor para reemplazar NaN/inf (opcional)
            
        Returns:
            pd.Series: Columna convertida
            
        Raises:
            ValueError: Si la conversión no es posible
        """
        series = self._dataframe[column]
        
        # Manejar valores nulos/infinitos según el tipo objetivo
        if target_type in ['int64', 'float64']:
            if fill_value is not None:
                # Reemplazar valores nulos/infinitos con el valor especificado
                series = series.replace([np.inf, -np.inf], fill_value)
                series = series.fillna(fill_value)
            else:
                # Verificar si hay valores nulos o infinitos
                if series.isnull().any() or np.isinf(series.replace([None], 0)).any():
                    raise ValueError(
                        f"La columna '{column}' contiene valores nulos o infinitos. "
                        "Especifique un valor de reemplazo con fill_value"
                    )
        
        try:
            return series.astype(target_type)
        except Exception as e:
            raise ValueError(f"Error al convertir la columna '{column}': {str(e)}")

    def validate_column_types(self, column_types: Dict[str, str], 
                            fill_values: Dict[str, Union[int, float, str]] = None) -> bool:
        """
        Validar que las columnas tengan los tipos de datos esperados.
        
        Args:
            column_types (Dict[str, str]): Diccionario de columnas y sus tipos esperados
            fill_values (Dict[str, Union[int, float, str]], optional): Valores para reemplazar NaN/inf
            
        Returns:
            bool: True si la validación es exitosa
            
        Raises:
            ValueError: Si una columna no existe o no tiene el tipo esperado
            TypeError: Si los tipos especificados no son válidos
        """
        valid_types = {'int64', 'float64', 'object', 'bool', 'datetime64[ns]'}
        fill_values = fill_values or {}
        
        for column, expected_type in column_types.items():
            if expected_type not in valid_types:
                raise TypeError(f"Tipo de dato no válido: {expected_type}")
                
            if column not in self._dataframe.columns:
                raise ValueError(f"La columna '{column}' no existe en el DataFrame")
                
            current_type = str(self._dataframe[column].dtype)
            if current_type != expected_type:
                try:
                    # Convertir la columna con el valor de reemplazo si se proporciona
                    self._dataframe[column] = self._safe_convert_column(
                        column, 
                        expected_type,
                        fill_values.get(column)
                    )
                    logging.info(
                        f"Columna '{column}' convertida a {expected_type}"
                        + (f" (valores nulos/inf reemplazados con {fill_values[column]})" 
                           if column in fill_values else "")
                    )
                except Exception as e:
                    raise ValueError(str(e))
                    
        return True

    def validate_value_ranges(self, ranges: Dict[str, Dict[str, Union[float, int]]]) -> bool:
        """
        Validar que los valores numéricos estén dentro de rangos específicos.
        
        Args:
            ranges (Dict[str, Dict[str, Union[float, int]]]): Diccionario de columnas y sus rangos
            Ejemplo: {'columna1': {'min': 0, 'max': 100}}
            
        Returns:
            bool: True si la validación es exitosa
            
        Raises:
            ValueError: Si los valores están fuera de rango
        """
        for column, range_values in ranges.items():
            if column not in self._dataframe.columns:
                raise ValueError(f"La columna '{column}' no existe")
                
            if not pd.api.types.is_numeric_dtype(self._dataframe[column]):
                raise TypeError(f"La columna '{column}' no es numérica")
                
            min_val = range_values.get('min', -np.inf)
            max_val = range_values.get('max', np.inf)
            
            # Ignorar valores nulos en la validación de rango
            valid_data = self._dataframe[column].dropna()
            mask = (valid_data < min_val) | (valid_data > max_val)
            invalid_count = mask.sum()
            
            if invalid_count > 0:
                raise ValueError(
                    f"La columna '{column}' tiene {invalid_count} valores fuera del rango "
                    f"[{min_val}, {max_val}]"
                )
                
        return True