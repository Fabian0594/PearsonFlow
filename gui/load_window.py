from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, OptionMenu, Frame, ttk, messagebox
from core.csv_loader import CSVLoader
from utils.csv_validator import ValidatorCSV
import pandas as pd
import logging

class LoadWindow(CSVLoader):
    """Ventana para subir un archivo CSV."""

    TIPOS_DATOS = ["int64", "float64", "object"]

    def __init__(self):
        super().__init__(path="")
        self.root = Tk()
        self.setup_window()
        self.init_variables()
        self.create_widgets()

    def setup_window(self):
        """Configurar la ventana principal."""
        self.root.title("PearsonFlow - Carga de Datos")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        
        # Crear frame principal
        self.main_frame = Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

    def init_variables(self):
        """Inicializar variables."""
        self.message_var = StringVar()
        self.column_type_var = StringVar(value=self.TIPOS_DATOS[0])
        self.widgets = {}

    def create_widgets(self):
        """Crear los elementos de la ventana."""
        # Título
        Label(self.main_frame, text="Carga y Validación de Datos", 
              font=("Arial", 16, "bold")).pack(pady=10)

        # Botón de carga
        self.widgets['upload_button'] = ttk.Button(
            self.main_frame, 
            text="Seleccionar Archivo CSV",
            command=self.load_file
        )
        self.widgets['upload_button'].pack(pady=10)

        # Mensaje de estado
        Label(self.main_frame, textvariable=self.message_var,
              wraplength=400, font=("Arial", 10)).pack(pady=10)

        # Frame para validación
        self.validation_frame = Frame(self.main_frame)
        self.create_validation_widgets()

    def create_validation_widgets(self):
        """Crear widgets para validación."""
        # Guía de tipos
        Label(self.validation_frame, 
              text="Validación de Columnas (Opcional)",
              font=("Arial", 12, "bold")).pack(pady=5)
        
        Label(self.validation_frame,
              text="Si desea validar una columna, ingrese su nombre y tipo de dato esperado",
              font=("Arial", 10)).pack(pady=5)

        # Entrada para nombre de columna
        ttk.Label(self.validation_frame, text="Nombre de la columna:").pack(pady=5)
        self.widgets['column_name'] = ttk.Entry(self.validation_frame)
        self.widgets['column_name'].pack(pady=5)

        # Selector de tipo
        ttk.Label(self.validation_frame, text="Tipo de dato:").pack(pady=5)
        ttk.OptionMenu(self.validation_frame, self.column_type_var, 
                      self.TIPOS_DATOS[0], *self.TIPOS_DATOS).pack(pady=5)

        # Botones
        button_frame = Frame(self.validation_frame)
        button_frame.pack(pady=10)
        
        self.widgets['validate_button'] = ttk.Button(
            button_frame, text="Validar Columna", command=self.validate_column)
        self.widgets['validate_button'].pack(side='left', padx=5)
        
        self.widgets['visualize_button'] = ttk.Button(
            button_frame, text="Visualizar Datos", command=self.advance_to_visualizer)
        self.widgets['visualize_button'].pack(side='left', padx=5)

    def load_file(self):
        """Cargar archivo CSV."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Archivos CSV", "*.csv")],
                title="Seleccionar Archivo CSV"
            )
            
            if not file_path:
                return
                
            self.path = file_path
            pd.read_csv(self.path)  # Validar que se puede leer
            
            self.message_var.set(f"Archivo cargado: {self.path}")
            self.validation_frame.pack(expand=True, fill='both')
            logging.info(f"Archivo cargado exitosamente: {self.path}")
            
        except Exception as e:
            self.message_var.set(f"Error al cargar el archivo: {str(e)}")
            logging.error(f"Error al cargar archivo: {e}")

    def validate_column(self):
        """Validar una columna específica."""
        try:
            column_name = self.widgets['column_name'].get().strip()
            if not column_name:
                raise ValueError("Debe ingresar un nombre de columna")

            df = pd.read_csv(self.path)
            validator = ValidatorCSV(df)
            
            # Verificar valores nulos primero
            null_counts = validator.validate_no_nulls([column_name])
            nulls = null_counts.get(column_name, 0)
            
            if nulls > 0:
                # Si hay valores nulos y el tipo es numérico, preguntar qué hacer
                if self.column_type_var.get() in ['int64', 'float64']:
                    response = messagebox.askyesno(
                        "Valores Nulos Detectados",
                        f"La columna '{column_name}' tiene {nulls} valores nulos. "
                        "¿Desea reemplazarlos con 0?"
                    )
                    
                    if response:
                        # Validar tipo con reemplazo de nulos
                        validator.validate_column_types(
                            {column_name: self.column_type_var.get()},
                            fill_values={column_name: 0}
                        )
                        self.message_var.set(
                            f"Columna '{column_name}' validada correctamente. "
                            f"{nulls} valores nulos reemplazados con 0"
                        )
                    else:
                        self.message_var.set(
                            f"Advertencia: La columna '{column_name}' tiene {nulls} valores nulos"
                        )
                else:
                    # Para tipos no numéricos, solo informar
                    validator.validate_column_types({column_name: self.column_type_var.get()})
                    self.message_var.set(
                        f"Columna '{column_name}' validada. "
                        f"Contiene {nulls} valores nulos"
                    )
            else:
                # Si no hay nulos, validar normalmente
                validator.validate_column_types({column_name: self.column_type_var.get()})
                self.message_var.set(f"Columna '{column_name}' validada correctamente")
            
        except Exception as e:
            self.message_var.set(f"Error de validación: {str(e)}")
            logging.error(f"Error en validación: {e}")
        
        # Habilitar el botón de visualización independientemente del resultado
        self.widgets['visualize_button'].config(state='normal')

    def advance_to_visualizer(self):
        """Avanzar a la visualización."""
        self.root.quit()
        self.root.destroy()
        self.on_visualize_callback(self.path)

    def run(self, on_visualize_callback):
        """Ejecutar la ventana."""
        self.on_visualize_callback = on_visualize_callback
        self.root.mainloop()