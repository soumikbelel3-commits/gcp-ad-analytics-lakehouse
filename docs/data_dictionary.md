# Data Dictionary: GCP Ad Analytics Lakehouse

Comprehensive schema reference for all Medallion architecture layers across Google Cloud Storage (GCS) and BigQuery.

---

## 1. Bronze Layer (`ad_analytics_bronze`)

Raw ingestion tables mirrored from operational sources and event streaming dumps.

### `advertiser`
| Column | Type | Description |
|---|---|---|
| `advertiser_id` | STRING | Primary Key for advertiser entity |
| `name` | STRING | Legal/Display name of the brand/advertiser |
| `billing_email` | STRING | Financial contact email address |
| `status` | STRING | Account status (`active`, `paused`, `suspended`) |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### `campaign`
| Column | Type | Description |
|---|---|---|
| `campaign_id` | STRING | Primary Key for campaign |
| `advertiser_id` | STRING | Foreign Key referencing `advertiser` |
| `name` | STRING | Campaign campaign title |
| `objective` | STRING | Goal (`conversions`, `traffic`, `awareness`, `sales`) |
| `budget_total` | NUMERIC | Lifetime allocated budget in USD |
| `budget_daily` | NUMERIC | Target daily pacing budget in USD |
| `start_date` | DATE | Scheduled campaign start date |
| `end_date` | DATE | Scheduled campaign end date |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### `ad_group`
| Column | Type | Description |
|---|---|---|
| `ad_group_id` | STRING | Primary Key for ad group |
| `campaign_id` | STRING | Foreign Key referencing `campaign` |
| `name` | STRING | Name of target segment or cluster |
| `targeting_type` | STRING | Strategy (`keyword`, `demographic`, `retargeting`, `interest`) |
| `bid_strategy` | STRING | Bidding algorithm (`manual_cpc`, `target_cpa`, `cpc`, `maximize_conversions`) |
| `max_cpc` | NUMERIC | Upper bound cost-per-click ceiling |
| `status` | STRING | Status (`active`, `paused`) |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### `ad_creative`
| Column | Type | Description |
|---|---|---|
| `creative_id` | STRING | Primary Key for creative asset |
| `ad_group_id` | STRING | Foreign Key referencing `ad_group` |
| `name` | STRING | Creative asset name |
| `format` | STRING | Format type (`banner`, `video`, `carousel`, `search_headline`) |
| `asset_url` | STRING | CDN hosted URL for the creative asset |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### `ad_impression`
*Partitioned by `DATE(created_at)`, Clustered by `creative_id, placement`*
| Column | Type | Description |
|---|---|---|
| `impression_id` | STRING | UUID identifier for impression event |
| `creative_id` | STRING | Foreign Key referencing `ad_creative` |
| `session_id` | STRING | User browsing session identifier |
| `customer_id` | STRING | Unique consumer identifier |
| `placement` | STRING | Location (`search_top`, `feed_in_stream`, `product_detail_page`, etc.) |
| `cost` | FLOAT64 | CPM impression cost in USD |
| `impressed_at` | TIMESTAMP | Timestamp when impression was served |
| `created_at` | TIMESTAMP | Partition ingestion timestamp |

### `ad_click`
*Partitioned by `DATE(created_at)`, Clustered by `impression_id`*
| Column | Type | Description |
|---|---|---|
| `click_id` | STRING | UUID identifier for click event |
| `impression_id` | STRING | Foreign Key referencing `ad_impression` |
| `session_id` | STRING | User session identifier |
| `cost` | FLOAT64 | Cost-per-click charged in USD |
| `clicked_at` | TIMESTAMP | Timestamp of user interaction |
| `created_at` | TIMESTAMP | Partition ingestion timestamp |

### `ad_conversion`
*Partitioned by `DATE(created_at)`, Clustered by `click_id, order_id`*
| Column | Type | Description |
|---|---|---|
| `conversion_id` | STRING | UUID identifier for conversion event |
| `click_id` | STRING | Foreign Key referencing `ad_click` |
| `order_id` | STRING | E-commerce order number |
| `revenue` | FLOAT64 | Total gross revenue generated from conversion in USD |
| `attribution` | STRING | Attribution model (`last_click`, `position_based`, etc.) |
| `converted_at` | TIMESTAMP | Timestamp of purchase completion |
| `created_at` | TIMESTAMP | Partition ingestion timestamp |

---

## 2. Silver Layer (`ad_analytics_silver`)

Conformed, enriched dimensions and partitioned facts.

- **`dim_advertiser`**: Cleansed advertiser profiles with active boolean flags.
- **`dim_campaign`**: Campaign dimension with nested `ad_groups` array structs, duration calculations, and active status.
- **`fct_ad_impressions`**: Impression facts joined with creative metadata and normalized currency (`cost_in_cents`).
- **`fct_ad_clicks`**: Click facts with `cost_in_cents` representation for precision accounting.
- **`fct_ad_conversions`**: Conversion facts with attribution models and integer `revenue_in_cents`.

---

## 3. Gold Layer (`ad_analytics_gold`)

Analytics-ready One Big Table (OBT) and aggregate dimensional marts.

- **`obt_ad_impressions`**: Denormalized wide table joining all Silver entities at impression grain, including `is_clicked`, `is_converted`, `total_cost`, campaign budgets, and placement.
- **`ad_campaign_performance`**: Campaign x Day grain summary. Contains:
  - `total_impressions`, `total_clicks`, `total_conversions`
  - `total_spend`, `total_revenue`, `roas`
  - Rolling window indicators: `roas_l7d`, `roas_l30d`, `roas_l90d`
- **`ad_funnel_summary`**: Ad Group x Day grain funnel summary. Contains:
  - `ctr` (`clicks / impressions`)
  - `cvr` (`conversions / clicks`)
  - `cpa` (`spend / conversions`)
  - Rolling window indicators: `cvr_l7d`, `cvr_l30d`, `cvr_l90d`
