
import sys
from datetime import datetime
import pandas as pd
from pymongo.errors import PyMongoError
from config import DB_NAME, SOURCE_COLLECTION, GCS_GLAMIRA_RAW_FOLDER_NAME
from .conn import get_mongo_client, get_gcs_client
from .utils import check_and_create_dir, cleanup_local_file
from .logging import setup_logging

logger = setup_logging()

def export_to_gcs():
    BATCH_SIZE = 50000  # Adjust based on your VM memory limits
    FILE_FORMAT = "jsonl"  # Options: parquet, jsonl, csv

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
                    batch, batch_count, FILE_FORMAT, bucket, GCS_GLAMIRA_RAW_FOLDER_NAME
                )
                batch = []

        # Export any remaining documents
        if batch:
            batch_count += 1
            total_records += len(batch)
            process_and_upload_batch(
                batch, batch_count, FILE_FORMAT, bucket, GCS_GLAMIRA_RAW_FOLDER_NAME
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
    local_filename = f"mongo_data/batch_{batch_num}_{timestamp}.{file_format}"
    blob_name = f"{blob_prefix}/batch_{batch_num}_{timestamp}.{file_format}"

    
    check_and_create_dir(local_filename)  # Ensure local directory exists
    
    try:
        logger.info(
            f"Converting batch #{batch_num} ({len(batch)} records) to {file_format.upper()}..."
        )
        df = pd.DataFrame(batch)

        if 'price' in df.columns:
            # Force column to string type to perform safe replacements
            df['price'] = df['price'].astype(str)

            # Remove any spaces (including standard spaces and non-breaking spaces '\xa0')
            df['price'] = df['price'].str.replace(r'[\s\xa0]+', '', regex=True)

            # Replace the European decimal comma ',' with a standard dot '.'
            df['price'] = df['price'].str.replace(',', '.', regex=False)

            # Convert the cleaned string column to a true Float64 type
            df['price'] = pd.to_numeric(df['price'], errors='coerce')

            # Fill any empty/null prices with 0.0 or handle them based on business logic
            df['price'] = df['price'].fillna(0.0)

        # Clean recommendation_clicked_position
        if 'recommendation_clicked_position' in df.columns:
            df['recommendation_clicked_position'] = df['recommendation_clicked_position'].fillna(0)
            df['recommendation_clicked_position'] = df['recommendation_clicked_position'].astype(int)

        # 1. Select all text/object columns that could contain a broken string 
        string_cols = [col for col in df.select_dtypes(include=['object']).columns]
        # 2. Strip out carriage returns and newline characters from string values
        for col in string_cols:
            # Ensure we only process column values that are actually strings
            df[col] = df[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()

        # ensure "option" values are in []
        if 'option' in df.columns:
            df['option'] = df['option'].astype(object).apply(lambda x: x if isinstance(x, list) else [x] if pd.notnull(x) else [])    

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
        #Cleanup local file to keep VM disk space clean
        cleanup_local_file(local_filename)
        logger.debug(f"Cleaned up local file: {local_filename}")



# if __name__ == "__main__":
#     export_to_gcs()