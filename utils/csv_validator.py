import pandas as pd
import numpy as np
from typing import List, Dict, Union, Optional, Tuple
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
        self.dataframe = dataframe.copy()

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
            
        missing_columns = [col for col in required_columns if col not in self.dataframe.columns]
        if missing_columns:
            raise ValueError(f"Faltan las siguientes columnas requeridas: {missing_columns}")
        return True

    def validate_no_nulls(self, columns: List[str]) -> Dict[str, int]:
        """
        Validar que las columnas especificadas no tengan valores nulos.
        
        Args:
            columns: Lista de nombres de columnas a validar
            
        Returns:
            Dict[str, int]: Diccionario con el conteo de valores nulos por columna
            
        Raises:
            ValueError: Si alguna columna no existe en el DataFrame
        """
        result = {}
        
        for column in columns:
            if not self.validate_column_exists(column):
                raise ValueError(f"La columna '{column}' no existe en el DataFrame")
            
            null_count = self.dataframe[column].isna().sum()
            result[column] = null_count
            
        return result

    def validate_column_exists(self, column_name: str) -> bool:
        """
        Validar que una columna existe en el DataFrame.
        
        Args:
            column_name: Nombre de la columna a validar
            
        Returns:
            bool: True si la columna existe, False en caso contrario
            
        Raises:
            ValueError: Si el nombre de columna está vacío
        """
        if not column_name:
            raise ValueError("El nombre de columna no puede estar vacío")
            
        return column_name in self.dataframe.columns

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
        series = self.dataframe[column]
        
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
                             fill_values: Optional[Dict[str, Union[int, float, str]]] = None) -> bool:
        """
        Validar y convertir tipos de datos de columnas.
        
        Args:
            column_types: Diccionario con nombres de columnas y sus tipos esperados
            fill_values: Diccionario con valores para reemplazar nulos por columna
            
        Returns:
            bool: True si todas las conversiones fueron exitosas
            
        Raises:
            ValueError: Si alguna columna no existe o no puede convertirse al tipo especificado
        """
        if not column_types:
            return True
            
        # Convertir tipos de columnas en copia para no modificar el original
        df_copy = self.dataframe.copy()
        
        for column, dtype in column_types.items():
            if not self.validate_column_exists(column):
                raise ValueError(f"La columna '{column}' no existe en el DataFrame")
                
            try:
                # Reemplazar valores nulos si es necesario
                if fill_values and column in fill_values:
                    df_copy[column] = df_copy[column].fillna(fill_values[column])
                    
                # Convertir tipo
                df_copy[column] = df_copy[column].astype(dtype)
                
                # Actualizar DataFrame original
                self.dataframe[column] = df_copy[column]
                
            except (ValueError, TypeError) as e:
                problematic_values = self._find_problematic_values(column, dtype)
                error_msg = f"Error al convertir columna '{column}' a {dtype}: {str(e)}"
                if problematic_values:
                    error_msg += f"\nValores problemáticos: {problematic_values}"
                raise ValueError(error_msg)
                
        return True

    def _find_problematic_values(self, column: str, target_type: str) -> List:
        """
        Encontrar valores que no pueden convertirse al tipo especificado.
        
        Args:
            column: Nombre de la columna
            target_type: Tipo de dato objetivo
            
        Returns:
            List: Lista de valores problemáticos (máximo 5)
        """
        problematic = []
        
        # Filtrar valores no nulos
        non_null_values = self.dataframe[column].dropna()
        
        if target_type in ('int64', 'int'):
            # Para enteros, verificar si son números y no tienen parte decimal
            for val in non_null_values.sample(min(10, len(non_null_values))):
                try:
                    float_val = float(val)
                    if float_val != int(float_val):
                        problematic.append(val)
                except:
                    problematic.append(val)
                
                if len(problematic) >= 5:
                    break
                    
        elif target_type in ('float64', 'float'):
            # Para flotantes, verificar si son números
            for val in non_null_values.sample(min(10, len(non_null_values))):
                try:
                    float(val)
                except:
                    problematic.append(val)
                
                if len(problematic) >= 5:
                    break
                    
        # Limitar la cantidad de valores problemáticos mostrados
        return problematic[:5]

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
            if column not in self.dataframe.columns:
                raise ValueError(f"La columna '{column}' no existe")
                
            if not pd.api.types.is_numeric_dtype(self.dataframe[column]):
                raise TypeError(f"La columna '{column}' no es numérica")
                
            min_val = range_values.get('min', -np.inf)
            max_val = range_values.get('max', np.inf)
            
            # Ignorar valores nulos en la validación de rango
            valid_data = self.dataframe[column].dropna()
            mask = (valid_data < min_val) | (valid_data > max_val)
            invalid_count = mask.sum()
            
            if invalid_count > 0:
                raise ValueError(
                    f"La columna '{column}' tiene {invalid_count} valores fuera del rango "
                    f"[{min_val}, {max_val}]"
                )
                
        return True

    def validate_unique_values(self, column: str) -> Tuple[bool, int]:
        """
        Validar que una columna tenga valores únicos.
        
        Args:
            column: Nombre de la columna
            
        Returns:
            Tuple[bool, int]: (Es única, Número de duplicados)
            
        Raises:
            ValueError: Si la columna no existe
        """
        if not self.validate_column_exists(column):
            raise ValueError(f"La columna '{column}' no existe en el DataFrame")
            
        duplicates = self.dataframe[column].duplicated().sum()
        return duplicates == 0, duplicates

    def validate_value_range(self, column: str, min_value: float = None, 
                           max_value: float = None) -> Tuple[bool, List]:
        """
        Validar que los valores de una columna estén dentro de un rango.
        
        Args:
            column: Nombre de la columna
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            
        Returns:
            Tuple[bool, List]: (Todos en rango, Lista de valores fuera de rango)
            
        Raises:
            ValueError: Si la columna no existe o no es numérica
        """
        if not self.validate_column_exists(column):
            raise ValueError(f"La columna '{column}' no existe en el DataFrame")
            
        # Verificar que la columna sea numérica
        if not pd.api.types.is_numeric_dtype(self.dataframe[column]):
            raise ValueError(f"La columna '{column}' no es numérica")
            
        out_of_range = []
        
        # Filtrar por mínimo si se especifica
        if min_value is not None:
            below_min = self.dataframe[self.dataframe[column] < min_value][column]
            if not below_min.empty:
                out_of_range.extend(below_min.head(5).tolist())
                
        # Filtrar por máximo si se especifica
        if max_value is not None:
            above_max = self.dataframe[self.dataframe[column] > max_value][column]
            if not above_max.empty:
                out_of_range.extend(above_max.head(5).tolist())
                
        return len(out_of_range) == 0, out_of_range