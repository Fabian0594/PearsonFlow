from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, OptionMenu
from core.csv_loader import CSVLoader
from utils.csv_validator import ValidatorCSV
import pandas as pd

class LoadWindow(CSVLoader):
    """Ventana para subir un archivo CSV."""

    def __init__(self):
        super().__init__(path="")
        self.root = Tk()
        self.root.title("Subir Archivo CSV")
        self.root.geometry("500x400")
        self.message_label = None
        self.validate_button = None
        self.visualize_button = None
        self.guide_label = None
        self.column_name_entry = None
        self.column_type_var = None
        self.create_widgets()

    def create_widgets(self):
        """Crear los elementos de la ventana."""
        # Etiqueta de título
        label = Label(self.root, text="Subir Archivo", font=("Arial", 14))
        label.pack(pady=10)

        # Botón para cargar archivo
        upload_button = Button(self.root, text="Cargar Archivo", command=self.load_file)
        upload_button.pack(pady=10)

        # Etiqueta para mostrar mensajes
        self.message_label = Label(self.root, text="", font=("Arial", 12), fg="green")
        self.message_label.pack(pady=10)

    def load_file(self):
        """Método para cargar el archivo usando un diálogo de selección."""
        try:
            # Abrir diálogo para seleccionar archivo
            self.path = filedialog.askopenfilename(
                filetypes=[("Archivos CSV", "*.csv")],
                title="Seleccionar Archivo CSV"
            )
            if not self.path:
                raise ValueError("No se seleccionó ningún archivo.")

            # Mostrar mensaje de éxito
            self.message_label.config(text=f"Archivo cargado: {self.path}", fg="green")

            # Crear widgets para validar columna si no existen
            self.add_column_validation_widgets()

            # Crear botón para avanzar a la visualización si no existe
            if not self.visualize_button:
                self.visualize_button = Button(self.root, text="Visualizar Datos", command=self.advance_to_visualizer)
                self.visualize_button.pack(pady=10)

        except ValueError as e:
            self.message_label.config(text=f"Error: {e}", fg="red")
        except Exception as e:
            self.message_label.config(text=f"Error inesperado: {e}", fg="red")

    def add_column_validation_widgets(self):
        """Crear widgets para validar una columna específica (solo una vez)."""
        # Mostrar guía de tipos
        if not self.guide_label:
            self.guide_label = Label(
                self.root,
                text="Guía de Tipos: int64, float64, object (texto)",
                font=("Arial", 10),
                fg="blue"
            )
            self.guide_label.pack(pady=5)

        # Entrada para el nombre de la columna
        if not self.column_name_entry:
            Label(self.root, text="Nombre de la columna:", font=("Arial", 12)).pack(pady=5)
            self.column_name_entry = Entry(self.root)
            self.column_name_entry.pack(pady=5)

        # Menú desplegable para seleccionar el tipo de dato
        if not self.column_type_var:
            Label(self.root, text="Tipo de dato esperado:", font=("Arial", 12)).pack(pady=5)
            self.column_type_var = StringVar(self.root)
            self.column_type_var.set("int64")  # Valor por defecto
            column_type_menu = OptionMenu(self.root, self.column_type_var, "int64", "float64", "object")
            column_type_menu.pack(pady=5)

        # Botón para validar la columna
        if not self.validate_button:
            self.validate_button = Button(self.root, text="Validar Columna", command=self.validate_column)
            self.validate_button.pack(pady=10)

    def validate_column(self):
        """Método para validar una columna específica."""
        try:
            dataframe = pd.read_csv(self.path)
            validator = ValidatorCSV(dataframe)

            # Obtener el nombre de la columna y el tipo esperado
            column_name = self.column_name_entry.get()
            column_type = self.column_type_var.get()

            if not column_name:
                raise ValueError("Debe ingresar un nombre de columna.")

            # Validar el tipo de la columna
            validator.validate_column_types({column_name: column_type})

            # Verificar si hay valores nulos en la columna
            if dataframe[column_name].isnull().any():
                self.message_label.config(
                    text=f"Advertencia: La columna '{column_name}' contiene valores nulos.",
                    fg="orange"
                )
            else:
                self.message_label.config(
                    text=f"Columna '{column_name}' validada correctamente.",
                    fg="green"
                )
        except ValueError as e:
            self.message_label.config(text=f"Error de validación: {e}", fg="red")
        except Exception as e:
            self.message_label.config(text=f"Error inesperado: {e}", fg="red")

    def advance_to_visualizer(self):
        """Método para avanzar a la visualización de datos."""
        self.root.quit()  # Detener el bucle principal
        self.root.destroy()  # Cerrar la ventana de carga
        self.on_visualize_callback(self.path)  # Llamar al callback para avanzar

    def run(self, on_visualize_callback):
        """Ejecutar la ventana."""
        self.on_visualize_callback = on_visualize_callback  # Guardar el callback
        self.root.mainloop()