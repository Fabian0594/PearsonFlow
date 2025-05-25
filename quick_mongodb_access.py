#!/usr/bin/env python3
"""
Script de acceso rápido a MongoDB para PearsonFlow
Permite conectar y seleccionar colecciones de forma segura usando credenciales del archivo config.py
"""

import sys
import os
import logging
from typing import Optional, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """Cargar configuración desde config.py"""
    try:
        from config import MONGODB_CONFIG
        return MONGODB_CONFIG
    except ImportError:
        print("❌ Error: No se encontró el archivo config.py")
        print("📝 Por favor, copia config.example.py como config.py y completa las credenciales")
        sys.exit(1)

def list_collections(mongo_config: dict) -> List[str]:
    """Listar colecciones disponibles en la base de datos"""
    try:
        from core.mongo_loader import MongoDBLoader
        
        with MongoDBLoader() as loader:
            if loader.connect(mongo_config["connection_string"], mongo_config["database_name"]):
                collections = loader.list_collections()
                return collections
            else:
                print("❌ Error: No se pudo conectar a MongoDB")
                return []
                
    except ImportError:
        print("❌ Error: No se pudo importar MongoDBLoader")
        return []
    except Exception as e:
        print(f"❌ Error al listar colecciones: {str(e)}")
        return []

def select_collection(collections: List[str]) -> Optional[str]:
    """Permitir al usuario seleccionar una colección"""
    if not collections:
        print("⚠️  No hay colecciones disponibles en la base de datos")
        return None
    
    print("\n📋 Colecciones disponibles:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i}. {collection}")
    
    while True:
        try:
            choice = input(f"\n🔢 Selecciona una colección (1-{len(collections)}) o 'q' para salir: ").strip()
            
            if choice.lower() == 'q':
                return None
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(collections):
                return collections[choice_num - 1]
            else:
                print(f"❌ Por favor, ingresa un número entre 1 y {len(collections)}")
                
        except ValueError:
            print("❌ Por favor, ingresa un número válido")

def launch_pearsonflow(mongo_config: dict, collection_name: str):
    """Lanzar PearsonFlow con la colección seleccionada"""
    connection_string = mongo_config["connection_string"]
    database_name = mongo_config["database_name"]
    
    # Construir el identificador MongoDB para PearsonFlow
    mongodb_identifier = f"mongodb://{database_name}/{collection_name}"
    
    print(f"\n🚀 Iniciando PearsonFlow con:")
    print(f"   📊 Base de datos: {database_name}")
    print(f"   📁 Colección: {collection_name}")
    
    try:
        # Importar y ejecutar la aplicación
        from gui.app import App
        app = App(mongodb_identifier)
        return app.run()
        
    except ImportError as e:
        print(f"❌ Error al importar la aplicación: {str(e)}")
        return 1
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {str(e)}")
        return 1

def main():
    """Función principal del script"""
    print("🔗 PearsonFlow - Acceso Rápido a MongoDB")
    print("=" * 50)
    
    # Cargar configuración
    mongo_config = load_config()
    
    # Listar colecciones
    print("🔍 Conectando a MongoDB y listando colecciones...")
    collections = list_collections(mongo_config)
    
    if not collections:
        print("❌ No se pudieron obtener las colecciones. Verifica tu configuración.")
        return 1
    
    # Seleccionar colección
    selected_collection = select_collection(collections)
    
    if not selected_collection:
        print("👋 Saliendo...")
        return 0
    
    # Lanzar aplicación
    return launch_pearsonflow(mongo_config, selected_collection)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación cerrada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1) 