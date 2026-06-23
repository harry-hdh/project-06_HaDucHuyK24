from google.cloud import bigquery

TABLE_SCHEMA = [
    bigquery.SchemaField("_id", "STRING", mode="REQUIRED", description="MongoDB ObjectId"),
    bigquery.SchemaField("time_stamp", "INTEGER", mode="NULLABLE", description="Epoch timestamp"),
    bigquery.SchemaField("ip", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("user_agent", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("resolution", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("user_id_db", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("device_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("api_version", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("store_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("local_time", "DATETIME", mode="NULLABLE", description="YYYY-MM-DD HH:MM:SS format"),
    bigquery.SchemaField("show_recommendation", "STRING", mode="NULLABLE"),  # Strings like "false" or null
    bigquery.SchemaField("current_url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("referrer_url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("email_address", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommendation", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("utm_source", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("utm_medium", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("collection", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("product_id", "STRING", mode="NULLABLE"),
    
    # Polymorphic and complex fields stored cleanly as JSON
    bigquery.SchemaField("option", "JSON", mode="NULLABLE", description="Polymorphic field (Array or Object)"),
    bigquery.SchemaField("cart_products", "JSON", mode="NULLABLE", description="Array of products in cart"),
    
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
]