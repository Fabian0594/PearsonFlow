from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, OptionMenu, Frame, ttk, messagebox, font
import tkinter as tk
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
    FUENTES_DATOS = ["Archivo CSV", "MongoDB"]

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
        
        # Estilo destacado para botón de acceso directo a MongoDB
        self.style.configure('DirectAccess.TButton', 
                           font=('Helvetica', 12, 'bold'),
                           background='#2980b9', 
                           foreground='white')
        
        # Configuración general de fuentes
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=10)
        self.root.option_add("*Font", default_font)

    def init_variables(self):
        """Inicializar variables."""
        self.message_var = StringVar()
        self.column_type_var = StringVar(value=self.TIPOS_DATOS[0])
        self.file_path_var = StringVar(value="Ningún archivo seleccionado")
        self.data_source_var = StringVar(value=self.FUENTES_DATOS[0])
        self.widgets = {}
        self.validation_status = {}
        self.mongodb_conn_string = StringVar(value="mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/")
        self.mongodb_database = StringVar(value="PeasonFlow")
        self.mongodb_collection = StringVar(value="datos_prueba")
        self.validation_result_var = StringVar()  # Para mostrar resultados de validación
        self.data_identifier = None  # Para guardar la ruta del archivo o el ID de la conexión MongoDB

    def create_widgets(self):
        """Crear los elementos de la ventana."""
        # Título principal
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        
        Label(header_frame, text="PearsonFlow", 
              font=("Helvetica", 24, "bold"), foreground=self.COLORS['primary']).pack(pady=(0, 5))
        
        Label(header_frame, text="Carga y Validación de Datos", 
              font=("Helvetica", 16), foreground=self.COLORS['text']).pack(pady=(0, 10))
        
        # Selector de fuente de datos
        source_frame = ttk.LabelFrame(self.main_frame, text="Fuente de Datos", padding=(15, 10))
        source_frame.pack(fill="x", pady=(0, 15))
        
        source_container = ttk.Frame(source_frame)
        source_container.pack(fill="x", pady=10)
        
        ttk.Label(source_container, text="Seleccione fuente:").pack(side="left", padx=(0, 10))
        
        source_menu = ttk.Combobox(source_container, textvariable=self.data_source_var, 
                              values=self.FUENTES_DATOS, state='readonly', width=20)
        source_menu.pack(side="left", padx=(0, 10))
        source_menu.current(0)
        source_menu.bind("<<ComboboxSelected>>", self.on_source_changed)
        
        # Crear frames para cada fuente de datos
        self.csv_frame = ttk.LabelFrame(self.main_frame, text="Archivo CSV", padding=(15, 10))
        self.mongodb_frame = ttk.LabelFrame(self.main_frame, text="Conexión MongoDB", padding=(15, 10))
        
        # Por defecto, mostrar el frame de CSV
        self.csv_frame.pack(fill="x", pady=(0, 15))
        self.create_csv_widgets()
        self.create_mongodb_widgets()
        
        # Marco para mensajes de estado
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(status_frame, textvariable=self.message_var, 
               wraplength=600, style="Info.TLabel").pack(fill="x")

        # Frame para validación
        self.validation_frame = ttk.LabelFrame(self.main_frame, text="Validación de Columnas", padding=(15, 10))
        
        self.create_validation_widgets()

    def create_csv_widgets(self):
        """Crear widgets para carga de archivos CSV."""
        # Mostrar ruta del archivo seleccionado
        path_container = ttk.Frame(self.csv_frame)
        path_container.pack(fill="x", pady=10)
        
        ttk.Label(path_container, text="Archivo:").pack(side="left", padx=(0, 10))
        ttk.Label(path_container, textvariable=self.file_path_var, foreground=self.COLORS['accent'], 
                 wraplength=400).pack(side="left", expand=True, fill="x")
        
        # Botón de carga con estilo mejorado
        btn_frame = ttk.Frame(self.csv_frame)
        btn_frame.pack(fill="x", pady=10)
        
        self.widgets['upload_button'] = ttk.Button(
            btn_frame, 
            text="Seleccionar Archivo CSV",
            command=self.load_file,
            style="Primary.TButton"
        )
        self.widgets['upload_button'].pack(side="left", padx=(0, 10))
        
        # Mensaje de ayuda
        ttk.Label(self.csv_frame, text="Seleccione un archivo CSV para comenzar la validación.", 
                 style="Info.TLabel").pack(anchor="w", pady=(0, 5))

    def create_mongodb_widgets(self):
        """Crear widgets para conexión a MongoDB."""
        # Cadena de conexión
        conn_frame = ttk.Frame(self.mongodb_frame)
        conn_frame.pack(fill="x", pady=(5, 10))
        
        ttk.Label(conn_frame, text="Cadena de conexión:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        conn_entry = ttk.Entry(conn_frame, width=40, textvariable=self.mongodb_conn_string)
        conn_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Base de datos
        ttk.Label(conn_frame, text="Base de datos:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        db_entry = ttk.Entry(conn_frame, width=30, textvariable=self.mongodb_database)
        db_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Establecer el valor predeterminado correcto
        self.mongodb_database.set("PeasonFlow")
        # Deshabilitar el campo para evitar que el usuario introduzca un valor incorrecto
        db_entry.config(state='readonly')
        
        # Colección
        ttk.Label(conn_frame, text="Colección:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        collection_entry = ttk.Entry(conn_frame, width=30, textvariable=self.mongodb_collection)
        collection_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Botón de conexión
        btn_frame = ttk.Frame(self.mongodb_frame)
        btn_frame.pack(fill="x", pady=10)
        
        self.widgets['connect_mongo_button'] = ttk.Button(
            btn_frame, 
            text="Conectar a MongoDB",
            command=self.connect_to_mongodb,
            style="Primary.TButton"
        )
        self.widgets['connect_mongo_button'].pack(side="left", padx=(0, 10))
        
        # Establecer la URI predeterminada
        self.mongodb_conn_string.set("mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/")
        
        # Mensaje informativo
        ttk.Label(self.mongodb_frame, 
                 text="Ingrese la cadena de conexión a MongoDB Atlas y la colección para cargar datos.", 
                 wraplength=500, 
                 style="Info.TLabel").pack(anchor="w", pady=(0, 5))

    def on_source_changed(self, event):
        """Manejar cambio en la fuente de datos seleccionada."""
        source = self.data_source_var.get()
        
        # Ocultar todos los frames
        self.csv_frame.pack_forget()
        self.mongodb_frame.pack_forget()
        
        # Eliminar el botón de acceso directo si existe
        if hasattr(self, 'direct_access_btn'):
            self.direct_access_btn.pack_forget()
            self.direct_access_btn.destroy()
        
        # Mostrar el frame correspondiente
        if source == "Archivo CSV":
            self.csv_frame.pack(fill="x", pady=(0, 15), after=self.main_frame.winfo_children()[1])
        elif source == "MongoDB":
            self.mongodb_frame.pack(fill="x", pady=(0, 15), after=self.main_frame.winfo_children()[1])
            
            # Crear un marco contenedor para el botón de acceso directo
            direct_btn_frame = ttk.Frame(self.main_frame)
            direct_btn_frame.pack(fill="x", pady=(0, 15), after=self.mongodb_frame)
            
            # Título para destacar la opción de acceso directo
            ttk.Label(direct_btn_frame, 
                text="Acceso Rápido", 
                style="Title.TLabel").pack(pady=(0, 5), anchor="center")
            
            # Crear botón de acceso directo a MongoDB con estilo destacado
            self.direct_access_btn = ttk.Button(
                direct_btn_frame,
                text="Ir a la base de datos de MongoDB",
                command=self.direct_mongodb_access,
                style="DirectAccess.TButton"
            )
            self.direct_access_btn.pack(fill="x", pady=(5, 10), padx=20, ipady=10)
            
            # Mensaje explicativo
            ttk.Label(direct_btn_frame, 
                text="Esta opción te llevará directamente a visualizar los datos de la colección 'datos_prueba'", 
                wraplength=500,
                style="Info.TLabel").pack(pady=(0, 5), anchor="center")

    def direct_mongodb_access(self):
        """Acceder directamente a la base de datos MongoDB y avanzar a la visualización."""
        # Usar valores predeterminados
        conn_string = self.mongodb_conn_string.get()
        db_name = "PeasonFlow"
        collection_name = "datos_prueba"  # Colección predeterminada
        
        try:
            # Mostrar mensaje de carga
            self.message_var.set("Conectando a MongoDB...")
            self.root.update_idletasks()  # Actualizar la interfaz para mostrar el mensaje
            
            # Importar módulos necesarios
            from core.data_repository import DataRepository
            from core.mongo_loader import MongoDBLoader
            
            # Crear loader y verificar conexión
            print(f"Intentando conectar a MongoDB: {conn_string}, {db_name}")
            mongo_loader = MongoDBLoader(conn_string, db_name)
            
            if not mongo_loader.connect():
                messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {db_name}")
                return
                
            # Verificar que la colección existe
            collections = mongo_loader.list_collections()
            if collection_name not in collections:
                # Si la colección predeterminada no existe, intentar usar la primera disponible
                if collections:
                    collection_name = collections[0]
                    print(f"La colección 'datos_prueba' no existe. Usando: {collection_name}")
                else:
                    messagebox.showinfo("Información", "No hay colecciones disponibles en esta base de datos.")
                    return
            
            # Cargar los datos
            print(f"Cargando datos desde: {conn_string}, {db_name}, {collection_name}")
            repo = DataRepository()
            df, metadata = repo.load_from_mongodb(conn_string, db_name, collection_name)
            
            # Crear identificador para la conexión
            self.data_identifier = f"mongodb://{db_name}/{collection_name}"
            print(f"Identificador creado: {self.data_identifier}")
            
            # Avanzar a la visualización
            print(f"Avanzando al visualizador con identificador: {self.data_identifier}")
            self.root.destroy()
            self.on_visualize_callback(self.data_identifier)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al acceder a MongoDB: {str(e)}")
            self.message_var.set(f"Error al acceder a MongoDB: {str(e)}")

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
        self.widgets['validate_button'].config(state="disabled")

    def load_file(self):
        """Cargar archivo CSV."""
        # Abrir diálogo para seleccionar archivo
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if not file_path:
            return  # Cancelado por el usuario
            
        try:
            # Cargar el archivo CSV
            self.set_path(file_path)
            df = self.get_data()
            
            # Verificar que se cargó correctamente
            if df.empty:
                self.message_var.set("El archivo está vacío.")
                return
                
            # Mostrar la ruta del archivo
            self.file_path_var.set(file_path)
            
            # Guardar el identificador para uso posterior
            self.data_identifier = file_path
            
            # Mostrar mensaje de éxito con información sobre el dataset
            self.message_var.set(
                f"Archivo cargado con éxito. "
                f"Filas: {len(df)}, Columnas: {len(df.columns)}"
            )
            
            # Activar botones
            self.widgets['visualize_button'].config(state="normal")
            self.widgets['validate_button'].config(state="normal")
            
            # Mostrar opciones de validación
            self.validation_frame.pack(fill="x", pady=(0, 15))
            
            # Actualizar lista de columnas disponibles
            self.update_column_list(df.columns)
            
        except Exception as e:
            self.message_var.set(f"Error al cargar archivo: {str(e)}")
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
    
    def connect_to_mongodb(self):
        """Conectar a MongoDB y cargar los datos."""
        # Obtener valores
        conn_string = self.mongodb_conn_string.get()
        
        # Usar siempre la base de datos correcta
        db_name = "PeasonFlow"
        self.mongodb_database.set(db_name)  # Actualizar el campo en la interfaz
        
        collection_name = self.mongodb_collection.get()
        
        # Validar entradas
        if not conn_string:
            messagebox.showerror("Error", "La cadena de conexión no puede estar vacía.")
            return
        
        try:
            # Importar dinamicamente para no requerir pymongo si no es necesario
            from core.data_repository import DataRepository
            from core.mongo_loader import MongoDBLoader
            
            # Crear loader para MongoDB
            mongo_loader = MongoDBLoader(conn_string, db_name)
            
            # Intentar conectar
            if not mongo_loader.connect():
                messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {db_name}")
                return
            
            # Obtener lista de colecciones
            collections = mongo_loader.list_collections()
            
            if not collections:
                messagebox.showinfo("Información", "No hay colecciones disponibles en esta base de datos.")
                return
            
            # Mostrar selector de colección si no se especificó una
            if not collection_name:
                self.show_collection_selector(conn_string, db_name, collections)
            else:
                # Verificar que la colección existe
                if collection_name not in collections:
                    messagebox.showerror("Error", f"La colección '{collection_name}' no existe en la base de datos.")
                    return
                    
                # Crear repositorio y cargar datos
                repo = DataRepository()
                df, metadata = repo.load_from_mongodb(conn_string, db_name, collection_name)
                
                # Si llegamos aquí, la carga fue exitosa
                self.on_mongodb_collection_selected(conn_string, db_name, collection_name)
            
        except Exception as e:
            self.message_var.set(f"Error al conectar a MongoDB: {str(e)}")
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{str(e)}")
    
    def show_collection_selector(self, conn_string, db_name, collections):
        """Mostrar ventana emergente para seleccionar colección."""
        # Crear ventana emergente
        select_window = tk.Toplevel(self.root)
        select_window.title(f"Seleccionar Colección - {db_name}")
        select_window.geometry("400x400")
        select_window.transient(self.root)
        select_window.grab_set()
        
        # Centrar ventana
        select_window.update_idletasks()
        width = select_window.winfo_width()
        height = select_window.winfo_height()
        x = (select_window.winfo_screenwidth() // 2) - (width // 2)
        y = (select_window.winfo_screenheight() // 2) - (height // 2)
        select_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Crear marco principal
        main_frame = ttk.Frame(select_window, padding="15")
        main_frame.pack(expand=True, fill='both')
        
        # Título
        ttk.Label(
            main_frame, 
            text=f"Colecciones disponibles en {db_name}",
            style="Title.TLabel"
        ).pack(pady=(0, 15))
        
        # Frame para la lista
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(expand=True, fill='both', pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de colecciones
        listbox = tk.Listbox(
            list_frame, 
            selectmode="single",
            height=10,
            yscrollcommand=scrollbar.set,
            font=("Helvetica", 12)
        )
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Llenar la lista
        for collection in collections:
            listbox.insert(tk.END, collection)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=15)
        
        # Botón de selección
        select_btn = ttk.Button(
            button_frame,
            text="Seleccionar",
            style="Action.TButton",
            command=lambda: self.on_collection_selected(select_window, listbox, conn_string, db_name)
        )
        select_btn.pack(side="right", padx=5)
        
        # Botón de cancelar
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancelar",
            command=select_window.destroy
        )
        cancel_btn.pack(side="right", padx=5)
    
    def on_collection_selected(self, window, listbox, conn_string, db_name):
        """Manejar selección de colección."""
        # Obtener índice seleccionado
        selection = listbox.curselection()
        
        # Verificar que hay selección
        if not selection:
            messagebox.showwarning("Advertencia", "Debe seleccionar una colección.")
            return
        
        # Obtener nombre de la colección seleccionada
        collection_name = listbox.get(selection[0])
        
        # Cerrar ventana de selección
        window.destroy()
        
        # Procesar la selección
        self.on_mongodb_collection_selected(conn_string, db_name, collection_name)
    
    def on_mongodb_collection_selected(self, conn_string, db_name, collection_name):
        """Procesar la colección seleccionada."""
        try:
            # Asegurar que usamos la base de datos correcta
            db_name = "PeasonFlow"
            
            # Debug
            print(f"Procesando selección de colección: {collection_name} en base de datos {db_name}")
            
            # Actualizar el campo de colección
            self.mongodb_collection.set(collection_name)
            
            # Crear un repositorio para cargar los datos
            from core.data_repository import DataRepository
            repo = DataRepository()
            
            # Cargar los datos
            print(f"Intentando cargar datos de MongoDB: {conn_string}, {db_name}, {collection_name}")
            df, metadata = repo.load_from_mongodb(conn_string, db_name, collection_name)
            print(f"Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
            
            # Crear identificador único para la conexión
            self.data_identifier = f"mongodb://{db_name}/{collection_name}"
            print(f"Identifier creado: {self.data_identifier}")
            
            # Mostrar mensaje de éxito con información sobre el dataset
            self.message_var.set(
                f"Conexión exitosa a MongoDB. "
                f"Base de datos: {db_name}, Colección: {collection_name}, "
                f"Filas: {len(df)}, Columnas: {len(df.columns)}"
            )
            
            # Activar botones
            self.widgets['visualize_button'].config(state="normal")
            self.widgets['validate_button'].config(state="normal")
            
            # Mostrar opciones de validación
            self.validation_frame.pack(fill="x", pady=(0, 15))
            
            # Actualizar lista de columnas disponibles
            self.update_column_list(df.columns)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.message_var.set(f"Error al cargar la colección: {str(e)}")
            messagebox.showerror("Error", f"No se pudo cargar la colección:\n{str(e)}")

    def update_column_list(self, columns):
        """Actualizar lista de columnas para validación."""
        # Si hay un combobox para seleccionar columnas, actualizarlo aquí
        pass
        
    def validate_column(self):
        """Validar una columna específica del dataset cargado."""
        # Obtener nombre de columna y tipo esperado
        column_name = self.widgets['column_name'].get()
        expected_type = self.column_type_var.get()
        
        if not column_name:
            messagebox.showerror("Error", "Debe especificar un nombre de columna para validar.")
            return
            
        try:
            # Importar dinámicamente
            from core.data_repository import DataRepository
            
            # Crear un repositorio temporal para la validación
            repo = DataRepository()
            
            # Cargar los datos según la fuente
            if self.data_source_var.get() == "Archivo CSV":
                file_path = self.data_identifier
                df, _ = repo.load_csv(file_path)
                dataset_id = file_path
            else:  # MongoDB
                conn_string = self.mongodb_conn_string.get()
                db_name = self.mongodb_database.get()
                collection_name = self.mongodb_collection.get()
                df, _ = repo.load_from_mongodb(conn_string, db_name, collection_name)
                dataset_id = f"mongodb://{db_name}/{collection_name}"
            
            # Validar la columna
            result = repo.validate_column(dataset_id, column_name, expected_type)
            
            # Mostrar resultado
            if result['validated']:
                self.validation_result_var.set(
                    f"Validación exitosa. La columna '{column_name}' es compatible con el tipo {expected_type}. "
                    f"Valores nulos: {result['null_count']}"
                )
                self.validation_status[column_name] = True
            else:
                self.validation_result_var.set(
                    f"Validación fallida. Error: {result.get('error', 'Tipo incompatible')}. "
                    f"Valores nulos: {result['null_count']}"
                )
                self.validation_status[column_name] = False
                
        except Exception as e:
            self.validation_result_var.set(f"Error en la validación: {str(e)}")
            self.validation_status[column_name] = False
            
    def advance_to_visualizer(self):
        """Pasar datos al visualizador."""
        if not self.data_identifier:
            messagebox.showerror("Error", "No hay datos cargados para visualizar.")
            return
            
        # Imprimir diagnóstico
        print(f"Avanzando al visualizador con identificador: {self.data_identifier}")
        
        # Cerrar ventana actual
        self.root.destroy()
        
        # Llamar a la función de callback para mostrar el visualizador con el archivo/identificador
        self.on_visualize_callback(self.data_identifier)
            
    def run(self, on_visualize_callback):
        """Ejecutar la ventana."""
        self.on_visualize_callback = on_visualize_callback
        self.center_window()
        self.root.mainloop()
        
    def center_window(self):
        """Centrar la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))