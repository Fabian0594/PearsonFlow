import tkinter as tk
from tkinter import messagebox
import sys
import traceback
import pandas as pd
import logging
import os
from typing import Optional, Callable, Dict, Any, Union
from gui.load_window import LoadWindow
from gui.visualizer_window import VisualizerWindow
from core.data_visualizer import DataVisualizerGUI

class App:
    """
    Aplicación principal que coordina las ventanas de carga y visualización.
    Actúa como controlador principal en el patrón MVC.
    """
    
    # Constantes de configuración MongoDB
    # NOTA: En producción, estas credenciales deberían estar en variables de entorno
    MONGODB_CONN_STRING = "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/"
    DB_NAME = "PeasonFlow"
    
    def __init__(self, data_source: Optional[str] = None):
        """
        Inicializar la aplicación principal.
        
        Args:
            data_source: Ruta a archivo CSV o identificador MongoDB para carga automática
        """
        # Configurar ventana raíz oculta para diálogos del sistema
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Configurar manejo global de excepciones
        sys.excepthook = self.handle_exception
        
        # Mantener referencia a la ventana activa para gestión de memoria
        self.active_window = None
        
        # Registrar inicio de la aplicación
        logging.info(f"Iniciando aplicación con fuente de datos: {data_source}")
        
        # Determinar flujo inicial basado en parámetros
        if data_source:
            # Carga directa si se especifica fuente de datos
            self.on_data_loaded(data_source)
        else:
            # Mostrar selector de fuente de datos
            self.load_data()
    
    def load_data(self) -> None:
        """Mostrar ventana de selección y carga de datos."""
        try:
            load_window = LoadWindow()
            self.active_window = load_window
            load_window.run(self.on_data_loaded)
        except Exception as e:
            self.show_error(f"Error al iniciar la ventana de carga: {str(e)}")
            logging.error(f"Error al iniciar la ventana de carga: {str(e)}")
            if logging.getLogger().level <= logging.DEBUG:
                traceback.print_exc()
    
    def on_data_loaded(self, data_source: str) -> None:
        """
        Procesar datos cargados y dirigir al visualizador apropiado.
        
        Args:
            data_source: Ruta del archivo CSV o identificador de conexión MongoDB
        """
        try:
            logging.info(f"Procesando fuente de datos: {data_source}")
            
            # Validar que se proporcionó una fuente de datos
            if not data_source:
                self.show_error("No se ha seleccionado ninguna fuente de datos.")
                return
            
            # Importar repositorio de datos (lazy loading)
            from core.data_repository import DataRepository
            repo = DataRepository()
                
            # Determinar tipo de fuente y procesar apropiadamente
            is_mongodb = isinstance(data_source, str) and data_source.startswith("mongodb://")
            logging.info(f"Tipo de fuente de datos: {'MongoDB' if is_mongodb else 'Archivo'}")
            
            if is_mongodb:
                self._handle_mongodb_source(data_source)
            else:
                self._handle_file_source(data_source)
                    
        except Exception as e:
            self.show_error(f"Error general: {str(e)}")
            logging.error(f"Error general al cargar datos: {str(e)}", exc_info=True)
            self.load_data()  # Volver al selector de datos en caso de error
    
    def _handle_mongodb_source(self, data_source: str) -> None:
        """
        Procesar y validar fuente de datos MongoDB.
        
        Args:
            data_source: Identificador de conexión MongoDB en formato mongodb://db_name/collection_name
        """
        try:
            # Parsear identificador de conexión MongoDB
            parts = data_source.replace("mongodb://", "").split("/")
            
            db_name = parts[0]
            collection_name = parts[1] if len(parts) > 1 else None
            logging.info(f"MongoDB - Base de datos: {db_name}, Colección: {collection_name}")
            
            # Manejar caso donde no se especificó colección
            if not collection_name:
                logging.info("No se especificó colección, mostrando ventana de selección")
                self.load_data_with_mongodb_selected(db_name)
                return
            
            try:
                logging.info(f"Intentando iniciar visualizador con datos de MongoDB: {db_name}/{collection_name}")
                
                # Crear e inicializar visualizador con datos MongoDB
                visualizer_gui = DataVisualizerGUI(data_source)
                self.active_window = visualizer_gui
                visualizer_gui.run()
                    
            except Exception as e:
                self.show_error(f"Error al mostrar el visualizador: {str(e)}")
                logging.error(f"Error al mostrar el visualizador con MongoDB: {str(e)}", exc_info=True)
                self.load_data()  # Fallback al selector de datos
                
        except Exception as e:
            self.show_error(f"Error al procesar fuente MongoDB: {str(e)}")
            logging.error(f"Error al procesar fuente MongoDB: {str(e)}", exc_info=True)
            self.load_data()
    
    def _handle_file_source(self, file_path: str) -> None:
        """
        Procesar y validar fuente de datos basada en archivo.
        
        Args:
            file_path: Ruta al archivo de datos
        """
        try:
            logging.info(f"Procesando archivo: {file_path}")
            
            # Validar existencia del archivo
            if not os.path.exists(file_path):
                self.show_error(f"El archivo no existe: {file_path}")
                logging.error(f"El archivo no existe: {file_path}")
                self.load_data()
                return
                
            # Validar formato y contenido del archivo
            try:
                df = pd.read_csv(file_path)
                
                # Verificar que el archivo contiene datos
                if df.empty:
                    self.show_error("El archivo está vacío.")
                    logging.warning(f"El archivo está vacío: {file_path}")
                    self.load_data()
                    return
                    
                # Inicializar visualizador con archivo validado
                logging.info(f"Iniciando visualizador con archivo: {file_path}")
                visualizer_gui = DataVisualizerGUI(file_path)
                self.active_window = visualizer_gui
                visualizer_gui.run()
            
            except pd.errors.EmptyDataError:
                self.show_error("El archivo CSV está vacío.")
                logging.warning(f"Archivo CSV vacío: {file_path}")
                self.load_data()
            except pd.errors.ParserError as e:
                self.show_error(f"Error al analizar el archivo CSV. Formato inválido: {str(e)}")
                logging.error(f"Error de formato CSV: {str(e)}")
                self.load_data()
            except Exception as e:
                self.show_error(f"Error al cargar los datos: {str(e)}")
                logging.error(f"Error al cargar datos del archivo: {str(e)}", exc_info=True)
                self.load_data()
                
        except Exception as e:
            self.show_error(f"Error al procesar archivo: {str(e)}")
            logging.error(f"Error al procesar archivo: {str(e)}", exc_info=True)
            self.load_data()
    
    def load_data_with_mongodb_selected(self, db_name: str) -> None:
        """
        Mostrar ventana de carga con MongoDB preconfigurado.
        
        Args:
            db_name: Nombre de la base de datos MongoDB a preseleccionar
        """
        try:
            # Crear ventana de carga con configuración específica
            load_window = LoadWindow()
            self.active_window = load_window
            
            # Preconfigurar MongoDB como fuente de datos
            load_window.data_source_var.set("MongoDB")
            load_window.on_source_changed(None)  # Actualizar interfaz para mostrar opciones MongoDB
            
            # Configurar parámetros de conexión MongoDB predeterminados
            load_window.mongodb_conn_string.set(self.MONGODB_CONN_STRING)
            load_window.mongodb_database.set(self.DB_NAME)
            
            # Ejecutar ventana de carga con configuración preestablecida
            load_window.run(self.on_data_loaded)
            
        except Exception as e:
            self.show_error(f"Error al iniciar la ventana de carga: {str(e)}")
            logging.error(f"Error al iniciar ventana de carga con MongoDB: {str(e)}", exc_info=True)
    
    def show_error(self, message: str) -> None:
        """
        Mostrar diálogo de error al usuario.
        
        Args:
            message: Mensaje de error a mostrar
        """
        messagebox.showerror("Error", message)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Manejar excepciones no capturadas globalmente.
        
        Args:
            exc_type: Tipo de excepción
            exc_value: Valor de la excepción
            exc_traceback: Traceback de la excepción
        """
        # Permitir salida normal con Ctrl+C
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        # Formatear y mostrar error al usuario
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.show_error(f"Error inesperado: {str(exc_value)}")
        
        # Registrar error completo en logs para debugging
        logging.critical(f"ERROR NO CAPTURADO: {error_msg}")
    
    def run(self) -> int:
        """
        Iniciar la aplicación y entrar en el bucle principal de eventos.
        
        Returns:
            int: Código de salida (0 para éxito, otro valor para error)
        """
        try:
            # Verificar si ya hay una ventana activa ejecutándose
            if self.active_window:
                return 0  # La ventana ya se está ejecutando
            
            # Iniciar bucle principal de Tkinter
            self.root.mainloop()
            return 0
        except Exception as e:
            logging.critical(f"Error en el bucle principal: {str(e)}", exc_info=True)
            return 1
        
    def cleanup(self) -> None:
        """Limpiar recursos y cerrar conexiones antes de salir."""
        try:
            # Destruir ventana raíz de Tkinter para liberar recursos
            if self.root:
                self.root.destroy()
        except Exception as e:
            logging.error(f"Error al limpiar recursos: {str(e)}")

