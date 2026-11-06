"""
Visual and Diagram Generator for GCP Ad Analytics Lakehouse.
Generates publication-ready architecture diagrams, data lineage charts,
and ad tech performance visuals using Matplotlib and PIL.
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd


def setup_diagram_dirs():
    os.makedirs("docs/diagrams", exist_ok=True)
    os.makedirs("charts", exist_ok=True)


# =============================================================================
# 1. GCP End-to-End System Architecture Diagram
# =============================================================================
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.patch.set_facecolor('#0F172A')  # Slate-900 background
    ax.set_facecolor('#0F172A')

    # Color Palette (GCP Themed)
    c_gcp_blue = '#4285F4'
    c_gcp_red = '#EA4335'
    c_gcp_yellow = '#FBBC05'
    c_gcp_green = '#34A853'
    c_bronze = '#CD7F32'
    c_silver = '#94A3B8'
    c_gold = '#F59E0B'
    c_card_bg = '#1E293B'
    c_border = '#334155'
    c_text_main = '#F8FAFC'
    c_text_sub = '#94A3B8'

    # Title & Header
    ax.text(0.04, 0.94, "GCP Ad Analytics Lakehouse — Production Architecture",
            fontsize=20, fontweight='bold', color=c_text_main, va='top')
    ax.text(0.04, 0.90, "End-to-End Medallion Lakehouse on Google Cloud Platform: Airflow (Composer) | PySpark (Dataproc) | BigQuery | Looker Studio",
            fontsize=11, color=c_text_sub, va='top')

    # Stage Containers (Columns)
    stages = [
        {"title": "1. INGESTION & SOURCES", "x": 0.04, "w": 0.16, "color": c_gcp_red},
        {"title": "2. STORAGE & LANDING", "x": 0.22, "w": 0.16, "color": c_gcp_yellow},
        {"title": "3. COMPUTE & PIPELINE", "x": 0.40, "w": 0.18, "color": c_gcp_blue},
        {"title": "4. MEDALLION WAREHOUSE", "x": 0.60, "w": 0.20, "color": c_gcp_green},
        {"title": "5. BI & OBSERVABILITY", "x": 0.82, "w": 0.15, "color": '#A855F7'},
    ]

    for s in stages:
        # Container header card
        rect = patches.FancyBboxPatch(
            (s["x"], 0.10), s["w"], 0.76,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            facecolor='#162032', edgecolor=s["color"], linewidth=1.5, alpha=0.9
        )
        ax.add_patch(rect)
        ax.text(s["x"] + s["w"] / 2, 0.83, s["title"],
                fontsize=10, fontweight='bold', color=s["color"], ha='center', va='center')

    # 1. Sources Cards
    sources = [
        ("Cloud SQL (Postgres)", "Advertiser, Campaign,\nAd Group, Creatives"),
        ("Ad Event Streams", "Live Impression Stream\n(20k+ events/day)"),
        ("Click & Conv Pixels", "Real-time Ad Clicks\n& Purchase Conversions"),
    ]
    y_pos = [0.66, 0.46, 0.26]
    for (name, desc), y in zip(sources, y_pos):
        card = patches.FancyBboxPatch(
            (0.055, y - 0.07), 0.13, 0.14,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=c_card_bg, edgecolor=c_border, linewidth=1
        )
        ax.add_patch(card)
        ax.text(0.12, y + 0.03, name, fontsize=10, fontweight='bold', color=c_text_main, ha='center')
        ax.text(0.12, y - 0.03, desc, fontsize=8, color=c_text_sub, ha='center', linespacing=1.2)

    # 2. Storage Cards
    storage_nodes = [
        ("GCS Raw Landing", "gs://...-raw-landing/\nBatch drops & Parquet"),
        ("GCS Lakehouse", "gs://...-lakehouse/\nIceberg / Parquet format"),
        ("GCS Artifacts", "gs://...-code-artifacts/\nPySpark scripts & configs"),
    ]
    for (name, desc), y in zip(storage_nodes, y_pos):
        card = patches.FancyBboxPatch(
            (0.235, y - 0.07), 0.13, 0.14,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=c_card_bg, edgecolor=c_border, linewidth=1
        )
        ax.add_patch(card)
        ax.text(0.30, y + 0.03, name, fontsize=10, fontweight='bold', color=c_text_main, ha='center')
        ax.text(0.30, y - 0.03, desc, fontsize=8, color=c_text_sub, ha='center', linespacing=1.2)

    # 3. Compute Cards
    compute_nodes = [
        ("Cloud Composer 2", "Managed Apache Airflow\nDAG Orchestrator & Alerts"),
        ("Cloud Dataproc", "Serverless Spark / PySpark\nPartition overwrites (Idempotent)"),
        ("BigQuery Engine", "Serverless SQL transforms\nMERGE, Clustering, Views"),
    ]
    for (name, desc), y in zip(compute_nodes, y_pos):
        card = patches.FancyBboxPatch(
            (0.415, y - 0.07), 0.15, 0.14,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=c_card_bg, edgecolor=c_border, linewidth=1
        )
        ax.add_patch(card)
        ax.text(0.49, y + 0.03, name, fontsize=10, fontweight='bold', color=c_gcp_blue, ha='center')
        ax.text(0.49, y - 0.03, desc, fontsize=8, color=c_text_sub, ha='center', linespacing=1.2)

    # 4. Medallion Cards (Bronze -> Silver -> Gold)
    medallion_nodes = [
        ("Bronze (Raw Stage)", "7 Raw Tables | GCS External\nappend & full snapshot", c_bronze),
        ("Silver (Conformed)", "Dims & Partitioned Facts\nType casting & cents conversion", c_silver),
        ("Gold (Marts & OBT)", "obt_ad_impressions (Wide)\nCampaign Perf & Funnel Marts", c_gold),
    ]
    for (name, desc, color), y in zip(medallion_nodes, y_pos):
        card = patches.FancyBboxPatch(
            (0.615, y - 0.07), 0.17, 0.14,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=c_card_bg, edgecolor=color, linewidth=1.5
        )
        ax.add_patch(card)
        ax.text(0.70, y + 0.03, name, fontsize=10, fontweight='bold', color=color, ha='center')
        ax.text(0.70, y - 0.03, desc, fontsize=8, color=c_text_sub, ha='center', linespacing=1.2)

    # 5. BI & Observability
    bi_nodes = [
        ("Looker Studio", "Executive KPI Dashboards\nROAS, CTR, CVR, Spend trends"),
        ("Soda Core (WAP)", "Write-Audit-Publish gate\nZero bad data leakage"),
        ("Cloud Monitoring", "Alerting, Audit Logs,\nResource metrics & SLA"),
    ]
    for (name, desc), y in zip(bi_nodes, y_pos):
        card = patches.FancyBboxPatch(
            (0.835, y - 0.07), 0.12, 0.14,
            boxstyle="round,pad=0.01,rounding_size=0.015",
            facecolor=c_card_bg, edgecolor=c_border, linewidth=1
        )
        ax.add_patch(card)
        ax.text(0.895, y + 0.03, name, fontsize=10, fontweight='bold', color=c_text_main, ha='center')
        ax.text(0.895, y - 0.03, desc, fontsize=8, color=c_text_sub, ha='center', linespacing=1.2)

    # Connecting Flow Arrows
    arrow_props = dict(arrowstyle="->", color=c_gcp_blue, lw=2, mutation_scale=15)
    ax.annotate("", xy=(0.235, 0.66), xytext=(0.185, 0.66), arrowprops=arrow_props)
    ax.annotate("", xy=(0.235, 0.46), xytext=(0.185, 0.46), arrowprops=arrow_props)
    ax.annotate("", xy=(0.235, 0.26), xytext=(0.185, 0.26), arrowprops=arrow_props)

    ax.annotate("", xy=(0.415, 0.46), xytext=(0.365, 0.46), arrowprops=arrow_props)
    ax.annotate("", xy=(0.615, 0.66), xytext=(0.565, 0.66), arrowprops=arrow_props)
    ax.annotate("", xy=(0.615, 0.46), xytext=(0.565, 0.46), arrowprops=arrow_props)
    ax.annotate("", xy=(0.615, 0.26), xytext=(0.565, 0.26), arrowprops=arrow_props)

    arrow_gold = dict(arrowstyle="->", color=c_gold, lw=2, mutation_scale=15)
    ax.annotate("", xy=(0.835, 0.66), xytext=(0.785, 0.26), arrowprops=arrow_gold)
    ax.annotate("", xy=(0.835, 0.46), xytext=(0.785, 0.26), arrowprops=arrow_gold)

    # Footer note
    ax.text(0.50, 0.04, "Designed & Engineered by Soumik Belel | GitHub: soumikbelel3-commits",
            fontsize=10, color=c_text_sub, ha='center')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    output_path = "docs/diagrams/gcp_architecture.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Generated {output_path}")


# =============================================================================
# 2. Medallion Data Lineage & Flow Diagram
# =============================================================================
def generate_medallion_lineage_diagram():
    fig, ax = plt.subplots(figsize=(15, 8), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')

    c_blue = '#38BDF8'
    c_bronze = '#D97706'
    c_silver = '#94A3B8'
    c_gold = '#FBBF24'
    c_box = '#1E293B'
    c_text = '#F8FAFC'
    c_dim = '#64748B'

    ax.text(0.04, 0.94, "Medallion Data Lineage & Transformation Topology",
            fontsize=18, fontweight='bold', color=c_text)
    ax.text(0.04, 0.90, "Detailed data flow from Raw Ingestion to Silver conformed dimensional models to Gold OBT and Aggregates",
            fontsize=10, color=c_dim)

    # Layer columns
    layers = [
        ("Postgres / Raw", 0.08, c_blue),
        ("Bronze Layer", 0.30, c_bronze),
        ("Silver Layer", 0.54, c_silver),
        ("Gold Layer", 0.82, c_gold),
    ]
    for title, x, col in layers:
        ax.text(x, 0.84, title, fontsize=12, fontweight='bold', color=col, ha='center')
        ax.plot([x - 0.09, x + 0.09], [0.82, 0.82], color=col, lw=2)

    # Nodes definition
    nodes = {
        # Sources
        "s_adv": (0.08, 0.74, "advertiser"),
        "s_cmp": (0.08, 0.64, "campaign"),
        "s_ag": (0.08, 0.54, "ad_group"),
        "s_cr": (0.08, 0.44, "ad_creative"),
        "s_imp": (0.08, 0.34, "ad_impression"),
        "s_clk": (0.08, 0.24, "ad_click"),
        "s_cnv": (0.08, 0.14, "ad_conversion"),

        # Bronze
        "b_adv": (0.30, 0.74, "bronze.advertiser"),
        "b_cmp": (0.30, 0.64, "bronze.campaign"),
        "b_ag": (0.30, 0.54, "bronze.ad_group"),
        "b_cr": (0.30, 0.44, "bronze.ad_creative"),
        "b_imp": (0.30, 0.34, "bronze.ad_impression"),
        "b_clk": (0.30, 0.24, "bronze.ad_click"),
        "b_cnv": (0.30, 0.14, "bronze.ad_conversion"),

        # Silver
        "v_adv": (0.54, 0.74, "dim_advertiser"),
        "v_cmp": (0.54, 0.59, "dim_campaign\n(nested ad_groups)"),
        "v_imp": (0.54, 0.39, "fct_ad_impressions\n(joined ad_creative)"),
        "v_clk": (0.54, 0.24, "fct_ad_clicks"),
        "v_cnv": (0.54, 0.14, "fct_ad_conversions"),

        # Gold
        "g_obt": (0.82, 0.52, "obt_ad_impressions\n(Wide One Big Table)"),
        "g_perf": (0.82, 0.30, "ad_campaign_performance\n(ROAS & rolling windows)"),
        "g_funnel": (0.82, 0.12, "ad_funnel_summary\n(CTR, CVR, CPA)"),
    }

    # Render Node Boxes
    for k, (x, y, label) in nodes.items():
        border_c = c_gold if k.startswith("g_") else (c_silver if k.startswith("v_") else (c_bronze if k.startswith("b_") else c_blue))
        box = patches.FancyBboxPatch(
            (x - 0.08, y - 0.038), 0.16, 0.076,
            boxstyle="round,pad=0.008,rounding_size=0.015",
            facecolor=c_box, edgecolor=border_c, linewidth=1.2
        )
        ax.add_patch(box)
        ax.text(x, y, label, fontsize=8, color=c_text, ha='center', va='center', fontweight='semibold')

    # Draw Connections
    connections = [
        # Source to Bronze
        ("s_adv", "b_adv"), ("s_cmp", "b_cmp"), ("s_ag", "b_ag"),
        ("s_cr", "b_cr"), ("s_imp", "b_imp"), ("s_clk", "b_clk"), ("s_cnv", "b_cnv"),

        # Bronze to Silver
        ("b_adv", "v_adv"),
        ("b_cmp", "v_cmp"),
        ("b_ag", "v_cmp"),
        ("b_cr", "v_imp"),
        ("b_imp", "v_imp"),
        ("b_clk", "v_clk"),
        ("b_cnv", "v_cnv"),

        # Silver to Gold OBT
        ("v_adv", "g_obt"),
        ("v_cmp", "g_obt"),
        ("v_imp", "g_obt"),
        ("v_clk", "g_obt"),
        ("v_cnv", "g_obt"),

        # Gold OBT to Aggregates
        ("g_obt", "g_perf"),
        ("g_obt", "g_funnel"),
    ]

    for src, dst in connections:
        sx, sy, _ = nodes[src]
        dx, dy, _ = nodes[dst]
        ax.annotate("", xy=(dx - 0.08, dy), xytext=(sx + 0.08, sy),
                    arrowprops=dict(arrowstyle="->", color='#475569', lw=1.2, mutation_scale=10))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    output_path = "docs/diagrams/medallion_data_flow.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Generated {output_path}")


# =============================================================================
# 3. Campaign Performance Comparison Visual
# =============================================================================
def generate_performance_visual():
    raw_conv_path = Path("data/raw/ad_conversion.parquet")
    raw_click_path = Path("data/raw/ad_click.parquet")
    raw_imp_path = Path("data/raw/ad_impression.parquet")
    raw_cmp_path = Path("data/raw/campaign.parquet")
    raw_ag_path = Path("data/raw/ad_group.parquet")
    raw_cr_path = Path("data/raw/ad_creative.parquet")

    if not (raw_conv_path.exists() and raw_cmp_path.exists()):
        print("[!] Raw parquet files missing, skipping campaign_performance.png generation.")
        return

    df_conv = pd.read_parquet(raw_conv_path)
    df_click = pd.read_parquet(raw_click_path)
    df_imp = pd.read_parquet(raw_imp_path)
    df_cmp = pd.read_parquet(raw_cmp_path)
    df_ag = pd.read_parquet(raw_ag_path)
    df_cr = pd.read_parquet(raw_cr_path)

    # Calculate campaign metrics
    imp_with_ag = df_imp.merge(df_cr[['creative_id', 'ad_group_id']], on='creative_id', how='left')
    imp_with_cmp = imp_with_ag.merge(df_ag[['ad_group_id', 'campaign_id']], on='ad_group_id', how='left')
    
    imp_spend = imp_with_cmp.groupby('campaign_id')['cost'].sum().reset_index().rename(columns={'cost': 'imp_cost'})
    
    clk_with_cmp = df_click.merge(imp_with_cmp[['impression_id', 'campaign_id']], on='impression_id', how='left')
    clk_spend = clk_with_cmp.groupby('campaign_id')['cost'].sum().reset_index().rename(columns={'cost': 'clk_cost'})

    conv_with_cmp = df_conv.merge(clk_with_cmp[['click_id', 'campaign_id']], on='click_id', how='left')
    conv_rev = conv_with_cmp.groupby('campaign_id')['revenue'].sum().reset_index()

    perf = df_cmp[['campaign_id', 'name', 'objective']].merge(imp_spend, on='campaign_id', how='left')
    perf = perf.merge(clk_spend, on='campaign_id', how='left')
    perf = perf.merge(conv_rev, on='campaign_id', how='left').fillna(0)
    perf['total_spend'] = perf['imp_cost'] + perf['clk_cost']
    perf['roas'] = np.where(perf['total_spend'] > 0, perf['revenue'] / perf['total_spend'], 0)
    perf = perf[perf['total_spend'] > 50].sort_values(by='revenue', ascending=False).head(8)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    fig.patch.set_facecolor('#0F172A')
    ax1.set_facecolor('#0F172A')
    ax2.set_facecolor('#0F172A')

    # Bar chart: Revenue vs Spend
    names = [n[:18] for n in perf['name']]
    y = np.arange(len(names))
    height = 0.35

    ax1.barh(y - height/2, perf['revenue'], height, label='Total Revenue ($)', color='#10B981', alpha=0.9)
    ax1.barh(y + height/2, perf['total_spend'], height, label='Total Spend ($)', color='#EF4444', alpha=0.8)
    ax1.set_yticks(y)
    ax1.set_yticklabels(names, color='#F8FAFC', fontsize=9)
    ax1.invert_yaxis()
    ax1.set_xlabel('Amount (USD $)', color='#94A3B8', fontsize=10)
    ax1.set_title('Top Campaigns: Spend vs. Revenue ($)', color='#F8FAFC', fontsize=12, fontweight='bold', pad=12)
    ax1.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC')
    ax1.tick_params(colors='#94A3B8')
    ax1.grid(color='#1E293B', linestyle='--', alpha=0.7)

    # Bar chart: ROAS
    colors = ['#F59E0B' if r >= 2.0 else '#38BDF8' for r in perf['roas']]
    ax2.barh(y, perf['roas'], 0.5, color=colors, alpha=0.9)
    ax2.axvline(x=2.0, color='#EF4444', linestyle='--', linewidth=1.5, label='Target ROAS (2.0x)')
    ax2.set_yticks(y)
    ax2.set_yticklabels(names, color='#F8FAFC', fontsize=9)
    ax2.invert_yaxis()
    ax2.set_xlabel('ROAS (Revenue / Spend)', color='#94A3B8', fontsize=10)
    ax2.set_title('Campaign Return on Ad Spend (ROAS)', color='#F8FAFC', fontsize=12, fontweight='bold', pad=12)
    ax2.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC')
    ax2.tick_params(colors='#94A3B8')
    ax2.grid(color='#1E293B', linestyle='--', alpha=0.7)

    plt.tight_layout()
    output_path = "charts/campaign_performance.png"
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Generated {output_path}")


if __name__ == "__main__":
    setup_diagram_dirs()
    generate_architecture_diagram()
    generate_medallion_lineage_diagram()
    generate_performance_visual()
