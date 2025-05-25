#!/usr/bin/env python3
"""
Script de línea de comandos para interactuar con MongoDB usando configuración segura
"""

import sys
import logging
from pymongo import MongoClient
import pandas as pd

def load_config():
    """Cargar configuración de MongoDB de forma segura"""
    try:
        from config import MONGODB_CONFIG
        return MONGODB_CONFIG
    except ImportError:
        print("❌ Error: No se encontró el archivo config.py")
        print("📝 Por favor, copia config.example.py como config.py y completa las credenciales")
        sys.exit(1)

def connect_to_mongodb():
    # URI de conexión
    config = load_config()
    uri = config["connection_string"]
    db_name = config["database_name"]
    
    try:
        # Conectar a MongoDB
        print("🔗 Conectando a MongoDB...")
        print(f"📊 Base de datos: {db_name}")
        client = MongoClient(uri)
        
        # Probar conexión
        client.admin.command('ping')
        print("✅ Conexión exitosa")
        
        # Listar bases de datos disponibles
        print("\nBases de datos disponibles:")
        dbs = client.list_database_names()
        for db in dbs:
            print(f"- {db}")
        
        # Seleccionar base de datos
        db = client[db_name]
        
        # Listar colecciones
        print(f"\n📋 Colecciones disponibles ({len(db.list_collection_names())}) en {db_name}:")
        collections = db.list_collection_names()
        if collections:
            for i, collection_name in enumerate(collections, 1):
                collection = db[collection_name]
                count = collection.count_documents({})
                print(f"  {i}. {collection_name} ({count} documentos)")
            
            # Mostrar información adicional
            print(f"\n📊 Información de la base de datos:")
            stats = db.command("dbstats")
            print(f"  • Tamaño: {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
            print(f"  • Índices: {stats.get('indexSize', 0) / 1024 / 1024:.2f} MB")
            print(f"  • Colecciones: {stats.get('collections', 0)}")
            
            # Seleccionar una colección
            if len(collections) == 1:
                collection_name = collections[0]
            else:
                print("\nSeleccione una colección (número):")
                selection = input("> ")
                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(collections):
                        collection_name = collections[idx]
                    else:
                        print("Selección inválida. Usando la primera colección.")
                        collection_name = collections[0]
                except ValueError:
                    print("Entrada inválida. Usando la primera colección.")
                    collection_name = collections[0]
            
            # Mostrar datos de la colección
            collection = db[collection_name]
            documents = list(collection.find(limit=10))
            
            if documents:
                # Convertir a DataFrame para mejor visualización
                df = pd.DataFrame(documents)
                if '_id' in df.columns:
                    df = df.drop('_id', axis=1)
                
                print(f"\nMostrando hasta 10 documentos de '{collection_name}':")
                print(df)
                
                # Mostrar estadísticas básicas
                print("\nEstadísticas básicas:")
                numeric_cols = df.select_dtypes(include=['number']).columns
                if not numeric_cols.empty:
                    print(df[numeric_cols].describe())
                else:
                    print("No hay columnas numéricas para análisis estadístico")
                
                print(f"\nTotal de documentos en la colección: {collection.count_documents({})}")
            else:
                print(f"La colección '{collection_name}' está vacía")
        else:
            print("No hay colecciones en esta base de datos")
            
            # Crear una colección de prueba
            print("\n¿Desea crear una colección de prueba? (s/n)")
            response = input("> ")
            if response.lower() in ["s", "si", "y", "yes"]:
                collection_name = "datos_prueba"
                collection = db[collection_name]
                
                # Crear datos de prueba
                import numpy as np
                # Crear un DataFrame con datos aleatorios
                np.random.seed(42)
                df = pd.DataFrame({
                    'nombre': [f'Usuario{i}' for i in range(1, 11)],
                    'edad': np.random.randint(18, 65, 10),
                    'salario': np.random.randint(30000, 100000, 10),
                    'activo': np.random.choice([True, False], 10),
                })
                
                # Insertar datos
                records = df.to_dict('records')
                result = collection.insert_many(records)
                
                print(f"Se han insertado {len(result.inserted_ids)} documentos en '{collection_name}'")
                print("\nDocumentos insertados:")
                print(df)
        
        # Cerrar conexión
        client.close()
        print("\n👋 Conexión cerrada")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    return True

def main():
    """Función principal del script"""
    print("🔗 MongoDB Command Line Tool - PearsonFlow")
    print("=" * 50)
    
    connect_to_mongodb()

if __name__ == "__main__":
    main() 