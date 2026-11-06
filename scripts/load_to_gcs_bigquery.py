"""
GCP Ingestion Utility: Uploads raw ad tech events to Google Cloud Storage (GCS)
and triggers BigQuery load jobs into the Bronze dataset.
"""

import argparse
import os
from pathlib import Path


def upload_to_gcs_and_load_bigquery(
    project_id: str,
    bucket_name: str,
    data_dir: str = "data/raw",
    dataset_bronze: str = "ad_analytics_bronze",
):
    print(f"[*] Starting ingestion into GCP Project: {project_id}")
    print(f"[*] Target GCS Bucket: gs://{bucket_name}/raw/")
    print(f"[*] Target BigQuery Dataset: {dataset_bronze}")

    try:
        from google.cloud import storage, bigquery
    except ImportError:
        print("[!] Note: 'google-cloud-storage' and 'google-cloud-bigquery' are required for GCP execution.")
        print("    Install them with: pip install google-cloud-storage google-cloud-bigquery")
        return

    storage_client = storage.Client(project=project_id)
    bq_client = bigquery.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)

    files = list(Path(data_dir).glob("*.parquet"))
    if not files:
        print(f"[!] No parquet files found in {data_dir}. Run 'python scripts/generate_ad_data.py' first.")
        return

    for file_path in files:
        table_name = file_path.stem
        blob_path = f"raw/{table_name}/{file_path.name}"
        blob = bucket.blob(blob_path)

        print(f"[+] Uploading {file_path.name} -> gs://{bucket_name}/{blob_path}...")
        blob.upload_from_filename(str(file_path))

        gcs_uri = f"gs://{bucket_name}/{blob_path}"
        table_ref = f"{project_id}.{dataset_bronze}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
            if table_name in ["advertiser", "campaign", "ad_group", "ad_creative"]
            else bigquery.WriteDisposition.WRITE_APPEND,
        )

        print(f"[+] Submitting BigQuery Load Job for {table_ref}...")
        load_job = bq_client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
        load_job.result()
        print(f"[OK] Table {table_ref} loaded successfully ({load_job.output_rows} rows).")

    print("\n[SUCCESS] Bronze Layer ingestion complete in Google Cloud Platform!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload ad tech data to GCS and load into BigQuery Bronze")
    parser.add_argument("--project", default=os.environ.get("GCP_PROJECT_ID", "ad-analytics-gcp-prod"), help="GCP Project ID")
    parser.add_argument("--bucket", default=os.environ.get("GCS_LAKEHOUSE_BUCKET", "ad-analytics-lakehouse"), help="GCS Bucket Name")
    parser.add_argument("--data-dir", default="data/raw", help="Local directory containing parquet/csv data")
    args = parser.parse_args()

    upload_to_gcs_and_load_bigquery(args.project, args.bucket, args.data_dir)
