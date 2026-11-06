#!/usr/bin/env bash
# =============================================================================
# GCP Environment Initialization & Terraform Setup Script
# =============================================================================
set -e

PROJECT_ID=${1:-"ad-analytics-gcp-prod"}
REGION=${2:-"us-central1"}

echo "=== Initializing Google Cloud Platform Project: ${PROJECT_ID} ==="

# 1. Configure gcloud CLI
gcloud config set project "${PROJECT_ID}"

# 2. Enable Required GCP APIs
echo "Enabling GCP APIs..."
gcloud services enable \
  storage.googleapis.com \
  bigquery.googleapis.com \
  bigquerystorage.googleapis.com \
  dataproc.googleapis.com \
  composer.googleapis.com \
  iam.googleapis.com \
  cloudbuild.googleapis.com

echo "GCP APIs enabled."

# 3. Initialize Terraform
echo "Initializing Terraform..."
cd terraform
terraform init
terraform plan -var="project_id=${PROJECT_ID}" -var="region=${REGION}"

echo "=== Setup complete! Run 'terraform apply' inside terraform/ to deploy ==="
