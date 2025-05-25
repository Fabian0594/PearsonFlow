import pandas as pd
from pymongo import MongoClient
from typing import List, Dict, Any, Optional, Tuple, Union
import logging

class MongoDBLoader:
    """
    Cargador especializado para datos de MongoDB con soporte para context managers.
    
    Proporciona funcionalidades para conectar, consultar y manipular datos
    en bases de datos MongoDB, con conversión automática a pandas DataFrame.
    """
    
    def __init__(self, connection_string: Optional[str] = None, db_name: Optional[str] = None):
        """
        Inicializar el cargador de MongoDB con parámetros de conexión.
        
        Args:
            connection_string: URI de conexión a MongoDB (por defecto: mongodb://localhost:27017)
            db_name: Nombre de la base de datos a utilizar
        """
        self.connection_string = connection_string or "mongodb://localhost:27017"
        self.db_name = db_name
        self.client = None  # Cliente de conexión MongoDB
        self.db = None      # Referencia a la base de datos activa
        
    def connect(self, connection_string: Optional[str] = None, db_name: Optional[str] = None) -> bool:
        """
        Establecer conexión con la base de datos MongoDB.
        
        Args:
            connection_string: URI de conexión a MongoDB (opcional)
            db_name: Nombre de la base de datos a usar (opcional)
            
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Actualizar parámetros de conexión si se proporcionan
            if connection_string:
                self.connection_string = connection_string
            if db_name:
                self.db_name = db_name
                
            # Validar que tenemos los datos necesarios para conectar
            if not self.db_name:
                raise ValueError("Se requiere el nombre de la base de datos")
                
            # Cerrar conexión previa si existe para evitar memory leaks
            if self.client:
                self.client.close()
                
            # Establecer nueva conexión con timeout configurado
            logging.info(f"Conectando a MongoDB: {self.db_name}")
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            
            # Seleccionar la base de datos específica
            self.db = self.client[self.db_name]
            
            # Verificar conectividad con comando ping
            self.client.admin.command('ping')
            logging.info("Conexión a MongoDB establecida exitosamente")
            
            return True
            
        except Exception as e:
            logging.error(f"Error al conectar a MongoDB: {str(e)}")
            # Limpiar referencias en caso de error
            self.client = None
            self.db = None
            return False
    
    def list_collections(self) -> List[str]:
        """
        Obtener lista de colecciones disponibles en la base de datos.
        
        Returns:
            List[str]: Lista de nombres de colecciones disponibles
        
        Raises:
            ConnectionError: Si no hay conexión establecida a MongoDB
        """
        if self.db is None:
            raise ConnectionError("No hay conexión establecida a MongoDB")
            
        return self.db.list_collection_names()
    
    def load_collection(self, collection_name: str, query: Optional[Dict[str, Any]] = None, 
                      limit: int = 0, projection: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Cargar datos de una colección MongoDB en un DataFrame de pandas.
        
        Args:
            collection_name: Nombre de la colección a consultar
            query: Filtro de consulta MongoDB (opcional)
            limit: Límite máximo de documentos a cargar (0 = sin límite)
            projection: Campos específicos a incluir o excluir (opcional)
            
        Returns:
            pd.DataFrame: DataFrame con los datos de la colección
            
        Raises:
            ConnectionError: Si no hay conexión establecida a MongoDB
            RuntimeError: Si ocurre un error durante la carga de datos
        """
        if self.db is None:
            raise ConnectionError("No hay conexión establecida a MongoDB")
            
        try:
            # Obtener referencia a la colección
            collection = self.db[collection_name]
            
            # Construir y ejecutar consulta MongoDB
            cursor = collection.find(
                query or {},        # Filtro de consulta (vacío por defecto)
                projection or None  # Proyección de campos
            )
            
            # Aplicar límite de documentos si se especifica
            if limit > 0:
                cursor = cursor.limit(limit)
                
            # Convertir cursor a lista de documentos
            documents = list(cursor)
            
            # Manejar caso de colección vacía
            if not documents:
                logging.info(f"La colección {collection_name} está vacía o no hay documentos que coincidan con la consulta")
                return pd.DataFrame()
                
            # Convertir documentos a DataFrame
            df = pd.DataFrame(documents)
            
            # Remover campo _id específico de MongoDB para limpieza
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
                
            logging.info(f"Cargados {len(df)} documentos de la colección {collection_name}")
            return df
            
        except Exception as e:
            error_msg = f"Error al cargar la colección {collection_name}: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
    
    def save_dataframe_to_collection(self, df: pd.DataFrame, collection_name: str, 
                                   drop_existing: bool = False) -> int:
        """
        Exportar DataFrame de pandas a una colección de MongoDB.
        
        Args:
            df: DataFrame a exportar
            collection_name: Nombre de la colección de destino
            drop_existing: Si True, elimina la colección existente antes de insertar
            
        Returns:
            int: Número de documentos insertados exitosamente
            
        Raises:
            ConnectionError: Si no hay conexión establecida a MongoDB
            RuntimeError: Si ocurre un error durante la exportación
            ValueError: Si el DataFrame está vacío
        """
        if self.db is None:
            raise ConnectionError("No hay conexión establecida a MongoDB")
            
        # Validar que el DataFrame contiene datos
        if df.empty:
            raise ValueError("No se puede guardar un DataFrame vacío")
            
        try:
            # Obtener referencia a la colección
            collection = self.db[collection_name]
            
            # Eliminar colección existente si se solicita
            if drop_existing:
                collection.drop()
                logging.info(f"Colección {collection_name} eliminada")
                
            # Convertir DataFrame a formato de documentos MongoDB
            records = df.to_dict('records')
            
            # Insertar documentos en la colección
            if records:
                result = collection.insert_many(records)
                inserted_count = len(result.inserted_ids)
                logging.info(f"Insertados {inserted_count} documentos en la colección {collection_name}")
                return inserted_count
            else:
                logging.warning(f"No se insertaron documentos en la colección {collection_name}")
                return 0
                
        except Exception as e:
            error_msg = f"Error al guardar en la colección {collection_name}: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Verificar existencia de una colección en la base de datos.
        
        Args:
            collection_name: Nombre de la colección a verificar
            
        Returns:
            bool: True si la colección existe, False en caso contrario
            
        Raises:
            ConnectionError: Si no hay conexión establecida a MongoDB
        """
        if self.db is None:
            raise ConnectionError("No hay conexión establecida a MongoDB")
            
        # Verificar existencia usando lista de colecciones
        return collection_name in self.list_collections()
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Obtener estadísticas detalladas de una colección específica.
        
        Args:
            collection_name: Nombre de la colección a analizar
            
        Returns:
            Dict[str, Any]: Diccionario con estadísticas de la colección (tamaño, índices, etc.)
            
        Raises:
            ConnectionError: Si no hay conexión establecida a MongoDB
            ValueError: Si la colección especificada no existe
        """
        if self.db is None:
            raise ConnectionError("No hay conexión establecida a MongoDB")
            
        # Validar existencia de la colección antes de obtener estadísticas
        if not self.collection_exists(collection_name):
            raise ValueError(f"La colección {collection_name} no existe")
            
        # Ejecutar comando de estadísticas de MongoDB
        return self.db.command("collStats", collection_name)
    
    def close(self) -> None:
        """Cerrar conexión con MongoDB y liberar recursos."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            logging.info("Conexión a MongoDB cerrada correctamente")
            
    def __enter__(self):
        """Soporte para context manager - entrada del bloque 'with'."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Soporte para context manager - salida del bloque 'with' con limpieza automática."""
        self.close() 