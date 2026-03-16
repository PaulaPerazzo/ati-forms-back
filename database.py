import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")
COLLECTION_NAME = "projects"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def append_to_sheet(data_dict: dict):
    """
    Simulates appending to a sheet by inserting a document into MongoDB.
    :param data_dict: Dictionary containing form data.
    """
    try:
        collection.insert_one(data_dict)
    except Exception as e:
        raise Exception(f"Erro ao inserir documento no MongoDB: {e}")

def get_all_data():
    """Fetches all documents from the MongoDB collection."""
    try:
        records = list(collection.find({}))
        # Map MongoDB _id to row_index (as a string) for compatibility with existing frontend
        for record in records:
            record["row_index"] = str(record["_id"])
            del record["_id"] # Remove the internal _id to avoid serialization issues
        return records
    except Exception as e:
        raise Exception(f"Erro ao ler os dados do MongoDB: {e}")

def update_project_status(row_index: str, status: str):
    """Updates the 'status' field of a specific document."""
    try:
        collection.update_one(
            {"_id": ObjectId(row_index)},
            {"$set": {"status": status}}
        )
    except Exception as e:
        raise Exception(f"Erro ao atualizar o status no MongoDB: {e}")

def update_project_priority(row_index: str, priority: str):
    """Updates the 'manual_priority' field of a specific document."""
    try:
        collection.update_one(
            {"_id": ObjectId(row_index)},
            {"$set": {"manual_priority": priority}}
        )
    except Exception as e:
        raise Exception(f"Erro ao atualizar a prioridade manual no MongoDB: {e}")
