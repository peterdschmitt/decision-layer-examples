"""Offline checks of choose-then-write. Made-up scores, not model output."""

import datetime as dt
import json
import os
import unittest

from request import build_body
from route import add_calendar_flags, compare, is_holiday, route, split_cases

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "sample_input.json"), encoding="utf-8"))


def keep_all(kept):
    return [{"ids": [k["id"]], "owner": k["owner"], "name": k["title"]} for k in kept]


def items(*specs):
    return [{"id": i, "date": "2027-02-10", "title": i, "doc_date": "2026-11-01"} for i in specs]


class RouteTest(unittest.TestCase):
    def test_drops_only_when_fairly_sure(self):
        scores = {"a": {"family": 0.45, "drop": 0.55}, "b": {"family": 0.51, "drop": 0.49}}
        out, who = route(items("a", "b"), lambda _: scores, keep_all, None)
        self.assertEqual(who, "decision_model")
        self.assertEqual([m["ids"] for m in out], [["b"]])

    def test_picks_the_most_likely_owner(self):
        scores = {"a": {"eldest_son": 0.2, "eldest_daughter": 0.7, "drop": 0.1}}
        out, _ = route(items("a"), lambda _: scores, keep_all, None)
        self.assertEqual(out[0]["owner"], "eldest_daughter")

    def test_anything_the_writer_drops_goes_back_in(self):
        scores = {"a": {"family": 0.9, "drop": 0.1}, "b": {"family": 0.9, "drop": 0.1}}
        out, _ = route(items("a", "b"), lambda _: scores, lambda kept: keep_all(kept[:1]), None)
        self.assertEqual(sorted(i for m in out for i in m["ids"]), ["a", "b"])

    def test_either_step_failing_runs_the_old_path(self):
        def down(_):
            raise TimeoutError

        self.assertEqual(route(items("a"), down, keep_all, lambda _: ["old"]), (["old"], "old_llm"))
        scores = {"a": {"family": 0.9, "drop": 0.1}}
        self.assertEqual(route(items("a"), lambda _: scores, down, lambda _: ["old"]), (["old"], "old_llm"))

    def test_newest_document_wins(self):
        two = [
            {"id": "new", "date": "2027-02-10", "title": "x", "doc_date": "2026-11-01"},
            {"id": "old", "date": "2027-02-10", "title": "x", "doc_date": "2026-04-05"},
        ]
        scores = {"new": {"family": 0.1, "drop": 0.9}, "old": {"family": 0.8, "drop": 0.2}}
        out, _ = route(two, lambda _: scores, keep_all, None)
        self.assertEqual(out, [])

    def test_calendar_math_is_done_in_code(self):
        self.assertTrue(is_holiday(dt.date(2027, 3, 22)))  # equinox on a Sunday moves to Monday
        self.assertFalse(is_holiday(dt.date(2027, 3, 23)))
        flagged = add_calendar_flags(DATA["items"])
        self.assertNotIn("e3", [i["id"] for i in flagged])
        self.assertEqual(flagged[0]["weekday"], "Wednesday")

    def test_one_request_for_the_batch_with_shared_rules_once(self):
        flagged = add_calendar_flags(DATA["items"])
        body = build_body(DATA["rules"], flagged)
        self.assertEqual(body["input"], DATA["rules"])
        self.assertEqual(len(body["questions"]), len(flagged))
        self.assertIn("drop", body["questions"]["e1"]["criteria"])

    def test_split_cases_and_dry_run_diff(self):
        flagged = add_calendar_flags(DATA["items"])
        self.assertEqual([c[0] for c in split_cases(flagged, DATA["scores"])], ["e8", "e9"])
        diff = compare([{"name": "Pool day", "owner": "family"}], [{"name": "Pool day", "owner": "eldest_daughter"}])
        self.assertEqual(diff, {"added": [], "removed": [], "moved": ["Pool day"]})


if __name__ == "__main__":
    unittest.main()
