"""
Cloud Composer / Apache Airflow DAG: GCP Ad Analytics Lakehouse Pipeline
Orchestrates end-to-end Medallion architecture on Google Cloud Platform:
GCS Raw -> Bronze Ingestion -> Silver Dims & Facts -> Gold OBT -> Gold Marts -> Soda Data Quality Audit.
"""

from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryExecuteQueryOperator,
    BigQueryInsertJobOperator,
)

# Pipeline Configuration
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "ad-analytics-gcp-prod")
GCS_LAKEHOUSE_BUCKET = os.environ.get("GCS_LAKEHOUSE_BUCKET", "ad-analytics-lakehouse")
SQL_BASE_PATH = os.environ.get("SQL_BASE_PATH", "/home/airflow/gcs/dags/bigquery")

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["soumikbelel3@gmail.com"],
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="gcp_ad_analytics_lakehouse_daily",
    default_args=default_args,
    description="Daily automated GCP Medallion ETL & Data Quality Pipeline",
    schedule_interval="0 2 * * *",  # 2:00 AM UTC daily
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["gcp", "bigquery", "dataproc", "ad-analytics", "medallion"],
) as dag:

    start_pipeline = EmptyOperator(task_id="start_pipeline")

    # -------------------------------------------------------------------------
    # Bronze Layer Ingestion
    # -------------------------------------------------------------------------
    ingest_bronze = BigQueryExecuteQueryOperator(
        task_id="ingest_bronze_tables",
        sql="""
        -- Refresh raw partition data from GCS external tables / landing stage
        CALL `ad_analytics_bronze.refresh_ad_events`();
        """,
        use_legacy_sql=False,
    )

    # -------------------------------------------------------------------------
    # Silver Layer (Dimensions & Facts in Parallel)
    # -------------------------------------------------------------------------
    transform_dim_advertiser = BigQueryExecuteQueryOperator(
        task_id="silver_dim_advertiser",
        sql=f"""
        CREATE OR REPLACE TABLE `{GCP_PROJECT_ID}.ad_analytics_silver.dim_advertiser` AS
        SELECT
            advertiser_id,
            name AS advertiser_name,
            billing_email,
            status,
            (status = 'active') AS is_active,
            created_at,
            updated_at,
            CURRENT_TIMESTAMP() AS _transformed_at
        FROM `{GCP_PROJECT_ID}.ad_analytics_bronze.advertiser`;
        """,
        use_legacy_sql=False,
    )

    transform_dim_campaign = BigQueryExecuteQueryOperator(
        task_id="silver_dim_campaign",
        sql=f"""
        CREATE OR REPLACE TABLE `{GCP_PROJECT_ID}.ad_analytics_silver.dim_campaign` AS
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
            FROM `{GCP_PROJECT_ID}.ad_analytics_bronze.ad_group`
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
        FROM `{GCP_PROJECT_ID}.ad_analytics_bronze.campaign` c
        LEFT JOIN ad_groups_aggregated ag
            ON c.campaign_id = ag.campaign_id;
        """,
        use_legacy_sql=False,
    )

    transform_fct_impressions = BigQueryExecuteQueryOperator(
        task_id="silver_fct_ad_impressions",
        sql=f"""
        MERGE INTO `{GCP_PROJECT_ID}.ad_analytics_silver.fct_ad_impressions` T
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
            FROM `{GCP_PROJECT_ID}.ad_analytics_bronze.ad_impression` ai
            LEFT JOIN `{GCP_PROJECT_ID}.ad_analytics_bronze.ad_creative` ac
                ON ai.creative_id = ac.creative_id
            WHERE ai.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)
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
        """,
        use_legacy_sql=False,
    )

    transform_fct_clicks = BigQueryExecuteQueryOperator(
        task_id="silver_fct_ad_clicks",
        sql=f"""
        MERGE INTO `{GCP_PROJECT_ID}.ad_analytics_silver.fct_ad_clicks` T
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
            FROM `{GCP_PROJECT_ID}.ad_analytics_bronze.ad_click`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)
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
        """,
        use_legacy_sql=False,
    )

    transform_fct_conversions = BigQueryExecuteQueryOperator(
        task_id="silver_fct_ad_conversions",
        sql=f"""
        MERGE INTO `{GCP_PROJECT_ID}.ad_analytics_silver.fct_ad_conversions` T
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
            FROM `{GCP_PROJECT_ID}.ad_analytics_bronze.ad_conversion`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)
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
        """,
        use_legacy_sql=False,
    )

    silver_sync_complete = EmptyOperator(task_id="silver_sync_complete")

    # -------------------------------------------------------------------------
    # Gold Layer: OBT Generation & Aggregations
    # -------------------------------------------------------------------------
    build_gold_obt = BigQueryExecuteQueryOperator(
        task_id="gold_obt_ad_impressions",
        sql=f"""
        MERGE INTO `{GCP_PROJECT_ID}.ad_analytics_gold.obt_ad_impressions` T
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
                FROM `{GCP_PROJECT_ID}.ad_analytics_silver.dim_campaign` c,
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
            FROM `{GCP_PROJECT_ID}.ad_analytics_silver.fct_ad_impressions` imp
            LEFT JOIN `{GCP_PROJECT_ID}.ad_analytics_silver.fct_ad_clicks` clk
                ON imp.impression_id = clk.impression_id
            LEFT JOIN `{GCP_PROJECT_ID}.ad_analytics_silver.fct_ad_conversions` cnv
                ON clk.click_id = cnv.click_id
            LEFT JOIN exploded_campaigns cmp
                ON imp.ad_group_id = cmp.ad_group_id
            LEFT JOIN `{GCP_PROJECT_ID}.ad_analytics_silver.dim_advertiser` adv
                ON cmp.advertiser_id = adv.advertiser_id
            WHERE imp.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)
        ) S
        ON T.impression_id = S.impression_id
        WHEN MATCHED THEN
            UPDATE SET
                creative_id = S.creative_id,
                ad_group_id = S.ad_group_id,
                placement = S.placement,
                impression_cost = S.impression_cost,
                click_id = S.click_id,
                click_cost = S.click_cost,
                conversion_id = S.conversion_id,
                conversion_revenue = S.conversion_revenue,
                total_cost = S.total_cost,
                is_clicked = S.is_clicked,
                is_converted = S.is_converted,
                _loaded_at = S._loaded_at
        WHEN NOT MATCHED THEN
            INSERT ROW;
        """,
        use_legacy_sql=False,
    )

    build_campaign_performance = BigQueryExecuteQueryOperator(
        task_id="gold_ad_campaign_performance",
        sql=f"""
        CREATE OR REPLACE TABLE `{GCP_PROJECT_ID}.ad_analytics_gold.ad_campaign_performance`
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
            FROM `{GCP_PROJECT_ID}.ad_analytics_gold.obt_ad_impressions`
            GROUP BY
                event_date, campaign_id, campaign_name, advertiser_id, advertiser_name,
                objective, budget_total, budget_daily, campaign_is_active
        ),
        rolling_metrics AS (
            SELECT
                *,
                SAFE_DIVIDE(
                    SUM(total_revenue) OVER (PARTITION BY campaign_id ORDER BY event_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
                    SUM(total_spend) OVER (PARTITION BY campaign_id ORDER BY event_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                ) AS roas_l7d,
                SAFE_DIVIDE(
                    SUM(total_revenue) OVER (PARTITION BY campaign_id ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW),
                    SUM(total_spend) OVER (PARTITION BY campaign_id ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
                ) AS roas_l30d,
                SAFE_DIVIDE(
                    SUM(total_revenue) OVER (PARTITION BY campaign_id ORDER BY event_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW),
                    SUM(total_spend) OVER (PARTITION BY campaign_id ORDER BY event_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW)
                ) AS roas_l90d
            FROM daily_metrics
        )
        SELECT
            event_date, campaign_id, campaign_name, advertiser_id, advertiser_name,
            objective, budget_total, budget_daily, campaign_is_active,
            total_impressions, total_clicks, total_conversions, total_spend, total_revenue,
            ROUND(roas, 4) AS roas,
            ROUND(roas_l7d, 4) AS roas_l7d,
            ROUND(roas_l30d, 4) AS roas_l30d,
            ROUND(roas_l90d, 4) AS roas_l90d,
            CURRENT_TIMESTAMP() AS _computed_at
        FROM rolling_metrics;
        """,
        use_legacy_sql=False,
    )

    build_funnel_summary = BigQueryExecuteQueryOperator(
        task_id="gold_ad_funnel_summary",
        sql=f"""
        CREATE OR REPLACE TABLE `{GCP_PROJECT_ID}.ad_analytics_gold.ad_funnel_summary`
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
            FROM `{GCP_PROJECT_ID}.ad_analytics_gold.obt_ad_impressions`
            GROUP BY
                event_date, ad_group_id, ad_group_name, campaign_id, campaign_name,
                advertiser_id, advertiser_name, bid_strategy, ad_group_is_active
        ),
        rolling_metrics AS (
            SELECT
                *,
                SAFE_DIVIDE(
                    SUM(total_conversions) OVER (PARTITION BY ad_group_id ORDER BY event_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
                    SUM(total_clicks) OVER (PARTITION BY ad_group_id ORDER BY event_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                ) AS cvr_l7d,
                SAFE_DIVIDE(
                    SUM(total_conversions) OVER (PARTITION BY ad_group_id ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW),
                    SUM(total_clicks) OVER (PARTITION BY ad_group_id ORDER BY event_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
                ) AS cvr_l30d,
                SAFE_DIVIDE(
                    SUM(total_conversions) OVER (PARTITION BY ad_group_id ORDER BY event_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW),
                    SUM(total_clicks) OVER (PARTITION BY ad_group_id ORDER BY event_date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW)
                ) AS cvr_l90d
            FROM daily_metrics
        )
        SELECT
            event_date, ad_group_id, ad_group_name, campaign_id, campaign_name,
            advertiser_id, advertiser_name, bid_strategy, ad_group_is_active,
            total_impressions, total_clicks, total_conversions, total_spend,
            ROUND(ctr, 4) AS ctr,
            ROUND(cvr, 4) AS cvr,
            ROUND(cpa, 2) AS cpa,
            ROUND(cvr_l7d, 4) AS cvr_l7d,
            ROUND(cvr_l30d, 4) AS cvr_l30d,
            ROUND(cvr_l90d, 4) AS cvr_l90d,
            CURRENT_TIMESTAMP() AS _computed_at
        FROM rolling_metrics;
        """,
        use_legacy_sql=False,
    )

    # -------------------------------------------------------------------------
    # Data Quality Gates: Soda Core Write-Audit-Publish (WAP)
    # -------------------------------------------------------------------------
    audit_data_quality = BashOperator(
        task_id="soda_data_quality_audit",
        bash_command="""
        soda scan -d gcp_bigquery -c /home/airflow/gcs/dags/soda/configuration.yml \
          /home/airflow/gcs/dags/gold/contracts/ad_campaign_performance.yaml \
          /home/airflow/gcs/dags/gold/contracts/ad_funnel_summary.yaml
        """,
    )

    pipeline_complete = EmptyOperator(task_id="pipeline_complete")

    # DAG Task Dependencies
    start_pipeline >> ingest_bronze
    ingest_bronze >> [
        transform_dim_advertiser,
        transform_dim_campaign,
        transform_fct_impressions,
        transform_fct_clicks,
        transform_fct_conversions,
    ] >> silver_sync_complete
    silver_sync_complete >> build_gold_obt
    build_gold_obt >> [build_campaign_performance, build_funnel_summary]
    [build_campaign_performance, build_funnel_summary] >> audit_data_quality >> pipeline_complete
