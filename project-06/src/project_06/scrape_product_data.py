import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .utils import save_to_csv, read_product_csv, process_json_data, upload_file_to_gcs
from .config import GCS_PRODUCT_INFO_FOLDER_NAME
from .conn import get_gcs_client
from .logging import setup_logging

#ua = UserAgent()

logger = setup_logging()

async def fetch_and_parse(session, url, id, semaphore): # Controls how many requests
    async with semaphore:
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        #     "Accept-Language": "en-US,en;q=0.9",
        # }
        try:
            # Set a timeout so a single slow website won't hang script indefinitely
            timeout = aiohttp.ClientTimeout(total=15)
            async with session.get(url, timeout=timeout) as response:
                # if url have 'checkout' or status not equal to 200 try to use URL + product_id once
                if "checkout" in url or response.status != 200:
                    print(f"{response.status}: {url}. Attempting fallback with product_id.")
                    
                    fallback_url = f"https://www.glamira.com/catalog/product/view/id/{id}/"
                    async with session.get(fallback_url, timeout=timeout) as fallback_response:
                        if fallback_response.status == 200:
                            html = await fallback_response.text()
                            soup = BeautifulSoup(html, 'html.parser')

                            json_data = process_json_data(soup, fallback_url)

                            return json_data
                        else:
                            print(f"Fallback URL also failed: {fallback_url} with status {fallback_response.status}")

                            return {"title": "Failed to Fetch with Fallback", "url": fallback_url, "product_info": {}}

                elif response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # title_tag = soup.find('span', class_='base', attrs={"data-ui-id": "page-title-wrapper"})
                    # title = title_tag.text.strip() if title_tag else 'No Title Found'

                    json_data = process_json_data(soup, url)

                    return json_data

                else:
                    print(f"Failed to fetch {url}: Status {response.status}")
                    return {"title": "Failed to Fetch", "url": url, "product_info": {}}

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return {"title": "Error Occurred", "url": url, "product_info": {}}

#SAMPLE DATA json_data = {"product_id":110644,"name":"F\u00f6rlovningsring Titina 0.5 crt","sku":"titina05","attribute_set_id":55,"attribute_set":"diamonds","type_id":"simple","price":"7749.000000","min_price":"2098.000000","max_price":"461205.000000","min_price_format":"2\u00a0098,00\u00a0Kr","max_price_format":"461\u00a0205,00\u00a0Kr","gold_weight":"1.2051","none_metal_weight":0,"fixed_silver_weight":0,"material_design":null,"qty":1,"collection":"classic_solitaire","collection_id":"5171","product_type":"ring","product_type_value":"1","category":"605","category_name":"F\u00f6rlovningsringar","store_code":"glse","platinum_palladium_info_in_alloy":0,"bracelet_without_chain":0,"show_popup_quantity_eternity":0,"visible_contents":[""],"gender":"women"}

async def scrape_main(successful_save_path, err_save_path, urls, mode='w'):
    sem = asyncio.Semaphore(5)  #1. Limit to 5 concurrent requests
    # 2. Initialize a single client session
    async with aiohttp.ClientSession() as session:
        # 3. Create tasks for all URLs
        tasks = [fetch_and_parse(session, url, id, sem) for url, id in urls]
        # 4. Gather results
        results = await asyncio.gather(*tasks)
        # Check if results is error or failed to fetch and save to failed_urls.csv
        failed_results = [result for result in results if result["title"] in ["Failed to Fetch", "Failed to Fetch with Fallback", "Error Occurred"]]
        if failed_results:
            save_to_csv(failed_results, ["title", "url", "product_info"], err_save_path, mode=mode)
        # 5. Save successful results to CSV
        successful_results = [result for result in results if result["title"] not in ["Failed to Fetch", "Failed to Fetch with Fallback", "Error Occurred"]]
        if successful_results:
            save_to_csv(successful_results, ["title", "url", "name", "sku", "attribute_set_id", "attribute_set", "type_id", "price", "min_price", "max_price", "min_price_format", "max_price_format", "gold_weight", "none_metal_weight", "fixed_silver_weight", "material_design", "qty", "collection", "collection_id", "product_type", "product_type_value", "category", "category_name", "store_code", "platinum_palladium_info_in_alloy", "bracelet_without_chain", "show_popup_quantity_eternity", "visible_contents", "gender"], successful_save_path, mode=mode)
    bucket = get_gcs_client()
    if not bucket:
        logger.error("Failed to initialize GCS Client. Exiting.")
        return
    logger.info("Successfully initialized GCS Client.")
    upload_file_to_gcs(successful_save_path, "product_info", "csv" , bucket, GCS_PRODUCT_INFO_FOLDER_NAME)
    


#URLS = [(record["referrer_url"], record["product_id"]) for record in read_product_csv(CSV_FILE_PATH1)]
#asyncio.run(scrape_main(SAVE_PATH1, URLS))