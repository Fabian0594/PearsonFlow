import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
from utils.csv_validator import ValidatorCSV
import os
from core.mongo_loader import MongoDBLoader

class DataRepository:
    """
    Repositorio para acceso centralizado a datos.
    Implementa el patrón Repository para abstraer el acceso a diferentes fuentes de datos.
    """
    
    def __init__(self):
        """Inicializar el repositorio de datos."""
        self.cached_data = {}  # Cache de DataFrames indexado por identificador único
        self.validators = {}   # Validadores CSV indexados por identificador
        self.mongo_loader = None  # Instancia reutilizable del cargador MongoDB
        
    def load_csv(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cargar datos desde un archivo CSV con cache automático.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: DataFrame con los datos y metadatos
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            pd.errors.EmptyDataError: Si el archivo está vacío
            pd.errors.ParserError: Si el formato del archivo es inválido
        """
        # Validar existencia del archivo
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo {file_path} no existe")
            
        try:
            # Verificar cache antes de cargar
            if file_path in self.cached_data:
                logging.debug(f"Datos cargados desde cache: {file_path}")
                return self.cached_data[file_path], self._get_metadata(file_path)
                
            # Cargar archivo CSV
            logging.info(f"Cargando archivo CSV: {file_path}")
            df = pd.read_csv(file_path)
            
            # Almacenar en cache para futuras consultas
            self.cached_data[file_path] = df
            
            # Crear validador para este dataset
            self.validators[file_path] = ValidatorCSV(df)
            
            logging.info(f"CSV cargado exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            return df, self._get_metadata(file_path)
            
        except pd.errors.EmptyDataError:
            raise pd.errors.EmptyDataError("El archivo CSV está vacío")
        except pd.errors.ParserError:
            raise pd.errors.ParserError("Formato de archivo CSV inválido")
        except Exception as e:
            logging.error(f"Error al cargar el archivo {file_path}: {str(e)}")
            raise
    
    def load_from_mongodb(self, connection_string: str, db_name: str, collection_name: str,
                        query: Dict[str, Any] = None, limit: int = 0) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cargar datos desde una colección de MongoDB con cache automático.
        
        Args:
            connection_string: Cadena de conexión a MongoDB
            db_name: Nombre de la base de datos
            collection_name: Nombre de la colección
            query: Filtro de consulta MongoDB (opcional)
            limit: Límite de documentos a cargar (0 = sin límite)
            
        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: DataFrame con los datos y metadatos
            
        Raises:
            ConnectionError: Si no se puede establecer conexión con MongoDB
            RuntimeError: Si hay un error al cargar los datos
        """
        # Normalizar nombre de base de datos
        db_name = "PeasonFlow"
        
        # Crear identificador único para cache
        conn_id = f"mongodb://{db_name}/{collection_name}"
        
        # Verificar cache antes de conectar
        if conn_id in self.cached_data:
            logging.debug(f"Datos MongoDB cargados desde cache: {conn_id}")
            return self.cached_data[conn_id], self._get_metadata(conn_id)
            
        try:
            # Inicializar cargador MongoDB si es necesario
            if self.mongo_loader is None:
                self.mongo_loader = MongoDBLoader()
            
            # Establecer conexión
            logging.info(f"Conectando a MongoDB: {db_name}/{collection_name}")
            if not self.mongo_loader.connect(connection_string, db_name):
                raise ConnectionError(f"No se pudo conectar a la base de datos MongoDB: {db_name}")
                
            # Cargar datos de la colección
            df = self.mongo_loader.load_collection(collection_name, query, limit)
            
            # Validar que se cargaron datos
            if df.empty:
                raise RuntimeError(f"La colección {collection_name} está vacía o no se encontraron documentos")
                
            # Almacenar en cache
            self.cached_data[conn_id] = df
            
            # Crear validador para este dataset
            self.validators[conn_id] = ValidatorCSV(df)
            
            logging.info(f"MongoDB cargado exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            return df, self._get_metadata(conn_id)
            
        except Exception as e:
            logging.error(f"Error al cargar datos de MongoDB: {str(e)}")
            raise
    
    def _get_metadata(self, identifier: str) -> Dict[str, Any]:
        """
        Generar metadatos para un dataset cargado.
        
        Args:
            identifier: Identificador del dataset (ruta de archivo o identificador de MongoDB)
            
        Returns:
            Dict[str, Any]: Diccionario con metadatos del dataset
        """
        df = self.cached_data.get(identifier)
        if df is None:
            return {}
            
        # Detectar tipo de fuente por el identificador
        is_mongo = identifier.startswith("mongodb://")
        
        # Metadatos base comunes
        base_metadata = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'numeric_columns': list(df.select_dtypes(include=['int64', 'float64']).columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        if is_mongo:
            # Extraer información específica de MongoDB
            parts = identifier.replace("mongodb://", "").split("/")
            db_name = parts[0] if len(parts) > 0 else "unknown"
            collection_name = parts[1] if len(parts) > 1 else "unknown"
            
            return {
                'source': 'mongodb',
                'database': db_name,
                'collection': collection_name,
                **base_metadata
            }
        else:
            # Metadatos específicos para archivo CSV
            return {
                'source': 'csv',
                'filename': os.path.basename(identifier),
                'filepath': identifier,
                **base_metadata
            }
        
    def validate_column(self, identifier: str, column_name: str, 
                       expected_type: str, fill_null_with: Optional[Any] = None) -> Dict[str, Any]:
        """
        Validar una columna específica de un dataset cargado.
        
        Args:
            identifier: Identificador del dataset
            column_name: Nombre de la columna a validar
            expected_type: Tipo de dato esperado ('int64', 'float64', 'object')
            fill_null_with: Valor para reemplazar nulos (opcional)
            
        Returns:
            Dict[str, Any]: Resultados de la validación con estado y detalles
            
        Raises:
            ValueError: Si la columna no existe o el dataset no está cargado
        """
        # Verificar que el dataset está disponible
        if identifier not in self.validators:
            raise ValueError(f"El dataset '{identifier}' no está cargado")
            
        validator = self.validators[identifier]
        
        # Validar existencia de la columna
        if not validator.validate_column_exists(column_name):
            raise ValueError(f"La columna '{column_name}' no existe en el dataset")
            
        # Contar valores nulos
        null_counts = validator.validate_no_nulls([column_name])
        nulls = null_counts.get(column_name, 0)
        
        # Intentar validación de tipo
        try:
            # Aplicar relleno de nulos si se especifica
            if fill_null_with is not None:
                validator.validate_column_types(
                    {column_name: expected_type},
                    fill_values={column_name: fill_null_with}
                )
                fill_action = f"Se reemplazaron {nulls} valores nulos con {fill_null_with}"
            else:
                validator.validate_column_types({column_name: expected_type})
                fill_action = None
                
            # Retornar resultado exitoso
            return {
                'column': column_name,
                'expected_type': expected_type,
                'actual_type': str(self.cached_data[identifier][column_name].dtype),
                'null_count': nulls,
                'validated': True,
                'fill_action': fill_action
            }
            
        except ValueError as e:
            # Retornar resultado fallido con detalles del error
            return {
                'column': column_name,
                'expected_type': expected_type,
                'actual_type': str(self.cached_data[identifier][column_name].dtype),
                'null_count': nulls,
                'validated': False,
                'error': str(e)
            }
    
    def get_data_for_visualization(self, identifier: str, x_column: Optional[str] = None, 
                                 n_points: int = 50) -> Tuple[Any, pd.DataFrame, str]:
        """
        Preparar datos optimizados para visualización con muestreo automático.
        
        Args:
            identifier: Identificador del dataset (ruta o identificador MongoDB)
            x_column: Columna para el eje X (opcional, usa índice si no se especifica)
            n_points: Número máximo de puntos a mostrar para optimizar rendimiento
            
        Returns:
            Tuple[Any, pd.DataFrame, str]: Valores X, DataFrame con valores Y, nombre de columna X
            
        Raises:
            ValueError: Si no hay columnas numéricas para visualizar o el dataset no existe
        """
        # Determinar tipo de fuente y cargar datos
        is_mongo = identifier.startswith("mongodb://")
        
        if not is_mongo and os.path.exists(identifier):
            # Manejar archivo CSV con recarga automática
            try:
                if not os.path.exists(identifier):
                    raise FileNotFoundError(f"El archivo {identifier} no existe")
                    
                # Recargar datos del archivo para asegurar actualización
                df = pd.read_csv(identifier)
                self.cached_data[identifier] = df.copy()
                
            except Exception as e:
                # Fallback a cache si hay error de lectura
                if identifier not in self.cached_data:
                    raise ValueError(f"Error al cargar el archivo: {str(e)}")
                df = self.cached_data[identifier].copy()
        else:
            # Usar datos de cache para MongoDB u otros identificadores
            if identifier not in self.cached_data:
                raise ValueError(f"No se encontró el dataset '{identifier}' en la caché")
            df = self.cached_data[identifier].copy()
        
        # Aplicar muestreo para optimizar rendimiento
        if n_points <= 0:
            n_points = len(df)
        elif n_points > len(df):
            n_points = len(df)
            
        # Tomar muestra de los últimos n_points registros
        df = df.tail(n_points).copy()
        
        # Configurar columna X para el eje horizontal
        if not x_column:
            # Usar índice secuencial como eje X por defecto
            x_values = range(len(df))
            x_col = "Índice"
        else:
            # Validar existencia de la columna especificada
            if x_column not in df.columns:
                raise ValueError(f"La columna '{x_column}' no existe en el dataset")
                
            # Intentar conversión a datetime para series temporales
            try:
                if df[x_column].dtype == 'object':
                    df[x_column] = pd.to_datetime(df[x_column], errors='ignore')
                x_values = df[x_column]
            except Exception:
                x_values = df[x_column]
            
            x_col = x_column
            
        # Seleccionar columnas numéricas para el eje Y
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        # Excluir columna X si es numérica para evitar redundancia
        if x_col in numeric_cols and x_col != "Índice":
            numeric_cols = numeric_cols.drop(x_col)
            
        # Validar que existan columnas numéricas para graficar
        if len(numeric_cols) == 0:
            raise ValueError("No hay columnas numéricas disponibles para graficar")
            
        return x_values, df[numeric_cols], x_col
        
    def clear_cache(self, identifier: Optional[str] = None):
        """
        Limpiar cache de datos y liberar recursos.
        
        Args:
            identifier: Identificador específico a limpiar (si es None, limpia todo el cache)
        """
        if identifier:
            # Limpiar entrada específica del cache
            if identifier in self.cached_data:
                del self.cached_data[identifier]
                logging.debug(f"Cache eliminado para: {identifier}")
            if identifier in self.validators:
                del self.validators[identifier]
        else:
            # Limpiar todo el cache y cerrar conexiones
            self.cached_data = {}
            self.validators = {}
            logging.info("Cache completo limpiado")
            
            # Cerrar conexión MongoDB si está activa
            if self.mongo_loader:
                self.mongo_loader.close()
                self.mongo_loader = None 