"""
Shared GCP and Local Configuration for Ad Analytics Data Platform.
Provides dynamic resolution of BigQuery datasets, GCS bucket paths, and Spark catalogs.
"""

import os

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "ad-analytics-gcp-prod")
GCS_LAKEHOUSE_BUCKET = os.environ.get("GCS_LAKEHOUSE_BUCKET", "ad-analytics-lakehouse")
SPARK_CATALOG = os.environ.get("SPARK_CATALOG", "local")

# Database / JDBC settings (e.g. Cloud SQL or local Postgres)
JDBC_URL = os.environ.get(
    "JDBC_URL",
    f"jdbc:postgresql://{os.environ.get('POSTGRES_HOST', 'postgres')}:5432/ecommerce"
)
JDBC_PROPERTIES = {
    "user": os.environ.get("POSTGRES_USER", "dataengineer"),
    "password": os.environ.get("POSTGRES_PASSWORD", "datapipeline"),
    "driver": "org.postgresql.Driver",
}

# Medallion Table Names
def get_table_name(layer: str, table_name: str) -> str:
    """Returns catalog-qualified table name or GCS path depending on environment."""
    return f"{SPARK_CATALOG}.{layer}.{table_name}"
