from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, OptionMenu, Frame, ttk, messagebox, font
from core.csv_loader import CSVLoader
from utils.csv_validator import ValidatorCSV
import pandas as pd
import logging
import os

class LoadWindow(CSVLoader):
    """Ventana para subir un archivo CSV."""
    
    # Paleta de colores
    COLORS = {
        'primary': '#3498db',    # Azul principal
        'secondary': '#2ecc71',  # Verde secundario
        'accent': '#e74c3c',     # Rojo acento
        'text': '#2c3e50',       # Texto oscuro
        'bg_light': '#f8f9fa',   # Fondo claro
        'bg_medium': '#e9ecef'   # Fondo medio
    }
    
    TIPOS_DATOS = ["int64", "float64", "object"]

    def __init__(self):
        super().__init__(path="")
        self.root = Tk()
        self.setup_window()
        self.setup_style()
        self.init_variables()
        self.create_widgets()

    def setup_window(self):
        """Configurar la ventana principal."""
        self.root.title("PearsonFlow - Carga de Datos")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.minsize(600, 500)
        
        # Configurar ícono si está disponible
        try:
            icon_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icon.png")
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconphoto(True, ttk.PhotoImage(file=icon_path))
                    break
        except Exception:
            pass
            
        # Crear frame principal con padding
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(expand=True, fill='both')
        
    def setup_style(self):
        """Configurar estilos personalizados para la interfaz."""
        self.style = ttk.Style()
        
        # Configurar colores y estilos generales
        self.style.configure('TFrame', background=self.COLORS['bg_light'])
        self.style.configure('TLabel', background=self.COLORS['bg_light'], foreground=self.COLORS['text'])
        self.style.configure('TButton', background=self.COLORS['primary'], foreground='white')
        
        # Estilos específicos
        self.style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'), foreground=self.COLORS['primary'])
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 12, 'bold'), foreground=self.COLORS['text'])
        self.style.configure('Info.TLabel', font=('Helvetica', 10, 'italic'), foreground=self.COLORS['text'])
        
        # Configuración para botones de acción
        self.style.configure('Action.TButton', background=self.COLORS['secondary'])
        self.style.configure('Primary.TButton', background=self.COLORS['primary'])
        
        # Configuración general de fuentes
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=10)
        self.root.option_add("*Font", default_font)

    def init_variables(self):
        """Inicializar variables."""
        self.message_var = StringVar()
        self.column_type_var = StringVar(value=self.TIPOS_DATOS[0])
        self.file_path_var = StringVar(value="Ningún archivo seleccionado")
        self.widgets = {}
        self.validation_status = {}

    def create_widgets(self):
        """Crear los elementos de la ventana."""
        # Título principal
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        
        Label(header_frame, text="PearsonFlow", 
              font=("Helvetica", 24, "bold"), foreground=self.COLORS['primary']).pack(pady=(0, 5))
        
        Label(header_frame, text="Carga y Validación de Datos", 
              font=("Helvetica", 16), foreground=self.COLORS['text']).pack(pady=(0, 10))
        
        # Marco para la selección de archivo
        file_frame = ttk.LabelFrame(self.main_frame, text="Selección de Archivo", padding=(15, 10))
        file_frame.pack(fill="x", pady=(0, 15))
        
        # Mostrar ruta del archivo seleccionado
        path_container = ttk.Frame(file_frame)
        path_container.pack(fill="x", pady=10)
        
        ttk.Label(path_container, text="Archivo:").pack(side="left", padx=(0, 10))
        ttk.Label(path_container, textvariable=self.file_path_var, foreground=self.COLORS['accent'], 
                 wraplength=400).pack(side="left", expand=True, fill="x")
        
        # Botón de carga con estilo mejorado
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill="x", pady=10)
        
        self.widgets['upload_button'] = ttk.Button(
            btn_frame, 
            text="Seleccionar Archivo CSV",
            command=self.load_file,
            style="Primary.TButton"
        )
        self.widgets['upload_button'].pack(side="left", padx=(0, 10))
        
        # Mensaje de ayuda
        ttk.Label(file_frame, text="Seleccione un archivo CSV para comenzar la validación.", 
                 style="Info.TLabel").pack(anchor="w", pady=(0, 5))

        # Marco para mensajes de estado
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(status_frame, textvariable=self.message_var, 
               wraplength=600, style="Info.TLabel").pack(fill="x")

        # Frame para validación
        self.validation_frame = ttk.LabelFrame(self.main_frame, text="Validación de Columnas", padding=(15, 10))
        
        self.create_validation_widgets()

    def create_validation_widgets(self):
        """Crear widgets para validación."""
        # Explicación del proceso
        ttk.Label(self.validation_frame, text="Validación Opcional de Columnas", 
                 style="Subtitle.TLabel").pack(anchor="w", pady=(5, 10))
        
        info_text = ("Si desea validar una columna específica, ingrese su nombre y seleccione "
                    "el tipo de dato que debería tener. La validación ayudará a identificar "
                    "posibles problemas en sus datos antes de visualizarlos.")
        
        ttk.Label(self.validation_frame, text=info_text, wraplength=600).pack(anchor="w", pady=(0, 15))

        # Formulario de validación
        form_frame = ttk.Frame(self.validation_frame)
        form_frame.pack(fill="x", pady=10)
        
        # Organizar en grid para mejor alineación
        form_frame.columnconfigure(0, weight=0)
        form_frame.columnconfigure(1, weight=1)
        
        # Entrada para nombre de columna
        ttk.Label(form_frame, text="Nombre de la columna:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.widgets['column_name'] = ttk.Entry(form_frame, width=30)
        self.widgets['column_name'].grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Selector de tipo
        ttk.Label(form_frame, text="Tipo de dato:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        type_combo = ttk.Combobox(form_frame, textvariable=self.column_type_var, values=self.TIPOS_DATOS, width=28, state="readonly")
        type_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        type_combo.current(0)
        
        # Mostrador del estado de validación
        status_frame = ttk.Frame(self.validation_frame)
        status_frame.pack(fill="x", pady=(15, 10))
        
        # Área para mostrar resultados de validación
        self.validation_result_var = StringVar(value="")
        result_label = ttk.Label(status_frame, textvariable=self.validation_result_var, 
                              wraplength=600, foreground=self.COLORS['secondary'])
        result_label.pack(anchor="w", fill="x", pady=5)

        # Botones de acción en un frame con mejor organización
        button_frame = ttk.Frame(self.validation_frame)
        button_frame.pack(fill="x", pady=(15, 10))
        
        # Botón de validar a la izquierda
        self.widgets['validate_button'] = ttk.Button(
            button_frame, text="Validar Columna", 
            command=self.validate_column,
            style="Primary.TButton"
        )
        self.widgets['validate_button'].pack(side="left", padx=5)
        
        # Botón de visualizar a la derecha
        self.widgets['visualize_button'] = ttk.Button(
            button_frame, text="Visualizar Datos", 
            command=self.advance_to_visualizer,
            style="Action.TButton"
        )
        self.widgets['visualize_button'].pack(side="right", padx=5)
        
        # Por defecto deshabilitamos el botón de visualización hasta que se cargue un archivo
        self.widgets['visualize_button'].config(state="disabled")
        
        # Nota informativa
        note_text = "Nota: La validación es opcional. Puede proceder directamente a la visualización después de cargar un archivo."
        ttk.Label(self.validation_frame, text=note_text, style="Info.TLabel").pack(anchor="w", pady=(10, 0))

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
            self.file_path_var.set(os.path.basename(file_path))
            
            # Verificar que el archivo se puede leer
            df = pd.read_csv(self.path) 
            num_rows = len(df)
            num_cols = len(df.columns)
            
            # Mostrar mensaje de éxito
            self.message_var.set(f"✅ Archivo cargado exitosamente: {num_rows} filas, {num_cols} columnas")
            
            # Actualizar la lista de columnas disponibles
            self.update_column_list(df.columns)
            
            # Mostrar el panel de validación
            self.validation_frame.pack(expand=True, fill='both', padx=0, pady=(0, 10))
            
            # Habilitar botón de visualizar
            self.widgets['visualize_button'].config(state="normal")
            
            logging.info(f"Archivo cargado exitosamente: {self.path}")
            
        except pd.errors.EmptyDataError:
            self.message_var.set("❌ Error: El archivo está vacío")
            logging.error("Error al cargar archivo: Archivo vacío")
        except pd.errors.ParserError:
            self.message_var.set("❌ Error: El formato del archivo es inválido")
            logging.error("Error al cargar archivo: Formato inválido")
        except Exception as e:
            self.message_var.set(f"❌ Error al cargar el archivo: {str(e)}")
            logging.error(f"Error al cargar archivo: {e}")
    
    def update_column_list(self, columns):
        """Actualizar la lista de columnas disponibles en la interfaz."""
        self.widgets['column_name'].delete(0, 'end')  # Limpiar entrada actual
        
        # Crear un menú desplegable para seleccionar columnas
        if 'column_menu' in self.widgets:
            self.widgets['column_menu'].destroy()
        
        # Guardar lista de columnas para autocompletar
        self.available_columns = list(columns)

    def validate_column(self):
        """Validar una columna específica."""
        if not self.path:
            self.message_var.set("❌ Error: No hay archivo seleccionado")
            return
            
        try:
            column_name = self.widgets['column_name'].get().strip()
            if not column_name:
                self.validation_result_var.set("Por favor, ingrese un nombre de columna")
                return

            df = pd.read_csv(self.path)
            validator = ValidatorCSV(df)
            
            if not validator.validate_column_exists(column_name):
                self.validation_result_var.set(f"❌ Error: La columna '{column_name}' no existe en el archivo")
                return
            
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
                        self.validation_result_var.set(
                            f"✅ Columna '{column_name}' validada como {self.column_type_var.get()}. "
                            f"{nulls} valores nulos reemplazados con 0"
                        )
                    else:
                        self.validation_result_var.set(
                            f"⚠️ Advertencia: La columna '{column_name}' tiene {nulls} valores nulos"
                        )
                else:
                    # Para tipos no numéricos, solo informar
                    validator.validate_column_types({column_name: self.column_type_var.get()})
                    self.validation_result_var.set(
                        f"✅ Columna '{column_name}' validada como {self.column_type_var.get()}. "
                        f"Contiene {nulls} valores nulos"
                    )
            else:
                # Si no hay nulos, validar normalmente
                validator.validate_column_types({column_name: self.column_type_var.get()})
                self.validation_result_var.set(
                    f"✅ Columna '{column_name}' validada correctamente como {self.column_type_var.get()}"
                )
            
            # Actualizar estado de validación
            self.validation_status[column_name] = True
            
        except Exception as e:
            self.validation_result_var.set(f"❌ Error de validación: {str(e)}")
            logging.error(f"Error en validación: {e}")

    def advance_to_visualizer(self):
        """Avanzar a la visualización."""
        if not self.path:
            self.message_var.set("❌ Error: No hay archivo seleccionado")
            return
            
        self.root.destroy()
        self.on_visualize_callback(self.path)

    def run(self, on_visualize_callback):
        """Ejecutar la ventana."""
        self.on_visualize_callback = on_visualize_callback
        
        # Centrar la ventana en la pantalla
        self.center_window()
        
        self.root.mainloop()
        
    def center_window(self):
        """Centrar la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')