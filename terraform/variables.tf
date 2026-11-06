variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "ad-analytics-gcp-prod"
}

variable "region" {
  description = "Default GCP Region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "bq_location" {
  description = "BigQuery dataset location (US or EU multi-region, or single region)"
  type        = string
  default     = "US"
}

variable "enable_cloud_composer" {
  description = "Flag to enable or disable Cloud Composer environment creation"
  type        = bool
  default     = false
}
