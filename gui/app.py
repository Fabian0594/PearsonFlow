from tkinter import Tk
from gui.load_window import LoadWindow
from gui.visualizer_window import VisualizerWindow
import pandas as pd
import sys

class App:
    """Clase principal para conectar las interfaces."""

    def __init__(self):
        self.root = Tk()
        self.root.withdraw()  # Ocultar la ventana principal de Tkinter
        self.run_load_window()

    def run_load_window(self):
        """Ejecutar la ventana de carga."""
        load_window = LoadWindow()
        load_window.run(on_visualize_callback=self.run_visualizer_window)

    def run_visualizer_window(self, path: str):
        """Ejecutar la ventana de visualización."""
        try:
            dataframe = pd.read_csv(path)
            visualizer_window = VisualizerWindow(dataframe)
            visualizer_window.run()
        except ValueError as e:
            print(f"Error al cargar el archivo: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
        finally:
            self.close_app()

    def close_app(self):
        """Cerrar la aplicación."""
        print("Cerrando la aplicación...")
        if self.root:
            self.root.quit()
            self.root.destroy()

