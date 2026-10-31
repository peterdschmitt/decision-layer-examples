"""Offline checks of the routing rules. These use made-up answers, not model output."""

import unittest

from route import route


class RouteTest(unittest.TestCase):
    def test_sample_extraction_splits_the_facts(self):
        answers = {
            "business_type": {"noul": 0.97},
            "employees": {"noul": 0.93},
            "roofing": {"noul": 0.04},       # source says "occasionally we do small roof repairs"
            "prior_losses": {"noul": 0.03},  # source mentions a water damage claim
            "coverage_requested": {"noul": 0.98},
        }
        self.assertEqual(route(answers), {
            "pass_to_underwriter": ["business_type", "employees", "coverage_requested"],
            "send_back_to_llm": ["roofing", "prior_losses"],
            "person_checks": [],
        })

    def test_unclear_fact_goes_to_a_person(self):
        self.assertEqual(route({"x": {"noul": 0.6}})["person_checks"], ["x"])


if __name__ == "__main__":
    unittest.main()
