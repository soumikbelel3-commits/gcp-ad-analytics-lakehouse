"""
Unit tests for data enrichment and transformation helpers.
Compatible with standard library unittest and pytest.
"""

import unittest


class TestDataTransformations(unittest.TestCase):

    def test_cents_conversion(self):
        costs = [0.0125, 1.45, 10.99]
        cents = [int(round(c * 100)) for c in costs]
        self.assertEqual(cents, [1, 145, 1099])

    def test_active_status_flag(self):
        statuses = ["active", "paused", "archived", "active"]
        flags = [s == "active" for s in statuses]
        self.assertEqual(flags, [True, False, False, True])

    def test_ad_event_attribution(self):
        attributions = ["last_click", "first_click", "linear"]
        valid_set = {"last_click", "first_click", "linear", "position_based"}
        for attr in attributions:
            self.assertIn(attr, valid_set)


if __name__ == "__main__":
    unittest.main()
