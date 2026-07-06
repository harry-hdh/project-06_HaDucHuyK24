from google.cloud import bigquery

# TABLE_SCHEMA = [
#     bigquery.SchemaField("_id", "STRING", mode="REQUIRED", description="MongoDB ObjectId"),
#     bigquery.SchemaField("time_stamp", "INTEGER", mode="NULLABLE", description="Epoch timestamp"),
#     bigquery.SchemaField("ip", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("resolution", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("user_id_db", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("device_id", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("api_version", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("store_id", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("local_time", "DATETIME", mode="NULLABLE", description="YYYY-MM-DD HH:MM:SS format"),
#     bigquery.SchemaField("show_recommendation", "STRING", mode="NULLABLE"),  # Strings like "false" or null
#     bigquery.SchemaField("current_url", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("referrer_url", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("email_address", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("recommendation", "BOOLEAN", mode="NULLABLE"),
#     bigquery.SchemaField("utm_source", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("utm_medium", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("collection", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("product_id", "STRING", mode="NULLABLE"),
    
#     # Polymorphic and complex fields stored cleanly as JSON
#     bigquery.SchemaField("option", "JSON", mode="NULLABLE", description="Polymorphic field (Array or Object)"),
#     bigquery.SchemaField("cart_products", "JSON", mode="NULLABLE", description="Array of products in cart"),
    
#     # Nullable context fields
#     bigquery.SchemaField("cat_id", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("collect_id", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("viewing_product_id", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("price", "FLOAT", mode="NULLABLE"),
#     bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("is_paypal", "BOOLEAN", mode="NULLABLE"),
#     bigquery.SchemaField("recommendation_product_id", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("recommendation_clicked_position", "INTEGER", mode="NULLABLE"),
#     bigquery.SchemaField("key_search", "STRING", mode="NULLABLE"),
#     bigquery.SchemaField("order_id", "STRING", mode="NULLABLE"),
# ]

RAW_SCHEMA = [
    bigquery.SchemaField("_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("time_stamp", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("ip", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("resolution", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("user_id_db", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("device_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("api_version", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("store_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("local_time", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("show_recommendation", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("current_url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("referrer_url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("email_address", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommendation", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("utm_source", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("utm_medium", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("collection", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("product_id", "STRING", mode="NULLABLE"),
    # Nullable context fields
    bigquery.SchemaField("cat_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("collect_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("viewing_product_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("currency", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("is_paypal", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("recommendation_product_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommendation_clicked_position", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("key_search", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("order_id", "STRING", mode="NULLABLE"),
    
    # Nested Array/Struct to perfectly mirror MongoDB options
    bigquery.SchemaField(
        "option",
        "RECORD",
        mode="REPEATED",
        fields=[
            bigquery.SchemaField("option_label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("option_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("value_label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("value_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("quality", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("quality_label", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("alloy", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("diamond", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("shapediamond", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("product_id", "INTEGER", mode="NULLABLE"),
        ],
    ),
]


IP_LOCATION_SCHEMA = [
    bigquery.SchemaField("ip", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("region", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("city", "STRING", mode="NULLABLE")
]


PRODUCT_INFO_SCHEMA = [
    bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("product_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("sku", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("attribute_set_id", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("attribute_set", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("type_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("min_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("max_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("min_price_format", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("max_price_format", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("gold_weight", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("none_metal_weight", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("fixed_silver_weight", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("material_design", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("qty", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("collection", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("collection_id", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("product_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("product_type_value", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("category", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("category_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("store_code", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("platinum_palladium_info_in_alloy", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("bracelet_without_chain", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("show_popup_quantity_eternity", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("visible_contents", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("gender", "STRING", mode="NULLABLE")
]