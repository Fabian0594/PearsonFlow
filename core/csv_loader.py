from .data_loader import DataLoader
import pandas as pd
from tkinter import filedialog

class CSVLoader(DataLoader):

    def __init__(self, path):
        super().__init__(path)

    def load(self):
        
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo CSV",
            filetypes=[("CSV files","*.csv")]
        )
        if file_path:
            self.path = file_path
        else:
            raise ValueError("No se selecciono ningun archivo")