"""
Schema validation tests for BigQuery DDL files and Soda Core contracts.
Compatible with standard library unittest and pytest.
"""

from pathlib import Path
import unittest


class TestSchemasAndContracts(unittest.TestCase):

    def test_ddl_files_exist(self):
        expected_files = [
            "bigquery/bronze/ddl.sql",
            "bigquery/silver/dim_advertiser.sql",
            "bigquery/silver/dim_campaign.sql",
            "bigquery/silver/fct_ad_impressions.sql",
            "bigquery/silver/fct_ad_clicks.sql",
            "bigquery/silver/fct_ad_conversions.sql",
            "bigquery/gold/obt_ad_impressions.sql",
            "bigquery/gold/ad_campaign_performance.sql",
            "bigquery/gold/ad_funnel_summary.sql",
        ]
        for rel_path in expected_files:
            p = Path(rel_path)
            self.assertTrue(p.exists(), f"Missing required SQL DDL file: {rel_path}")
            content = p.read_text(encoding="utf-8")
            self.assertGreater(len(content.strip()), 0, f"SQL file is empty: {rel_path}")

    def test_soda_contracts_valid(self):
        contract_paths = [
            "gold/contracts/ad_campaign_performance.yaml",
            "gold/contracts/ad_funnel_summary.yaml",
        ]
        for rel_path in contract_paths:
            p = Path(rel_path)
            self.assertTrue(p.exists(), f"Contract file not found: {rel_path}")
            content = p.read_text(encoding="utf-8")
            self.assertIn("dataset:", content)
            self.assertIn("columns:", content)


if __name__ == "__main__":
    unittest.main()
