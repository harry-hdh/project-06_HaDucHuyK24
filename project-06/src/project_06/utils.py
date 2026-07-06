import logging
import os
import re
import json
import csv
from pathlib import Path
from .logging import setup_logging

logger = setup_logging()


def chunked(lst, size):
    for i in range(0,len(lst), size):
        yield lst[i:i + size]

def check_and_create_dir(file_path):
    parent_dir = os.path.dirname(file_path)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)

# def check_and_create_file(file_path):
#     if not os.path.exists(file_path):
#         check_and_create_dir(file_path)
#         with open(file_path, 'w', encoding='utf-8') as f:
#             pass  # Just create the file

#Cleanup local file
def cleanup_local_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def save_batch_csv(data, headers, file_name, batch_num, folder_name):
    file_path = f"{folder_name}/{file_name}_{batch_num}.csv"
    cleanup_local_file(file_path)
    logger.info(f"Existing file in {file_path} removed.")
    check_and_create_dir(file_path)
    logger.info(f"Folder in {file_path} created.")
    
    with open(file_path, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=headers)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    logger.info(f"Successfully saved {len(data)} records to {file_path}")


def save_to_csv(data, headers, file_path, mode='w'):
    if mode == 'w':
        cleanup_local_file(file_path)
        logger.info(f"Existing file in {file_path} removed.")
        check_and_create_dir(file_path)
        logger.info(f"Folder in {file_path} created.")

        with open(file_path, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=headers, extrasaction='ignore')
            dict_writer.writeheader()
            dict_writer.writerows(data)
        logger.info(f"Successfully saved {len(data)} records to {file_path}")
    elif mode == 'a':
        with open(file_path, 'a', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=headers, extrasaction='ignore')
            dict_writer.writerows(data)
        logger.info(f"Successfully appended {len(data)} records to {file_path}")
    else:
        logger.error(f"Invalid mode '{mode}' specified. Use 'w' for write or 'a' for append.")


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
#SAMPLE DATA json_data = {'title': 'Sužadėtuvių žiedas Primula 1.25 crt', 'url': 'https://www.glamira.lt/glamira-ring-primula-1.25-crt.html?itm_source=recommendation&itm_medium=sorting&fbclid=IwAR06BpNDzLB4eqFWR02Eozk0X8J23zY9AUXoeUZTgYOPOSZwcFw_LkKTeeY', 'product_id': 110641, 'name': 'Sužadėtuvių žiedas Primula 1.25 crt', 'sku': 'primula125', 'attribute_set_id': 55, 'attribute_set': 'diamonds', 'type_id': 'simple', 'price': '955.000000', 'min_price': '176.000000', 'max_price': '112171.000000', 'min_price_format': '176,00\xa0€', 'max_price_format': '112\xa0171,00\xa0€', 'gold_weight': '1.7511', 'none_metal_weight': 0, 'fixed_silver_weight': 0, 'material_design': None, 'qty': 1, 'collection': 'design_solitaire', 'collection_id': '5170', 'product_type': 'ring', 'product_type_value': '1', 'category': '605', 'category_name': 'Sužadėtuvių žiedai', 'store_code': 'gllt', 'platinum_palladium_info_in_alloy': 0, 'bracelet_without_chain': 0, 'show_popup_quantity_eternity': 0, 'visible_contents': [''], 'gender': 'women'}, {'title': 'Mannens giftering White Crown 4 mm', 'url': 'https://www.glamira.no/herrering-white-crown-4-mm.html?alloy=white-silber&itm_source=recommendation&itm_medium=sorting', 'product_id': 105956, 'name': 'Mannens giftering White Crown 4 mm', 'sku': 'GWD-N1112-4-M', 'attribute_set_id': 26, 'attribute_set': 'trauring', 'type_id': 'simple', 'price': '6656.000000', 'min_price': '1324.000000', 'max_price': '66842.000000', 'min_price_format': 'kr\xa01\xa0324,00', 'max_price_format': 'kr\xa066\xa0842,00', 'gold_weight': '1.3689', 'none_metal_weight': 0, 'fixed_silver_weight': 0, 'material_design': None, 'qty': 1, 'collection': 'simple', 'collection_id': '164', 'product_type': 'wedding_ring', 'product_type_value': '12', 'category': '690', 'category_name': 'Herreringer', 'store_code': 'glno', 'platinum_palladium_info_in_alloy': 0, 'bracelet_without_chain': 0, 'show_popup_quantity_eternity': 0, 'visible_contents': [''], 'gender': 'men'},
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
                "attribute_set_id": product_info.get('attribute_set_id', 'NULL'),
                "attribute_set": product_info.get('attribute_set', 'NULL'),
                "type_id": product_info.get('type_id', 'NULL'),
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
            logger.error(f"Error parsing JSON for {url}: {e}")
            return {"title": "Failed to Parse JSON", "url": url, "product_info": {}}
    else:
        logger.error(f"No react_data script tag found for {url}")
        return {"title": "No react_data Found", "url": url, "product_info": {}}


#upload to GCS
def upload_file_to_gcs(local_file_path, name, file_format, bucket, blob_prefix):
    blob_name = f"{blob_prefix}/{name}.{file_format}"

    try:
        # UPLOAD TO GCS
        logger.info(f"Uploading file {name}.{file_format} to GCS as gs://{bucket.name}/{blob_name}...")
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_file_path)
        logger.info(f"File {name}.{file_format} successfully uploaded.")
    finally:
        # Cleanup local file to keep VM disk space clean
        cleanup_local_file(local_file_path)
        logger.debug(f"Cleaned up local file: {local_file_path}")

# Get list of files in a folder
def list_files_in_folder(folder_path):
    try:
        files = os.listdir(folder_path)
        return files
    except Exception as e:
        logger.error(f"Error listing files in {folder_path}: {e}")
        return []