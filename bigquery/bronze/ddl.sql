-- =============================================================================
-- GCP BigQuery Bronze Layer: External / Native Staging DDL
-- Dataset: `ad_analytics_bronze`
-- Ingestion: Cloud Storage (GCS) Parquet/CSV -> BigQuery Raw
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS `ad_analytics_bronze`
OPTIONS (
  location = 'US',
  description = 'Raw ingested ad event streams and operational tables from GCS / Cloud SQL'
);

-- 1. Advertiser Dimension Raw Table
CREATE OR REPLACE TABLE `ad_analytics_bronze.advertiser` (
    advertiser_id STRING NOT NULL,
    name STRING NOT NULL,
    billing_email STRING,
    status STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
    description = "Bronze table for raw advertiser profiles"
);

-- 2. Campaign Raw Table
CREATE OR REPLACE TABLE `ad_analytics_bronze.campaign` (
    campaign_id STRING NOT NULL,
    advertiser_id STRING NOT NULL,
    name STRING NOT NULL,
    objective STRING,
    budget_total NUMERIC,
    budget_daily NUMERIC,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
    description = "Bronze table for raw marketing campaigns"
);

-- 3. Ad Group Raw Table
CREATE OR REPLACE TABLE `ad_analytics_bronze.ad_group` (
    ad_group_id STRING NOT NULL,
    campaign_id STRING NOT NULL,
    name STRING NOT NULL,
    targeting_type STRING,
    bid_strategy STRING,
    max_cpc NUMERIC,
    status STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
    description = "Bronze table for raw ad group configurations and bidding rules"
);

-- 4. Ad Creative Raw Table
CREATE OR REPLACE TABLE `ad_analytics_bronze.ad_creative` (
    creative_id STRING NOT NULL,
    ad_group_id STRING NOT NULL,
    name STRING NOT NULL,
    format STRING,
    asset_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
    description = "Bronze table for creative banners, videos, and headlines"
);

-- 5. Ad Impressions Raw Fact
CREATE OR REPLACE TABLE `ad_analytics_bronze.ad_impression` (
    impression_id STRING NOT NULL,
    creative_id STRING NOT NULL,
    session_id STRING,
    customer_id STRING,
    placement STRING,
    cost FLOAT64,
    impressed_at TIMESTAMP,
    created_at TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY creative_id, placement
OPTIONS (
    description = "Bronze table for raw ad impressions partitioned by created_at"
);

-- 6. Ad Clicks Raw Fact
CREATE OR REPLACE TABLE `ad_analytics_bronze.ad_click` (
    click_id STRING NOT NULL,
    impression_id STRING NOT NULL,
    session_id STRING,
    cost FLOAT64,
    clicked_at TIMESTAMP,
    created_at TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY impression_id
OPTIONS (
    description = "Bronze table for raw ad clicks partitioned by created_at"
);

-- 7. Ad Conversions Raw Fact
CREATE OR REPLACE TABLE `ad_analytics_bronze.ad_conversion` (
    conversion_id STRING NOT NULL,
    click_id STRING NOT NULL,
    order_id STRING,
    revenue FLOAT64,
    attribution STRING,
    converted_at TIMESTAMP,
    created_at TIMESTAMP,
    _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY click_id, order_id
OPTIONS (
    description = "Bronze table for raw conversion events partitioned by created_at"
);
