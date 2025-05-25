# PearsonFlow

Visualizador de datos con funcionalidades de análisis e inteligencia artificial.

## Características

- Carga y visualización de datos desde:
  - Archivos CSV
  - Bases de datos MongoDB (integración con MongoDB Atlas)
- Múltiples tipos de gráficos para visualización de datos:
  - Gráficos de dispersión
  - Histogramas
  - Diagramas de barras
  - Gráficos de líneas
  - Diagramas de caja (box plots)
  - Mapas de calor (heatmaps)
- Análisis estadístico automático
- Modelos de IA integrados:
  - Pronóstico Lineal
  - Detección de Anomalías
  - Agrupamiento (Clustering)
  - Análisis de Correlación
- Interfaz gráfica intuitiva con selección de columnas
- Exportación de resultados y gráficos

## Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`
- MongoDB (opcional, solo si se utiliza esta fuente de datos)

## Instalación

1. Clone el repositorio o descargue el código fuente:
```bash
git clone https://github.com/username/PearsonFlow.git
cd PearsonFlow
```

2. Instale las dependencias:
```bash
pip install -r requirements.txt
```

## 🔐 Configuración Segura (IMPORTANTE)

**Para proteger tus credenciales de MongoDB, sigue estos pasos:**

### Configuración Inicial de Credenciales

1. **Copia el archivo de configuración de ejemplo:**
   ```bash
   cp config.example.py config.py
   ```

2. **Edita `config.py` con tus credenciales reales:**
   ```python
   MONGODB_CONFIG = {
       "connection_string": "tu_cadena_de_conexion_mongodb",
       "database_name": "tu_base_de_datos",
       "default_collection": "tu_coleccion_por_defecto"
   }
   ```

3. **¡IMPORTANTE!** El archivo `config.py` está excluido del control de versiones por seguridad.

### Acceso Rápido y Seguro a MongoDB

**Usa el script de acceso rápido (recomendado):**
```bash
python quick_mongodb_access.py
```

Este script:
- ✅ Carga credenciales de forma segura
- ✅ Lista colecciones disponibles
- ✅ Permite seleccionar una colección interactivamente
- ✅ Lanza PearsonFlow automáticamente

### Scripts de Utilidad Seguros

- **Verificar conexión:** `python test_mongodb_connection.py`
- **Insertar datos de prueba:** `python insert_to_peasonflow.py`
- **Verificar estado de la base de datos:** `python check_mongodb.py`

📖 **Para más detalles de seguridad, consulta [SECURITY.md](SECURITY.md)**

## Estructura del Proyecto

```
PearsonFlow/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Este archivo
├── core/                   # Módulos principales
│   ├── data_loader.py      # Interfaz base para carga de datos
│   ├── csv_loader.py       # Cargador específico para CSV
│   ├── mongo_loader.py     # Cargador específico para MongoDB
│   ├── data_repository.py  # Repositorio central de datos
│   ├── data_visualizer.py  # Generador de visualizaciones
│   ├── chart_factory.py    # Fábrica de gráficos
│   └── ai_models.py        # Modelos de IA
├── gui/                    # Interfaz gráfica
│   ├── app.py              # Aplicación principal
│   ├── load_window.py      # Ventana de carga de datos
│   └── visualizer_window.py# Ventana de visualización
├── utils/                  # Utilidades
│   └── csv_validator.py    # Validador de archivos CSV
└── data/                   # Directorio para datos de ejemplo
```

## Uso

### Iniciar la aplicación

Para iniciar la aplicación con la interfaz gráfica:

```bash
python main.py
```

### Cargar desde archivo CSV

Para cargar un archivo CSV directamente:

```bash
python main.py --file ruta/al/archivo.csv
```

### Cargar desde MongoDB

#### **Comandos para acceder a MongoDB:**

**Opción 1: Comando directo con colección específica**
```bash
python main.py --mongodb "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/;PeasonFlow;datos_prueba"
```

**Opción 2: Comando para seleccionar colección (recomendado)**
```bash
python main.py --mongodb "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/;PeasonFlow;"
```

**Opción 3: Interfaz gráfica**
```bash
python main.py
```
Luego:
1. Selecciona "MongoDB" como fuente de datos
2. Usa el botón "Ir a la base de datos de MongoDB" para acceso rápido
3. O haz clic en "Conectar a MongoDB"

#### **Formato del parámetro MongoDB:**
El formato es: `"uri;database;collection"` donde:
- **uri**: `mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/`
- **database**: `PeasonFlow` (nombre de la base de datos)
- **collection**: nombre de la colección (opcional, ej: `datos_prueba`)

Si no se especifica la colección, se mostrará una interfaz para seleccionarla.

#### **Verificar conexión a MongoDB:**
Para verificar qué bases de datos y colecciones están disponibles:
```bash
python check_mongodb.py
```

### Otras opciones

Para activar el modo de depuración con logs detallados:

```bash
python main.py --debug
```

## Nuevas Mejoras

La versión actual incluye varias mejoras respecto a versiones anteriores:

### **Código Limpio y Documentado**
- **Comentarios profesionales**: Todo el código ahora incluye comentarios claros y concisos que explican la funcionalidad sin ser excesivos
- **Documentación de métodos**: Cada función y método tiene docstrings detallados con parámetros, valores de retorno y excepciones
- **Tipado completo**: Anotaciones de tipo para facilitar el desarrollo y documentación
- **Patrones de diseño documentados**: Identificación clara de patrones como Factory, Strategy, Repository, etc.

### **Arquitectura Mejorada**
- **Mejor manejo de errores**: Sistema de logging completo y manejo de excepciones robusto
- **Modularidad**: Código refactorizado para mayor claridad y mantenibilidad
- **Optimización**: Carga más eficiente de datos y mejor rendimiento
- **Context Managers**: Soporte para `with` en los cargadores de datos
- **Validación mejorada**: Validación más robusta de fuentes de datos
- **Consistencia**: Convenciones de código y estructura uniformes

### **Funcionalidades Técnicas**
- **Cache inteligente**: Sistema de cache automático para mejorar rendimiento
- **Lazy loading**: Carga de datos solo cuando es necesario
- **Detección automática**: Detección de delimitadores en archivos CSV
- **Manejo de memoria**: Gestión eficiente de recursos y limpieza automática
- **Logging estructurado**: Sistema de logs con diferentes niveles de detalle

### **Comentarios Implementados**
Los comentarios agregados siguen estas pautas profesionales:
- **Propósito claro**: Explican el "por qué" no solo el "qué"
- **Contexto técnico**: Identifican patrones de diseño y decisiones arquitectónicas
- **Información útil**: Proporcionan detalles sobre parámetros, excepciones y comportamiento
- **Mantenibilidad**: Facilitan futuras modificaciones y debugging
- **Sin redundancia**: Evitan comentarios obvios o repetitivos

## Solución de problemas comunes

### Error "No hay colecciones disponibles" en MongoDB

**Problema resuelto**: Este error ocurría porque el código buscaba en la base de datos incorrecta.

**Solución**: 
- La base de datos correcta es `PeasonFlow` (no `PeasonFlowDB`)
- La colección disponible es `datos_prueba`
- Use los comandos MongoDB especificados en la sección de uso

**Para verificar las colecciones disponibles:**
```bash
python check_mongodb.py
```

Este comando mostrará todas las bases de datos y colecciones disponibles en su instancia de MongoDB.

### Error de conexión a MongoDB

Si no puede conectarse a MongoDB:

1. Verifique que el servidor de MongoDB esté en ejecución
2. Compruebe que la URI de conexión, nombre de base de datos y colección sean correctos
3. Asegúrese de tener permisos para acceder a la base de datos
4. Verifique que pymongo esté instalado correctamente
5. Active el modo de depuración para ver mensajes de error detallados:
   ```bash
   python main.py --debug --mongodb "uri;database;collection"
   ```

### Error al cargar archivos CSV

Si tiene problemas al cargar archivos CSV:

1. Verifique que el archivo existe y tiene permisos de lectura
2. Asegúrese de que el formato del CSV es correcto (delimitadores, codificación)
3. Revise que el archivo no esté vacío o corrupto
4. Intente especificar manualmente el delimitador si no es una coma estándar

### Problemas con modelos de IA

Para evitar errores con los modelos de IA:

1. Seleccione solo columnas numéricas para el análisis
2. Elimine o trate los valores faltantes antes del análisis
3. Asegúrese de tener suficientes datos para el tipo de análisis seleccionado

## Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. Haga un fork del repositorio
2. Cree una rama para su característica (`git checkout -b feature/nueva-caracteristica`)
3. Realice sus cambios y haga commit (`git commit -m 'Añadir nueva característica'`)
4. Haga push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abra un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para más detalles.

## Créditos

Desarrollado como parte del proyecto PearsonFlow.
