import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class AIModel(ABC):
    """Clase abstracta base para todos los modelos de IA."""
    
    def __init__(self, name: str, description: str):
        """
        Inicializar un modelo de IA.
        
        Args:
            name: Nombre del modelo
            description: Descripción corta del modelo
        """
        self.name = name
        self.description = description
        self.is_fitted = False
        # Registro de tiempo de entrenamiento y predicción
        self.fit_time = 0
        self.predict_time = 0
    
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> None:
        """
        Entrenar el modelo con los datos.
        
        Args:
            data: DataFrame con los datos de entrenamiento
        """
        pass
    
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Realizar predicciones/transformaciones con el modelo.
        
        Args:
            data: DataFrame con los datos de entrada
            
        Returns:
            DataFrame con los resultados del modelo
        """
        pass
    
    @abstractmethod
    def plot(self, ax: plt.Axes, original_data: pd.DataFrame, 
            model_results: pd.DataFrame, x_values: Any) -> plt.Axes:
        """
        Visualizar los resultados del modelo.
        
        Args:
            ax: Ejes donde se dibujará el gráfico
            original_data: DataFrame con los datos originales
            model_results: DataFrame con los resultados del modelo
            x_values: Valores para el eje X
            
        Returns:
            Ejes actualizados con la visualización
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Obtener parámetros configurables del modelo.
        
        Returns:
            Diccionario con los parámetros y sus valores actuales
        """
        return {}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """
        Establecer parámetros del modelo.
        
        Args:
            params: Diccionario con los parámetros a establecer
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Valida y preprocesa los datos antes de utilizarlos.
        
        Args:
            data: DataFrame a validar
            
        Returns:
            DataFrame procesado y listo para usar
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Los datos deben ser un DataFrame de pandas")
        
        if data.empty:
            raise ValueError("El DataFrame está vacío")
        
        # Verificar columnas numéricas
        numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) == 0:
            raise ValueError("No hay columnas numéricas en los datos")
            
        return data


class LinearForecastModel(AIModel):
    """Modelo de pronóstico basado en regresión lineal."""
    
    def __init__(self, forecast_periods: int = 10):
        """
        Inicializar el modelo de pronóstico.
        
        Args:
            forecast_periods: Número de períodos a pronosticar
        """
        super().__init__(
            name="Pronóstico Lineal", 
            description="Predice valores futuros usando regresión lineal"
        )
        self.forecast_periods = forecast_periods
        self.model = LinearRegression()
        self.feature_names = []
        self.target_names = []
        
    def fit(self, data: pd.DataFrame) -> None:
        """
        Entrenar el modelo con los datos.
        
        Args:
            data: DataFrame con los datos de entrenamiento
        """
        if len(data.columns) < 1:
            raise ValueError("Se requiere al menos una columna numérica para el pronóstico")
            
        # Guardar nombres de columnas
        self.feature_names = ['time_index']
        self.target_names = data.columns.tolist()
        
        # Preparar X (índice de tiempo) e Y (valores a predecir)
        X = np.array(range(len(data))).reshape(-1, 1)
        y = data.values
        
        # Entrenar el modelo
        self.model.fit(X, y)
        self.is_fitted = True
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Realizar pronósticos con el modelo.
        
        Args:
            data: DataFrame con los datos de entrada
            
        Returns:
            DataFrame con los pronósticos
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado antes de hacer predicciones")
        
        # Crear índices para pronóstico
        last_index = len(data) - 1
        forecast_indices = np.array(range(last_index + 1, last_index + self.forecast_periods + 1))
        
        # Preparar X para pronóstico
        X_forecast = forecast_indices.reshape(-1, 1)
        
        # Hacer predicciones
        y_forecast = self.model.predict(X_forecast)
        
        # Crear DataFrame con resultados
        forecast_df = pd.DataFrame(y_forecast, columns=self.target_names)
        forecast_df.index = forecast_indices
        
        return forecast_df
    
    def plot(self, ax: plt.Axes, original_data: pd.DataFrame, 
            model_results: pd.DataFrame, x_values: Any) -> plt.Axes:
        """
        Visualizar los resultados del modelo.
        
        Args:
            ax: Ejes donde se dibujará el gráfico
            original_data: DataFrame con los datos originales
            model_results: DataFrame con los pronósticos
            x_values: Valores para el eje X
            
        Returns:
            Ejes actualizados con la visualización
        """
        # Graficar datos originales
        for i, column in enumerate(original_data.columns):
            ax.plot(x_values, original_data[column], 
                   label=column, 
                   marker='o', 
                   markersize=4,
                   linewidth=2)
        
        # Crear valores X para pronósticos (extensión de los valores originales)
        if isinstance(x_values, pd.DatetimeIndex) or isinstance(x_values, pd.Series):
            # Si los valores originales son fechas, extender con fechas futuras
            last_date = x_values[-1]
            if isinstance(last_date, pd.Timestamp):
                # Calcular el paso promedio entre fechas
                if len(x_values) > 1:
                    avg_delta = (x_values[-1] - x_values[0]) / (len(x_values) - 1)
                    forecast_x = [last_date + (i+1) * avg_delta for i in range(self.forecast_periods)]
                else:
                    # Si solo hay una fecha, asumir días como unidad
                    import datetime
                    forecast_x = [last_date + datetime.timedelta(days=i+1) for i in range(self.forecast_periods)]
            else:
                # Para otros tipos, usar índice numérico
                forecast_x = range(len(x_values), len(x_values) + self.forecast_periods)
        else:
            # Para valores no temporales, simplemente extender el rango
            if isinstance(x_values, range):
                last_x = max(x_values)
                forecast_x = range(last_x + 1, last_x + self.forecast_periods + 1)
            else:
                forecast_x = range(len(x_values), len(x_values) + self.forecast_periods)
        
        # Graficar pronósticos
        for i, column in enumerate(model_results.columns):
            ax.plot(forecast_x, model_results[column], 
                   label=f"{column} (Pronóstico)", 
                   marker='x', 
                   markersize=5,
                   linestyle='--',
                   linewidth=2)
        
        # Añadir área sombreada para indicar pronóstico
        try:
            # Obtener solo datos numéricos para calcular mínimos y máximos
            original_numeric = original_data.select_dtypes(include=['number'])
            model_numeric = model_results.select_dtypes(include=['number'])
            
            if not original_numeric.empty and not model_numeric.empty:
                min_original = original_numeric.min().min()
                max_original = original_numeric.max().max()
                min_model = model_numeric.min().min()
                max_model = model_numeric.max().max()
                
                min_y = min(min_original, min_model)
                max_y = max(max_original, max_model)
                margin = (max_y - min_y) * 0.1  # 10% de margen
                
                # Establecer límites del eje Y con margen
                ax.set_ylim(min_y - margin, max_y + margin)
            
            if isinstance(x_values, range) or isinstance(forecast_x, range):
                min_forecast_x = min(forecast_x)
                max_forecast_x = max(forecast_x)
                ax.axvspan(min_forecast_x, max_forecast_x, alpha=0.1, color='gray')
        except Exception as e:
            # Si hay un error en el cálculo de límites, continuar sin establecerlos
            print(f"Advertencia: No se pudieron calcular los límites del gráfico: {e}")
        
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_title("Datos históricos y pronóstico", fontweight='bold')
        
        # Añadir leyenda
        ax.legend(title="Variables", fontsize=9)
        
        return ax
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Obtener parámetros configurables del modelo.
        
        Returns:
            Diccionario con los parámetros y sus valores actuales
        """
        return {
            "forecast_periods": self.forecast_periods
        }
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """
        Establecer parámetros del modelo.
        
        Args:
            params: Diccionario con los parámetros a establecer
        """
        if "forecast_periods" in params:
            self.forecast_periods = int(params["forecast_periods"])


class AnomalyDetectionModel(AIModel):
    """Modelo para detección de anomalías basado en Isolation Forest."""
    
    def __init__(self, contamination: float = 0.05):
        """
        Inicializar el modelo de detección de anomalías.
        
        Args:
            contamination: Proporción esperada de anomalías en los datos (entre 0 y 0.5)
        """
        super().__init__(
            name="Detección de Anomalías", 
            description="Identifica valores atípicos en los datos"
        )
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
    
    def fit(self, data: pd.DataFrame) -> None:
        """
        Entrenar el modelo con los datos.
        
        Args:
            data: DataFrame con los datos de entrenamiento
        """
        if len(data.columns) < 1:
            raise ValueError("Se requiere al menos una columna numérica")
            
        # Normalizar datos
        X = self.scaler.fit_transform(data.values)
        
        # Entrenar el modelo
        self.model.fit(X)
        self.is_fitted = True
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detectar anomalías en los datos.
        
        Args:
            data: DataFrame con los datos de entrada
            
        Returns:
            DataFrame con las anomalías detectadas (1 para normal, -1 para anomalía)
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado antes de detectar anomalías")
        
        # Normalizar datos
        X = self.scaler.transform(data.values)
        
        # Detectar anomalías
        predictions = self.model.predict(X)
        scores = self.model.decision_function(X)
        
        # Crear DataFrame con resultados
        results = pd.DataFrame({
            'es_anomalia': predictions == -1,
            'score': scores
        })
        
        return results
    
    def plot(self, ax: plt.Axes, original_data: pd.DataFrame, 
            model_results: pd.DataFrame, x_values: Any) -> plt.Axes:
        """
        Visualizar las anomalías detectadas.
        
        Args:
            ax: Ejes donde se dibujará el gráfico
            original_data: DataFrame con los datos originales
            model_results: DataFrame con los resultados (es_anomalia, score)
            x_values: Valores para el eje X
            
        Returns:
            Ejes actualizados con la visualización
        """
        # Graficar cada columna y marcar anomalías
        for i, column in enumerate(original_data.columns):
            # Graficar serie normal
            ax.plot(x_values, original_data[column], 
                   label=column, 
                   marker='o', 
                   markersize=4,
                   linewidth=2,
                   alpha=0.7)
            
            # Marcar anomalías
            anomalies = model_results['es_anomalia']
            if anomalies.any():
                ax.scatter(
                    [x_values[i] for i in range(len(anomalies)) if anomalies[i]], 
                    [original_data[column].iloc[i] for i in range(len(anomalies)) if anomalies[i]],
                    color='red',
                    s=80,
                    marker='X',
                    label=f'{column} Anomalías' if i == 0 else "",
                    zorder=5
                )
        
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_title("Detección de Anomalías", fontweight='bold')
        
        # Añadir leyenda
        ax.legend(title="Variables", fontsize=9)
        
        return ax
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Obtener parámetros configurables del modelo.
        
        Returns:
            Diccionario con los parámetros y sus valores actuales
        """
        return {
            "contamination": self.contamination
        }
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """
        Establecer parámetros del modelo.
        
        Args:
            params: Diccionario con los parámetros a establecer
        """
        if "contamination" in params:
            self.contamination = float(params["contamination"])
            if self.is_fitted:
                # Reiniciar el modelo con nuevos parámetros
                self.model = IsolationForest(contamination=self.contamination, random_state=42)
                self.is_fitted = False


class ClusteringModel(AIModel):
    """Modelo para agrupamiento de datos basado en K-Means."""
    
    def __init__(self, n_clusters: int = 3):
        """
        Inicializar el modelo de agrupamiento.
        
        Args:
            n_clusters: Número de grupos a formar
        """
        super().__init__(
            name="Agrupamiento (Clustering)", 
            description="Agrupa datos similares en clusters"
        )
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.column_names = []
    
    def fit(self, data: pd.DataFrame) -> None:
        """
        Entrenar el modelo con los datos.
        
        Args:
            data: DataFrame con los datos de entrenamiento
            
        Raises:
            ValueError: Si no hay suficientes datos o columnas
        """
        # Validar datos
        data = self.validate_data(data)
        
        if len(data.columns) < 1:
            raise ValueError("Se requiere al menos una columna numérica")
        
        if len(data) < self.n_clusters:
            # Ajustar automáticamente el número de clusters si hay pocos datos
            self.n_clusters = max(2, min(len(data) // 2, self.n_clusters))
            self.model = KMeans(n_clusters=self.n_clusters, random_state=42)
            
        # Guardar nombres de columnas para referencias futuras
        self.column_names = data.columns.tolist()
        
        # Normalizar datos con manejo de errores
        try:
            # Usar solo columnas numéricas
            numeric_data = data.select_dtypes(include=['int64', 'float64'])
            if numeric_data.empty:
                raise ValueError("No hay columnas numéricas para clustering")
                
            self.column_names = numeric_data.columns.tolist()
            X = self.scaler.fit_transform(numeric_data.values)
            
            import time
            start_time = time.time()
            # Entrenar el modelo con timeout para evitar bloqueos
            self.model.fit(X)
            self.fit_time = time.time() - start_time
            
            self.is_fitted = True
            
        except Exception as e:
            self.is_fitted = False
            raise ValueError(f"Error al entrenar el modelo: {str(e)}")
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Asignar clusters a los datos.
        
        Args:
            data: DataFrame con los datos de entrada
            
        Returns:
            DataFrame con los clusters asignados
            
        Raises:
            ValueError: Si el modelo no ha sido entrenado o hay problemas con los datos
        """
        if not self.is_fitted:
            raise ValueError("El modelo debe ser entrenado antes de asignar clusters")
            
        if not self.column_names:
            raise ValueError("No hay columnas definidas para el modelo")
        
        # Verificar que todas las columnas necesarias están disponibles
        missing_cols = [col for col in self.column_names if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Faltan columnas requeridas en los datos: {missing_cols}")
        
        # Utilizar solo las columnas originales en el mismo orden
        data_subset = data[self.column_names].copy()
        
        # Manejar valores NaN
        if data_subset.isnull().values.any():
            data_subset = data_subset.fillna(data_subset.mean())
        
        # Normalizar datos
        try:
            X = self.scaler.transform(data_subset.values)
            
            import time
            start_time = time.time()
            # Asignar clusters
            clusters = self.model.predict(X)
            self.predict_time = time.time() - start_time
            
            # Obtener centroides transformados a escala original
            centroides_norm = self.model.cluster_centers_
            centroides = self.scaler.inverse_transform(centroides_norm)
            
            # Crear DataFrame con resultados
            results = pd.DataFrame({
                'cluster': clusters
            })
            
            # Añadir distancia al centroide
            for i in range(self.n_clusters):
                centroide_i = centroides_norm[i]
                results[f'dist_cluster_{i}'] = [
                    np.sqrt(np.sum((self.scaler.transform([data_subset.iloc[j].values])[0] - centroide_i) ** 2))
                    for j in range(len(data_subset))
                ]
            
            return results
            
        except Exception as e:
            raise ValueError(f"Error al predecir clusters: {str(e)}")
    
    def plot(self, ax: plt.Axes, original_data: pd.DataFrame, 
            model_results: pd.DataFrame, x_values: Any) -> plt.Axes:
        """
        Visualizar los clusters detectados.
        
        Args:
            ax: Ejes donde se dibujará el gráfico
            original_data: DataFrame con los datos originales
            model_results: DataFrame con los resultados (cluster, distancias)
            x_values: Valores para el eje X
            
        Returns:
            Ejes actualizados con la visualización
        """
        try:
            # Verificar que tenemos las columnas necesarias
            available_columns = set(original_data.columns)
            usable_columns = [col for col in self.column_names if col in available_columns]
            
            if not usable_columns:
                # Si no hay columnas utilizables, usar cualquier columna numérica
                usable_columns = original_data.select_dtypes(include=['int64', 'float64']).columns[:2].tolist()
                if len(usable_columns) == 0:
                    raise ValueError("No hay columnas numéricas para visualizar")
            
            # Asegurarse que model_results y original_data tienen la misma longitud
            if len(model_results) != len(original_data):
                # Usar el menor de los dos
                min_len = min(len(original_data), len(model_results))
                original_data = original_data.iloc[:min_len].copy()
                model_results = model_results.iloc[:min_len].copy()
            
            # Asegurarse de que la columna cluster es numérica
            if 'cluster' in model_results.columns and not pd.api.types.is_numeric_dtype(model_results['cluster']):
                model_results['cluster'] = pd.to_numeric(model_results['cluster'], errors='coerce')
                # Rellenar NaN con 0 si hay errores en la conversión
                model_results['cluster'] = model_results['cluster'].fillna(0).astype(int)
            
            # Si hay más de una columna, intentar hacer scatter plot
            if len(usable_columns) >= 2:
                # Usar las dos primeras columnas para el scatter plot
                x_col = usable_columns[0]
                y_col = usable_columns[1]
                
                # Colores para los clusters
                colors = plt.cm.tab10(np.linspace(0, 1, self.n_clusters))
                
                # Graficar puntos por cluster
                for cluster_id in range(self.n_clusters):
                    # Manejar posibles problemas de tipos de datos
                    try:
                        # Intentar crear la máscara de manera segura
                        cluster_column = model_results['cluster']
                        if pd.api.types.is_numeric_dtype(cluster_column):
                            mask = cluster_column == cluster_id
                        else:
                            mask = cluster_column.astype(str) == str(cluster_id)
                            
                        # Verificar que la máscara es válida
                        if not isinstance(mask, pd.Series):
                            mask = pd.Series([False] * len(model_results))
                            
                        # Verificar que hay datos para este cluster
                        if not mask.any():
                            continue
                            
                        # Extraer indices donde mask es True
                        mask_indices = mask[mask].index.tolist()
                        
                        # Usar esos indices para obtener los valores correspondientes
                        x_values_cluster = original_data.loc[mask_indices, x_col]
                        y_values_cluster = original_data.loc[mask_indices, y_col]
                        
                        ax.scatter(
                            x_values_cluster,
                            y_values_cluster,
                            label=f'Cluster {cluster_id}',
                            color=colors[cluster_id],
                            alpha=0.7,
                            edgecolors='w',
                            s=50
                        )
                    except Exception as e:
                        print(f"Error al representar el cluster {cluster_id}: {str(e)}")
                        continue
                
                # Graficar centroides (si hay datos suficientes)
                if len(original_data) >= 2 and self.is_fitted:
                    try:
                        centroides_norm = self.model.cluster_centers_
                        centroides_orig = self.scaler.inverse_transform(centroides_norm)
                        
                        for i, centroide in enumerate(centroides_orig):
                            if i < len(colors) and len(centroide) >= 2:
                                ax.scatter(
                                    centroide[0],
                                    centroide[1],
                                    marker='*',
                                    s=200,
                                    color=colors[i],
                                    edgecolors='k',
                                    label=f'Centroide {i}'
                                )
                    except Exception:
                        # Si no se pueden mostrar los centroides, continuar sin ellos
                        pass
                
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                
                # Añadir información de rendimiento si está disponible
                if self.fit_time > 0:
                    performance_text = f"Entrenamiento: {self.fit_time:.2f}s | Predicción: {self.predict_time:.4f}s"
                    ax.annotate(performance_text, xy=(0.01, 0.01), xycoords='axes fraction',
                                fontsize=8, alpha=0.6)
                    
            else:
                # Para una sola columna, usar gráfico de barras o líneas
                column = usable_columns[0] if usable_columns else original_data.columns[0]
                
                # Colores para los clusters
                colors = plt.cm.tab10(np.linspace(0, 1, self.n_clusters))
                
                for cluster_id in range(self.n_clusters):
                    try:
                        # Crear máscara de manera segura
                        cluster_column = model_results['cluster']
                        if pd.api.types.is_numeric_dtype(cluster_column):
                            mask = cluster_column == cluster_id
                        else:
                            mask = cluster_column.astype(str) == str(cluster_id)
                        
                        # Verificar que hay puntos en este cluster
                        if not mask.any():
                            continue
                        
                        # Crear lista de índices en lugar de usar la máscara directamente
                        mask_indices = np.where(mask)[0]
                        
                        # Manejar diferentes tipos de x_values
                        if isinstance(x_values, pd.Series) and len(x_values) >= len(mask):
                            x_vals = [x_values.iloc[i] for i in mask_indices if i < len(x_values)]
                        elif isinstance(x_values, range) and len(x_values) >= len(mask):
                            x_vals = [x_values[i] for i in mask_indices if i < len(x_values)]
                        else:
                            # Usar índice simple como respaldo
                            x_vals = mask_indices
                        
                        # Extraer valores y para este cluster de manera segura
                        y_vals = [original_data[column].iloc[i] for i in mask_indices if i < len(original_data)]
                            
                        # Verificar que tenemos suficientes puntos para graficar
                        if len(x_vals) > 0 and len(y_vals) > 0:
                            min_len = min(len(x_vals), len(y_vals))
                            ax.scatter(
                                x_vals[:min_len],
                                y_vals[:min_len],
                                label=f'Cluster {cluster_id}',
                                color=colors[cluster_id],
                                alpha=0.7,
                                edgecolors='w',
                                s=50
                            )
                    except Exception as e:
                        print(f"Error al representar el cluster {cluster_id}: {str(e)}")
                        continue
            
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.set_title("Agrupamiento de Datos (Clustering)", fontweight='bold')
            
            # Añadir leyenda si hay suficientes elementos
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(title="Clusters", fontsize=9)
            
        except Exception as e:
            # En caso de error en la visualización, mostrar un mensaje en el gráfico
            ax.text(0.5, 0.5, f"Error al visualizar clusters: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Error en la visualización", fontweight='bold', color='red')
        
        return ax
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Obtener parámetros configurables del modelo.
        
        Returns:
            Diccionario con los parámetros y sus valores actuales
        """
        return {
            "n_clusters": self.n_clusters
        }
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """
        Establecer parámetros del modelo.
        
        Args:
            params: Diccionario con los parámetros a establecer
        """
        if "n_clusters" in params:
            try:
                n_clusters = int(params["n_clusters"])
                if n_clusters < 2:
                    n_clusters = 2  # Asegurarse de que hay al menos 2 clusters
                self.n_clusters = n_clusters
                
                if self.is_fitted:
                    # Reiniciar el modelo con nuevos parámetros
                    self.model = KMeans(n_clusters=self.n_clusters, random_state=42)
                    self.is_fitted = False
            except (ValueError, TypeError):
                # Ignorar valores inválidos
                pass


class ModelFactory:
    """Fábrica para crear modelos de IA."""
    
    @staticmethod
    def get_available_models() -> List[Dict[str, Any]]:
        """
        Obtener la lista de modelos disponibles.
        
        Returns:
            Lista de diccionarios con información de los modelos
        """
        return [
            {
                'id': 'linear_forecast',
                'name': 'Pronóstico Lineal',
                'description': 'Predice valores futuros usando regresión lineal',
                'class': LinearForecastModel
            },
            {
                'id': 'anomaly_detection',
                'name': 'Detección de Anomalías',
                'description': 'Identifica valores atípicos en los datos',
                'class': AnomalyDetectionModel
            },
            {
                'id': 'clustering',
                'name': 'Agrupamiento (Clustering)',
                'description': 'Agrupa datos similares en clusters',
                'class': ClusteringModel
            }
        ]
    
    @staticmethod
    def create_model(model_id: str, **kwargs) -> AIModel:
        """
        Crear una instancia de un modelo específico.
        
        Args:
            model_id: Identificador del modelo
            **kwargs: Parámetros adicionales para el modelo
            
        Returns:
            Instancia del modelo solicitado
            
        Raises:
            ValueError: Si el modelo no existe
        """
        models = {model['id']: model['class'] for model in ModelFactory.get_available_models()}
        
        if model_id not in models:
            raise ValueError(f"Modelo no reconocido: {model_id}")
            
        model_class = models[model_id]
        return model_class(**kwargs) 