# PearsonFlow

Visualizador de datos con funcionalidades de análisis e inteligencia artificial.

## Características

- Carga y visualización de datos CSV
- Múltiples tipos de gráficos para visualización de datos
- Modelos de IA integrados:
  - Pronóstico Lineal
  - Detección de Anomalías
  - Agrupamiento (Clustering)
- Interfaz gráfica intuitiva con selección de columnas

## Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clone el repositorio o descargue el código fuente
2. Instale las dependencias:

```
pip install -r requirements.txt
```

## Uso

Para iniciar la aplicación:

```
python main.py
```

Para cargar un archivo CSV directamente:

```
python main.py --file ruta/al/archivo.csv
```

Para activar el modo de depuración:

```
python main.py --debug
```

## Solución de problemas comunes

### Error "ufunc 'greater_equal' did not contain a loop with signature matching types"

Este error ocurre cuando hay una incompatibilidad de tipos de datos. Asegúrese de:

1. Seleccionar solo columnas numéricas para el análisis con modelos de IA
2. No incluir columnas con valores no numéricos o cadenas de texto

### Error "Unalignable boolean Series provided as indexer"

Este error ocurre al intentar indexar con una serie booleana que no tiene la misma longitud que los datos. Si aparece:

1. Asegúrese de que los datos CSV tienen formatos consistentes
2. Intente seleccionar menos columnas para el análisis
3. Verifique que no hay valores faltantes (NaN) en las columnas seleccionadas

## Créditos

Desarrollado como parte del proyecto PearsonFlow.
