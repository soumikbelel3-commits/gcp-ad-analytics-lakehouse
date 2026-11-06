# =============================================================================
# IAM Service Accounts and Permissions
# =============================================================================

resource "google_service_account" "pipeline_sa" {
  account_id   = "sa-ad-analytics-pipeline"
  display_name = "Ad Analytics Pipeline Service Account"
  description  = "Service account executing Dataproc, BigQuery, and Airflow orchestration jobs"
}

# BigQuery Admin / Job User
resource "google_project_iam_member" "bq_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# GCS Storage Object Admin
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# Dataproc Worker Role
resource "google_project_iam_member" "dataproc_worker" {
  project = var.project_id
  role    = "roles/dataproc.worker"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}
