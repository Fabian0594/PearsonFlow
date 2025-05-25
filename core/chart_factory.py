import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional


class Chart(ABC):
    """Clase base abstracta para todos los tipos de gráficos usando patrón Strategy."""
    
    def __init__(self, colors: List[str]):
        """
        Inicializar un gráfico con paleta de colores.
        
        Args:
            colors: Lista de colores para usar en el gráfico
        """
        self.colors = colors
        
    @abstractmethod
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """
        Dibujar el gráfico en los ejes dados.
        
        Args:
            ax: Ejes de matplotlib donde dibujar
            x_values: Valores para el eje X
            y_data: DataFrame con datos para el eje Y
            **kwargs: Argumentos adicionales específicos del gráfico
            
        Returns:
            plt.Axes: Los ejes con el gráfico dibujado
        """
        pass
    
    def adjust_y_axis(self, ax: plt.Axes, y_data: pd.DataFrame) -> None:
        """
        Ajustar automáticamente el rango del eje Y para optimizar la visualización.
        
        Args:
            ax: Ejes a ajustar
            y_data: DataFrame con datos para determinar el rango óptimo
        """
        try:
            ymin = y_data.min().min()
            ymax = y_data.max().max()
            
            # Manejar casos especiales donde los valores son muy similares
            if abs(ymax - ymin) < 1e-10:
                if abs(ymax) < 1e-10:  # Ambos valores cercanos a cero
                    ax.set_ylim([-0.1, 0.1])
                else:  # Mismo valor pero no cero
                    margin = abs(ymax) * 0.1
                    ax.set_ylim([ymax - margin, ymax + margin])
                return
            
            # Aplicar márgenes proporcionales para mejor visualización
            if ymax <= 1:
                # Para valores pequeños, usar márgenes fijos
                margin = 0.1
                ax.set_ylim([ymin - margin if ymin > 0 else ymin * 1.1, ymax + margin])
            else:
                # Para valores grandes, usar márgenes proporcionales
                margin = abs(ymax - ymin) * 0.1
                ax.set_ylim([ymin - margin if ymin > 0 else ymin * 1.1, ymax + margin])
                
        except Exception:
            # Fallback: dejar que matplotlib ajuste automáticamente
            pass


class BarChart(Chart):
    """Implementación de gráfico de barras con soporte para múltiples series."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de barras agrupadas."""
        x_col = kwargs.get('x_col', 'X')
        
        # Configurar posiciones y ancho de barras
        x = np.arange(len(x_values))
        width = 0.8 / len(y_data.columns)  # Ancho ajustado por número de series
        
        # Crear una barra por cada columna de datos
        for i, column in enumerate(y_data.columns):
            ax.bar(x + i * width, y_data[column], 
                  width,
                  label=column, 
                  alpha=0.8,
                  color=self.colors[i % len(self.colors)])
        
        # Configurar etiquetas del eje X según el tipo de datos
        if isinstance(x_values, pd.DatetimeIndex):
            # Formatear fechas para mejor legibilidad
            ax.set_xticks(x + width * (len(y_data.columns) - 1) / 2)
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in x_values], rotation=45)
        else:
            # Centrar etiquetas entre grupos de barras
            ax.set_xticks(x + width * (len(y_data.columns) - 1) / 2)
            ax.set_xticklabels(x_values)
        
        self.adjust_y_axis(ax, y_data)
        return ax


class LineChart(Chart):
    """Implementación de gráfico de líneas con marcadores."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de líneas con marcadores para cada serie."""
        # Dibujar una línea por cada columna de datos
        for i, column in enumerate(y_data.columns):
            ax.plot(x_values, y_data[column], 
                   label=column, 
                   marker='o', 
                   markersize=4,
                   linewidth=2,
                   color=self.colors[i % len(self.colors)])
        
        self.adjust_y_axis(ax, y_data)
        return ax


class ScatterChart(Chart):
    """Implementación de gráfico de dispersión para análisis de correlación."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de dispersión con puntos diferenciados por serie."""
        # Crear scatter plot para cada columna de datos
        for i, column in enumerate(y_data.columns):
            ax.scatter(x_values, y_data[column], 
                     label=column, 
                     alpha=0.8,
                     s=50,  # Tamaño de punto optimizado para legibilidad
                     color=self.colors[i % len(self.colors)])
        
        self.adjust_y_axis(ax, y_data)
        return ax


class PieChart(Chart):
    """Implementación de gráfico de pastel con agrupación automática de valores pequeños."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de pastel con optimizaciones para legibilidad."""
        # Usar solo la primera columna numérica para el gráfico de pastel
        column = y_data.columns[0]
        values = y_data[column].abs()  # Usar valores absolutos para evitar errores
        total = values.sum()
        
        # Validar que hay datos para graficar
        if total == 0:
            raise ValueError("No hay datos válidos para el gráfico de pastel")
            
        # Agrupar valores pequeños en categoría "Otros" para mejor legibilidad
        threshold = 0.05  # Umbral del 5% del total
        small_mask = values/total < threshold
        
        if small_mask.any():
            # Separar valores grandes y agrupar pequeños
            large_values = values[~small_mask]
            otros_sum = values[small_mask].sum()
            if otros_sum > 0:
                otros = pd.Series({'Otros': otros_sum})
                values = pd.concat([large_values, otros])
        
        # Crear gráfico de pastel con efectos visuales
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=values.index,
            autopct='%1.1f%%',
            colors=self.colors[:len(values)],
            explode=[0.05] * len(values),  # Separar ligeramente las piezas
            shadow=True,  # Agregar sombra para profundidad
            startangle=90,  # Iniciar desde la parte superior
            textprops={'fontsize': 9, 'fontweight': 'bold'}
        )
        
        # Limpiar etiquetas innecesarias y agregar título
        ax.set_ylabel("")
        ax.set_title(f"Distribución de {column}", fontweight='bold', pad=20)
        return ax


class ChartFactory:
    """
    Fábrica para crear diferentes tipos de gráficos usando patrón Factory.
    Centraliza la creación y configuración de gráficos.
    """
    
    # Mapeo de tipos de gráfico a sus clases implementadoras
    CHART_TYPES = {
        'Barras': BarChart,
        'Líneas': LineChart,
        'Dispersión': ScatterChart,
        'Pastel': PieChart
    }
    
    @classmethod
    def create_chart(cls, chart_type: str, colors: List[str]) -> Chart:
        """
        Crear un gráfico del tipo especificado con validación de entrada.
        
        Args:
            chart_type: Tipo de gráfico a crear (Barras, Líneas, Dispersión, Pastel)
            colors: Lista de colores para usar en el gráfico
            
        Returns:
            Chart: Instancia del tipo de gráfico solicitado
            
        Raises:
            ValueError: Si el tipo de gráfico no es válido o los colores son inválidos
        """
        # Validar tipo de entrada
        if not isinstance(chart_type, str):
            raise ValueError(f"El tipo de gráfico debe ser una cadena, se recibió: {type(chart_type)}")
            
        # Proporcionar colores por defecto si no se especifican
        if not colors or not isinstance(colors, list) or len(colors) == 0:
            default_colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c']
            colors = default_colors
            
        # Verificar disponibilidad del tipo de gráfico solicitado
        if chart_type not in cls.CHART_TYPES:
            available_types = list(cls.CHART_TYPES.keys())
            default_type = available_types[0]
            print(f"ADVERTENCIA: Tipo de gráfico '{chart_type}' desconocido. Usando '{default_type}' en su lugar.")
            chart_type = default_type
            
        # Instanciar y retornar el gráfico solicitado
        chart_class = cls.CHART_TYPES[chart_type]
        return chart_class(colors)
    
    @classmethod
    def get_available_chart_types(cls) -> List[str]:
        """
        Obtener la lista de tipos de gráficos disponibles.
        
        Returns:
            List[str]: Lista de nombres de tipos de gráficos soportados
        """
        return list(cls.CHART_TYPES.keys())

    @classmethod
    def configure_chart(cls, ax: plt.Axes, chart_type: str, x_col: str) -> None:
        """
        Aplicar configuración visual estándar a los gráficos.
        
        Args:
            ax: Ejes donde se dibuja el gráfico
            chart_type: Tipo de gráfico para personalización específica
            x_col: Nombre de la columna X para etiquetas
        """
        # Aplicar configuración solo a gráficos que no sean de pastel
        if chart_type != "Pastel":
            # Generar títulos descriptivos según el tipo de gráfico
            chart_title = {
                "Barras": f"Gráfico de Barras - {x_col}",
                "Líneas": f"Gráfico de Líneas - {x_col}",
                "Dispersión": f"Gráfico de Dispersión - {x_col}"
            }.get(chart_type, f"Gráfico de {chart_type}")
            
            # Configurar título y etiquetas de ejes
            ax.set_title(chart_title, fontweight='bold', pad=20)
            ax.set_xlabel(x_col, fontsize=10, fontweight='bold')
            ax.set_ylabel("Valor", fontsize=10, fontweight='bold')
            
            # Ajustar espaciado para mejor legibilidad
            ax.xaxis.labelpad = 10
            ax.yaxis.labelpad = 10
            
            # Aplicar estilo minimalista removiendo bordes innecesarios
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(labelsize=9) 