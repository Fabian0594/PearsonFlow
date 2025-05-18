from tkinter import Tk, messagebox
import pandas as pd
from core.data_visualizer import DataVisualizerGUI

class VisualizerWindow:
    """Ventana para visualizar datos."""

    def __init__(self, file_path: str):
        """
        Iniciar la ventana de visualización.
        Args:
            file_path: Ruta al archivo CSV con los datos a visualizar
        """
        self.file_path = file_path
        self.visualizer = DataVisualizerGUI(file_path)

    def run(self):
        """Ejecutar la ventana de visualización."""
        # La visualización ahora es manejada directamente por DataVisualizerGUI
        # Esta clase se mantiene para compatibilidad con código existente
        pass