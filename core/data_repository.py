import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
from utils.csv_validator import ValidatorCSV
import os

class DataRepository:
    """
    Repositorio para acceso centralizado a datos.
    Implementa el patrón Repository para abstraer el acceso a diferentes fuentes de datos.
    """
    
    def __init__(self):
        """Inicializar el repositorio de datos."""
        self.cached_data = {}  # Caché de DataFrames por ruta
        self.validators = {}  # Validadores por ruta
        
    def load_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cargar datos desde un archivo CSV.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: DataFrame con los datos y metadatos
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            pd.errors.EmptyDataError: Si el archivo está vacío
            pd.errors.ParserError: Si el formato del archivo es inválido
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo {file_path} no existe")
            
        try:
            # Verificar si ya está en caché
            if file_path in self.cached_data:
                return self.cached_data[file_path], self._get_metadata(file_path)
                
            # Cargar el archivo
            df = pd.read_csv(file_path)
            
            # Guardar en caché
            self.cached_data[file_path] = df
            
            # Crear validador para este dataframe
            self.validators[file_path] = ValidatorCSV(df)
            
            # Retornar dataframe y metadatos
            return df, self._get_metadata(file_path)
            
        except pd.errors.EmptyDataError:
            raise pd.errors.EmptyDataError("El archivo CSV está vacío")
        except pd.errors.ParserError:
            raise pd.errors.ParserError("Formato de archivo CSV inválido")
        except Exception as e:
            logging.error(f"Error al cargar el archivo {file_path}: {str(e)}")
            raise
    
    def _get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Obtener metadatos para un archivo cargado.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Dict[str, Any]: Diccionario con metadatos
        """
        df = self.cached_data.get(file_path)
        if df is None:
            return {}
            
        return {
            'filename': os.path.basename(file_path),
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'numeric_columns': list(df.select_dtypes(include=['int64', 'float64']).columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
    def validate_column(self, file_path: str, column_name: str, 
                       expected_type: str, fill_null_with: Optional[Any] = None) -> Dict[str, Any]:
        """
        Validar una columna específica de un dataset.
        
        Args:
            file_path: Ruta al archivo CSV
            column_name: Nombre de la columna a validar
            expected_type: Tipo de dato esperado
            fill_null_with: Valor para reemplazar nulos (opcional)
            
        Returns:
            Dict[str, Any]: Resultados de la validación
            
        Raises:
            ValueError: Si la columna no existe o no puede convertirse al tipo especificado
        """
        # Asegurar que el archivo está cargado
        if file_path not in self.validators:
            self.load_csv(file_path)
            
        validator = self.validators[file_path]
        
        # Verificar que la columna existe
        if not validator.validate_column_exists(column_name):
            raise ValueError(f"La columna '{column_name}' no existe en el dataset")
            
        # Verificar valores nulos
        null_counts = validator.validate_no_nulls([column_name])
        nulls = null_counts.get(column_name, 0)
        
        # Validar tipo de datos
        try:
            if fill_null_with is not None:
                validator.validate_column_types(
                    {column_name: expected_type},
                    fill_values={column_name: fill_null_with}
                )
                fill_action = f"Se reemplazaron {nulls} valores nulos con {fill_null_with}"
            else:
                validator.validate_column_types({column_name: expected_type})
                fill_action = None
                
            return {
                'column': column_name,
                'expected_type': expected_type,
                'actual_type': str(self.cached_data[file_path][column_name].dtype),
                'null_count': nulls,
                'validated': True,
                'fill_action': fill_action
            }
            
        except ValueError as e:
            return {
                'column': column_name,
                'expected_type': expected_type,
                'actual_type': str(self.cached_data[file_path][column_name].dtype),
                'null_count': nulls,
                'validated': False,
                'error': str(e)
            }
    
    def get_data_for_visualization(self, file_path: str, x_column: Optional[str] = None, 
                                 n_points: int = 50) -> Tuple[Any, pd.DataFrame, str]:
        """
        Preparar datos para visualización.
        
        Args:
            file_path: Ruta al archivo CSV
            x_column: Columna para el eje X (opcional)
            n_points: Número de puntos a mostrar
            
        Returns:
            Tuple[Any, pd.DataFrame, str]: Valores X, DataFrame con valores Y, nombre de columna X
            
        Raises:
            ValueError: Si no hay columnas numéricas para visualizar
        """
        # Leer los datos del archivo directamente para asegurar datos frescos
        try:
            # Verificamos que el archivo exista
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"El archivo {file_path} no existe")
                
            # Leer datos directamente del archivo
            df = pd.read_csv(file_path)
            
            # Actualizar la caché con los nuevos datos
            self.cached_data[file_path] = df.copy()
        except Exception as e:
            # Si hay algún error, intentar usar la caché
            if file_path not in self.cached_data:
                raise ValueError(f"Error al cargar el archivo: {str(e)}")
            df = self.cached_data[file_path].copy()
        
        # Validar que n_points sea válido
        if n_points <= 0:
            n_points = len(df)
        elif n_points > len(df):
            n_points = len(df)
            
        # Tomar los últimos n_points
        df = df.tail(n_points).copy()
        
        # Preparar columna X
        if not x_column:
            # Si no se especifica columna X, usar el índice
            x_values = range(len(df))
            x_col = "Índice"
        else:
            # Verificar que la columna existe
            if x_column not in df.columns:
                raise ValueError(f"La columna '{x_column}' no existe en el dataset")
                
            # Convertir a datetime si es posible
            try:
                if df[x_column].dtype == 'object':  # Solo intentar convertir si es string/object
                    df[x_column] = pd.to_datetime(df[x_column], errors='ignore')
                x_values = df[x_column]
            except Exception:
                x_values = df[x_column]
            
            x_col = x_column
            
        # Obtener columnas numéricas para Y
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if x_col in numeric_cols and x_col != "Índice":
            numeric_cols = numeric_cols.drop(x_col)
            
        if len(numeric_cols) == 0:
            raise ValueError("No hay columnas numéricas disponibles para graficar")
            
        return x_values, df[numeric_cols], x_col
        
    def clear_cache(self, file_path: Optional[str] = None):
        """
        Limpiar la caché de datos.
        
        Args:
            file_path: Ruta específica a limpiar (si es None, se limpia toda la caché)
        """
        if file_path:
            if file_path in self.cached_data:
                del self.cached_data[file_path]
            if file_path in self.validators:
                del self.validators[file_path]
        else:
            self.cached_data = {}
            self.validators = {} 