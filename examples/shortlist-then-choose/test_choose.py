import unittest

from choose import NONE, accuracy, choose, error_cut, recall_at_k, share_by_source, shortlist


def fixed(answers):
    return lambda item, options: answers


def down(*_):
    raise RuntimeError("down")


class ChooseTests(unittest.TestCase):
    def test_shortlist_keeps_closest(self):
        cats = {"a": [1, 0], "b": [0, 1], "c": [0.9, 0.1]}
        self.assertEqual(shortlist([1, 0], cats, k=2), ["a", "c"])

    def test_confident_pick_is_taken(self):
        r = choose("x", ["a", "b"], fixed({"a": 0.9, "b": 0.08, NONE: 0.02}), lambda i, o: "b")
        self.assertEqual(r[:2], ("a", "decision_model"))

    def test_unsure_goes_to_llm(self):
        r = choose("x", ["a", "b"], fixed({"a": 0.5, "b": 0.45, NONE: 0.05}), lambda i, o: "b")
        self.assertEqual(r[:2], ("b", "llm"))

    def test_none_of_these_goes_to_llm(self):
        r = choose("x", ["a", "b"], fixed({"a": 0.05, "b": 0.05, NONE: 0.9}), lambda i, o: "a")
        self.assertEqual(r[:2], ("a", "llm"))

    def test_model_down_goes_to_llm(self):
        self.assertEqual(choose("x", ["a"], down, lambda i, o: "a")[:2], ("a", "llm"))

    def test_recall(self):
        self.assertEqual(recall_at_k(["p", "q"], {"p": "a", "q": "z"}, {"p": ["a", "b"], "q": ["a", "b"]}), 0.5)

    def test_error_cut_matches_channel3_arithmetic(self):
        self.assertAlmostEqual(error_cut(0.819, 0.972), 0.845, places=3)

    def test_accuracy_and_share(self):
        res = {"p": ("a", "decision_model", 0.9), "q": ("b", "llm", None)}
        self.assertEqual(accuracy(res, {"p": "a", "q": "c"}), 0.5)
        self.assertEqual(share_by_source(res), {"decision_model": 0.5, "llm": 0.5})


if __name__ == "__main__":
    unittest.main()
