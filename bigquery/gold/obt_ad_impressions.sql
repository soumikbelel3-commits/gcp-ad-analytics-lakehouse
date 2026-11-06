-- =============================================================================
-- GCP BigQuery Gold Layer: One Big Table (OBT) at Impression Grain
-- Destination: `ad_analytics_gold.obt_ad_impressions`
-- Pattern: Incremental Partition MERGE / Overwrite
-- Description: Denormalized wide table joining impressions, clicks, conversions,
--              campaign hierarchy, and advertiser dimensions.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS `ad_analytics_gold`
OPTIONS (
  location = 'US',
  description = 'Business-ready aggregated data marts and One Big Table (OBT)'
);

CREATE TABLE IF NOT EXISTS `ad_analytics_gold.obt_ad_impressions` (
    impression_id STRING NOT NULL,
    creative_id STRING,
    ad_group_id STRING,
    session_id STRING,
    customer_id STRING,
    placement STRING,
    impression_cost FLOAT64,
    impression_cost_in_cents INT64,
    impressed_at TIMESTAMP,
    created_at TIMESTAMP,
    click_id STRING,
    click_cost FLOAT64,
    click_cost_in_cents INT64,
    clicked_at TIMESTAMP,
    conversion_id STRING,
    order_id STRING,
    conversion_revenue FLOAT64,
    conversion_revenue_in_cents INT64,
    attribution STRING,
    converted_at TIMESTAMP,
    campaign_id STRING,
    advertiser_id STRING,
    campaign_name STRING,
    objective STRING,
    budget_total NUMERIC,
    budget_daily NUMERIC,
    start_date DATE,
    end_date DATE,
    campaign_is_active BOOL,
    campaign_duration_days INT64,
    ad_group_name STRING,
    targeting_type STRING,
    bid_strategy STRING,
    max_cpc NUMERIC,
    ad_group_is_active BOOL,
    is_cpc_bidding BOOL,
    advertiser_name STRING,
    billing_email STRING,
    advertiser_is_active BOOL,
    is_clicked BOOL,
    is_converted BOOL,
    total_cost FLOAT64,
    total_cost_in_cents INT64,
    _loaded_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY campaign_id, ad_group_id, placement;

-- Incremental MERGE statement
MERGE INTO `ad_analytics_gold.obt_ad_impressions` T
USING (
    WITH exploded_campaigns AS (
        SELECT
            c.campaign_id,
            c.advertiser_id,
            c.campaign_name,
            c.objective,
            c.budget_total,
            c.budget_daily,
            c.start_date,
            c.end_date,
            c.is_active AS campaign_is_active,
            c.campaign_duration_days,
            ag.ad_group_id,
            ag.ad_group_name,
            ag.targeting_type,
            ag.bid_strategy,
            ag.max_cpc,
            ag.is_active AS ad_group_is_active,
            ag.is_cpc_bidding
        FROM `ad_analytics_silver.dim_campaign` c,
        UNNEST(c.ad_groups) AS ag
    )
    SELECT
        imp.impression_id,
        imp.creative_id,
        imp.ad_group_id,
        imp.session_id,
        imp.customer_id,
        imp.placement,
        imp.cost AS impression_cost,
        imp.cost_in_cents AS impression_cost_in_cents,
        imp.impressed_at,
        imp.created_at,

        clk.click_id,
        clk.cost AS click_cost,
        clk.cost_in_cents AS click_cost_in_cents,
        clk.clicked_at,

        cnv.conversion_id,
        cnv.order_id,
        cnv.revenue AS conversion_revenue,
        cnv.revenue_in_cents AS conversion_revenue_in_cents,
        cnv.attribution,
        cnv.converted_at,

        cmp.campaign_id,
        cmp.advertiser_id,
        cmp.campaign_name,
        cmp.objective,
        cmp.budget_total,
        cmp.budget_daily,
        cmp.start_date,
        cmp.end_date,
        cmp.campaign_is_active,
        cmp.campaign_duration_days,
        cmp.ad_group_name,
        cmp.targeting_type,
        cmp.bid_strategy,
        cmp.max_cpc,
        cmp.ad_group_is_active,
        cmp.is_cpc_bidding,

        adv.advertiser_name,
        adv.billing_email,
        adv.is_active AS advertiser_is_active,

        (clk.click_id IS NOT NULL) AS is_clicked,
        (cnv.conversion_id IS NOT NULL) AS is_converted,
        (COALESCE(imp.cost, 0.0) + COALESCE(clk.cost, 0.0)) AS total_cost,
        (COALESCE(imp.cost_in_cents, 0) + COALESCE(clk.cost_in_cents, 0)) AS total_cost_in_cents,
        CURRENT_TIMESTAMP() AS _loaded_at
    FROM `ad_analytics_silver.fct_ad_impressions` imp
    LEFT JOIN `ad_analytics_silver.fct_ad_clicks` clk
        ON imp.impression_id = clk.impression_id
    LEFT JOIN `ad_analytics_silver.fct_ad_conversions` cnv
        ON clk.click_id = cnv.click_id
    LEFT JOIN exploded_campaigns cmp
        ON imp.ad_group_id = cmp.ad_group_id
    LEFT JOIN `ad_analytics_silver.dim_advertiser` adv
        ON cmp.advertiser_id = adv.advertiser_id
    WHERE imp.created_at >= @start_time AND imp.created_at < @end_time
) S
ON T.impression_id = S.impression_id
WHEN MATCHED THEN
    UPDATE SET
        creative_id = S.creative_id,
        ad_group_id = S.ad_group_id,
        session_id = S.session_id,
        customer_id = S.customer_id,
        placement = S.placement,
        impression_cost = S.impression_cost,
        impression_cost_in_cents = S.impression_cost_in_cents,
        impressed_at = S.impressed_at,
        created_at = S.created_at,
        click_id = S.click_id,
        click_cost = S.click_cost,
        click_cost_in_cents = S.click_cost_in_cents,
        clicked_at = S.clicked_at,
        conversion_id = S.conversion_id,
        order_id = S.order_id,
        conversion_revenue = S.conversion_revenue,
        conversion_revenue_in_cents = S.conversion_revenue_in_cents,
        attribution = S.attribution,
        converted_at = S.converted_at,
        campaign_id = S.campaign_id,
        advertiser_id = S.advertiser_id,
        campaign_name = S.campaign_name,
        objective = S.objective,
        budget_total = S.budget_total,
        budget_daily = S.budget_daily,
        start_date = S.start_date,
        end_date = S.end_date,
        campaign_is_active = S.campaign_is_active,
        campaign_duration_days = S.campaign_duration_days,
        ad_group_name = S.ad_group_name,
        targeting_type = S.targeting_type,
        bid_strategy = S.bid_strategy,
        max_cpc = S.max_cpc,
        ad_group_is_active = S.ad_group_is_active,
        is_cpc_bidding = S.is_cpc_bidding,
        advertiser_name = S.advertiser_name,
        billing_email = S.billing_email,
        advertiser_is_active = S.advertiser_is_active,
        is_clicked = S.is_clicked,
        is_converted = S.is_converted,
        total_cost = S.total_cost,
        total_cost_in_cents = S.total_cost_in_cents,
        _loaded_at = S._loaded_at
WHEN NOT MATCHED THEN
    INSERT ROW;
