import asyncio
from src.project_06.config import IP2LOCATION_DB_PATH, FOLDER_CURRENT_URLS, FOLDER_REFERRER_URLS, CRAWL_SAVE_PATH, FAIL_CRAWL_SAVE_PATH, LOCAL_OUTPUT_DATA_FOLDER, LOG_PATH
from src.project_06.collect_product_ids import extract_product_data
from src.project_06.scrape_product_data import scrape_main
from src.project_06.process_ip_loc import process_ip_loc
from src.project_06.conn import get_mongo_client
from src.project_06.utils import read_product_csv, list_files_in_folder, check_and_create_dir



if __name__ == "__main__":
    check_and_create_dir(LOG_PATH)  # Ensure log directory exists

    # Process IP locations 
    process_ip_loc(IP2LOCATION_DB_PATH, LOCAL_OUTPUT_DATA_FOLDER + "/ip2location_data.csv")

    # Extract product info and referrer URLs from MongoDB and save to CSV
    collections = [
    "view_product_detail",
    "select_product_option",
    "select_product_option_quality",
    "add_to_cart_action",
    "product_detail_recommendation_visible",
    "product_detail_recommendation_noticed"
    ]

    product_id_fallback = {"product_id": ["$product_id", "$viewing_product_id"]}

    extract_product_data(collection=get_mongo_client(), target_events=collections, fields_to_extract=["current_url"], id_fallbacks=product_id_fallback, folder_name=FOLDER_CURRENT_URLS, file_name="product_info")

    extract_product_data(collection=get_mongo_client(), target_events=[ "product_view_all_recommend_clicked" ], fields_to_extract=["referrer_url"], id_fallbacks={"product_id": ["$viewing_product_id", "$product_id"]}, folder_name=FOLDER_REFERRER_URLS, file_name="product_info_referrer_url")

    #Get files in output_current_urls and output_referrer_urls folders
    current_url_files = list_files_in_folder(FOLDER_CURRENT_URLS)
    
    referrer_url_files = list_files_in_folder(FOLDER_REFERRER_URLS)

    # Scrape product titles for URLs in CSV and save to new CSV
    

    for file in current_url_files:
        print(f"Processing file: {file}")
        URLS_IDS1 = [(record["current_url"], record["product_id"]) for record in read_product_csv(f"{FOLDER_CURRENT_URLS}/{file}", url_field="current_url")] 
        asyncio.run(scrape_main(successful_save_path=CRAWL_SAVE_PATH, err_save_path=FAIL_CRAWL_SAVE_PATH, urls=URLS_IDS1, mode='a'))  # Write results from first set of URLs to CSV

    for file in referrer_url_files:
        print(f"Processing file: {file}")
        URLS_IDS2 = [(record["referrer_url"], record["product_id"]) for record in read_product_csv(f"{FOLDER_REFERRER_URLS}/{file}", url_field="referrer_url")]
        #print(URLS_IDS2[:5])
        asyncio.run(scrape_main(successful_save_path=CRAWL_SAVE_PATH, err_save_path=FAIL_CRAWL_SAVE_PATH, urls=URLS_IDS2, mode='a'))  # Append results from second set of URLs to the same CSV

    export_to_gcs()
    