# First notice of loss triage

**Area:** claims intake. **Model:** jev-1.13.0. **Status:** routing rules checked offline; model call not yet run by us (expected, not measured).

Full write-up: [Labels, not essays](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays).

## The problem

A fresh first notice of loss needs a few small answers before it goes in a queue: what kind of loss, is anyone hurt, do we know where it happened, is it simple or messy. None of that needs a written answer. It needs a label and a sense of how sure you are.

## The questions

| Question | Type | Why it's worded this way |
|---|---|---|
| `loss_type` | Choice | "Other or unclear" is listed first, so a report the model can't place leans toward a person. |
| `injury_mentioned` | Noul (yes/no) | Broad on purpose. "A bit sore" can turn a bumper claim into a bodily injury claim weeks later. |
| `location_given` | Noul | If there's no location, ask the customer before assigning. |
| `complexity` | Score, 0 to 2 | Each level is written so it can't be confused with its neighbors. |

We don't ask about the date. Your form already captures it, and checking it against the policy period is a job for code.

## The routing

[`route.py`](route.py), in order: any hint of injury goes to injury review; an unsure or unplaceable loss type goes to manual triage; no location means ask the customer; a simple, confident glass claim goes to the glass fast track (a person still approves payment); everything else goes to its standard queue.

**Expected for the sample report:** "my neck is a bit sore" trips the injury rule, so the claim lands in front of a person the night it comes in.

## Where it breaks

- The model reads text only. Photos attached to the report aren't seen.
- The thresholds are placeholders. Check the model against a few hundred past reports where you know the answer, group its answers by probability, and count how often each group was right.
- No approvals, denials, payment amounts or fraud scores. The model picks a queue; a licensed person decides.
