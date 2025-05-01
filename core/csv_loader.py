from .data_loader import DataLoader
import pandas as pd
from tkinter import Tk, filedialog

class CSVLoader(DataLoader):

    def load(self):
        