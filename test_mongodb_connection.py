#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a MongoDB usando configuración segura
"""

import sys
import logging

def test_mongodb_connection():
    """Probar la conexión a MongoDB usando configuración segura"""
    try:
        # Cargar configuración de forma segura
        from config import MONGODB_CONFIG
        conn_string = MONGODB_CONFIG["connection_string"]
        db_name = MONGODB_CONFIG["database_name"]
        
        print(f"🔗 Probando conexión a MongoDB...")
        print(f"📊 Base de datos: {db_name}")
        
    except ImportError:
        print("❌ Error: No se encontró el archivo config.py")
        print("📝 Por favor, copia config.example.py como config.py y completa las credenciales")
        return False
    except Exception as e:
        print(f"❌ Error al cargar configuración: {str(e)}")
        return False
    
    try:
        from core.mongo_loader import MongoDBLoader
        
        # Crear loader y probar conexión
        mongo_loader = MongoDBLoader()
        
        if mongo_loader.connect(conn_string, db_name):
            print("✅ Conexión exitosa a MongoDB")
            
            # Listar colecciones
            collections = mongo_loader.list_collections()
            print(f"📋 Colecciones encontradas ({len(collections)}):")
            for i, collection in enumerate(collections, 1):
                print(f"  {i}. {collection}")
            
            mongo_loader.close()
            return True
        else:
            print("❌ No se pudo conectar a MongoDB")
            return False
            
    except ImportError:
        print("❌ Error: No se pudo importar MongoDBLoader")
        return False
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    sys.exit(0 if success else 1) 