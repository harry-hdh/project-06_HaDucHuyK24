import os
import logging
import functions_framework
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from src.project_06.table_schema import  RAW_SCHEMA, IP_LOCATION_SCHEMA, PRODUCT_INFO_SCHEMA
from src.project_06.config import PROJECT_ID, DATASET_ID, TABLE_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@functions_framework.cloud_event
def load_gcs_to_bigquery_trigger(cloud_event,):
    """
    Loads data from a GCS URI into a BigQuery Raw Table.
    gcs_uri example: 'gs://your-bucket-name/mongodb_exports/*.jsonl'
    """
    table_schema = os.environ.get("TABLE_SCHEMA").upper()
    target_folder = os.environ.get("TARGET_FOLDER")

    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]
    gcs_uri = f"gs://{bucket_name}/{target_folder}/{file_name}"
    

    logger.info(f"New data file {gcs_uri}")
    
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)
    table_ref = dataset_ref.table(TABLE_ID)

    # 1. Ensure Dataset Exists
    try:
        client.get_dataset(dataset_ref)
        logger.info(f"Dataset {DATASET_ID} already exists.")
    except NotFound:
        logger.info(f"Dataset {DATASET_ID} not found. Creating it...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # Adjust to your region
        client.create_dataset(dataset, timeout=30)
        logger.info(f"Created dataset {DATASET_ID}")

    # 2. Configure the Load Job
    job_config = bigquery.LoadJobConfig()
    job_config.schema = table_schema
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    job_config.autodetect = True
    #job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    
    # Handle formats dynamically
    if file_name.upper().endswith("PARQUET"):
        job_config.source_format = bigquery.SourceFormat.PARQUET
    elif file_name.upper().endswith("JSONL"):
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    elif file_name.upper().endswith("CSV"):
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.skip_leading_rows = 1 # Skip header row
    else:
        raise ValueError(f"Unsupported format: {file_name}. Supported formats are PARQUET, JSONL, and CSV.")

    # 3. Start BigQuery load job
    try:
        logger.info(f"Starting BigQuery load job from {gcs_uri}...")
        load_job = client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
        
        # Wait for the job to complete
        load_job.result() 
        
        destination_table = client.get_table(table_ref)
        logger.info(f"Successfully loaded data. Total rows now in table: {destination_table.num_rows}")
        
    except Exception as e:
        logger.critical(f"Failed to load file {gcs_uri} to BigQuery: {e}", exc_info=True)
        raise e
