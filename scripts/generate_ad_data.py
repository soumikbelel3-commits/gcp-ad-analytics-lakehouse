"""
Synthetic Ad Tech Data Generator for GCP Ad Analytics Lakehouse.
Generates statistically realistic e-commerce ad impression, click, and conversion event streams,
along with relational dimensions (advertisers, campaigns, ad groups, ad creatives).
"""

import argparse
import datetime
import os
import random
import uuid
from pathlib import Path
import pandas as pd
import numpy as np


def generate_ad_data(
    num_advertisers: int = 8,
    campaigns_per_adv: int = 4,
    ad_groups_per_campaign: int = 3,
    creatives_per_ad_group: int = 2,
    num_impressions: int = 50000,
    days_back: int = 90,
    output_dir: str = "data/raw",
    seed: int = 42,
):
    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)

    base_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)
    now = datetime.datetime.now(datetime.timezone.utc)

    # 1. Advertisers
    advertiser_names = [
        ("Nike Official", "advertising@nike.com"),
        ("Apple E-Commerce", "ad-ops@apple.com"),
        ("Samsung Electronics", "growth@samsung.com"),
        ("Sony Interactive", "campaigns@sony.com"),
        ("Zara Fashion Direct", "marketing@zara.com"),
        ("Sephora Beauty", "performance@sephora.com"),
        ("Dyson Home Tech", "media@dyson.com"),
        ("Adidas Performance", "digital@adidas.com"),
    ][:num_advertisers]

    advertisers = []
    for i, (name, email) in enumerate(advertiser_names, start=1):
        created_at = base_date - datetime.timedelta(days=random.randint(30, 180))
        advertisers.append({
            "advertiser_id": f"ADV-{i:03d}",
            "name": name,
            "billing_email": email,
            "status": "active",
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": (created_at + datetime.timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
        })
    df_advertisers = pd.DataFrame(advertisers)

    # 2. Campaigns
    objectives = ["conversions", "traffic", "awareness", "sales"]
    campaign_names_pool = [
        "Summer Season Mega Sale",
        "Retargeting High-Intent Shoppers",
        "Brand Awareness Q3 Launch",
        "Performance Max Flagship Campaign",
        "Holiday Special Discounts",
        "App Installs & Engagement",
        "Cross-Sell Loyal Customers",
        "New Customer Acquisition Push",
    ]

    campaigns = []
    camp_counter = 1
    for adv in advertisers:
        for _ in range(campaigns_per_adv):
            c_name = f"{random.choice(campaign_names_pool)} #{camp_counter}"
            start_date = (base_date + datetime.timedelta(days=random.randint(0, 30))).date()
            duration = random.randint(30, 120)
            end_date = start_date + datetime.timedelta(days=duration)
            budget_total = round(random.uniform(15000, 120000), 2)
            budget_daily = round(budget_total / duration, 2)
            c_created = datetime.datetime.combine(start_date, datetime.time(8, 0)) - datetime.timedelta(days=random.randint(2, 7))

            campaigns.append({
                "campaign_id": f"CMP-{camp_counter:04d}",
                "advertiser_id": adv["advertiser_id"],
                "name": c_name,
                "objective": random.choice(objectives),
                "budget_total": budget_total,
                "budget_daily": budget_daily,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "created_at": c_created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": c_created.strftime("%Y-%m-%d %H:%M:%S"),
            })
            camp_counter += 1
    df_campaigns = pd.DataFrame(campaigns)

    # 3. Ad Groups
    targeting_types = ["keyword", "demographic", "retargeting", "interest"]
    bid_strategies = ["manual_cpc", "target_cpa", "cpc", "maximize_conversions"]
    ad_groups = []
    ag_counter = 1
    for cmp in campaigns:
        for j in range(ad_groups_per_campaign):
            strategy = random.choice(bid_strategies)
            max_cpc = round(random.uniform(0.75, 4.50), 2)
            created_at = datetime.datetime.strptime(cmp["created_at"], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=random.randint(1, 12))
            ad_groups.append({
                "ad_group_id": f"AG-{ag_counter:05d}",
                "campaign_id": cmp["campaign_id"],
                "name": f"{cmp['name'][:20]} - Grp {j+1}",
                "targeting_type": random.choice(targeting_types),
                "bid_strategy": strategy,
                "max_cpc": max_cpc,
                "status": "active" if random.random() > 0.1 else "paused",
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
            ag_counter += 1
    df_ad_groups = pd.DataFrame(ad_groups)

    # 4. Ad Creatives
    formats = ["banner_300x250", "video_responsive", "carousel_card", "search_headline"]
    creatives = []
    cr_counter = 1
    for ag in ad_groups:
        for k in range(creatives_per_ad_group):
            fmt = random.choice(formats)
            c_created = datetime.datetime.strptime(ag["created_at"], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=random.randint(1, 8))
            creatives.append({
                "creative_id": f"CR-{cr_counter:05d}",
                "ad_group_id": ag["ad_group_id"],
                "name": f"Asset {cr_counter} ({fmt})",
                "format": fmt,
                "asset_url": f"https://cdn.ad-platform.storage/assets/{fmt}/{cr_counter}.webp",
                "created_at": c_created.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": c_created.strftime("%Y-%m-%d %H:%M:%S"),
            })
            cr_counter += 1
    df_creatives = pd.DataFrame(creatives)

    # 5. Ad Impressions, Clicks, Conversions (Event Streams)
    placements = ["search_top", "feed_in_stream", "product_detail_page", "sidebar_widget"]
    placement_costs = {
        "search_top": (0.015, 0.045),
        "feed_in_stream": (0.008, 0.025),
        "product_detail_page": (0.010, 0.030),
        "sidebar_widget": (0.003, 0.012),
    }

    impressions = []
    clicks = []
    conversions = []

    creative_ids = [c["creative_id"] for c in creatives]
    num_customers = 15000

    print(f"Generating {num_impressions} ad impressions over {days_back} days...")
    for idx in range(num_impressions):
        # Event timestamp with daily diurnal peak (higher midday/evening)
        event_day = random.randint(0, days_back - 1)
        hour_prob = np.array([1, 1, 1, 1, 2, 3, 5, 8, 10, 11, 12, 12, 11, 10, 9, 8, 9, 11, 12, 11, 8, 5, 3, 2], dtype=float)
        hour_prob /= hour_prob.sum()
        event_hour = np.random.choice(24, p=hour_prob)
        event_minute = random.randint(0, 59)
        event_second = random.randint(0, 59)
        event_time = base_date + datetime.timedelta(days=event_day, hours=int(event_hour), minutes=event_minute, seconds=event_second)
        
        if event_time > now:
            event_time = now - datetime.timedelta(minutes=random.randint(1, 60))

        creative_id = random.choice(creative_ids)
        session_id = f"SES-{uuid.uuid4().hex[:12]}"
        customer_id = f"CUST-{random.randint(1, num_customers):06d}"
        placement = random.choice(placements)
        cost_min, cost_max = placement_costs[placement]
        imp_cost = round(random.uniform(cost_min, cost_max), 4)

        imp_id = f"IMP-{uuid.uuid4().hex[:16]}"
        timestamp_str = event_time.strftime("%Y-%m-%d %H:%M:%S")

        impressions.append({
            "impression_id": imp_id,
            "creative_id": creative_id,
            "session_id": session_id,
            "customer_id": customer_id,
            "placement": placement,
            "cost": imp_cost,
            "impressed_at": timestamp_str,
            "created_at": timestamp_str,
        })

        # Click probability (CTR ~ 3.2% overall, varies by placement)
        ctr_rate = 0.045 if placement == "search_top" else (0.035 if placement == "feed_in_stream" else 0.018)
        if random.random() < ctr_rate:
            click_delay_sec = random.randint(2, 45)
            click_time = event_time + datetime.timedelta(seconds=click_delay_sec)
            click_cost = round(random.uniform(0.40, 3.20), 2)
            click_id = f"CLK-{uuid.uuid4().hex[:16]}"
            click_time_str = click_time.strftime("%Y-%m-%d %H:%M:%S")

            clicks.append({
                "click_id": click_id,
                "impression_id": imp_id,
                "session_id": session_id,
                "cost": click_cost,
                "clicked_at": click_time_str,
                "created_at": click_time_str,
            })

            # Conversion probability (CVR ~ 8.5% given click)
            if random.random() < 0.085:
                conv_delay_sec = random.randint(60, 1800)
                conv_time = click_time + datetime.timedelta(seconds=conv_delay_sec)
                conv_id = f"CNV-{uuid.uuid4().hex[:16]}"
                order_id = f"ORD-{uuid.uuid4().hex[:12]}"
                revenue = round(random.uniform(25.0, 380.0), 2)
                attribution = random.choice(["last_click", "last_touch", "position_based"])
                conv_time_str = conv_time.strftime("%Y-%m-%d %H:%M:%S")

                conversions.append({
                    "conversion_id": conv_id,
                    "click_id": click_id,
                    "order_id": order_id,
                    "revenue": revenue,
                    "attribution": attribution,
                    "converted_at": conv_time_str,
                    "created_at": conv_time_str,
                })

    df_impressions = pd.DataFrame(impressions)
    df_clicks = pd.DataFrame(clicks)
    df_conversions = pd.DataFrame(conversions)

    # Export to CSV and Parquet for fast GCS/BigQuery loading
    tables = {
        "advertiser": df_advertisers,
        "campaign": df_campaigns,
        "ad_group": df_ad_groups,
        "ad_creative": df_creatives,
        "ad_impression": df_impressions,
        "ad_click": df_clicks,
        "ad_conversion": df_conversions,
    }

    for name, df in tables.items():
        csv_path = Path(output_dir) / f"{name}.csv"
        parquet_path = Path(output_dir) / f"{name}.parquet"
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        print(f"  [+] {name}: {len(df):,} records saved to {csv_path.name} & {parquet_path.name}")

    print("\nAd Tech Dataset generation complete:")
    print(f"  - Advertisers: {len(df_advertisers):,}")
    print(f"  - Campaigns: {len(df_campaigns):,}")
    print(f"  - Ad Groups: {len(df_ad_groups):,}")
    print(f"  - Ad Creatives: {len(df_creatives):,}")
    print(f"  - Impressions: {len(df_impressions):,}")
    print(f"  - Clicks: {len(df_clicks):,} (CTR: {len(df_clicks)/len(df_impressions):.2%})")
    print(f"  - Conversions: {len(df_conversions):,} (CVR: {len(df_conversions)/len(df_clicks):.2%})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic ad events for GCP analytics")
    parser.add_argument("--impressions", type=int, default=30000, help="Number of impressions")
    parser.add_argument("--days", type=int, default=90, help="Days of history")
    parser.add_argument("--output", type=str, default="data/raw", help="Output directory")
    args = parser.parse_args()

    generate_ad_data(num_impressions=args.impressions, days_back=args.days, output_dir=args.output)
