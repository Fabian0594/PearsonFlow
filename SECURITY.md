# Guía de Seguridad - PearsonFlow

## 🔐 Configuración Segura de Credenciales

### Configuración Inicial

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

### 🚨 Archivos Protegidos

Los siguientes archivos están **excluidos del control de versiones** por seguridad:

- `config.py` - Configuración con credenciales reales
- `credentials.json` - Archivos de credenciales JSON
- `secrets.py` - Archivos con secretos
- `*mongodb_connection*` - Archivos de conexión MongoDB
- `*mongo_credentials*` - Archivos de credenciales MongoDB
- `*db_config*` - Archivos de configuración de base de datos

### 🛠️ Scripts de Acceso Seguro

#### Acceso Rápido a MongoDB
```bash
python quick_mongodb_access.py
```
Este script:
- ✅ Carga credenciales de forma segura desde `config.py`
- ✅ Lista colecciones disponibles
- ✅ Permite seleccionar una colección interactivamente
- ✅ Lanza PearsonFlow con la colección seleccionada

#### Verificación de Conexión
```bash
python test_mongodb_connection.py
```

#### Inserción de Datos de Prueba
```bash
python insert_to_peasonflow.py
```

### 📁 Estructura de Archivos de Configuración

```
PearsonFlow/
├── config.example.py          # ✅ Plantilla (incluida en Git)
├── config.py                  # ❌ Credenciales reales (excluida de Git)
├── quick_mongodb_access.py    # ✅ Script de acceso seguro
└── .gitignore                 # ✅ Configurado para excluir credenciales
```

### 🔒 Mejores Prácticas

1. **Nunca commits credenciales:**
   - Siempre usa `config.py` para credenciales reales
   - Mantén `config.example.py` como plantilla sin credenciales

2. **Verifica el .gitignore:**
   ```bash
   git status
   ```
   El archivo `config.py` NO debe aparecer en la lista de archivos a commitear

3. **Usa variables de entorno en producción:**
   ```python
   import os
   MONGODB_CONFIG = {
       "connection_string": os.getenv("MONGODB_URI"),
       "database_name": os.getenv("MONGODB_DB", "PeasonFlow")
   }
   ```

### 🚀 Uso en Desarrollo

1. **Primera vez:**
   ```bash
   cp config.example.py config.py
   # Editar config.py con tus credenciales
   python quick_mongodb_access.py
   ```

2. **Uso diario:**
   ```bash
   python quick_mongodb_access.py
   ```

### 🔧 Solución de Problemas

#### Error: "No se encontró config.py"
```bash
cp config.example.py config.py
# Editar config.py con las credenciales correctas
```

#### Error de conexión a MongoDB
1. Verifica las credenciales en `config.py`
2. Verifica la conectividad de red
3. Ejecuta: `python test_mongodb_connection.py`

#### Credenciales expuestas accidentalmente
1. **Inmediatamente:**
   ```bash
   git reset --soft HEAD~1  # Si no has hecho push
   ```
2. **Si ya hiciste push:**
   - Cambia las credenciales en MongoDB Atlas
   - Actualiza `config.py` con las nuevas credenciales
   - Considera usar `git filter-branch` para limpiar el historial

### 📞 Contacto de Seguridad

Si encuentras vulnerabilidades de seguridad, por favor:
1. NO abras un issue público
2. Contacta directamente al equipo de desarrollo
3. Proporciona detalles específicos del problema

---

**Recuerda:** La seguridad es responsabilidad de todos. Mantén tus credenciales seguras y nunca las compartas en repositorios públicos. 