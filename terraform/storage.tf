# =============================================================================
# Google Cloud Storage (GCS) Data Lake Buckets
# =============================================================================

# 1. Raw Landing Bucket (unprocessed event streams, CSV/Parquet uploads)
resource "google_storage_bucket" "raw_landing" {
  name                        = "${var.project_id}-raw-landing-${random_id.suffix.hex}"
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  labels = {
    environment = var.environment
    tier        = "landing"
    managed_by  = "terraform"
  }
}

# 2. Lakehouse Storage Bucket (PySpark Parquet / Apache Iceberg Medallion tiers)
resource "google_storage_bucket" "lakehouse" {
  name                        = "${var.project_id}-lakehouse-${random_id.suffix.hex}"
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
    tier        = "lakehouse"
    managed_by  = "terraform"
  }
}

# 3. Scripts, DAGs & Binaries Bucket (PySpark scripts, Soda contracts, Airflow code)
resource "google_storage_bucket" "code_artifacts" {
  name                        = "${var.project_id}-code-artifacts-${random_id.suffix.hex}"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    tier        = "artifacts"
    managed_by  = "terraform"
  }
}
