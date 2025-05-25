#!/usr/bin/env python3
"""
Script para crear una colección de prueba en MongoDB usando configuración segura
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime

def load_config():
    """Cargar configuración de MongoDB de forma segura"""
    try:
        from config import MONGODB_CONFIG
        return MONGODB_CONFIG
    except ImportError:
        print("❌ Error: No se encontró el archivo config.py")
        print("📝 Por favor, copia config.example.py como config.py y completa las credenciales")
        sys.exit(1)

def create_test_collection():
    """Crear una colección de prueba con datos sintéticos"""
    config = load_config()
    conn_string = config["connection_string"]
    db_name = config["database_name"]
    collection_name = "test_collection"
    
    try:
        from core.mongo_loader import MongoDBLoader
        
        print(f"🔗 Conectando a MongoDB...")
        print(f"📊 Base de datos: {db_name}")
        print(f"📁 Colección: {collection_name}")
        
        # Generar datos de prueba
        print("📊 Generando datos de prueba...")
        np.random.seed(123)
        n_records = 50
        
        data = {
            'id': range(1, n_records + 1),
            'producto': [f'Producto_{i}' for i in range(1, n_records + 1)],
            'categoria': np.random.choice(['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros'], n_records),
            'precio': np.random.uniform(10, 500, n_records).round(2),
            'stock': np.random.randint(0, 100, n_records),
            'rating': np.random.uniform(1, 5, n_records).round(1),
            'fecha_creacion': datetime.now().strftime('%Y-%m-%d'),
            'disponible': np.random.choice([True, False], n_records, p=[0.9, 0.1])
        }
        
        df = pd.DataFrame(data)
        print(f"✅ Generados {len(df)} registros de prueba")
        
        # Conectar e insertar datos
        with MongoDBLoader() as loader:
            if loader.connect(conn_string, db_name):
                print("✅ Conexión exitosa")
                
                # Insertar datos
                result = loader.save_dataframe_to_collection(df, collection_name)
                
                if result:
                    print(f"✅ Colección '{collection_name}' creada exitosamente")
                    print(f"📊 Total de registros insertados: {len(df)}")
                    
                    # Verificar creación
                    collections = loader.list_collections()
                    if collection_name in collections:
                        print(f"✅ Colección verificada en la base de datos")
                        
                        # Mostrar estadísticas
                        print(f"\n📈 Estadísticas de la colección:")
                        print(f"  • Categorías únicas: {df['categoria'].nunique()}")
                        print(f"  • Precio promedio: ${df['precio'].mean():.2f}")
                        print(f"  • Stock total: {df['stock'].sum()}")
                        print(f"  • Rating promedio: {df['rating'].mean():.1f}/5.0")
                    
                    return True
                else:
                    print("❌ Error al crear la colección")
                    return False
            else:
                print("❌ No se pudo conectar a MongoDB")
                return False
                
    except ImportError:
        print("❌ Error: No se pudo importar MongoDBLoader")
        return False
    except Exception as e:
        print(f"❌ Error durante la creación: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🏗️  Creación de Colección de Prueba - PearsonFlow")
    print("=" * 50)
    
    success = create_test_collection()
    
    if success:
        print("\n🎉 ¡Colección de prueba creada exitosamente!")
        print("💡 Usa quick_mongodb_access.py para acceder a los datos")
    else:
        print("\n❌ Error al crear la colección de prueba")
        sys.exit(1)

if __name__ == "__main__":
    main() 