import tkinter as tk
from tkinter import ttk, messagebox, font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from core.chart_factory import ChartFactory
from core.data_repository import DataRepository
from core.ai_models import ModelFactory

class DataVisualizerGUI:
    # Paleta de colores
    COLORS = {
        'primary': '#3498db',  # Azul principal
        'secondary': '#2ecc71',  # Verde secundario
        'accent': '#e74c3c',  # Rojo acento
        'text': '#2c3e50',  # Texto oscuro
        'bg_light': '#f8f9fa',  # Fondo claro
        'bg_medium': '#e9ecef',  # Fondo medio
        'chart_colors': ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c', '#34495e', '#d35400']
    }

    def __init__(self, file_path: str):
        """
        Inicializar el visualizador de datos.
        
        Args:
            file_path: Ruta al archivo CSV o identificador de MongoDB a visualizar
        """
        # Inicializar repositorio de datos
        self.data_repository = DataRepository()
        
        # Cargar datos
        try:
            # Determinar si es un archivo CSV o una conexión MongoDB
            if isinstance(file_path, str) and file_path.startswith("mongodb://"):
                # Es una conexión MongoDB
                print(f"DataVisualizerGUI: Cargando datos desde MongoDB: {file_path}")
                
                # Parsear el identificador de MongoDB
                parts = file_path.replace("mongodb://", "").split("/")
                
                # Asegurarnos de usar el nombre correcto de la base de datos
                db_name = parts[0] if len(parts) > 0 else "PeasonFlow"
                collection_name = parts[1] if len(parts) > 1 else "datos_prueba"
                
                # Cargar configuración de MongoDB de forma segura
                try:
                    from config import MONGODB_CONFIG
                    conn_string = MONGODB_CONFIG["connection_string"]
                    print(f"DataVisualizerGUI: Usando configuración segura para MongoDB")
                except ImportError:
                    # Fallback a configuración local si no existe config.py
                    conn_string = "mongodb://localhost:27017/"
                    print(f"DataVisualizerGUI: Usando configuración por defecto (config.py no encontrado)")
                except Exception as e:
                    print(f"DataVisualizerGUI: Error al cargar configuración: {str(e)}")
                    conn_string = "mongodb://localhost:27017/"
                
                # Cargar datos desde MongoDB
                self.dataframe, self.metadata = self.data_repository.load_from_mongodb(conn_string, db_name, collection_name)
            else:
                # Es un archivo CSV
                print(f"DataVisualizerGUI: Cargando datos desde CSV: {file_path}")
                self.dataframe, self.metadata = self.data_repository.load_csv(file_path)
            
            self.file_path = file_path
            print(f"DataVisualizerGUI: Datos cargados correctamente: {len(self.dataframe)} filas, {len(self.dataframe.columns)} columnas")
        except Exception as e:
            print(f"DataVisualizerGUI: Error al cargar los datos: {str(e)}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Error al cargar el archivo: {str(e)}")
        
        # Iniciar la interfaz
        self.setup_window()
        self.setup_style()
        self.create_widgets()
        self.current_canvas = None
        self.current_toolbar = None
        
        # Actualizar el gráfico automáticamente al inicio
        self.root.after(100, self.show_chart)

    def run(self):
        """Ejecutar el bucle principal de la interfaz."""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Error en la ejecución: {str(e)}")

    def setup_style(self):
        """Configurar el estilo general de la aplicación."""
        # Crear un estilo personalizado
        self.style = ttk.Style()
        
        # Configurar colores y estilos para diferentes widgets
        self.style.configure('TFrame', background=self.COLORS['bg_light'])
        self.style.configure('TLabel', background=self.COLORS['bg_light'], foreground=self.COLORS['text'])
        self.style.configure('TButton', background=self.COLORS['primary'], foreground='white')
        
        # Estilo para botones destacados
        self.style.configure('Accent.TButton', background=self.COLORS['secondary'], foreground='white')
        
        # Estilo para etiquetas de título
        self.style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'), foreground=self.COLORS['primary'])
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 12, 'bold'), foreground=self.COLORS['text'])
        
        # Configuración general de fuentes
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=10)
        self.root.option_add("*Font", default_font)

    def setup_window(self):
        """Configurar la ventana principal."""
        self.root = tk.Tk()
        self.root.title("PearsonFlow - Visualizador de Datos")
        self.root.geometry("1280x800")  # Tamaño más grande para mejor visualización
        self.root.minsize(1024, 700)    # Tamaño mínimo
        
        # Intentar establecer un ícono para la aplicación
        try:
            # Buscar en posibles ubicaciones del ícono
            icon_paths = [
                os.path.join(os.path.dirname(sys.argv[0]), "assets", "icon.png"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "icon.png")
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
                    break
        except Exception:
            # Si no se puede establecer el ícono, continuar sin él
            pass
        
        # Crear frame principal con padding
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill="both", expand=True)
        
        # Configurar la expansión del grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # Controles
        self.main_frame.rowconfigure(1, weight=1)  # Pestañas con contenido
        
        # Crear los frames internos
        self.control_frame = ttk.Frame(self.main_frame, padding="5")
        self.control_frame.grid(row=0, column=0, sticky="new", padx=5, pady=5)
        
        # Crear notebook (sistema de pestañas)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Pestaña 1: Visualización básica
        self.basic_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_tab, text="Visualización")
        
        # Pestaña 2: Análisis de IA
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text="Análisis de IA")
        
        # Configurar la pestaña de visualización básica (contenido original)
        self.content_frame = ttk.Frame(self.basic_tab)
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=3)  # El gráfico ocupa más espacio
        self.content_frame.rowconfigure(0, weight=1)
        
        # Frame para la tabla de datos (izquierda)
        self.data_frame = ttk.Frame(self.content_frame)
        self.data_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Frame para el gráfico (derecha)
        self.chart_frame = ttk.Frame(self.content_frame)
        self.chart_frame.grid(row=0, column=1, sticky="nsew")
        
        # Establecer un tamaño mínimo para el chart_frame
        self.chart_frame.config(width=800, height=600)
        self.chart_frame.grid_propagate(False)  # Impedir que el grid cambie el tamaño
        self.chart_frame.pack_propagate(False)  # Impedir que el pack cambie el tamaño
        
        # Configurar el contenido de la pestaña de análisis de IA
        self.setup_ai_analysis_tab()
        
        # Barra de estado
        self.status_frame = ttk.Frame(self.main_frame, relief="sunken")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 0))
        
        self.status_text = tk.StringVar(value="Aplicación iniciada. Listo para visualizar datos.")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_text, anchor="w", padding=(5, 2))
        status_label.pack(side="left", fill="x", expand=True)

    def setup_ai_analysis_tab(self):
        """Configurar el contenido de la pestaña de análisis de IA."""
        # Crear un marco con división izquierda/derecha similar a la pestaña principal
        ai_content = ttk.Frame(self.ai_tab)
        ai_content.pack(fill="both", expand=True)
        ai_content.columnconfigure(0, weight=1)
        ai_content.columnconfigure(1, weight=3)
        ai_content.rowconfigure(0, weight=1)
        
        # Panel izquierdo para controles y parámetros del modelo
        self.ai_controls_frame = ttk.Frame(ai_content)
        self.ai_controls_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Panel derecho para visualización de resultados
        self.ai_chart_frame = ttk.Frame(ai_content)
        self.ai_chart_frame.grid(row=0, column=1, sticky="nsew")
        
        # Establecer un tamaño mínimo para el frame del gráfico de IA
        self.ai_chart_frame.config(width=800, height=600)
        self.ai_chart_frame.grid_propagate(False)  # Impedir que el grid cambie el tamaño
        self.ai_chart_frame.pack_propagate(False)  # Impedir que el pack cambie el tamaño
        
        # Título para la sección de análisis de IA
        ai_title = ttk.Label(self.ai_controls_frame, 
                           text="Análisis con Inteligencia Artificial", 
                           style='Title.TLabel')
        ai_title.pack(anchor="w", padx=5, pady=10)
        
        # Información sobre el modelo seleccionado (inicialmente vacío)
        self.ai_model_info_frame = ttk.LabelFrame(self.ai_controls_frame, 
                                            text="Información del Modelo", 
                                            padding=(10, 5))
        self.ai_model_info_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Label(self.ai_model_info_frame, 
                text="Seleccione un modelo de IA en el panel principal\ny haga clic en 'Aplicar Modelo de IA'",
                wraplength=250).pack(padx=10, pady=10)
        
        # Frame para los resultados del análisis (inicialmente vacío)
        self.ai_results_frame = ttk.LabelFrame(self.ai_controls_frame, 
                                        text="Resultados del Análisis", 
                                        padding=(10, 5))
        self.ai_results_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def create_widgets(self):
        """Crear todos los widgets de la interfaz."""
        self.create_control_widgets()
        self.create_data_table()

    def create_control_widgets(self):
        """Crear widgets de control."""
        # Título
        title = ttk.Label(self.control_frame, text="Visualizador de Datos", style='Title.TLabel')
        title.grid(row=0, column=0, sticky="w", padx=5, pady=5, columnspan=6)
        
        # Configurar columnas
        for i in range(6):
            self.control_frame.columnconfigure(i, weight=1)
        
        # Marco para controles de visualización
        controls = ttk.LabelFrame(self.control_frame, text="Opciones de Visualización", padding=(10, 5))
        controls.grid(row=1, column=0, columnspan=6, sticky="ew", padx=5, pady=10)
        
        # Configurar grid de controles
        for i in range(4):
            controls.columnconfigure(i, weight=1)
        
        # Tipo de gráfico
        ttk.Label(controls, text="Tipo de Gráfico:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Obtener tipos de gráficos disponibles desde la fábrica
        self.chart_types = ChartFactory.get_available_chart_types()
        
        self.chart_combo = ttk.Combobox(controls, width=15)
        self.chart_combo['values'] = self.chart_types
        self.chart_combo.current(0)  # Establecer primer tipo como valor inicial
        self.chart_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Asociar el cambio de selección con un callback
        self.chart_combo.bind('<<ComboboxSelected>>', self.on_chart_type_changed)
        
        # Selector de columna X
        ttk.Label(controls, text="Columna X:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        self.x_combo = ttk.Combobox(controls, width=15)
        self.x_combo['values'] = list(self.dataframe.columns)
        self.x_combo.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Número de puntos a mostrar
        ttk.Label(controls, text="Mostrar últimos N puntos:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.n_points = tk.StringVar(value="50")
        points_entry = ttk.Entry(controls, textvariable=self.n_points, width=10)
        points_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Opciones de visualización
        self.show_grid = tk.BooleanVar(value=True)
        grid_check = ttk.Checkbutton(controls, text="Mostrar Cuadrícula", variable=self.show_grid)
        grid_check.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        self.rotate_labels = tk.BooleanVar(value=True)
        rotate_check = ttk.Checkbutton(controls, text="Rotar Etiquetas", variable=self.rotate_labels)
        rotate_check.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Botón para actualizar gráfico
        self.update_btn = ttk.Button(controls, text="Actualizar Gráfico", 
                                   command=self.show_chart, style='Accent.TButton')
        self.update_btn.grid(row=2, column=3, sticky="e", padx=5, pady=10)
        
        # Sección para modelos de IA
        ai_controls = ttk.LabelFrame(self.control_frame, text="Modelos de Inteligencia Artificial", padding=(10, 5))
        ai_controls.grid(row=2, column=0, columnspan=6, sticky="ew", padx=5, pady=10)
        
        # Configurar grid de controles de IA
        for i in range(4):
            ai_controls.columnconfigure(i, weight=1)
        
        # Obtener modelos de IA disponibles desde el factory
        self.ai_models = ModelFactory.get_available_models()
        self.ai_model_names = [model['name'] for model in self.ai_models]
        
        # Selector de modelo de IA
        ttk.Label(ai_controls, text="Modelo de IA:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.ai_model_combo = ttk.Combobox(ai_controls, width=25)
        self.ai_model_combo['values'] = ["Ninguno"] + self.ai_model_names
        self.ai_model_combo.current(0)  # "Ninguno" como valor inicial
        self.ai_model_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Asociar el cambio de modelo con un callback
        self.ai_model_combo.bind('<<ComboboxSelected>>', self.on_ai_model_changed)
        
        # Selector de columnas mediante checkboxes
        ttk.Label(ai_controls, text="Columnas para análisis:").grid(row=0, column=2, sticky="nw", padx=5, pady=5)
        
        # Frame para los checkboxes de columnas
        self.columns_frame = ttk.Frame(ai_controls)
        self.columns_frame.grid(row=0, column=3, rowspan=2, sticky="nw", padx=5, pady=5)
        
        # Obtener columnas numéricas
        numeric_cols = list(self.dataframe.select_dtypes(include=['int64', 'float64']).columns)
        
        # Crear el gestor de checkboxes con un callback que actualiza el estado de la UI
        def on_column_selection_changed(selected_columns):
            if selected_columns:
                self.status_text.set(f"Columnas seleccionadas: {', '.join(selected_columns)}")
                if self.current_ai_model is not None:
                    self.apply_ai_btn.config(state="normal")
            else:
                self.status_text.set("No hay columnas seleccionadas para análisis")
                if self.current_ai_model is not None:
                    self.apply_ai_btn.config(state="disabled")
            print(f"Selección cambiada: {selected_columns}")
        
        # Crear el gestor de checkboxes
        self.checkbox_manager = CheckboxManager(
            self.columns_frame,
            numeric_cols,
            callback=on_column_selection_changed
        )
        
        # Frame para parámetros del modelo (inicialmente vacío)
        self.ai_params_frame = ttk.Frame(ai_controls)
        self.ai_params_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Botón para aplicar el modelo
        self.apply_ai_btn = ttk.Button(ai_controls, text="Aplicar Modelo de IA", 
                                       command=self.apply_ai_model, style='Accent.TButton')
        self.apply_ai_btn.grid(row=2, column=3, sticky="e", padx=5, pady=5)
        
        # Inicialmente, establecer el botón como deshabilitado
        self.apply_ai_btn.config(state="disabled")
        
        # Variable para almacenar la instancia del modelo actual
        self.current_ai_model = None
        self.ai_model_results = None

    def create_data_table(self):
        """Crear tabla de datos con scroll."""
        # Crear un marco para la tabla con etiqueta
        table_container = ttk.LabelFrame(self.data_frame, text="Datos", padding=(5, 5))
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para la tabla con scrollbar
        table_frame = ttk.Frame(table_container)
        table_frame.pack(fill="both", expand=True)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame)
        y_scroll.pack(side="right", fill="y")
        
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        # Tabla con estilo
        self.tree = ttk.Treeview(table_frame, yscrollcommand=y_scroll.set,
                                xscrollcommand=x_scroll.set, style="Treeview")
        self.tree["columns"] = list(self.dataframe.columns)
        self.tree["show"] = "headings"
        
        # Configurar columnas
        for col in self.dataframe.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # Insertar datos (optimizado para conjuntos de datos grandes)
        max_rows = 1000  # Limitar filas para evitar sobrecargas
        df_display = self.dataframe.head(max_rows)
        for _, row in df_display.iterrows():
            self.tree.insert("", "end", values=list(row))
        
        if len(self.dataframe) > max_rows:
            self.tree.insert("", "end", values=[f"... mostrando {max_rows} de {len(self.dataframe)} filas"] + [""] * (len(self.dataframe.columns) - 1))
        
        # Configurar scrollbars
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        self.tree.pack(fill="both", expand=True)
        
        # Información resumen
        stats_frame = ttk.Frame(self.data_frame, padding="5")
        stats_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Mostrar información resumida del DataFrame usando los metadatos
        num_rows = self.metadata['rows']
        num_cols = self.metadata['columns']
        ttk.Label(stats_frame, text=f"Filas: {num_rows} | Columnas: {num_cols}", 
                 style="Subtitle.TLabel").pack(side="left")

    def on_chart_type_changed(self, event):
        """Manejar el evento de cambio de tipo de gráfico."""
        selected_type = self.chart_combo.get()
        self.status_text.set(f"Tipo de gráfico cambiado a: {selected_type}")

    def on_ai_model_changed(self, event):
        """Manejar el cambio de modelo de IA seleccionado."""
        selected_model = self.ai_model_combo.get()
        
        # Limpiar el frame de parámetros
        for widget in self.ai_params_frame.winfo_children():
            widget.destroy()
            
        if selected_model == "Ninguno":
            self.apply_ai_btn.config(state="disabled")
            self.current_ai_model = None
            self.ai_model_results = None  # Limpiar resultados anteriores
            
            # Mostrar mensaje de deselección de modelo
            ttk.Label(self.ai_params_frame, text="No hay modelo de IA seleccionado", 
                    style="Subtitle.TLabel", foreground="#999999").grid(
                row=0, column=0, columnspan=4, sticky="w", padx=5, pady=10)
                
            self.status_text.set("Modelo de IA desactivado")
            
            # Actualizar el estado del botón basado en la selección actual de columnas
            selected_columns = self.checkbox_manager.get_selected()
            if not selected_columns:
                self.apply_ai_btn.config(state="disabled")
            
            return
            
        # Encontrar el modelo seleccionado
        model_info = next((m for m in self.ai_models if m['name'] == selected_model), None)
        if not model_info:
            return
            
        # Crear instancia del modelo
        try:
            self.current_ai_model = ModelFactory.create_model(model_info['id'])
            self.ai_model_results = None  # Limpiar resultados anteriores
            
            # Mostrar estado del modelo para dar mejor feedback
            model_status_frame = ttk.Frame(self.ai_params_frame)
            model_status_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
            
            # Indicador visual del estado del modelo
            model_status = ttk.Label(
                model_status_frame, 
                text="◉ Modelo seleccionado",
                foreground="green",
                style="Subtitle.TLabel"
            )
            model_status.pack(side="left", padx=5)
            
            # Botón para mostrar/ocultar información adicional
            help_btn = ttk.Button(
                model_status_frame, 
                text="?", 
                width=2,
                command=lambda: messagebox.showinfo("Información del Modelo", 
                         self.get_model_help_text(self.current_ai_model.name))
            )
            help_btn.pack(side="right", padx=5)
            
            # Obtener parámetros del modelo
            params = self.current_ai_model.get_parameters()
            
            # Mostrar descripción del modelo
            if hasattr(self.current_ai_model, 'description'):
                desc = self.current_ai_model.description
                ttk.Label(self.ai_params_frame, text=f"Descripción: {desc}",
                         style='Subtitle.TLabel').grid(row=1, column=0, columnspan=4, 
                                                      sticky="w", padx=5, pady=2)
            
            # Crear widgets para los parámetros
            self.param_vars = {}
            row = 2
            for i, (param_name, param_value) in enumerate(params.items()):
                col = i % 2 * 2  # Distribuir en 2 columnas
                if i % 2 == 0 and i > 0:
                    row += 1
                
                ttk.Label(self.ai_params_frame, text=f"{param_name}:").grid(
                    row=row, column=col, sticky="w", padx=5, pady=5)
                
                # Crear variable para el valor del parámetro
                if isinstance(param_value, bool):
                    var = tk.BooleanVar(value=param_value)
                    widget = ttk.Checkbutton(self.ai_params_frame, variable=var)
                elif isinstance(param_value, int) or isinstance(param_value, float):
                    var = tk.StringVar(value=str(param_value))
                    widget = ttk.Entry(self.ai_params_frame, textvariable=var, width=10)
                else:
                    var = tk.StringVar(value=str(param_value))
                    widget = ttk.Entry(self.ai_params_frame, textvariable=var, width=15)
                    
                widget.grid(row=row, column=col+1, sticky="w", padx=5, pady=5)
                self.param_vars[param_name] = (var, type(param_value))
                
            # Mensaje de ayuda corto
            if hasattr(self.current_ai_model, 'name'):
                help_text = self.get_model_help_text(self.current_ai_model.name)
                if help_text:
                    # Mostrar solo la primera línea o un resumen del texto de ayuda
                    short_help = help_text.split('.')[0] + "."
                    ttk.Label(self.ai_params_frame, text=short_help, 
                             wraplength=400, justify="left").grid(
                        row=row+1, column=0, columnspan=4, sticky="w", padx=5, pady=10)
            
            # Actualizar mensaje de estado
            self.status_text.set(f"Modelo {selected_model} seleccionado. Configure los parámetros y seleccione columnas.")
            
            # Actualizar el estado del botón de aplicar basado en la selección actual de columnas
            selected_columns = self.checkbox_manager.get_selected() 
            if selected_columns:
                self.apply_ai_btn.config(state="normal")
            else:
                self.apply_ai_btn.config(state="disabled")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar el modelo: {str(e)}")
            self.apply_ai_btn.config(state="disabled")

    def get_model_help_text(self, model_name):
        """Obtener texto de ayuda para un modelo específico."""
        help_texts = {
            "Pronóstico Lineal": "Predice valores futuros basados en tendencias lineales en los datos históricos. "
                               "Útil para datos con tendencias claras.",
            "Detección de Anomalías": "Identifica valores atípicos en los datos que difieren significativamente "
                                    "del patrón normal. Los puntos marcados en rojo son anomalías.",
            "Agrupamiento (Clustering)": "Agrupa puntos de datos similares. Seleccione al menos 2 columnas numéricas "
                                       "para visualización óptima. Los puntos del mismo color pertenecen al mismo grupo."
        }
        return help_texts.get(model_name, "")

    def apply_ai_model(self):
        """Aplicar el modelo de IA seleccionado a los datos."""
        try:
            if not self.current_ai_model:
                messagebox.showinfo("Información", "Seleccione un modelo de IA primero.")
                return
            
            # Obtener columnas seleccionadas usando el checkbox manager
            selected_columns = self.checkbox_manager.get_selected()
            
            # Debug para verificar cuáles están seleccionadas
            print(f"Aplicando modelo a columnas: {selected_columns}")
            
            if not selected_columns:
                messagebox.showinfo("Información", "Seleccione al menos una columna para análisis.")
                return
            
            # Mostrar las columnas que se utilizarán
            self.status_text.set(f"Utilizando columnas: {', '.join(selected_columns)}")
            self.root.update_idletasks()
            
            # Actualizar parámetros del modelo
            params = {}
            try:
                for param_name, (var, param_type) in self.param_vars.items():
                    if param_type == bool:
                        params[param_name] = var.get()
                    elif param_type == int:
                        params[param_name] = int(var.get())
                    elif param_type == float:
                        params[param_name] = float(var.get())
                    else:
                        params[param_name] = var.get()
            except ValueError as e:
                messagebox.showerror("Error de Parámetro", 
                                    f"Valor inválido para parámetro: {str(e)}\n"
                                    "Por favor verifique que todos los parámetros tengan valores adecuados.")
                return
            
            # Desactivar UI durante el procesamiento
            self.apply_ai_btn.config(state="disabled")
            self.update_btn.config(state="disabled")
            self.root.config(cursor="watch")
            self.root.update_idletasks()
            
            # Crear una barra de progreso temporal en la barra de estado
            progress_var = tk.DoubleVar()
            progress = ttk.Progressbar(self.status_frame, variable=progress_var, length=200, mode='indeterminate')
            progress.pack(side="right", padx=10, pady=2)
            progress.start()
            self.root.update_idletasks()
            
            try:
                # Preparar los datos para el modelo
                self.status_text.set("Preparando datos para análisis...")
                self.root.update_idletasks()
                
                # Seleccionar solo columnas numéricas para evitar errores de tipos
                try:
                    # Obtener columnas seleccionadas y verificar que sean numéricas
                    numeric_cols = []
                    for col in selected_columns:
                        if col in self.dataframe.columns and pd.api.types.is_numeric_dtype(self.dataframe[col]):
                            numeric_cols.append(col)
                        else:
                            print(f"Advertencia: La columna '{col}' no es numérica o no existe. Será ignorada.")
                    
                    if not numeric_cols:
                        messagebox.showerror("Error", 
                                           "No se han seleccionado columnas numéricas válidas. " +
                                           "Los modelos de IA requieren datos numéricos.")
                        progress.destroy()
                        return
                        
                    # Indicar las columnas que realmente se usarán
                    if len(numeric_cols) < len(selected_columns):
                        messagebox.showwarning("Advertencia", 
                                            f"Solo se utilizarán {len(numeric_cols)} columnas numéricas de las {len(selected_columns)} seleccionadas.")
                    
                    # Usar solo las columnas numéricas para el modelo
                    model_data = self.dataframe[numeric_cols].copy()
                    
                    # Eliminar filas con valores NaN
                    original_len = len(model_data)
                    model_data = model_data.dropna()
                    dropped_rows = original_len - len(model_data)
                    
                    if dropped_rows > 0:
                        messagebox.showwarning("Advertencia", 
                            f"Se eliminaron {dropped_rows} filas con valores faltantes.")
                    
                    if model_data.empty:
                        messagebox.showerror("Error", "No hay datos válidos para análisis después de eliminar valores NaN.")
                        progress.destroy()
                        return
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error al preparar los datos: {str(e)}")
                    progress.destroy()
                    return
                
                # Actualizar parámetros y entrenar el modelo
                self.status_text.set("Entrenando modelo de IA...")
                self.root.update_idletasks()
                
                # Entrenar el modelo con manejo de excepciones
                try:
                    self.current_ai_model.set_parameters(params)
                    self.current_ai_model.fit(model_data)
                except Exception as e:
                    messagebox.showerror("Error de Entrenamiento", 
                        f"No se pudo entrenar el modelo: {str(e)}\n\n"
                        "Sugerencia: Verifique que las columnas seleccionadas sean apropiadas para este modelo.")
                    progress.destroy()
                    return
                
                self.status_text.set("Generando predicciones...")
                self.root.update_idletasks()
                
                # Obtener resultados
                try:
                    self.ai_model_results = self.current_ai_model.predict(model_data)
                except Exception as e:
                    messagebox.showerror("Error de Predicción", 
                        f"No se pudieron generar predicciones: {str(e)}")
                    progress.destroy()
                    return
                
                # Actualizar mensaje con información sobre el tiempo de procesamiento
                if hasattr(self.current_ai_model, 'fit_time'):
                    fit_time_str = f" (Tiempo: {self.current_ai_model.fit_time:.2f}s)"
                else:
                    fit_time_str = ""
                    
                self.status_text.set(f"Modelo {self.current_ai_model.name} aplicado a {len(model_data)} filas{fit_time_str}.")
                
                # Actualizar ambos gráficos: el normal y el de análisis de IA
                self.show_chart()
                self.show_ai_analysis_chart(model_data, selected_columns)
                
                # Cambiar a la pestaña de análisis de IA
                self.notebook.select(self.ai_tab)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al aplicar el modelo: {str(e)}")
                import traceback
                traceback.print_exc()
                self.status_text.set(f"Error al aplicar modelo de IA: {str(e)}")
                
            finally:
                # Eliminar la barra de progreso
                if 'progress' in locals():
                    progress.destroy()
                
        except Exception as e:
            messagebox.showerror("Error general", f"Ocurrió un error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Restaurar UI
            self.apply_ai_btn.config(state="normal")
            self.update_btn.config(state="normal")
            self.root.config(cursor="")

    def show_chart(self):
        """Mostrar el gráfico seleccionado."""
        try:
            # Desactivar el botón durante la actualización
            self.update_btn.config(state="disabled")
            self.status_text.set("Generando gráfico...")
            self.root.update_idletasks()  # Actualizar la interfaz
            
            # Guardar dimensiones actuales del frame antes de limpiar
            original_width = self.chart_frame.winfo_width() or 800
            original_height = self.chart_frame.winfo_height() or 600
            
            # Si las dimensiones son demasiado pequeñas, establecer valores mínimos
            if original_width < 400:
                original_width = 800
            if original_height < 300:
                original_height = 600
                
            # Limpiar completamente el frame del gráfico antes de agregar contenido nuevo
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Forzar explícitamente las dimensiones originales
            self.chart_frame.config(width=original_width, height=original_height)
            self.chart_frame.update_idletasks()
                
            # Configurar figura y ejes
            fig = Figure(figsize=(original_width/100, original_height/100), dpi=100)
            ax = fig.add_subplot(111)
            
            # Obtener tipo de gráfico y columna X
            chart_type = self.chart_combo.get()
            x_column = self.x_combo.get() if self.x_combo.get() else None
            
            # Limitar datos a los últimos N puntos
            try:
                n_points = int(self.n_points.get())
                if n_points <= 0:
                    n_points = len(self.dataframe)
            except ValueError:
                n_points = len(self.dataframe)
                
            df_display = self.dataframe.iloc[-n_points:].copy()
            
            # Preparar valores X
            x_values = None
            if x_column and x_column in df_display.columns:
                x_values = df_display[x_column]
            else:
                x_values = df_display.index
            
            # Crear el gráfico desde la fábrica
            chart = ChartFactory.create_chart(chart_type, self.COLORS['chart_colors'])
            
            # Seleccionar columnas numéricas para graficar
            numeric_cols = df_display.select_dtypes(include=['int64', 'float64']).columns
            
            # Excluir la columna X de los datos Y si es numérica
            if x_column in numeric_cols:
                numeric_cols = numeric_cols.drop(x_column)
                
            if len(numeric_cols) == 0:
                messagebox.showinfo("Información", "No hay columnas numéricas para graficar.")
                self.update_btn.config(state="normal")
                return
                
            y_data = df_display[numeric_cols]
            
            # Dibujar el gráfico
            ax = chart.plot(ax, x_values, y_data, x_col=x_column)
            
            # Si hay un modelo de IA aplicado, añadir sus resultados al gráfico
            model_desc = ""
            if self.current_ai_model and self.ai_model_results is not None:
                try:
                    # Limitar los resultados al mismo rango que los datos mostrados
                    ai_results_display = self.ai_model_results
                    
                    if len(ai_results_display) > n_points:
                        ai_results_display = ai_results_display.iloc[-n_points:].copy()
                    
                    # Asegurarse de que los datos numéricos sean compatibles
                    for col in ai_results_display.columns:
                        if col not in ai_results_display.select_dtypes(include=['number']).columns:
                            # Convertir columnas no numéricas a numéricas si es posible
                            try:
                                if ai_results_display[col].dtype == bool:
                                    ai_results_display[col] = ai_results_display[col].astype(int)
                                else:
                                    # Intentar convertir strings a números, o dejarlos como cero
                                    ai_results_display[col] = pd.to_numeric(
                                        ai_results_display[col], errors='coerce').fillna(0)
                            except:
                                # Si no se puede convertir, eliminar la columna
                                print(f"Advertencia: La columna {col} no se puede convertir a numérica")
                    
                    # Visualizar resultados del modelo
                    ax = self.current_ai_model.plot(ax, df_display, ai_results_display, x_values)
                    model_desc = f" con modelo {self.current_ai_model.name}"
                    
                except TypeError as te:
                    error_msg = str(te)
                    messagebox.showwarning("Advertencia", 
                        f"Error de tipo al visualizar resultados del modelo de IA: {error_msg}\n" +
                        "Se mostrará solo el gráfico básico.")
                except ValueError as ve:
                    error_msg = str(ve)
                    messagebox.showwarning("Advertencia", 
                        f"Error de valor al visualizar resultados del modelo de IA: {error_msg}\n" +
                        "Se mostrará solo el gráfico básico.")
                except Exception as e:
                    error_msg = str(e)
                    messagebox.showwarning("Advertencia", 
                        f"Error al visualizar resultados del modelo de IA: {error_msg}\n" +
                        "Se mostrará solo el gráfico básico.")
                    import traceback
                    traceback.print_exc()
            
            # Aplicar opciones de visualización
            if self.show_grid.get():
                ax.grid(True, linestyle='--', alpha=0.3)
                
            if self.rotate_labels.get():
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                
            # Añadir título descriptivo al gráfico
            ax.set_title(f"Gráfico de {chart_type}{model_desc}", fontweight='bold')
                
            # Ajustar márgenes
            fig.tight_layout()
            
            # Crear un contenedor principal que ocupe todo el espacio disponible
            chart_container = tk.Frame(self.chart_frame)
            chart_container.pack(fill=tk.BOTH, expand=True)
            
            # Mostrar el gráfico en la interfaz con expansión
            canvas = FigureCanvasTkAgg(fig, master=chart_container)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Agregar barra de herramientas de navegación
            toolbar_frame = tk.Frame(chart_container)
            toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()
            
            # Guardar referencias para limpiar más tarde
            self.current_canvas = canvas
            self.current_toolbar = toolbar
            
            # Añadir información sobre el modelo si hay uno aplicado
            model_info = ""
            if self.current_ai_model and self.ai_model_results is not None:
                model_info = f" | Modelo: {self.current_ai_model.name}"
            
            self.status_text.set(f"Gráfico actualizado. Mostrando {len(df_display)} filas{model_info}")
            
            # Asegurar que el tamaño se mantiene
            self.chart_frame.update_idletasks()
            self.chart_frame.config(width=original_width, height=original_height)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar el gráfico: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_text.set(f"Error al mostrar el gráfico: {str(e)}")
            
        finally:
            # Reactivar el botón de actualización
            self.update_btn.config(state="normal")

    def show_ai_analysis_chart(self, model_data, selected_columns):
        """Mostrar el gráfico de análisis de IA."""
        try:
            # Desactivar el botón durante la actualización
            self.apply_ai_btn.config(state="disabled")
            self.status_text.set("Generando gráfico de análisis de IA...")
            self.root.update_idletasks()  # Actualizar la interfaz
            
            # Guardar dimensiones actuales del frame antes de limpiar
            original_width = self.ai_chart_frame.winfo_width() or 800
            original_height = self.ai_chart_frame.winfo_height() or 600
            
            # Si las dimensiones son demasiado pequeñas, establecer valores mínimos
            if original_width < 400:
                original_width = 800
            if original_height < 300:
                original_height = 600
                
            # Limpiar completamente el frame del gráfico antes de agregar contenido nuevo
            for widget in self.ai_chart_frame.winfo_children():
                widget.destroy()
                
            # Limpiar y actualizar los frames de información
            for widget in self.ai_model_info_frame.winfo_children():
                widget.destroy()
                
            for widget in self.ai_results_frame.winfo_children():
                widget.destroy()
            
            # Actualizar información del modelo
            model_name = ttk.Label(self.ai_model_info_frame, 
                                 text=f"Modelo: {self.current_ai_model.name}", 
                                 style="Subtitle.TLabel")
            model_name.pack(anchor="w", padx=5, pady=2)
            
            if hasattr(self.current_ai_model, 'description'):
                desc = ttk.Label(self.ai_model_info_frame, 
                              text=f"Descripción: {self.current_ai_model.description}", 
                              wraplength=250)
                desc.pack(anchor="w", padx=5, pady=2)
                
            # Mostrar columnas utilizadas
            cols_label = ttk.Label(self.ai_model_info_frame, 
                                text=f"Columnas analizadas: {', '.join(selected_columns)}", 
                                wraplength=250)
            cols_label.pack(anchor="w", padx=5, pady=5)
            
            # Mostrar tiempo de procesamiento
            if hasattr(self.current_ai_model, 'fit_time'):
                time_label = ttk.Label(self.ai_model_info_frame, 
                                    text=f"Tiempo de entrenamiento: {self.current_ai_model.fit_time:.2f}s", 
                                    wraplength=250)
                time_label.pack(anchor="w", padx=5, pady=2)
                
            # Resultados del análisis
            result_title = ttk.Label(self.ai_results_frame, 
                                  text="Resultados del Análisis:", 
                                  style="Subtitle.TLabel")
            result_title.pack(anchor="w", padx=5, pady=5)
            
            # Mostrar información basada en el tipo de modelo
            if self.current_ai_model.name == "Pronóstico Lineal":
                forecast_info = ttk.Label(self.ai_results_frame, 
                                      text="Se han generado pronósticos para periodos futuros.", 
                                      wraplength=250)
                forecast_info.pack(anchor="w", padx=5, pady=2)
                
            elif self.current_ai_model.name == "Detección de Anomalías":
                # Contar anomalías detectadas
                if self.ai_model_results is not None and 'es_anomalia' in self.ai_model_results.columns:
                    try:
                        # Asegurar que es_anomalia sea booleano o numérico
                        if self.ai_model_results['es_anomalia'].dtype == bool:
                            anomaly_count = self.ai_model_results['es_anomalia'].sum()
                        else:
                            anomaly_count = self.ai_model_results['es_anomalia'].astype(float).sum()
                        anomaly_info = ttk.Label(self.ai_results_frame, 
                                             text=f"Se detectaron {int(anomaly_count)} anomalías.", 
                                             wraplength=250)
                        anomaly_info.pack(anchor="w", padx=5, pady=2)
                    except:
                        anomaly_info = ttk.Label(self.ai_results_frame, 
                                             text="Se detectaron anomalías en los datos.", 
                                             wraplength=250)
                        anomaly_info.pack(anchor="w", padx=5, pady=2)
                    
            elif self.current_ai_model.name == "Agrupamiento (Clustering)":
                # Contar clusters
                if self.ai_model_results is not None and 'cluster' in self.ai_model_results.columns:
                    try:
                        # Convertir a string para asegurar compatibilidad con todos los tipos de datos
                        cluster_count = len(pd.unique(self.ai_model_results['cluster'].astype(str)))
                        cluster_info = ttk.Label(self.ai_results_frame, 
                                            text=f"Se identificaron {cluster_count} grupos distintos.", 
                                            wraplength=250)
                        cluster_info.pack(anchor="w", padx=5, pady=2)
                    except:
                        cluster_info = ttk.Label(self.ai_results_frame, 
                                            text="Se identificaron múltiples grupos en los datos.", 
                                            wraplength=250)
                        cluster_info.pack(anchor="w", padx=5, pady=2)
            
            # Forzar explícitamente las dimensiones originales
            self.ai_chart_frame.config(width=original_width, height=original_height)
            self.ai_chart_frame.update_idletasks()
                
            # Configurar figura y ejes
            fig = Figure(figsize=(original_width/100, original_height/100), dpi=100)
            ax = fig.add_subplot(111)
            
            # Crear el gráfico de análisis de IA
            try:
                # Asegurarse de que los datos sean solo numéricos para evitar errores de tipo
                numeric_data = model_data.select_dtypes(include=['number'])
                
                # Asegurarse de que los resultados del modelo son compatibles
                if self.ai_model_results is not None:
                    try:
                        # Preparar los resultados del modelo IA para visualización
                        ai_results_display = self.ai_model_results.copy()
                        
                        # Convertir columnas no numéricas a str y columnas booleanas a int para evitar errores de tipo
                        for col in ai_results_display.columns:
                            if col not in ai_results_display.select_dtypes(include=['number']).columns:
                                if ai_results_display[col].dtype == bool:
                                    # Convertir booleanos a enteros (0/1)
                                    ai_results_display[col] = ai_results_display[col].astype(int)
                                else:
                                    # Convertir otras columnas no numéricas a string
                                    ai_results_display[col] = ai_results_display[col].astype(str)
                    except TypeError as type_error:
                        # Error específico para problemas de tipo de datos
                        error_msg = str(type_error)
                        # Mostrar advertencia al usuario pero intentar mostrar el gráfico básico
                        messagebox.showwarning("Advertencia", 
                                            f"Error al visualizar resultados del modelo de IA: {error_msg}\n\n"
                                            "Se mostrará solo el gráfico básico.")
                        
                        # Mostrar un gráfico básico
                        for col in numeric_data.columns:
                            ax.plot(range(len(numeric_data)), numeric_data[col], label=col)
                        ax.set_title("Visualización básica (error en modelo avanzado)", color='orange')
                        ax.legend()
                        ax.grid(True, linestyle='--', alpha=0.3)
                
                else:
                    ai_results_display = None
                    
                # Valores X para el gráfico (usar índices numéricos para evitar errores)
                x_values = range(len(numeric_data))
                
                # Llamar al método plot del modelo con los parámetros correctos
                ax = self.current_ai_model.plot(ax, numeric_data, ai_results_display, x_values)
                
                # Añadir título descriptivo al gráfico
                ax.set_title(f"Análisis de IA para {', '.join(selected_columns)}", fontweight='bold')
                
                # Grid para mejor visualización
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # Asegurarse de que se muestre la leyenda
                if len(ax.get_lines()) > 0 or len(ax.collections) > 0:
                    ax.legend(loc='best')
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                ax.text(0.5, 0.5, f"Error al generar gráfico: {str(e)}", 
                      ha='center', va='center', fontsize=12, color='red')
                ax.set_title("Error de visualización", fontweight='bold', color='red')
                
            # Ajustar márgenes
            fig.tight_layout()
            
            # Crear un contenedor principal que ocupe todo el espacio disponible
            chart_container = tk.Frame(self.ai_chart_frame)
            chart_container.pack(fill=tk.BOTH, expand=True)
            
            # Mostrar el gráfico en la interfaz con expansión
            canvas = FigureCanvasTkAgg(fig, master=chart_container)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            # Agregar barra de herramientas de navegación
            toolbar_frame = tk.Frame(chart_container)
            toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()
            
            # Guardar referencias para limpiar más tarde
            self.current_ai_analysis_canvas = canvas
            self.current_ai_analysis_toolbar = toolbar
            
            self.status_text.set(f"Análisis de IA completado para el modelo {self.current_ai_model.name}")
            
            # Asegurar que el tamaño se mantiene
            self.ai_chart_frame.update_idletasks()
            self.ai_chart_frame.config(width=original_width, height=original_height)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar el análisis de IA: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_text.set(f"Error al mostrar el análisis de IA: {str(e)}")
            
        finally:
            # Reactivar el botón de aplicar
            self.apply_ai_btn.config(state="normal")

class CheckboxManager:
    """Clase para gestionar checkboxes y su estado."""
    
    def __init__(self, master, items, callback=None, select_all=True):
        """
        Inicializar el gestor de checkboxes.
        
        Args:
            master: Widget padre donde se crearán los checkboxes
            items: Lista de elementos para los checkboxes
            callback: Función a llamar cuando cambia el estado de un checkbox
            select_all: Si se debe incluir un checkbox "Seleccionar Todo"
        """
        self.master = master
        self.items = items
        self.callback = callback
        self.checkboxes = {}
        self.states = {item: False for item in items}  # Estado explícito
        self.widgets = {}  # Almacenar referencia a widgets
        
        # Limpiar contenido existente
        for widget in self.master.winfo_children():
            widget.destroy()
            
        if not items:
            ttk.Label(self.master, text="No hay elementos disponibles").grid(row=0, column=0)
            return
            
        # Crear checkbox "Seleccionar Todo" si se solicita
        if select_all:
            self.select_all_widget = ttk.Checkbutton(
                self.master, 
                text="Seleccionar Todo",
                command=self._on_select_all_clicked
            )
            self.select_all_widget.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=2)
            
            # Añadir separador
            ttk.Separator(self.master, orient="horizontal").grid(
                row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
                
        # Crear checkboxes para cada elemento
        for i, item in enumerate(items):
            cb = ttk.Checkbutton(
                self.master, 
                text=item,
                command=lambda i=item: self._on_checkbox_clicked(i)
            )
            
            # Posicionar (considerando espacio para Select All y separador)
            offset = 2 if select_all else 0
            row, col_pos = divmod(i, 3)
            cb.grid(row=row+offset, column=col_pos, sticky="w", padx=5, pady=2)
            
            # Guardar referencia al widget
            self.widgets[item] = cb
    
    def _on_checkbox_clicked(self, item):
        """Manejar el click en un checkbox."""
        # Invertir el estado actual
        self.states[item] = not self.states[item]
        
        # Actualizar el estado visual del checkbox
        if self.states[item]:
            self.widgets[item].state(['selected'])
        else:
            self.widgets[item].state(['!selected'])
            
        # Actualizar el checkbox "Select All" si existe
        if hasattr(self, 'select_all_widget'):
            if all(self.states.values()):
                self.select_all_widget.state(['selected'])
            else:
                self.select_all_widget.state(['!selected'])
        
        # Llamar al callback si existe
        if self.callback:
            self.callback(self.get_selected())
            
    def _on_select_all_clicked(self):
        """Manejar el click en el checkbox "Seleccionar Todo"."""
        # Determinar el nuevo estado basado en el estado visual actual
        new_state = 'selected' not in self.select_all_widget.state()
        
        # Actualizar todos los checkboxes
        for item in self.items:
            self.states[item] = new_state
            if new_state:
                self.widgets[item].state(['selected'])
            else:
                self.widgets[item].state(['!selected'])
                
        # Actualizar el propio checkbox "Select All"
        if new_state:
            self.select_all_widget.state(['selected'])
        else:
            self.select_all_widget.state(['!selected'])
            
        # Llamar al callback si existe
        if self.callback:
            self.callback(self.get_selected())
    
    def get_selected(self):
        """Obtener lista de elementos seleccionados."""
        return [item for item, state in self.states.items() if state]
    
    def get_selected_count(self):
        """Obtener número de elementos seleccionados."""
        return sum(1 for state in self.states.values() if state)