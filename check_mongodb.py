#!/usr/bin/env python3
"""
Script para verificar el estado de MongoDB usando configuración segura
"""

import sys

def load_config():
    """Cargar configuración de MongoDB de forma segura"""
    try:
        from config import MONGODB_CONFIG
        return MONGODB_CONFIG
    except ImportError:
        print("❌ Error: No se encontró el archivo config.py")
        print("📝 Por favor, copia config.example.py como config.py y completa las credenciales")
        sys.exit(1)

def check_mongodb_status():
    """Verificar el estado completo de MongoDB"""
    config = load_config()
    conn_string = config["connection_string"]
    db_name = config["database_name"]
    
    try:
        from pymongo import MongoClient
        
        print(f"🔗 Verificando estado de MongoDB...")
        print(f"📊 Base de datos: {db_name}")
        
        # Conectar
        client = MongoClient(conn_string, serverSelectionTimeoutMS=5000)
        
        # Verificar conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa")
        
        # Información del servidor
        server_info = client.server_info()
        print(f"\n🖥️  Información del servidor:")
        print(f"  • Versión de MongoDB: {server_info.get('version', 'N/A')}")
        print(f"  • Plataforma: {server_info.get('os', {}).get('name', 'N/A')}")
        
        # Acceder a la base de datos
        db = client[db_name]
        
        # Estadísticas de la base de datos
        try:
            stats = db.command("dbstats")
            print(f"\n📊 Estadísticas de la base de datos '{db_name}':")
            print(f"  • Tamaño de datos: {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
            print(f"  • Tamaño de índices: {stats.get('indexSize', 0) / 1024 / 1024:.2f} MB")
            print(f"  • Número de colecciones: {stats.get('collections', 0)}")
            print(f"  • Número de objetos: {stats.get('objects', 0)}")
        except Exception as e:
            print(f"⚠️  No se pudieron obtener estadísticas: {str(e)}")
        
        # Listar colecciones
        collections = db.list_collection_names()
        print(f"\n📋 Colecciones disponibles ({len(collections)}):")
        
        if not collections:
            print("  ⚠️  No hay colecciones en esta base de datos")
            print("  💡 Ejecuta insert_to_peasonflow.py para crear datos de prueba")
        else:
            total_documents = 0
            for i, coll_name in enumerate(collections, 1):
                coll = db[coll_name]
                count = coll.count_documents({})
                total_documents += count
                print(f"  {i}. {coll_name} ({count:,} documentos)")
                
                # Mostrar índices de la colección
                indexes = list(coll.list_indexes())
                if len(indexes) > 1:  # Más que solo el índice _id
                    print(f"     🔍 Índices: {len(indexes)} (incluyendo _id)")
            
            print(f"\n📈 Total de documentos en la base de datos: {total_documents:,}")
        
        # Verificar permisos
        try:
            # Intentar crear una colección temporal para verificar permisos de escritura
            test_coll = db["_temp_permission_test"]
            test_coll.insert_one({"test": True})
            test_coll.drop()
            print(f"\n✅ Permisos de lectura/escritura: OK")
        except Exception as e:
            print(f"\n⚠️  Permisos limitados: {str(e)}")
        
        # Cerrar conexión
        client.close()
        print("\n👋 Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🔍 Verificación de Estado de MongoDB - PearsonFlow")
    print("=" * 60)
    
    success = check_mongodb_status()
    
    if success:
        print("\n✅ Verificación completada exitosamente")
    else:
        print("\n❌ La verificación falló")
        sys.exit(1)

if __name__ == "__main__":
    main() 