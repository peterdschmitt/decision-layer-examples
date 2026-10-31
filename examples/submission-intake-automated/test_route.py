"""Offline checks of the routing rules. These use made-up answers, not model output."""

import unittest

from route import route


class RouteTest(unittest.TestCase):
    def test_fully_supported_sheet_goes_straight_to_market(self):
        answers = {"business_type": {"noul": 0.97}, "employees": {"noul": 0.91}}
        self.assertEqual(route(answers), ("send_to_market", []))

    def test_sample_sheet_needs_only_two_facts_confirmed(self):
        answers = {
            "business_type": {"noul": 0.97},
            "employees": {"noul": 0.93},
            "roofing": {"noul": 0.04},       # source says "occasionally we do small roof repairs"
            "prior_losses": {"noul": 0.03},  # source mentions a water damage claim
            "coverage_requested": {"noul": 0.98},
        }
        self.assertEqual(route(answers), ("person_confirms_facts", ["roofing", "prior_losses"]))


if __name__ == "__main__":
    unittest.main()
