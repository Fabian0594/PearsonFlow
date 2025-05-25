from pymongo import MongoClient

def check_mongodb():
    """Verificar las bases de datos y colecciones disponibles en MongoDB Atlas"""
    # Conectar a MongoDB Atlas
    conn_string = "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/"
    client = MongoClient(conn_string)
    
    try:
        # Listar bases de datos
        print("Bases de datos disponibles:")
        dbs = client.list_database_names()
        for i, db_name in enumerate(dbs, 1):
            print(f"{i}. {db_name}")
            
            # Listar colecciones en cada base de datos
            db = client[db_name]
            collections = db.list_collection_names()
            if collections:
                print(f"   Colecciones en {db_name}:")
                for j, coll_name in enumerate(collections, 1):
                    print(f"   {j}. {coll_name}")
                    
                    # Contar documentos en cada colección
                    count = db[coll_name].count_documents({})
                    print(f"      Documentos: {count}")
            else:
                print(f"   No hay colecciones en {db_name}")
            print()
    
    except Exception as e:
        print(f"Error al verificar MongoDB: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    check_mongodb() 