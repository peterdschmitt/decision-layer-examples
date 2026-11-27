# Alert call, then explain

**Area:** any team that watches systems and drowns in alerts: databases, servers, fraud, security, support queues. **Model:** a decision model for the yes-or-no call on each alert, plus an LLM that writes an explanation only when a person asks. **Status:** checked offline with made-up readings; model calls not yet run by us (expected, not measured).

The pattern follows pgEdge's AI DBA Workbench, whose open-source alerter asks a decision model "Is this a real issue that requires attention?" and calls an LLM for reasons only when someone opens the alert ([pgEdge docs](https://docs.pgedge.com/ai-dba-workbench/development/developer-guide/alerter/anomaly-detection/)). This is our own code, not pgEdge's.

## The steps

1. **Write the final call as one plain question.**
2. **Let the decision model answer it** with a percentage for "yes, this is real".
3. **Hide an alert only when the decision model is clearly sure it is a false alarm** (`hide_bar`, default 0.5).
4. **Make every failure raise the alert.** Decision model fails: the LLM decides. Both fail: the alert goes out.
5. **Pay for the LLM's words once,** when a person first opens the alert.
6. **Before switching, compare with your past calls** and count which way each decision model is wrong: extra alerts are noisier but safe, hidden real ones are the danger. Try several bars on your own data.

## Files

- **`alerts.py`**: `final_call`, `Explainer` (explain once, on request), `compare_with_past` (agreement plus direction of every disagreement) and `sweep_bar`.
- **`test_route.py`**: 10 offline tests. Run `python3 -m unittest test_route`.
- **`run.py`**: a demo on five made-up database readings.

Agreement with past calls is not accuracy: without an answer key you only learn how often the new model matches the old one, and which way it differs.
