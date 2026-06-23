from pymongo import MongoClient
from google.cloud import storage
from google.api_core import exceptions
from config import MONGO_URI, DB_NAME, SOURCE_COLLECTION, GCS_BUCKET_NAME

# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "glamira"
# SOURCE_COLLECTION = "summary19"
# TARGET_COLLECTION = "ip_locations"


def get_mongo_client():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        source_col = db[SOURCE_COLLECTION]
        print(f"Successfully connected to {db}.{source_col}.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return
    return source_col, client

# get_mongo_client()

def get_gcs_client():
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        print("Successfully authenticated with Google Cloud Storage.")
    except exceptions.GoogleAPIError as e:
        print(f"Error authenticating with GCS: {e}")
        return
    return bucket