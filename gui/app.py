from tkinter import Tk, messagebox
import sys
import traceback
import pandas as pd
from gui.load_window import LoadWindow
from gui.visualizer_window import VisualizerWindow
from core.data_visualizer import DataVisualizerGUI

class App:
    """Aplicación principal que coordina las ventanas de carga y visualización."""
    
    def __init__(self):
        """Inicializar la aplicación."""
        # Raíz de Tk oculta para mensajes
        self.root = Tk()
        self.root.withdraw()
        
        # Configurar controladores de excepciones
        sys.excepthook = self.handle_exception
        
        # Iniciar flujo de la aplicación
        self.load_data()
    
    def load_data(self):
        """Mostrar ventana de carga de datos."""
        try:
            load_window = LoadWindow()
            load_window.run(self.on_data_loaded)
        except Exception as e:
            self.show_error(f"Error al iniciar la ventana de carga: {str(e)}")
    
    def on_data_loaded(self, file_path):
        """Manejar evento de datos cargados."""
        try:
            if not file_path:
                self.show_error("No se ha seleccionado ningún archivo.")
                sys.exit(1)
                
            # Verificar que el archivo existe antes de continuar
            try:
                df = pd.read_csv(file_path)
                
                # Verificar que hay datos
                if df.empty:
                    self.show_error("El archivo está vacío.")
                    self.load_data()
                    return
                    
                # Crear y mostrar visualizador
                try:
                    # Pasar el file_path en lugar del DataFrame
                    visualizer_gui = DataVisualizerGUI(file_path)
                    # Iniciar el bucle de la interfaz para mantenerla abierta
                    visualizer_gui.run()
                except Exception as e:
                    self.show_error(f"Error al mostrar el visualizador: {str(e)}")
                    traceback.print_exc()
            
            except pd.errors.EmptyDataError:
                self.show_error("El archivo CSV está vacío.")
                self.load_data()
            except pd.errors.ParserError:
                self.show_error("Error al analizar el archivo CSV. Formato inválido.")
                self.load_data()
            except Exception as e:
                self.show_error(f"Error al cargar los datos: {str(e)}")
                self.load_data()
        except Exception as e:
            self.show_error(f"Error general: {str(e)}")
            self.load_data()
    
    def show_error(self, message):
        """Mostrar mensaje de error."""
        messagebox.showerror("Error", message)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Manejar excepciones no capturadas."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Permitir salir con Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.show_error(f"Ha ocurrido un error inesperado:\n{str(exc_value)}")
        
        # Registrar el error completo en la consola
        print(f"ERROR NO CAPTURADO: {error_msg}", file=sys.stderr)

