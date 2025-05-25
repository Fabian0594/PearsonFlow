# Archivo de configuración de ejemplo para PearsonFlow
# Copia este archivo como 'config.py' y completa con tus credenciales reales

# Configuración de MongoDB
MONGODB_CONFIG = {
    "connection_string": "mongodb+srv://usuario:password@cluster.mongodb.net/",
    "database_name": "PeasonFlow",
    "default_collection": "datos_prueba"
}

# Configuración de la aplicación
APP_CONFIG = {
    "debug_mode": False,
    "log_level": "INFO",
    "cache_enabled": True
}

# Configuración de archivos
FILE_CONFIG = {
    "default_data_dir": "data/",
    "temp_dir": "data/temp/",
    "log_dir": "logs/"
} 