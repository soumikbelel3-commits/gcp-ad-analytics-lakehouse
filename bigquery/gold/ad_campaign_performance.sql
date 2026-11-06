-- =============================================================================
-- GCP BigQuery Gold Layer: Campaign Performance Summary (Daily Grain)
-- Destination: `ad_analytics_gold.ad_campaign_performance`
-- Grain: campaign_id x event_date
-- Metrics: Impressions, Clicks, Conversions, Spend, Revenue, ROAS,
--          Rolling 7-day, 30-day, 90-day ROAS windows.
-- =============================================================================

CREATE OR REPLACE TABLE `ad_analytics_gold.ad_campaign_performance`
PARTITION BY event_date
CLUSTER BY campaign_id, advertiser_id AS
WITH daily_metrics AS (
    SELECT
        DATE(created_at) AS event_date,
        campaign_id,
        campaign_name,
        advertiser_id,
        advertiser_name,
        objective,
        budget_total,
        budget_daily,
        campaign_is_active,
        COUNT(impression_id) AS total_impressions,
        COUNT(click_id) AS total_clicks,
        COUNT(conversion_id) AS total_conversions,
        ROUND(SUM(COALESCE(impression_cost, 0.0) + COALESCE(click_cost, 0.0)), 4) AS total_spend,
        ROUND(SUM(COALESCE(conversion_revenue, 0.0)), 2) AS total_revenue,
        SAFE_DIVIDE(
            SUM(COALESCE(conversion_revenue, 0.0)),
            SUM(COALESCE(impression_cost, 0.0) + COALESCE(click_cost, 0.0))
        ) AS roas
    FROM `ad_analytics_gold.obt_ad_impressions`
    GROUP BY
        event_date,
        campaign_id,
        campaign_name,
        advertiser_id,
        advertiser_name,
        objective,
        budget_total,
        budget_daily,
        campaign_is_active
),
rolling_metrics AS (
    SELECT
        *,
        SAFE_DIVIDE(
            SUM(total_revenue) OVER (
                PARTITION BY campaign_id
                ORDER BY event_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ),
            SUM(total_spend) OVER (
                PARTITION BY campaign_id
                ORDER BY event_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            )
        ) AS roas_l7d,
        SAFE_DIVIDE(
            SUM(total_revenue) OVER (
                PARTITION BY campaign_id
                ORDER BY event_date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ),
            SUM(total_spend) OVER (
                PARTITION BY campaign_id
                ORDER BY event_date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            )
        ) AS roas_l30d,
        SAFE_DIVIDE(
            SUM(total_revenue) OVER (
                PARTITION BY campaign_id
                ORDER BY event_date
                ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
            ),
            SUM(total_spend) OVER (
                PARTITION BY campaign_id
                ORDER BY event_date
                ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
            )
        ) AS roas_l90d
    FROM daily_metrics
)
SELECT
    event_date,
    campaign_id,
    campaign_name,
    advertiser_id,
    advertiser_name,
    objective,
    budget_total,
    budget_daily,
    campaign_is_active,
    total_impressions,
    total_clicks,
    total_conversions,
    total_spend,
    total_revenue,
    ROUND(roas, 4) AS roas,
    ROUND(roas_l7d, 4) AS roas_l7d,
    ROUND(roas_l30d, 4) AS roas_l30d,
    ROUND(roas_l90d, 4) AS roas_l90d,
    CURRENT_TIMESTAMP() AS _computed_at
FROM rolling_metrics;
