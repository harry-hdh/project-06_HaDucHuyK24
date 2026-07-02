from conn import get_mongo_client
from utils import save_batch_csv, chunked


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)],
)

def extract_product_data(collection, target_events, fields_to_extract, folder_name, file_name, id_fallbacks=None):

    # 1. Base Match Stage (Filters event types)
    pipeline = [
        {"$match": {"collection": {"$in": target_events}}}
    ]
    # 2. Dynamically build the $project stage
    project_stage = {
        "_id": 0,
        "event_type": "$collection"  # Always keep track of which event it came from
    }

    for field in fields_to_extract:
        project_stage[field] = 1

    if id_fallbacks:
        for target_field, fallback_list in id_fallbacks.items():
            project_stage[target_field] = {"$ifNull": fallback_list}

    pipeline.append({"$project": project_stage})

    # 3. Filter out records where the main identifier ended up null
    if id_fallbacks:
        # Grabs the first target field defined (usually product_id) to ensure it's not empty
        main_id = list(id_fallbacks.keys())[0]
        pipeline.append({"$match": {main_id: {"$ne": None}}})

        # 4. Group by product_id to keep only unique entries
        group_stage = {
            "_id": f"${main_id}",  # Group keys by the generated product_id
            "event_type": {"$first": "$event_type"}  # Keep the first event type seen
        }
        for field in fields_to_extract:
            group_stage[field] = {"$first": f"${field}"}
        pipeline.append({"$group": group_stage})

        # 5. Clean up the grouped fields so the formatting stays pristine
        final_project_stage = {
            "_id": 0,
            main_id: "$_id",  # Turn '_id' back into your named property (e.g., 'product_id')
            "event_type": 1
        }
        for field in fields_to_extract:
            final_project_stage[field] = 1
            
        pipeline.append({"$project": final_project_stage})

    #Running aggregation query on MongoDB
    cursor = collection.aggregate(pipeline)
    # Convert cursor to a list of dicts to write to CSV
    extracted_records = list(cursor)

    # Save data to csv 
    if extracted_records:
        fieldnames = list(extracted_records[0].keys())

        for i, batch in enumerate(chunked(extracted_records, 1000), 1):  
            save_batch_csv(batch, fieldnames, file_name, i, folder_name)
    else:
        logging.info("No matching event data found based on your criteria.")


# collections = [
#     "view_product_detail",
#     "select_product_option",
#     "select_product_option_quality",
#     "add_to_cart_action",
#     "product_detail_recommendation_visible",
#     "product_detail_recommendation_noticed"
# ]
# product_id_fallback = {"product_id": ["$product_id", "$viewing_product_id"]}

# extract_product_data(collection=get_mongo_client(), target_events=collections, fields_to_extract=["current_url"], id_fallbacks=product_id_fallback, folder_name="output_current_urls", file_name="product_info")

# extract_product_data(collection=get_mongo_client(), target_events=[ "product_view_all_recommend_clicked" ], fields_to_extract=["referrer_url"], id_fallbacks={"product_id": ["$viewing_product_id", "$product_id"]}, folder_name="output", file_name="product_info_referrer_url")