"""Offline demo with made-up music-assistant requests and stand-in models."""
from relabel import triage, RulingLog

EXAMPLES = [
    {"id": "1", "state": "play road rock", "question": "intent", "label": "song"},
    {"id": "2", "state": "play the song Road Rock", "question": "intent", "label": "song"},
    {"id": "3", "state": "something for a long drive", "question": "intent", "label": "playlist"},
    {"id": "4", "state": "rock", "question": "intent", "label": "playlist"},
]


def decide(state, q):
    if "the song" in state:
        return {"song": 0.96, "playlist": 0.04}
    if "road rock" in state:
        return {"playlist": 0.93, "song": 0.07}
    if state == "rock":
        return {"playlist": 0.5, "song": 0.5}
    return {"playlist": 0.88, "song": 0.12}


def llm_label(state, q):
    return "song" if "the song" in state else "playlist"


if __name__ == "__main__":
    keep, people = triage(EXAMPLES, decide, llm_label)
    for e in keep:
        print("keep", e["id"], e["label"], "(relabelled)" if e.get("relabelled") else "")
    log = RulingLog()
    for e, why, a, b in people:
        print("to people", e["id"], why, a, b)
        log.settle(e, "playlist", "a bare genre word means a playlist")
    print("rules to reword:", log.rules_needing_wording(min_count=1))
