output "raw_landing_bucket" {
  description = "GCS bucket for raw event drops"
  value       = google_storage_bucket.raw_landing.name
}

output "lakehouse_bucket" {
  description = "GCS bucket for Iceberg / Parquet lakehouse storage"
  value       = google_storage_bucket.lakehouse.name
}

output "code_artifacts_bucket" {
  description = "GCS bucket for PySpark jobs, DAGs and artifacts"
  value       = google_storage_bucket.code_artifacts.name
}

output "bigquery_bronze_dataset" {
  description = "Bronze BigQuery dataset"
  value       = google_bigquery_dataset.bronze.dataset_id
}

output "bigquery_silver_dataset" {
  description = "Silver BigQuery dataset"
  value       = google_bigquery_dataset.silver.dataset_id
}

output "bigquery_gold_dataset" {
  description = "Gold BigQuery dataset"
  value       = google_bigquery_dataset.gold.dataset_id
}

output "pipeline_service_account" {
  description = "Email of the created Pipeline Service Account"
  value       = google_service_account.pipeline_sa.email
}
