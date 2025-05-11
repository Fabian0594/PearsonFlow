from .data_loader import DataLoader
import pandas as pd
from tkinter import Tk, filedialog

class CSVLoader(DataLoader):
    """ Clase para cargar un archivo CSV de forma grafica """

    def __init__(self, path: str = ""):
        super().__init__(path)
    
    def load(self):
        """ Metodo para cargar el archivo CSV """
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.path = file_path
        else:
            raise ValueError("No se selecciono ningun archivo")

            


    
    
