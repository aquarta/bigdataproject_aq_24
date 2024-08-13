from pymongo import MongoClient
import os

DB_USER = os.environ.get("MONGO_USER","")
DB_PASSWORD = os.environ.get("MONGO_PASSWORD","")
DB_URL = os.environ.get("MONGO_HOST","mongo-db")
DB_NAME = os.environ.get("MONGO_DB_NAME","flaskdash_db")



def get_database():
 
    if DB_USER:
        user_login = f"{DB_USER}:{DB_PASSWORD}@"
    else:
        user_login = ""
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = f"mongodb://{user_login}{DB_URL}"


    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[DB_NAME]
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
    # Get the database
    dbname = get_database()
    