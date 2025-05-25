#!/usr/bin/env python3
"""
PearsonFlow - Visualizador de datos con IA
-------------------------------------------
Aplicación para análisis y visualización de datos con funcionalidades de IA.
"""

import sys
import os
import logging
import traceback
import argparse
from typing import Optional, Union

# Importar dependencias específicas al inicio
try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Configurar el backend no interactivo
except ImportError as e:
    logging.warning(f"Advertencia en importación: {str(e)}")

# Constantes
DB_NAME = "PeasonFlow"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def setup_environment() -> None:
    """Configura el entorno de ejecución para un rendimiento óptimo."""
    # Configuraciones de NumPy para ignorar advertencias comunes
    if 'np' in globals():
        np.seterr(divide='ignore', invalid='ignore')
    
    # Otras configuraciones de entorno que puedan ser necesarias
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def configure_logging(debug_mode: bool) -> None:
    """Configura el sistema de logging basado en el modo de ejecución.
    
    Args:
        debug_mode: Si True, configura logging en modo DEBUG, de lo contrario INFO
    """
    level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT)
    
    if debug_mode:
        logging.debug("Modo de depuración activado")

def parse_args() -> argparse.Namespace:
    """Analiza los argumentos de línea de comandos.
    
    Returns:
        Namespace con los argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='PearsonFlow - Visualizador de datos con IA',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Grupo mutuamente excluyente para fuentes de datos
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        '--file', '-f', 
        help='Ruta al archivo CSV para cargar automáticamente'
    )
    source_group.add_argument(
        '--mongodb', '-m', 
        help='Especificar datos de conexión a MongoDB en formato "uri;database;collection"'
    )
    
    # Otras opciones
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Activar modo de depuración'
    )
    
    return parser.parse_args()

def setup_file_data_source(file_path: str) -> Optional[str]:
    """Configura una fuente de datos basada en archivos.
    
    Args:
        file_path: Ruta al archivo de datos
        
    Returns:
        Identificador de la fuente de datos o None si hubo un error
    """
    if not os.path.exists(file_path):
        logging.error(f"El archivo no existe: {file_path}")
        return None
    
    if not os.path.isfile(file_path):
        logging.error(f"La ruta no corresponde a un archivo: {file_path}")
        return None
    
    logging.info(f"Usando archivo: {file_path}")
    return file_path

def setup_mongodb_data_source(mongodb_conn_string: str) -> Optional[str]:
    """Configura una fuente de datos basada en MongoDB.
    
    Args:
        mongodb_conn_string: Cadena de conexión en formato "uri;database;collection"
        
    Returns:
        Identificador de la fuente de datos o None si hubo un error
    """
    # Importar aquí para no requerir MongoDB si no se usa
    try:
        from core.mongo_loader import MongoDBLoader
    except ImportError:
        logging.error("No se pudo importar el módulo MongoDBLoader. Verifique que las dependencias estén instaladas.")
        return None
    
    # Analizar cadena de conexión
    parts = mongodb_conn_string.split(';')
    if len(parts) < 1:
        logging.error("Error: El formato para MongoDB debe ser 'uri;database;collection'")
        return None
    
    conn_string = parts[0]
    collection_name = parts[2] if len(parts) > 2 else None
    
    logging.info(f"Intentando conectar a MongoDB: {conn_string}")
    logging.info(f"Base de datos: {DB_NAME}")
    
    # Intentar conexión
    try:
        mongo_loader = MongoDBLoader(conn_string, DB_NAME)
        
        if not mongo_loader.connect():
            logging.error(f"Error: No se pudo conectar a la base de datos MongoDB: {DB_NAME}")
            return None
        
        logging.info("Conexión exitosa a MongoDB")
        
        # Listar colecciones disponibles
        collections = mongo_loader.list_collections()
        if not collections:
            logging.warning("No hay colecciones disponibles en esta base de datos.")
            return None
        
        logging.info(f"Colecciones disponibles en {DB_NAME}:")
        for i, coll in enumerate(collections, 1):
            logging.info(f"{i}. {coll}")
        
        # Verificar/configurar colección
        if not collection_name:
            logging.info("No se especificó colección. Iniciando interfaz gráfica para seleccionar una colección.")
            return f"mongodb://{DB_NAME}"
        
        if collection_name not in collections:
            logging.error(f"Error: La colección '{collection_name}' no existe en la base de datos.")
            logging.error(f"Colecciones disponibles: {', '.join(collections)}")
            return None
        
        data_source = f"mongodb://{DB_NAME}/{collection_name}"
        logging.info(f"Fuente de datos configurada: {data_source}")
        return data_source
        
    except Exception as e:
        logging.error(f"Error al configurar la conexión a MongoDB: {str(e)}")
        return None

def cleanup_resources() -> None:
    """Limpia recursos utilizados por la aplicación."""
    try:
        # Cerrar todas las figuras de matplotlib
        import matplotlib.pyplot as plt
        plt.close('all')
    except Exception as e:
        logging.debug(f"Error al limpiar recursos de matplotlib: {str(e)}")
    
    # Aquí se pueden agregar más limpiezas de recursos

def main() -> int:
    """Punto de entrada principal de la aplicación.
    
    Returns:
        Código de salida (0 para éxito, otro valor para error)
    """
    try:
        # Analizar argumentos primero para configurar logging adecuadamente
        args = parse_args()
        
        # Configurar logging basado en modo debug
        configure_logging(args.debug)
        
        # Configurar entorno
        setup_environment()
        
        # Determinar la fuente de datos
        data_source = None
        
        # Priorizar archivo si se especificó
        if args.file:
            data_source = setup_file_data_source(args.file)
            if data_source is None:
                return 1
        
        # Verificar MongoDB como alternativa
        elif args.mongodb:
            data_source = setup_mongodb_data_source(args.mongodb)
            if data_source is None:
                return 1
        
        # Si no hay fuente de datos, se abrirá la interfaz para seleccionar
        if data_source is None:
            logging.info("No se especificó fuente de datos. Iniciando interfaz para seleccionar una.")
        else:
            logging.info(f"Iniciando la aplicación con fuente de datos: {data_source}")
        
        # Iniciar la aplicación
        from gui.app import App
        app = App(data_source)
        return app.run()
        
    except KeyboardInterrupt:
        logging.info("Aplicación cerrada por el usuario.")
        return 0
    except ImportError as e:
        logging.error(f"Error de importación. Verifique que todas las dependencias estén instaladas: {str(e)}")
        if args.debug:
            traceback.print_exc()
        return 1
    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        if 'args' in locals() and args.debug:
            traceback.print_exc()
        return 1
    finally:
        cleanup_resources()

if __name__ == "__main__":
    sys.exit(main())

        