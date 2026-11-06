-- =============================================================================
-- GCP BigQuery Gold Layer: Funnel Performance Summary (Daily Grain)
-- Destination: `ad_analytics_gold.ad_funnel_summary`
-- Grain: ad_group_id x event_date
-- Metrics: Impressions, Clicks, Conversions, Spend, CTR, CVR, CPA,
--          Rolling 7-day, 30-day, 90-day CVR windows.
-- =============================================================================

CREATE OR REPLACE TABLE `ad_analytics_gold.ad_funnel_summary`
PARTITION BY event_date
CLUSTER BY ad_group_id, campaign_id AS
WITH daily_metrics AS (
    SELECT
        DATE(created_at) AS event_date,
        ad_group_id,
        ad_group_name,
        campaign_id,
        campaign_name,
        advertiser_id,
        advertiser_name,
        bid_strategy,
        ad_group_is_active,
        COUNT(impression_id) AS total_impressions,
        COUNT(click_id) AS total_clicks,
        COUNT(conversion_id) AS total_conversions,
        ROUND(SUM(COALESCE(impression_cost, 0.0) + COALESCE(click_cost, 0.0)), 4) AS total_spend,
        SAFE_DIVIDE(COUNT(click_id), COUNT(impression_id)) AS ctr,
        SAFE_DIVIDE(COUNT(conversion_id), COUNT(click_id)) AS cvr,
        SAFE_DIVIDE(
            SUM(COALESCE(impression_cost, 0.0) + COALESCE(click_cost, 0.0)),
            COUNT(conversion_id)
        ) AS cpa
    FROM `ad_analytics_gold.obt_ad_impressions`
    GROUP BY
        event_date,
        ad_group_id,
        ad_group_name,
        campaign_id,
        campaign_name,
        advertiser_id,
        advertiser_name,
        bid_strategy,
        ad_group_is_active
),
rolling_metrics AS (
    SELECT
        *,
        SAFE_DIVIDE(
            SUM(total_conversions) OVER (
                PARTITION BY ad_group_id
                ORDER BY event_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ),
            SUM(total_clicks) OVER (
                PARTITION BY ad_group_id
                ORDER BY event_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            )
        ) AS cvr_l7d,
        SAFE_DIVIDE(
            SUM(total_conversions) OVER (
                PARTITION BY ad_group_id
                ORDER BY event_date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ),
            SUM(total_clicks) OVER (
                PARTITION BY ad_group_id
                ORDER BY event_date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            )
        ) AS cvr_l30d,
        SAFE_DIVIDE(
            SUM(total_conversions) OVER (
                PARTITION BY ad_group_id
                ORDER BY event_date
                ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
            ),
            SUM(total_clicks) OVER (
                PARTITION BY ad_group_id
                ORDER BY event_date
                ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
            )
        ) AS cvr_l90d
    FROM daily_metrics
)
SELECT
    event_date,
    ad_group_id,
    ad_group_name,
    campaign_id,
    campaign_name,
    advertiser_id,
    advertiser_name,
    bid_strategy,
    ad_group_is_active,
    total_impressions,
    total_clicks,
    total_conversions,
    total_spend,
    ROUND(ctr, 4) AS ctr,
    ROUND(cvr, 4) AS cvr,
    ROUND(cpa, 2) AS cpa,
    ROUND(cvr_l7d, 4) AS cvr_l7d,
    ROUND(cvr_l30d, 4) AS cvr_l30d,
    ROUND(cvr_l90d, 4) AS cvr_l90d,
    CURRENT_TIMESTAMP() AS _computed_at
FROM rolling_metrics;
