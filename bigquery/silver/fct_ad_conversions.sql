-- =============================================================================
-- GCP BigQuery Silver Layer: Fact Ad Conversions
-- Destination: `ad_analytics_silver.fct_ad_conversions`
-- Pattern: Incremental MERGE / Idempotent Partition Overwrite
-- =============================================================================

CREATE TABLE IF NOT EXISTS `ad_analytics_silver.fct_ad_conversions` (
    conversion_id STRING NOT NULL,
    click_id STRING NOT NULL,
    order_id STRING,
    revenue FLOAT64,
    revenue_in_cents INT64,
    attribution STRING,
    converted_at TIMESTAMP,
    created_at TIMESTAMP,
    _transformed_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY click_id, order_id;

MERGE INTO `ad_analytics_silver.fct_ad_conversions` T
USING (
    SELECT
        conversion_id,
        click_id,
        order_id,
        revenue,
        CAST(ROUND(revenue * 100) AS INT64) AS revenue_in_cents,
        attribution,
        converted_at,
        created_at,
        CURRENT_TIMESTAMP() AS _transformed_at
    FROM `ad_analytics_bronze.ad_conversion`
    WHERE created_at >= @start_time AND created_at < @end_time
) S
ON T.conversion_id = S.conversion_id
WHEN MATCHED THEN
    UPDATE SET
        click_id = S.click_id,
        order_id = S.order_id,
        revenue = S.revenue,
        revenue_in_cents = S.revenue_in_cents,
        attribution = S.attribution,
        converted_at = S.converted_at,
        created_at = S.created_at,
        _transformed_at = S._transformed_at
WHEN NOT MATCHED THEN
    INSERT ROW;
