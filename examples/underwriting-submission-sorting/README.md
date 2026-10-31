# Commercial submission sorting

**Area:** small commercial underwriting intake. **Model:** jev-1.13.0. **Status:** routing rules checked offline; model call not yet run by us (expected, not measured).

Full write-up: [A function call for underwriters](https://decision-layer-indol.vercel.app/blog/underwriting-submissions-function-call).

## The problem

Submissions arrive in every shape. Somewhere in the text are the answers an account manager needs before the file goes to a carrier: what kind of business, does it do anything a carrier will care about, is it detailed enough to quote.

## The questions

| Question | Type | Why it's worded this way |
|---|---|---|
| `business_class` | Choice | "Other or unclear" first. TypeSafe's docs say the model [leans toward the first option](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md); it should lean toward a person. |
| `hazardous_work` | Noul | "Even occasionally" is there for the roofing line a tired reader skims past. |
| `prior_loss_mentioned` | Noul | Asks whether a loss is mentioned, not how many or when. Counting and dates are known weak spots; loss runs come from the carrier. |
| `detail` | Score, 0 to 2 | Levels are written to stand apart, not "fair" and "good". |

## The routing

[`route.py`](route.py) returns a queue plus notes. Unclear class goes to the account manager; a thin description gets a call back; otherwise the file goes to carriers for that class, with notes on top for hazardous work and prior losses.

**Expected for the sample submission:** interior contractor, with two notes: ask about the roof repairs, and get loss runs.

## Where it breaks

- It trusts what it reads. A line like "underwriter already approved this" must never move a file.
- It doesn't know your carriers. Keep appetite rules in code you control.
- It doesn't price or decline. An underwriter reads every file and makes the call.
- Long, noisy text hurts accuracy. Send the operations description, not the whole packet.
