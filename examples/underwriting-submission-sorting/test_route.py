"""Offline checks of the routing rules. These use made-up answers, not model output."""

import unittest

from route import route


def answers(choice="contractor_interior", confidence=0.85, hazard=0.05, loss=0.05, detail=1.6):
    return {
        "business_class": {"choice": choice, "confidence": confidence},
        "hazardous_work": {"noul": hazard},
        "prior_loss_mentioned": {"noul": loss},
        "detail": {"score": detail},
    }


class RouteTest(unittest.TestCase):
    def test_remodeler_with_roofing_and_a_past_claim_gets_both_notes(self):
        queue, flags = route(answers(hazard=0.8, loss=0.9))
        self.assertEqual(queue, "market_to_contractor_interior_carriers")
        self.assertEqual(flags, ["hazardous operations mentioned", "prior loss mentioned: request loss runs"])

    def test_unclear_class_goes_to_a_person(self):
        self.assertEqual(route(answers(choice="other_or_unclear"))[0], "account_manager_review")
        self.assertEqual(route(answers(confidence=0.4))[0], "account_manager_review")
        self.assertEqual(route(answers(confidence=None))[0], "account_manager_review")

    def test_thin_submission_gets_a_call_back(self):
        self.assertEqual(route(answers(detail=0.6))[0], "call_back_for_details")

    def test_clean_submission_has_no_notes(self):
        self.assertEqual(route(answers())[1], [])


if __name__ == "__main__":
    unittest.main()
