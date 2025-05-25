from .data_loader import DataLoader
import pandas as pd
from tkinter import Tk, filedialog
import os
import logging
from typing import Optional, Dict, Any, List, Union

class CSVLoader(DataLoader):
    """
    Cargador especializado para archivos CSV con detección automática de formato.
    
    Implementa la interfaz DataLoader proporcionando funcionalidades específicas
    para archivos CSV incluyendo detección de delimitadores y validación de formato.
    """

    def __init__(self, path: str = "", **kwargs):
        """
        Inicializar el cargador de CSV con opciones configurables.
        
        Args:
            path: Ruta al archivo CSV (opcional, se puede seleccionar interactivamente)
            **kwargs: Argumentos adicionales para pandas.read_csv (encoding, sep, etc.)
        """
        super().__init__(path)
        self.csv_options = kwargs  # Opciones de pandas para lectura de CSV
        
        # Metadatos del archivo CSV
        self.metadata = {
            "file_type": "csv",
            "encoding": kwargs.get("encoding", "utf-8"),
            "separator": kwargs.get("sep", ",")
        }
    
    def load(self) -> pd.DataFrame:
        """
        Cargar archivo CSV con validación y manejo de errores robusto.
        
        Si no se especifica ruta, abre diálogo de selección de archivo.
        Detecta automáticamente el formato y aplica validaciones.
        
        Returns:
            pd.DataFrame: DataFrame con los datos del CSV cargado
            
        Raises:
            FileNotFoundError: Si el archivo especificado no existe
            ValueError: Si no se selecciona archivo o hay errores de formato
        """
        # Seleccionar archivo interactivamente si no se especificó ruta
        if not self.path:
            self._select_file_dialog()
            
        # Validar existencia del archivo
        if not os.path.exists(self.path):
            error_msg = f"El archivo no existe: {self.path}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        try:
            # Cargar CSV con pandas aplicando opciones configuradas
            logging.info(f"Cargando archivo CSV: {self.path}")
            df = pd.read_csv(self.path, **self.csv_options)
            
            # Actualizar metadatos con información del archivo cargado
            self.metadata.update({
                "file_path": self.path,
                "file_name": os.path.basename(self.path),
                "file_size": os.path.getsize(self.path),
                "rows": len(df),
                "columns": len(df.columns)
            })
            
            # Almacenar DataFrame y retornar
            self._dataframe = df
            logging.info(f"CSV cargado exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            return df
            
        except pd.errors.EmptyDataError:
            error_msg = f"El archivo CSV está vacío: {self.path}"
            logging.error(error_msg)
            raise ValueError(error_msg)
            
        except pd.errors.ParserError as e:
            error_msg = f"Error al analizar el archivo CSV. Formato inválido: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = f"Error al cargar el archivo CSV: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
    
    def _select_file_dialog(self) -> None:
        """
        Mostrar diálogo de selección de archivo CSV.
        
        Utiliza tkinter para mostrar un diálogo nativo del sistema operativo
        con filtros específicos para archivos CSV.
        
        Raises:
            ValueError: Si el usuario cancela la selección
        """
        # Crear ventana temporal de Tkinter
        root = Tk()
        root.withdraw()  # Ocultar ventana principal
        
        # Mostrar diálogo de selección con filtros apropiados
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        root.destroy()  # Limpiar recursos de Tkinter
        
        # Procesar resultado de la selección
        if file_path:
            self.path = file_path
            logging.info(f"Archivo CSV seleccionado: {file_path}")
        else:
            error_msg = "No se seleccionó ningún archivo"
            logging.warning(error_msg)
            raise ValueError(error_msg)
    
    def save_to_csv(self, output_path: Optional[str] = None, **kwargs) -> str:
        """
        Exportar DataFrame actual a archivo CSV.
        
        Args:
            output_path: Ruta de destino (por defecto sobreescribe el archivo original)
            **kwargs: Argumentos adicionales para pandas.to_csv
            
        Returns:
            str: Ruta del archivo guardado
            
        Raises:
            ValueError: Si no hay datos cargados o error en la escritura
        """
        # Validar que hay datos para guardar
        if self._dataframe is None:
            raise ValueError("No hay datos para guardar")
            
        # Determinar ruta de destino
        save_path = output_path or self.path
        
        if not save_path:
            raise ValueError("No se ha especificado una ruta para guardar el archivo")
            
        try:
            # Exportar DataFrame a CSV
            self._dataframe.to_csv(save_path, index=False, **kwargs)
            logging.info(f"Archivo CSV guardado en: {save_path}")
            return save_path
            
        except Exception as e:
            error_msg = f"Error al guardar el archivo CSV: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
    
    def get_column_types(self) -> Dict[str, str]:
        """
        Obtener información de tipos de datos de las columnas.
        
        Returns:
            Dict[str, str]: Mapeo de nombre de columna a tipo de dato
        """
        if self._dataframe is None:
            return {}
            
        return {col: str(dtype) for col, dtype in self._dataframe.dtypes.items()}
    
    def get_preview(self, rows: int = 5) -> pd.DataFrame:
        """
        Generar vista previa de los datos cargados.
        
        Args:
            rows: Número de filas a incluir en la vista previa
            
        Returns:
            pd.DataFrame: Subconjunto de datos para vista previa
        """
        df = self.get_data()
        return df.head(rows)
    
    def detect_delimiter(self, sample_size: int = 1000) -> str:
        """
        Detectar automáticamente el delimitador del archivo CSV.
        
        Analiza una muestra del archivo para determinar el delimitador más probable
        basándose en la frecuencia de caracteres separadores comunes.
        
        Args:
            sample_size: Número de bytes a analizar para la detección
            
        Returns:
            str: Delimitador detectado (coma, punto y coma, tabulación, etc.)
        """
        # Validar que el archivo existe
        if not os.path.exists(self.path):
            return ","  # Delimitador por defecto
            
        try:
            # Leer muestra del archivo
            with open(self.path, 'r', errors='ignore') as f:
                sample = f.read(sample_size)
                
            # Contar frecuencia de delimitadores comunes
            delimiters = {
                ',': sample.count(','),
                ';': sample.count(';'),
                '\t': sample.count('\t'),
                '|': sample.count('|')
            }
            
            # Seleccionar el delimitador más frecuente
            delimiter = max(delimiters, key=delimiters.get)
            self.metadata["separator"] = delimiter
            logging.debug(f"Delimitador detectado: '{delimiter}'")
            return delimiter
            
        except Exception as e:
            # Fallback a delimitador por defecto en caso de error
            logging.warning(f"Error al detectar delimitador: {str(e)}")
            return ","

            


    
    
