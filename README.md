# project-06_HaDucHuyK24
project-05 continue

- Depoy function on gcp
```
gcloud functions deploy load_gcs_to_bigquery \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --main-entry-point=trigger_bigquery_load \
    --trigger-event-resource=projects/_/buckets/your-gcs-bucket-name \
    --trigger-event=google.storage.object.v1.finalized
```