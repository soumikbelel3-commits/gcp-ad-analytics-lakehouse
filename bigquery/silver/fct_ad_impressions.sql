-- =============================================================================
-- GCP BigQuery Silver Layer: Fact Ad Impressions
-- Destination: `ad_analytics_silver.fct_ad_impressions`
-- Pattern: Incremental MERGE / Idempotent Partition Overwrite
-- =============================================================================

CREATE TABLE IF NOT EXISTS `ad_analytics_silver.fct_ad_impressions` (
    impression_id STRING NOT NULL,
    creative_id STRING NOT NULL,
    ad_group_id STRING,
    session_id STRING,
    customer_id STRING,
    placement STRING,
    cost FLOAT64,
    cost_in_cents INT64,
    impressed_at TIMESTAMP,
    created_at TIMESTAMP,
    _transformed_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY ad_group_id, creative_id, placement;

-- Incremental / Partition Run (parameters: @start_time, @end_time)
MERGE INTO `ad_analytics_silver.fct_ad_impressions` T
USING (
    SELECT
        ai.impression_id,
        ai.creative_id,
        ac.ad_group_id,
        ai.session_id,
        ai.customer_id,
        ai.placement,
        ai.cost,
        CAST(ROUND(ai.cost * 100) AS INT64) AS cost_in_cents,
        ai.impressed_at,
        ai.created_at,
        CURRENT_TIMESTAMP() AS _transformed_at
    FROM `ad_analytics_bronze.ad_impression` ai
    LEFT JOIN `ad_analytics_bronze.ad_creative` ac
        ON ai.creative_id = ac.creative_id
    WHERE ai.created_at >= @start_time AND ai.created_at < @end_time
) S
ON T.impression_id = S.impression_id
WHEN MATCHED THEN
    UPDATE SET
        creative_id = S.creative_id,
        ad_group_id = S.ad_group_id,
        session_id = S.session_id,
        customer_id = S.customer_id,
        placement = S.placement,
        cost = S.cost,
        cost_in_cents = S.cost_in_cents,
        impressed_at = S.impressed_at,
        created_at = S.created_at,
        _transformed_at = S._transformed_at
WHEN NOT MATCHED THEN
    INSERT ROW;
