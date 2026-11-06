# =============================================================================
# BigQuery Datasets for Medallion Architecture (Bronze, Silver, Gold)
# =============================================================================

# 1. Bronze Dataset
resource "google_bigquery_dataset" "bronze" {
  dataset_id                  = "ad_analytics_bronze"
  friendly_name               = "Ad Analytics Bronze Layer"
  description                 = "Raw ingestion tables from Postgres / Cloud Storage event drops"
  location                    = var.bq_location
  delete_contents_on_destroy  = false

  labels = {
    tier        = "bronze"
    environment = var.environment
    managed_by  = "terraform"
  }
}

# 2. Silver Dataset
resource "google_bigquery_dataset" "silver" {
  dataset_id                  = "ad_analytics_silver"
  friendly_name               = "Ad Analytics Silver Layer"
  description                 = "Conformed dimensional models and cleaned fact tables"
  location                    = var.bq_location
  delete_contents_on_destroy  = false

  labels = {
    tier        = "silver"
    environment = var.environment
    managed_by  = "terraform"
  }
}

# 3. Gold Dataset
resource "google_bigquery_dataset" "gold" {
  dataset_id                  = "ad_analytics_gold"
  friendly_name               = "Ad Analytics Gold Layer"
  description                 = "Aggregated data marts (Campaign Performance, Funnel Summary, and OBT)"
  location                    = var.bq_location
  delete_contents_on_destroy  = false

  labels = {
    tier        = "gold"
    environment = var.environment
    managed_by  = "terraform"
  }
}
