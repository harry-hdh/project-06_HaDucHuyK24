import logging
import sys
from datetime import datetime
import pandas as pd
from pymongo.errors import PyMongoError
from config import LOG_PATH, DB_NAME, SOURCE_COLLECTION
from conn import get_mongo_client, get_gcs_client
from utils import check_and_create_dir, cleanup_local_file

check_and_create_dir(LOG_PATH)  # Ensure log directory exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def export_to_gcs():
    BATCH_SIZE = 10000  # Adjust based on your VM memory limits
    FILE_FORMAT = "jsonl"  # Options: parquet, jsonl, csv
    GCS_BLOB_PREFIX = f"{DB_NAME}_{SOURCE_COLLECTION}"

    try:
        logger.info("Connecting to MongoDB.")
        source_col, mongo_client = get_mongo_client()

        if not mongo_client:
            logger.error("Failed to connect to MongoDB. Exiting.")
            return
        logger.info("Successfully connected to MongoDB.")

        # Initialize GCS Client
        logger.info("Initializing GCS Client.")
        bucket = get_gcs_client()

        if not bucket:
             logger.error("Failed to initialize GCS Client. Exiting.")
             return
        logger.info("Successfully initialized GCS Client.")

        #EXTRACT DATA IN BATCHES
        logger.info(f"Starting extraction from {DB_NAME}.{SOURCE_COLLECTION}.")
        cursor = source_col.find({})
        batch = []
        batch_count = 0
        total_records = 0

        for doc in cursor:
            # Convert MongoDB ObjectId to string for file format compatibility
            if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            batch.append(doc)

            if len(batch) >= BATCH_SIZE:
                batch_count += 1
                total_records += len(batch)
                process_and_upload_batch(
                    batch, batch_count, FILE_FORMAT, bucket, GCS_BLOB_PREFIX
                )
                batch = []

        # Export any remaining documents
        if batch:
            batch_count += 1
            total_records += len(batch)
            process_and_upload_batch(
                batch, batch_count, FILE_FORMAT, bucket, GCS_BLOB_PREFIX
            )
        logger.info(f"Extraction completed. Total records exported: {total_records}")
    
    #ERROR HANDLING   
    except PyMongoError as e:
        logger.critical(f"MongoDB Database error: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB connection closed.")

def process_and_upload_batch(batch, batch_num, file_format, bucket, blob_prefix):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    local_filename = f"data/batch_{batch_num}_{timestamp}.{file_format}"
    blob_name = f"{blob_prefix}/batch_{batch_num}_{timestamp}.{file_format}"

    
    check_and_create_dir(local_filename)  # Ensure local directory exists
    
    try:
        logger.info(
            f"Converting batch #{batch_num} ({len(batch)} records) to {file_format.upper()}..."
        )
        df = pd.DataFrame(batch)
        print(df.head())
        if file_format == "parquet":
            df.to_parquet(local_filename, index=False)
        elif file_format == "jsonl":
            df.to_json(local_filename, orient="records", lines=True)
        elif file_format == "csv":
            df.to_csv(local_filename, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        # UPLOAD TO GCS
        logger.info(f"Uploading batch #{batch_num} to GCS as gs://{bucket.name}/{blob_name}...")
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_filename)
        logger.info(f"Batch #{batch_num} successfully uploaded.")

    finally:
        Cleanup local file to keep VM disk space clean
        cleanup_local_file(local_filename)
        logger.debug(f"Cleaned up local file: {local_filename}")



if __name__ == "__main__":
    export_to_gcs()