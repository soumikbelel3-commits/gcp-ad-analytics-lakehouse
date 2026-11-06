"""
Unit tests for Ad Analytics KPI metric calculations.
Compatible with standard library unittest and pytest.
"""

import unittest


def calculate_roas(revenue: float, spend: float):
    if spend <= 0:
        return None
    return round(revenue / spend, 4)


def calculate_ctr(clicks: int, impressions: int):
    if impressions <= 0:
        return None
    return round(clicks / impressions, 4)


def calculate_cvr(conversions: int, clicks: int):
    if clicks <= 0:
        return None
    return round(conversions / clicks, 4)


def calculate_cpa(spend: float, conversions: int):
    if conversions <= 0:
        return None
    return round(spend / conversions, 2)


class TestAdMetrics(unittest.TestCase):

    def test_roas_calculation(self):
        # $10,000 revenue on $2,500 spend = 4.0x ROAS
        self.assertEqual(calculate_roas(10000.0, 2500.0), 4.0)
        # $0 spend returns None (safe divide)
        self.assertIsNone(calculate_roas(500.0, 0.0))

    def test_ctr_calculation(self):
        # 250 clicks on 10,000 impressions = 2.5% CTR
        self.assertEqual(calculate_ctr(250, 10000), 0.025)
        self.assertIsNone(calculate_ctr(0, 0))

    def test_cvr_calculation(self):
        # 20 conversions on 250 clicks = 8.0% CVR
        self.assertEqual(calculate_cvr(20, 250), 0.08)
        self.assertIsNone(calculate_cvr(5, 0))

    def test_cpa_calculation(self):
        # $2,500 spend for 50 conversions = $50.00 CPA
        self.assertEqual(calculate_cpa(2500.0, 50), 50.0)
        self.assertIsNone(calculate_cpa(150.0, 0))


if __name__ == "__main__":
    unittest.main()
