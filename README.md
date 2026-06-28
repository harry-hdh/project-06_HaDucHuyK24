# project-06_HaDucHuyK24
project-05 continue

- Depoy function on gcp
```
gcloud functions deploy load_gcs_to_bigquery_v4 \
--gen2 \
--runtime=python311 \
--region=us-central1 \
--trigger-location=us \
--entry-point=load_gcs_to_bigquery_trigger \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=glamira_data-1" \
--service-account="myaccount@<project>.iam.gserviceaccount.com" \
--cpu=2 \
--memory=4Gi
```