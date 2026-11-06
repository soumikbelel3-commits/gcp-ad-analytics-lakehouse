# =============================================================================
# Google Cloud Composer (Managed Apache Airflow 2)
# Optional: enabled when enable_cloud_composer = true
# =============================================================================

resource "google_composer_environment" "composer_env" {
  count  = var.enable_cloud_composer ? 1 : 0
  name   = "ad-analytics-composer"
  region = var.region

  config {
    software_config {
      image_version = "composer-2-airflow-2.8.1"
      pypi_packages = {
        soda-core-bigquery = ">=3.3.0"
        apache-airflow-providers-google = ">=10.15.0"
      }
      env_variables = {
        GCP_PROJECT_ID   = var.project_id
        BQ_DATASET_GOLD  = google_bigquery_dataset.gold.dataset_id
      }
    }

    node_config {
      service_account = google_service_account.pipeline_sa.email
    }
  }
}
