-- =============================================================================
-- GCP BigQuery Silver Layer: Dimension Campaign (with nested ad_groups array)
-- Destination: `ad_analytics_silver.dim_campaign`
-- Pattern: Full Overwrite with Aggregated Nested Structs
-- =============================================================================

CREATE OR REPLACE TABLE `ad_analytics_silver.dim_campaign` AS
WITH ad_groups_aggregated AS (
    SELECT
        campaign_id,
        ARRAY_AGG(
            STRUCT(
                ad_group_id,
                name AS ad_group_name,
                targeting_type,
                bid_strategy,
                max_cpc,
                status,
                (status = 'active') AS is_active,
                (bid_strategy IN ('cpc', 'manual_cpc')) AS is_cpc_bidding,
                created_at,
                updated_at
            )
        ) AS ad_groups
    FROM `ad_analytics_bronze.ad_group`
    GROUP BY campaign_id
)
SELECT
    c.campaign_id,
    c.advertiser_id,
    c.name AS campaign_name,
    c.objective,
    c.budget_total,
    c.budget_daily,
    c.start_date,
    c.end_date,
    (CURRENT_DATE() >= c.start_date AND CURRENT_DATE() <= c.end_date) AS is_active,
    DATE_DIFF(c.end_date, c.start_date, DAY) AS campaign_duration_days,
    c.created_at,
    c.updated_at,
    COALESCE(ag.ad_groups, []) AS ad_groups,
    CURRENT_TIMESTAMP() AS _transformed_at
FROM `ad_analytics_bronze.campaign` c
LEFT JOIN ad_groups_aggregated ag
    ON c.campaign_id = ag.campaign_id;
