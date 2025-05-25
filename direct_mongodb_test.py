#!/usr/bin/env python3
"""
Prueba directa de MongoDB usando configuración segura
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

def test_direct_mongodb():
    """Prueba directa de conexión y operaciones con MongoDB"""
    config = load_config()
    uri = config["connection_string"]
    db_name = config["database_name"]
    
    try:
        from pymongo import MongoClient
        
        print(f"🔗 Conectando a MongoDB...")
        print(f"📊 Base de datos: {db_name}")
        
        # Conectar
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Verificar conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa")
        
        # Acceder a la base de datos
        db = client[db_name]
        
        # Listar colecciones
        collections = db.list_collection_names()
        print(f"\n📋 Colecciones disponibles ({len(collections)}):")
        
        if not collections:
            print("  ⚠️  No hay colecciones en esta base de datos")
            print("  💡 Ejecuta insert_to_peasonflow.py para crear datos de prueba")
            return False
        
        for i, coll_name in enumerate(collections, 1):
            coll = db[coll_name]
            count = coll.count_documents({})
            print(f"  {i}. {coll_name} ({count} documentos)")
            
            # Mostrar un documento de ejemplo
            if count > 0:
                sample_doc = coll.find_one()
                print(f"     📄 Ejemplo de documento:")
                for key, value in list(sample_doc.items())[:3]:  # Solo primeros 3 campos
                    if key != '_id':
                        print(f"       • {key}: {value}")
                if len(sample_doc) > 3:
                    print(f"       • ... y {len(sample_doc) - 3} campos más")
                print()
        
        # Cerrar conexión
        client.close()
        print("👋 Conexión cerrada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🧪 Prueba Directa de MongoDB - PearsonFlow")
    print("=" * 50)
    
    success = test_direct_mongodb()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 