import unittest
from relabel import triage, RulingLog, both_right, shuffle_flip_rate, top


def ex(i, label, state="s"):
    return {"id": str(i), "state": state, "question": "intent", "label": label}


class TestRelabel(unittest.TestCase):
    def test_top(self):
        self.assertEqual(top({"a": 0.2, "b": 0.8}), ("b", 0.8))

    def test_agreeing_models_correct_a_wrong_label(self):
        keep, people = triage([ex(1, "song")], lambda s, q: {"playlist": 0.95, "song": 0.05},
                              lambda s, q: "playlist")
        self.assertEqual(keep[0]["label"], "playlist")
        self.assertTrue(keep[0]["relabelled"])
        self.assertEqual(people, [])

    def test_disagreement_goes_to_people(self):
        keep, people = triage([ex(2, "song")], lambda s, q: {"playlist": 0.95, "song": 0.05},
                              lambda s, q: "song")
        self.assertEqual(keep, [])
        self.assertEqual(people[0][1], "the two models disagree")

    def test_unsure_goes_to_people(self):
        _, people = triage([ex(3, "song")], lambda s, q: {"playlist": 0.35, "song": 0.33, "other": 0.32},
                           lambda s, q: "playlist")
        self.assertEqual(people[0][1], "decision model unsure")

    def test_agreeing_but_not_sure_enough_keeps_old_label(self):
        keep, _ = triage([ex(4, "song")], lambda s, q: {"playlist": 0.7, "song": 0.3},
                         lambda s, q: "playlist")
        self.assertEqual(keep[0]["label"], "song")
        self.assertNotIn("relabelled", keep[0])

    def test_matching_label_passes(self):
        keep, _ = triage([ex(5, "song")], lambda s, q: {"song": 0.9, "playlist": 0.1}, lambda s, q: "song")
        self.assertEqual(keep[0]["label"], "song")

    def test_ruling_log(self):
        log = RulingLog()
        e = log.settle(ex(6, "song"), "playlist", "genre words mean a playlist")
        log.settle(ex(7, "song"), "playlist", "genre words mean a playlist")
        log.settle(ex(8, "song"), "song", "quoted titles mean a song")
        self.assertTrue(e["settled_by_person"])
        self.assertEqual(log.rules_needing_wording(), ["genre words mean a playlist"])

    def test_both_right(self):
        recs = [{"state": "a", "labels": {"route": "music", "intent": "play"}},
                {"state": "b", "labels": {"route": "music", "intent": "search"}}]
        pred = lambda s: {"route": "music", "intent": "play"}
        self.assertEqual(both_right(recs, pred), 0.5)

    def test_shuffle_flip_rate_stable_model(self):
        recs = [{"state": "x", "options": {"intent": ["play", "search", "other"]}}] * 5
        stable = lambda s, q, opts: {o: (0.9 if o == "play" else 0.05) for o in opts}
        self.assertEqual(shuffle_flip_rate(recs, stable), 0.0)

    def test_shuffle_flip_rate_order_biased_model(self):
        recs = [{"state": "x", "options": {"intent": ["play", "search", "other", "stop"]}}] * 20
        first_wins = lambda s, q, opts: {o: (0.6 if i == 0 else 0.4 / 3) for i, o in enumerate(opts)}
        self.assertGreater(shuffle_flip_rate(recs, first_wins), 0.3)


if __name__ == "__main__":
    unittest.main()
