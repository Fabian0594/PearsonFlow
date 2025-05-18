from tkinter import Tk, messagebox
import pandas as pd
from core.data_visualizer import DataVisualizerGUI

class VisualizerWindow:
    """Ventana para visualizar datos."""

    def __init__(self, dataframe: pd.DataFrame):
        """
        Iniciar la ventana de visualización.
        Args:
            dataframe: DataFrame con los datos a visualizar
        """
        self.dataframe = dataframe
        self.visualizer = DataVisualizerGUI(dataframe)

    def run(self):
        """Ejecutar la ventana de visualización."""
        # La visualización ahora es manejada directamente por DataVisualizerGUI
        # Esta clase se mantiene para compatibilidad con código existente
        pass