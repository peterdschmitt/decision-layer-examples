"""Offline demo with made-up readings. Swap `decide` for a real decision model."""
from alerts import final_call, Explainer, compare_with_past, sweep_bar

PAST = [
    {"context": "query time 40x its normal range, replication slot inactive", "past_alert": True},
    {"context": "connections up 8% during the usual Monday peak", "past_alert": False},
    {"context": "archive failures rising, disk 93% full", "past_alert": True},
    {"context": "one slow query during a nightly report", "past_alert": False},
    {"context": "cache hit rate dipped then recovered within a minute", "past_alert": False},
]
P = {0: 0.94, 1: 0.12, 2: 0.88, 3: 0.55, 4: 0.20}   # stand-in percentages for "yes, real"
decide = lambda q, ctx: P[[c["context"] for c in PAST].index(ctx)]

for c in PAST:
    r = final_call(c["context"], decide)
    print(("ALERT " if r["alert"] else "hide  "), f'{r["p_real"]:.2f}', c["context"])

cmp = compare_with_past(PAST, decide)
print(f"agreement {cmp.agreement:.0%}, extra alerts {cmp.extra_alerts}, hidden real {cmp.hidden_real}")
print("bar sweep (bar, agreement, hidden real, extra):", sweep_bar(PAST, decide))

e = Explainer(lambda d: f"Flagged because: {d['context']}")
print(e.why("alert-1", PAST[0]), "| LLM calls:", e.calls)
