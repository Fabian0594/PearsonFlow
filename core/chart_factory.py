import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional


class Chart(ABC):
    """Clase base abstracta para todos los tipos de gráficos."""
    
    def __init__(self, colors: List[str]):
        """
        Inicializar un gráfico.
        
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
        Ajustar el rango del eje Y basado en los datos.
        
        Args:
            ax: Ejes a ajustar
            y_data: DataFrame con datos para determinar el rango
        """
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


class BarChart(Chart):
    """Implementación de gráfico de barras."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de barras."""
        x_col = kwargs.get('x_col', 'X')
        
        x = np.arange(len(x_values))  # Posiciones de las barras
        width = 0.8 / len(y_data.columns)  # Ancho de las barras
        
        for i, column in enumerate(y_data.columns):
            ax.bar(x + i * width, y_data[column], 
                  width,
                  label=column, 
                  alpha=0.8,
                  color=self.colors[i % len(self.colors)])
        
        # Configurar eje X
        if isinstance(x_values, pd.DatetimeIndex):
            ax.set_xticks(x + width * (len(y_data.columns) - 1) / 2)
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in x_values])
        else:
            ax.set_xticks(x + width * (len(y_data.columns) - 1) / 2)
            ax.set_xticklabels(x_values)
        
        self.adjust_y_axis(ax, y_data)
        return ax


class LineChart(Chart):
    """Implementación de gráfico de líneas."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de líneas."""
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
    """Implementación de gráfico de dispersión."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de dispersión."""
        for i, column in enumerate(y_data.columns):
            ax.scatter(x_values, y_data[column], 
                     label=column, 
                     alpha=0.8,
                     s=50,  # tamaño de punto
                     color=self.colors[i % len(self.colors)])
        
        self.adjust_y_axis(ax, y_data)
        return ax


class PieChart(Chart):
    """Implementación de gráfico de pastel."""
    
    def plot(self, ax: plt.Axes, x_values: Any, y_data: pd.DataFrame, **kwargs) -> plt.Axes:
        """Crear gráfico de pastel."""
        # Para gráfico de pastel, usar solo la primera columna numérica
        column = y_data.columns[0]
        values = y_data[column].abs()  # Usar valores absolutos
        total = values.sum()
        
        if total == 0:
            raise ValueError("No hay datos válidos para el gráfico de pastel")
            
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
            colors=self.colors[:len(values)],
            explode=[0.05] * len(values),  # Separar las piezas
            shadow=True,  # Sombra
            startangle=90,  # Iniciar desde arriba
            textprops={'fontsize': 9, 'fontweight': 'bold'}
        )
        ax.set_ylabel("")
        ax.set_title(f"Distribución de {column}", fontweight='bold', pad=20)
        return ax


class ChartFactory:
    """Fábrica para crear diferentes tipos de gráficos."""
    
    # Diccionario para mapear tipos de gráfico a sus clases
    CHART_TYPES = {
        'Barras': BarChart,
        'Líneas': LineChart,
        'Dispersión': ScatterChart,
        'Pastel': PieChart
    }
    
    @classmethod
    def create_chart(cls, chart_type: str, colors: List[str]) -> Chart:
        """
        Crear un gráfico del tipo especificado.
        
        Args:
            chart_type: Tipo de gráfico a crear (Barras, Líneas, Dispersión, Pastel)
            colors: Lista de colores para usar en el gráfico
            
        Returns:
            Chart: Instancia del tipo de gráfico solicitado
            
        Raises:
            ValueError: Si el tipo de gráfico no es válido
        """
        if chart_type not in cls.CHART_TYPES:
            raise ValueError(f"Tipo de gráfico desconocido: {chart_type}")
            
        chart_class = cls.CHART_TYPES[chart_type]
        return chart_class(colors)
    
    @classmethod
    def get_available_chart_types(cls) -> List[str]:
        """
        Obtener la lista de tipos de gráficos disponibles.
        
        Returns:
            List[str]: Lista de nombres de tipos de gráficos
        """
        return list(cls.CHART_TYPES.keys())

    @classmethod
    def configure_chart(cls, ax: plt.Axes, chart_type: str, x_col: str) -> None:
        """
        Configurar elementos generales del gráfico.
        
        Args:
            ax: Ejes donde se dibuja el gráfico
            chart_type: Tipo de gráfico
            x_col: Nombre de la columna X
        """
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
            
            # Personalizar bordes y ticks
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(labelsize=9) 