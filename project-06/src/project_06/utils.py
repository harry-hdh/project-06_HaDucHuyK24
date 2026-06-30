import logging
import os
import re
import json
import csv
from pathlib import Path
from config import LOG_PATH

check_and_create_dir(LOG_PATH)  # Ensure log directory exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def chunked(lst, size):
    for i in range(0,len(lst), size):
        yield lst[i:i + size]

def check_and_create_dir(file_path):
    parent_dir = os.path.dirname(file_path)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)

#Cleanup local file
def cleanup_local_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def save_batch_csv(data, headers, file_name, batch_num, folder_name):
    file_path = f"{folder_name}/{file_name}_{batch_num}.csv"

    cleanup_local_file(file_path)
    logger.info(f"Existing file in {file_path} removed.")
    check_and_create_dir(file_path)
    print(f"Folder in {file_path} created.")
    
    with open(file_path, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=headers)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Successfully saved {len(data)} records to {file_path}")


def save_to_csv(data, headers, file_path, mode='w'):
    if mode == 'w':
        cleanup_local_file(file_path)
        print(f"Existing file in {file_path} removed.")
        check_and_create_dir(file_path)
        print(f"Folder in {file_path} created.")

        with open(file_path, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=headers)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Successfully saved {len(data)} records to {file_path}")
    elif mode == 'a':
        with open(file_path, 'a', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=headers)
            dict_writer.writerows(data)
        print(f"Successfully appended {len(data)} records to {file_path}")
    else:
        print(f"Invalid mode '{mode}' specified. Use 'w' for write or 'a' for append.")


# read csv file and remove duplicates based on product_id, remevoe missing referrer_url, and return a list of referrer_url
def read_product_csv(file_path, url_field, id_field="product_id"):
    unique_records = {}
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_id = row.get(id_field)
            url = row.get(url_field)
            if product_id and url:  # Ensure both fields are present
                unique_records[product_id] = url  # This will automatically handle duplicates by overwriting
    #return [url for pid,url in unique_records.items()]            
    return [{"product_id": pid, url_field: url} for pid, url in unique_records.items()]

# Process json data
#SAMPLE DATA json_data = {"product_id":110644,"name":"F\u00f6rlovningsring Titina 0.5 crt","sku":"titina05","attribute_set_id":55,"attribute_set":"diamonds","type_id":"simple","price":"7749.000000","min_price":"2098.000000","max_price":"461205.000000","min_price_format":"2\u00a0098,00\u00a0Kr","max_price_format":"461\u00a0205,00\u00a0Kr","gold_weight":"1.2051","none_metal_weight":0,"fixed_silver_weight":0,"material_design":null,"qty":1,"collection":"classic_solitaire","collection_id":"5171","product_type":"ring","product_type_value":"1","category":"605","category_name":"F\u00f6rlovningsringar","store_code":"glse","platinum_palladium_info_in_alloy":0,"bracelet_without_chain":0,"show_popup_quantity_eternity":0,"visible_contents":[""],"gender":"women"}
def process_json_data(soup, url):
    script_tag = soup.find('script', string=re.compile(r'react_data'))
    if script_tag:
        try:
            json_data = re.search(r'var\s+react_data\s*=\s*(.*?"gender"\s*:\s*[^,}]+)(?=[,}])', script_tag.string).group(1) + "}"
            
            data = json.loads(json_data)

            product_id = data.get('product_id', 'No Product ID Found')
            title = data.get('name', 'No Title Found')
            product_info = data

            return {
                "title": title,
                "url": url,
                "product_id": product_id,
                "name": product_info.get('name', 'NULL'),
                "sku": product_info.get('sku', 'NULL'),
                "price": product_info.get('price', 'NULL'),
                "min_price": product_info.get('min_price', 'NULL'),
                "max_price": product_info.get('max_price', 'NULL'),
                "min_price_format": product_info.get('min_price_format', 'NULL'),
                "max_price_format": product_info.get('max_price_format', 'NULL'),
                "gold_weight": product_info.get('gold_weight', 'NULL'),
                "none_metal_weight": product_info.get('none_metal_weight', 'NULL'),
                "fixed_silver_weight": product_info.get('fixed_silver_weight', 'NULL'),
                "material_design": product_info.get('material_design', 'NULL'),
                "qty": product_info.get('qty', 'NULL'),
                "collection": product_info.get('collection', 'NULL'),
                "collection_id": product_info.get('collection_id', 'NULL'),
                "product_type": product_info.get('product_type', 'NULL'),
                "product_type_value": product_info.get('product_type_value', 'NULL'),
                "category": product_info.get('category', 'NULL'),
                "category_name": product_info.get('category_name', 'NULL'),
                "store_code": product_info.get('store_code', 'NULL'),
                "platinum_palladium_info_in_alloy": product_info.get('platinum_palladium_info_in_alloy', 'NULL'),
                "bracelet_without_chain": product_info.get('bracelet_without_chain', 'NULL'),
                "show_popup_quantity_eternity": product_info.get('show_popup_quantity_eternity', 'NULL'),
                "visible_contents": product_info.get('visible_contents', 'NULL'),
                "gender": product_info.get('gender', 'NULL')
            }
        except Exception as e:
            print(f"Error parsing JSON for {url}: {e}")
            return {"title": "Failed to Parse JSON", "url": url, "product_info": {}}
    else:
        print(f"No react_data script tag found for {url}")
        return {"title": "No react_data Found", "url": url, "product_info": {}}


#upload to GCS
def upload_file_to_gcs(local_folder, name, file_format, bucket, blob_prefix):
    local_filename = f"{local_folder}/{name}.{file_format}"
    blob_name = f"{blob_prefix}/{name}.{file_format}"

    check_and_create_dir(local_filename)
    try:
        logger.info(
            f"Converting file {name} ({len(result)} records) to {file_format.upper()}."
        )

        # UPLOAD TO GCS
        logger.info(f"Uploading file {name}.{file_format} to GCS as gs://{bucket.name}/{blob_name}...")
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_filename)
        logger.info(f"File {name}.{file_format} successfully uploaded.")
    finally:
        # Cleanup local file to keep VM disk space clean
        cleanup_local_file(local_filename)
        logger.debug(f"Cleaned up local file: {local_filename}")