-- =============================================================================
-- GCP BigQuery Silver Layer: Dimension Advertiser
-- Destination: `ad_analytics_silver.dim_advertiser`
-- Pattern: Full Overwrite (Type 1 Dimension)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS `ad_analytics_silver`
OPTIONS (
  location = 'US',
  description = 'Cleaned, typed, and enriched dimension and fact tables'
);

CREATE OR REPLACE TABLE `ad_analytics_silver.dim_advertiser` AS
SELECT
    advertiser_id,
    name AS advertiser_name,
    billing_email,
    status,
    (status = 'active') AS is_active,
    created_at,
    updated_at,
    CURRENT_TIMESTAMP() AS _transformed_at
FROM `ad_analytics_bronze.advertiser`;
