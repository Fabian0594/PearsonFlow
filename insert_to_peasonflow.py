#!/usr/bin/env python3
"""
Script para insertar datos de prueba en MongoDB usando configuración segura
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_config():
    """Cargar configuración de MongoDB de forma segura"""
    try:
        from config import MONGODB_CONFIG
        return MONGODB_CONFIG
    except ImportError:
        print("❌ Error: No se encontró el archivo config.py")
        print("📝 Por favor, copia config.example.py como config.py y completa las credenciales")
        sys.exit(1)

def create_sample_data():
    """Crear datos de muestra para insertar"""
    print("📊 Generando datos de muestra...")
    
    # Generar datos de ejemplo
    np.random.seed(42)
    n_records = 100
    
    data = {
        'id': range(1, n_records + 1),
        'nombre': [f'Usuario_{i}' for i in range(1, n_records + 1)],
        'edad': np.random.randint(18, 80, n_records),
        'salario': np.random.normal(50000, 15000, n_records).round(2),
        'departamento': np.random.choice(['IT', 'Ventas', 'Marketing', 'RRHH', 'Finanzas'], n_records),
        'fecha_ingreso': [
            (datetime.now() - timedelta(days=np.random.randint(30, 1825))).strftime('%Y-%m-%d')
            for _ in range(n_records)
        ],
        'activo': np.random.choice([True, False], n_records, p=[0.8, 0.2]),
        'puntuacion': np.random.uniform(1, 10, n_records).round(2)
    }
    
    df = pd.DataFrame(data)
    print(f"✅ Generados {len(df)} registros de muestra")
    return df

def insert_data_to_mongodb():
    """Insertar datos en MongoDB usando configuración segura"""
    # Cargar configuración
    config = load_config()
    conn_string = config["connection_string"]
    db_name = config["database_name"]
    collection_name = "datos_prueba"
    
    try:
        from core.mongo_loader import MongoDBLoader
        
        print(f"🔗 Conectando a MongoDB...")
        print(f"📊 Base de datos: {db_name}")
        print(f"📁 Colección: {collection_name}")
        
        # Crear datos de muestra
        df = create_sample_data()
        
        # Conectar y insertar datos
        with MongoDBLoader() as loader:
            if loader.connect(conn_string, db_name):
                print("✅ Conexión exitosa")
                
                # Insertar datos
                result = loader.save_dataframe_to_collection(df, collection_name)
                
                if result:
                    print(f"✅ Datos insertados exitosamente en '{collection_name}'")
                    print(f"📊 Total de registros: {len(df)}")
                    
                    # Verificar inserción
                    collections = loader.list_collections()
                    if collection_name in collections:
                        print(f"✅ Colección '{collection_name}' creada/actualizada correctamente")
                    
                    return True
                else:
                    print("❌ Error al insertar datos")
                    return False
            else:
                print("❌ No se pudo conectar a MongoDB")
                return False
                
    except ImportError:
        print("❌ Error: No se pudo importar MongoDBLoader")
        return False
    except Exception as e:
        print(f"❌ Error durante la inserción: {str(e)}")
        return False

def main():
    """Función principal"""
    print("📥 Inserción de Datos de Prueba - PearsonFlow")
    print("=" * 50)
    
    success = insert_data_to_mongodb()
    
    if success:
        print("\n🎉 ¡Proceso completado exitosamente!")
        print("💡 Ahora puedes usar quick_mongodb_access.py para acceder a los datos")
    else:
        print("\n❌ El proceso falló. Revisa la configuración y vuelve a intentar.")
        sys.exit(1)

if __name__ == "__main__":
    main() 