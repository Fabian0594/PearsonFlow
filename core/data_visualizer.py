import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

class DataVisualizerGUI:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe
        self.setup_window()
        self.create_widgets()
        self.current_canvas = None
        self.current_toolbar = None

    def setup_window(self):
        """Configurar la ventana principal."""
        self.root = tk.Toplevel()
        self.root.title("Visualizador de Datos")
        self.root.geometry("1200x800")
        
        # Crear frames principales
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(fill="x", padx=10, pady=5)
        
        self.data_frame = ttk.Frame(self.root)
        self.data_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def create_widgets(self):
        """Crear todos los widgets de la interfaz."""
        self.create_control_widgets()
        self.create_data_table()

    def create_control_widgets(self):
        """Crear widgets de control."""
        # Frame para controles de visualización
        controls = ttk.LabelFrame(self.control_frame, text="Controles de Visualización")
        controls.pack(fill="x", pady=5)

        # Primera fila de controles
        row1 = ttk.Frame(controls)
        row1.pack(fill="x", padx=5, pady=5)

        # Tipo de gráfico
        ttk.Label(row1, text="Tipo de Gráfico:").pack(side="left", padx=5)
        self.chart_types = ["Barras", "Líneas", "Pastel", "Dispersión"]
        self.selected_chart = tk.StringVar(value=self.chart_types[0])
        ttk.Combobox(row1, textvariable=self.selected_chart, 
                    values=self.chart_types, state="readonly").pack(side="left", padx=5)

        # Selector de columna X
        ttk.Label(row1, text="Columna X:").pack(side="left", padx=5)
        self.x_column = tk.StringVar()
        self.x_combo = ttk.Combobox(row1, textvariable=self.x_column, 
                                   values=list(self.dataframe.columns), state="readonly")
        self.x_combo.pack(side="left", padx=5)

        # Segunda fila de controles
        row2 = ttk.Frame(controls)
        row2.pack(fill="x", padx=5, pady=5)

        # Opciones de visualización
        self.show_grid = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Mostrar Cuadrícula", 
                       variable=self.show_grid).pack(side="left", padx=5)

        self.rotate_labels = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Rotar Etiquetas", 
                       variable=self.rotate_labels).pack(side="left", padx=5)

        # Número de puntos a mostrar
        ttk.Label(row2, text="Mostrar últimos N puntos:").pack(side="left", padx=5)
        self.n_points = tk.StringVar(value="50")
        ttk.Entry(row2, textvariable=self.n_points, width=10).pack(side="left", padx=5)

        # Botón para actualizar gráfico
        ttk.Button(row2, text="Actualizar Gráfico", 
                  command=self.show_chart).pack(side="right", padx=5)

    def create_data_table(self):
        """Crear tabla de datos con scroll."""
        # Frame para la tabla con scrollbar
        table_frame = ttk.Frame(self.data_frame)
        table_frame.pack(fill="both", expand=True)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame)
        y_scroll.pack(side="right", fill="y")
        
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        x_scroll.pack(side="bottom", fill="x")

        # Tabla
        self.tree = ttk.Treeview(table_frame, yscrollcommand=y_scroll.set,
                                xscrollcommand=x_scroll.set)
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
            x_col = self.x_column.get()
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
                  alpha=0.7,
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
                   color=colors[i % len(colors)])
        
        self.adjust_y_axis(ax, y_data)
        return ax

    def plot_scatter_chart(self, ax, x_values, y_data, colors):
        """Crear gráfico de dispersión."""
        for i, column in enumerate(y_data.columns):
            ax.scatter(x_values, y_data[column], 
                     label=column, 
                     alpha=0.6,
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
            textprops={'fontsize': 8}
        )
        ax.set_ylabel("")
        return ax

    def configure_general_chart(self, ax, chart_type, x_col):
        """Configurar elementos generales del gráfico."""
        if chart_type != "Pastel":
            # Configurar título y etiquetas
            ax.set_xlabel(x_col, fontsize=10)
            ax.set_ylabel("Valor", fontsize=10)
            
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
            ax.tick_params(labelsize=8)
            
            # Leyenda
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    def show_chart(self):
        """Mostrar el gráfico seleccionado."""
        try:
            # Limpiar gráfico anterior
            if self.current_canvas:
                self.current_canvas.get_tk_widget().destroy()
            if self.current_toolbar:
                self.current_toolbar.destroy()

            # Preparar datos
            x_values, y_data, x_col = self.prepare_data_for_plot()
            if x_values is None or y_data is None or x_col is None:
                return

            # Crear figura con estilo mejorado
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Configurar colores y estilo
            colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c']
            ax.set_facecolor('#f8f9fa')
            fig.patch.set_facecolor('#ffffff')
            
            # Graficar según el tipo
            chart_type = self.selected_chart.get()
            
            try:
                if chart_type == "Barras":
                    ax = self.plot_bar_chart(ax, x_values, y_data, x_col, colors)
                elif chart_type == "Líneas":
                    ax = self.plot_line_chart(ax, x_values, y_data, colors)
                elif chart_type == "Dispersión":
                    ax = self.plot_scatter_chart(ax, x_values, y_data, colors)
                elif chart_type == "Pastel":
                    ax = self.plot_pie_chart(ax, y_data, colors)
                    if ax is None:
                        plt.close(fig)
                        return
                
                # Configuración general del gráfico
                self.configure_general_chart(ax, chart_type, x_col)
                
                # Ajustar layout
                if chart_type != "Pastel":
                    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Dejar espacio para la leyenda
                else:
                    plt.tight_layout()
                    
                # Crear canvas y toolbar
                self.current_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
                self.current_canvas.draw()
                self.current_canvas.get_tk_widget().pack(fill="both", expand=True)
                
                # Agregar barra de herramientas
                self.current_toolbar = NavigationToolbar2Tk(self.current_canvas, self.chart_frame)
                self.current_toolbar.update()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear el gráfico: {str(e)}")
                plt.close(fig)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error general: {str(e)}")