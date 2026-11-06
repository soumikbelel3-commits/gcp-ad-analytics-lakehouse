<#
.SYNOPSIS
    Automated GCP Environment Initialization for Windows PowerShell.
#>
param (
    [string]$ProjectId = "ad-analytics-gcp-prod",
    [string]$Region = "us-central1"
)

Write-Host "=== Initializing Google Cloud Platform Project: $ProjectId ===" -ForegroundColor Cyan

# Configure gcloud
Write-Host "Configuring gcloud default project..."
gcloud config set project $ProjectId

# Enable Services
Write-Host "Enabling essential GCP APIs..." -ForegroundColor Yellow
gcloud services enable `
    storage.googleapis.com `
    bigquery.googleapis.com `
    bigquerystorage.googleapis.com `
    dataproc.googleapis.com `
    composer.googleapis.com `
    iam.googleapis.com `
    cloudbuild.googleapis.com

Write-Host "APIs enabled successfully." -ForegroundColor Green

# Terraform
Write-Host "Initializing Terraform..." -ForegroundColor Cyan
Set-Location terraform
terraform init
terraform plan -var="project_id=$ProjectId" -var="region=$Region"
Set-Location ..

Write-Host "=== Setup ready! Run 'terraform apply' inside terraform/ to deploy ===" -ForegroundColor Green
