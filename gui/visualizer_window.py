from tkinter import Tk, Frame, Label, Button, Scrollbar, VERTICAL, HORIZONTAL, RIGHT, LEFT, Y, X, BOTH, BOTTOM
from tkinter.ttk import Treeview
import pandas as pd

class VisualizerWindow:
    """Ventana para mostrar los datos cargados en una tabla."""

    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
        self.root = Tk()
        self.root.title("Visualizador de Datos")
        self.root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        """Crear los elementos de la ventana."""

        # Frame para la tabla
        table_frame = Frame(self.root)
        table_frame.pack(fill=BOTH, expand=True)

        # Scrollbars
        y_scroll = Scrollbar(table_frame, orient=VERTICAL)
        x_scroll = Scrollbar(table_frame, orient=HORIZONTAL)

        # Tabla
        self.tree = Treeview(
            table_frame,
            columns=list(self.dataframe.columns),
            show="headings",
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )

        # Configurar scrollbars
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        y_scroll.pack(side=RIGHT, fill=Y)
        x_scroll.pack(side=BOTTOM, fill=X)

        # Configurar encabezados de columnas
        for col in self.dataframe.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        # Insertar datos en la tabla
        for _, row in self.dataframe.iterrows():
            self.tree.insert("", "end", values=list(row))

        self.tree.pack(fill=BOTH, expand=True)

        # Botón para cerrar la ventana
        close_button = Button(self.root, text="Cerrar", command=self.close_window)
        close_button.pack(pady=10)

    def close_window(self):
        """Cerrar la ventana de visualización."""
        self.root.quit()  # Detener el bucle principal
        self.root.destroy()  # Cerrar la ventana

    def run(self):
        """Ejecutar la ventana."""
        self.root.mainloop()