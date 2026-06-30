import logging
import sys
from conn import get_mongo_client, get_gcs_client
from utils import check_and_create_dir, cleanup_local_file, save_to_csv, upload_file_to_gcs
from config import LOG_PATH, DB_NAME, SOURCE_COLLECTION, IP2LOCATION_DB_PATH, GCS_BUCKET_NAME, LOCAL_OUTPUT_DATA_FOLDER, GCS_IP_LOCATION_FOLDER_NAME
import os
import IP2Location

check_and_create_dir(LOG_PATH)  # Ensure log directory exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def process_ip_loc(bin_path, local_output_csv_path):
    BUCKET_PREFIX = GCS_IP_LOCATION_FOLDER_NAME
    # Verify that the IP2Location database file exists
    source_col, mongo_client = get_mongo_client()
    logger.info("Initializing GCS Client.")

    bucket = get_gcs_client()

    if not bucket:
        logger.error("Failed to initialize GCS Client. Exiting.")
        return
    logger.info("Successfully initialized GCS Client.")

    if not os.path.exists(bin_path):
        logger.error(f"IP2Location database not found at {bin_path}")
        return
    logger.info(f"Using IP2Location database at: {bin_path}")
    # Initialize IP2Location
    ip_db = IP2Location.IP2Location(bin_path)
    
    # 2. Read unique IPs from main collection using aggregation
    pipeline = [
        # Change "ip_address" to whatever your field name is
        {"$group": {"_id": "$ip"}}, 
        {"$match": {"_id": {"$ne": None}}}
    ]
    unique_ips_cursor = source_col.aggregate(pipeline)

    # Process and store results
    results = []

    for doc in unique_ips_cursor:
        ip = doc["_id"]
        
        try:
            # 3. Use ip2location to get location data
            rec = ip_db.get_all(ip)
            
            # Create a structured dictionary of the results
            if rec:
                location_data = {
                    "ip": ip,
                    "country": rec.country_long,
                    "region": rec.region,
                    "city": rec.city
                }
                results.append(location_data)
            else:
                logger.warning(f"No geolocation data found for IP: {ip}")
        except Exception as e:
            logger.error(f"Error processing IP {ip}: {e}")
    
    if not results:
        logger.warning("No valid geolocation data found for any IPs.")
        return
    
    # 4. Write results to CSV

    keys = results[0].keys()
    
    save_to_csv(results, keys, local_output_csv_path)
    logger.info(f"Successfully saved {len(results)} records to {local_output_csv_path}")

    upload_file_to_gcs(local_output_csv_path, 'IP2Location', 'csv', bucket, BUCKET_PREFIX)
    logger.info(f"Successfully uploaded {local_output_csv_path} to {bucket.name} - {BUCKET_PREFIX}")



       
process_ip_loc(IP2LOCATION_DB_PATH, LOCAL_OUTPUT_DATA_FOLDER + "/ip2location_data.csv")