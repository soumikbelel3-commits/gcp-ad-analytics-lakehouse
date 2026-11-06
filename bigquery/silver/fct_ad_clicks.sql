-- =============================================================================
-- GCP BigQuery Silver Layer: Fact Ad Clicks
-- Destination: `ad_analytics_silver.fct_ad_clicks`
-- Pattern: Incremental MERGE / Idempotent Partition Overwrite
-- =============================================================================

CREATE TABLE IF NOT EXISTS `ad_analytics_silver.fct_ad_clicks` (
    click_id STRING NOT NULL,
    impression_id STRING NOT NULL,
    session_id STRING,
    cost FLOAT64,
    cost_in_cents INT64,
    clicked_at TIMESTAMP,
    created_at TIMESTAMP,
    _transformed_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY impression_id;

MERGE INTO `ad_analytics_silver.fct_ad_clicks` T
USING (
    SELECT
        click_id,
        impression_id,
        session_id,
        cost,
        CAST(ROUND(cost * 100) AS INT64) AS cost_in_cents,
        clicked_at,
        created_at,
        CURRENT_TIMESTAMP() AS _transformed_at
    FROM `ad_analytics_bronze.ad_click`
    WHERE created_at >= @start_time AND created_at < @end_time
) S
ON T.click_id = S.click_id
WHEN MATCHED THEN
    UPDATE SET
        impression_id = S.impression_id,
        session_id = S.session_id,
        cost = S.cost,
        cost_in_cents = S.cost_in_cents,
        clicked_at = S.clicked_at,
        created_at = S.created_at,
        _transformed_at = S._transformed_at
WHEN NOT MATCHED THEN
    INSERT ROW;
