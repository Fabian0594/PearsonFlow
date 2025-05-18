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

    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
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
        self.main_frame.rowconfigure(1, weight=1)  # Datos y gráfico
        
        # Crear los frames internos
        self.control_frame = ttk.Frame(self.main_frame, padding="5")
        self.control_frame.grid(row=0, column=0, sticky="new", padx=5, pady=5)
        
        # Frame para datos y gráfico (diseño de dos columnas)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(1, weight=3)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Frame para la tabla de datos (izquierda)
        self.data_frame = ttk.Frame(self.content_frame)
        self.data_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Frame para el gráfico (derecha)
        self.chart_frame = ttk.Frame(self.content_frame)
        self.chart_frame.grid(row=0, column=1, sticky="nsew")
        
        # Barra de estado
        self.status_frame = ttk.Frame(self.main_frame, relief="sunken")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(5, 0))
        
        self.status_text = tk.StringVar(value="Aplicación iniciada. Listo para visualizar datos.")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_text, anchor="w", padding=(5, 2))
        status_label.pack(side="left", fill="x", expand=True)

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
        self.chart_types = ["Barras", "Líneas", "Pastel", "Dispersión"]
        
        self.chart_combo = ttk.Combobox(controls, width=15)
        self.chart_combo['values'] = self.chart_types
        self.chart_combo.current(0)  # Establecer "Barras" como valor inicial
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
        
        # Mostrar información resumida del DataFrame
        num_rows = len(self.dataframe)
        num_cols = len(self.dataframe.columns)
        ttk.Label(stats_frame, text=f"Filas: {num_rows} | Columnas: {num_cols}", 
                 style="Subtitle.TLabel").pack(side="left")

    def on_chart_type_changed(self, event):
        """Manejar el evento de cambio de tipo de gráfico."""
        selected_type = self.chart_combo.get()
        self.status_text.set(f"Tipo de gráfico cambiado a: {selected_type}")

    def prepare_data_for_plot(self):
        """Preparar datos para el gráfico."""
        try:
            # Validar y obtener número de puntos a mostrar
            try:
                n = int(self.n_points.get())
                if n <= 0:
                    raise ValueError("El número de puntos debe ser mayor que 0")
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un número válido de puntos")
                return None, None, None
            
            # Preparar columna X
            x_col = self.x_combo.get()
            df = self.dataframe.tail(n).copy()
            
            if not x_col:
                # Si no se selecciona columna X, usar el índice
                x_values = range(len(df))
                x_col = "Índice"
            else:
                # Convertir a datetime si es posible
                try:
                    if df[x_col].dtype == 'object':  # Solo intentar convertir si es string/object
                        df[x_col] = pd.to_datetime(df[x_col], errors='ignore')
                    x_values = df[x_col]
                except Exception:
                    x_values = df[x_col]
            
            # Obtener columnas numéricas para Y de manera más eficiente
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if x_col in numeric_cols and x_col != "Índice":
                numeric_cols = numeric_cols.drop(x_col)
            
            if len(numeric_cols) == 0:
                messagebox.showerror("Error", "No hay columnas numéricas disponibles para graficar")
                return None, None, None
                
            return x_values, df[numeric_cols], x_col
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al preparar datos: {str(e)}")
            return None, None, None

    def adjust_y_axis(self, ax, y_data):
        """Ajustar el rango del eje Y basado en los datos."""
        try:
            ymin = y_data.min().min()
            ymax = y_data.max().max()
            
            # Evitar división por cero o valores muy cercanos a cero
            if abs(ymax - ymin) < 1e-10:
                if abs(ymax) < 1e-10:  # Ambos cercanos a cero
                    ax.set_ylim([-0.1, 0.1])
                else:  # Mismo valor pero no cero
                    ax.set_ylim([ymin * 0.9 if ymin > 0 else ymin * 1.1, 
                                ymax * 1.1 if ymax > 0 else ymax * 0.9])
                return
            
            # Ajuste normal
            if ymax <= 1:
                ax.set_ylim([ymin - 0.1 * abs(ymin) if ymin > 0 else ymin * 1.1 if ymin < 0 else 0, 
                            ymax + 0.1])
            else:
                ax.set_ylim([ymin - 0.1 * abs(ymin) if ymin > 0 else ymin * 1.1 if ymin < 0 else 0, 
                            ymax * 1.1])
        except Exception:
            # Si algo falla, dejar que matplotlib ajuste automáticamente
            pass

    def plot_bar_chart(self, ax, x_values, y_data, x_col, colors):
        """Crear gráfico de barras."""
        x = np.arange(len(x_values))  # Posiciones de las barras
        width = 0.8 / len(y_data.columns)  # Ancho de las barras
        
        for i, column in enumerate(y_data.columns):
            ax.bar(x + i * width, y_data[column], 
                  width,
                  label=column, 
                  alpha=0.8,
                  color=colors[i % len(colors)])
        
        # Configurar eje X
        if isinstance(x_values, pd.DatetimeIndex):
            ax.set_xticks(x + width * (len(y_data.columns) - 1) / 2)
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in x_values])
        else:
            ax.set_xticks(x + width * (len(y_data.columns) - 1) / 2)
            ax.set_xticklabels(x_values)
        
        self.adjust_y_axis(ax, y_data)
        return ax

    def plot_line_chart(self, ax, x_values, y_data, colors):
        """Crear gráfico de líneas."""
        for i, column in enumerate(y_data.columns):
            ax.plot(x_values, y_data[column], 
                   label=column, 
                   marker='o', 
                   markersize=4,
                   linewidth=2,
                   color=colors[i % len(colors)])
        
        self.adjust_y_axis(ax, y_data)
        return ax

    def plot_scatter_chart(self, ax, x_values, y_data, colors):
        """Crear gráfico de dispersión."""
        for i, column in enumerate(y_data.columns):
            ax.scatter(x_values, y_data[column], 
                     label=column, 
                     alpha=0.8,
                     s=50,  # tamaño de punto
                     color=colors[i % len(colors)])
        
        self.adjust_y_axis(ax, y_data)
        return ax

    def plot_pie_chart(self, ax, y_data, colors):
        """Crear gráfico de pastel."""
        # Para gráfico de pastel, usar solo la primera columna numérica
        column = y_data.columns[0]
        values = y_data[column].abs()  # Usar valores absolutos
        total = values.sum()
        
        if total == 0:
            messagebox.showerror("Error", "No hay datos válidos para el gráfico de pastel")
            return None
            
        # Agrupar valores pequeños en "Otros"
        threshold = 0.05  # 5% del total
        small_mask = values/total < threshold
        
        if small_mask.any():
            large_values = values[~small_mask]
            otros = pd.Series({'Otros': values[small_mask].sum()})
            values = pd.concat([large_values, otros])
        
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=values.index,
            autopct='%1.1f%%',
            colors=colors[:len(values)],
            explode=[0.05] * len(values),  # Separar las piezas
            shadow=True,  # Sombra
            startangle=90,  # Iniciar desde arriba
            textprops={'fontsize': 9, 'fontweight': 'bold'}
        )
        ax.set_ylabel("")
        ax.set_title(f"Distribución de {column}", fontweight='bold', pad=20)
        return ax

    def configure_general_chart(self, ax, chart_type, x_col):
        """Configurar elementos generales del gráfico."""
        if chart_type != "Pastel":
            # Configurar título y etiquetas
            chart_title = {
                "Barras": f"Gráfico de Barras - {x_col}",
                "Líneas": f"Gráfico de Líneas - {x_col}",
                "Dispersión": f"Gráfico de Dispersión - {x_col}"
            }.get(chart_type, f"Gráfico de {chart_type}")
            
            ax.set_title(chart_title, fontweight='bold', pad=20)
            ax.set_xlabel(x_col, fontsize=10, fontweight='bold')
            ax.set_ylabel("Valor", fontsize=10, fontweight='bold')
            
            # Ajustar espaciado de las etiquetas
            ax.xaxis.labelpad = 10
            ax.yaxis.labelpad = 10
            
            # Rotar etiquetas si está activado
            if self.rotate_labels.get():
                plt.xticks(rotation=45, ha='right')
            
            # Mostrar cuadrícula si está activado
            if self.show_grid.get():
                ax.grid(True, linestyle='--', alpha=0.3, color='gray')
            
            # Personalizar bordes y ticks
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(labelsize=9)
            
            # Leyenda con mejor formato
            legend = ax.legend(
                bbox_to_anchor=(1.05, 1), 
                loc='upper left',
                frameon=True,
                fancybox=True,
                shadow=True,
                fontsize=9
            )

    def show_chart(self):
        """Mostrar el gráfico seleccionado."""
        # Desactivar el botón durante la actualización
        self.update_btn.config(state="disabled")
        self.status_text.set("Generando gráfico...")
        self.root.update_idletasks()  # Actualizar la interfaz
        
        try:
            # Limpiar gráfico anterior
            plt.close('all')  # Cerrar todas las figuras abiertas
            
            if self.current_canvas:
                self.current_canvas.get_tk_widget().pack_forget()
                self.current_canvas.get_tk_widget().destroy()
                
            if self.current_toolbar:
                self.current_toolbar.pack_forget()
                self.current_toolbar.destroy()
                
            self.current_canvas = None
            self.current_toolbar = None

            # Preparar datos
            x_values, y_data, x_col = self.prepare_data_for_plot()
            if x_values is None or y_data is None or x_col is None:
                self.update_btn.config(state="normal")
                self.status_text.set("Error al preparar los datos.")
                return

            # Crear figura con estilo mejorado
            plt.style.use('seaborn-v0_8-whitegrid')
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # Configurar colores y estilo
            ax.set_facecolor(self.COLORS['bg_light'])
            fig.patch.set_facecolor('white')
            
            # Obtener el tipo de gráfico seleccionado directamente del combobox
            chart_type = self.chart_combo.get()
            
            try:
                if chart_type == "Barras":
                    ax = self.plot_bar_chart(ax, x_values, y_data, x_col, self.COLORS['chart_colors'])
                elif chart_type == "Líneas":
                    ax = self.plot_line_chart(ax, x_values, y_data, self.COLORS['chart_colors'])
                elif chart_type == "Dispersión":
                    ax = self.plot_scatter_chart(ax, x_values, y_data, self.COLORS['chart_colors'])
                elif chart_type == "Pastel":
                    ax = self.plot_pie_chart(ax, y_data, self.COLORS['chart_colors'])
                    if ax is None:
                        plt.close(fig)
                        self.update_btn.config(state="normal")
                        self.status_text.set("No se pudo crear el gráfico de pastel.")
                        return
                else:
                    messagebox.showerror("Error", f"Tipo de gráfico no reconocido: {chart_type}")
                    plt.close(fig)
                    self.update_btn.config(state="normal")
                    self.status_text.set("Error: tipo de gráfico no válido.")
                    return
                
                # Configuración general del gráfico
                self.configure_general_chart(ax, chart_type, x_col)
                
                # Ajustar layout
                if chart_type != "Pastel":
                    fig.tight_layout(rect=[0, 0, 0.85, 1])  # Dejar espacio para la leyenda
                else:
                    fig.tight_layout()
                
                # Limpiar el frame de gráfico
                for widget in self.chart_frame.winfo_children():
                    widget.destroy()
                    
                # Crear marco para el gráfico con etiqueta    
                chart_container = ttk.LabelFrame(self.chart_frame, text=f"Visualización - {chart_type}", padding=(5, 5))
                chart_container.pack(fill="both", expand=True, padx=5, pady=5)
                
                # Crear canvas y toolbar
                self.current_canvas = FigureCanvasTkAgg(fig, master=chart_container)
                self.current_canvas.draw()
                self.current_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
                
                # Agregar barra de herramientas
                toolbar_frame = ttk.Frame(chart_container)
                toolbar_frame.pack(fill="x", expand=False, padx=5)
                
                self.current_toolbar = NavigationToolbar2Tk(self.current_canvas, toolbar_frame)
                self.current_toolbar.update()
                
                self.status_text.set(f"Gráfico {chart_type} generado exitosamente.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear el gráfico: {str(e)}")
                plt.close(fig)
                self.status_text.set(f"Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error general: {str(e)}")
            self.status_text.set(f"Error general: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Reactivar el botón de actualización
            self.update_btn.config(state="normal")