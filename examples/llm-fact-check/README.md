# Read and weigh: an underwriting fact sheet

**In tandem:** the LLM reads a long submission and lays out the facts, the decision model weighs each fact against the source, and facts the source doesn't support go back to the LLM for another read. **Status:** routing rules checked offline; model calls not yet run by us (expected, not measured).

## Why the two work better together

An LLM turns a rambling submission into a clean, structured summary in seconds. A decision model can weigh any single statement against a source in milliseconds, but it can't write the summary. Put them together and you get both: the LLM's reading at the speed of a decision model's judgment.

Each fact gets one narrow question: does the source support this? Facts that clearly hold up go straight to the underwriter. Facts that don't go back to the LLM with the source in front of it. The underwriter starts with a sheet that's ready to act on, instead of re-reading the whole file to find out which parts are safe to trust.

## The flow

1. The LLM reads the [submission](source_submission.txt) and extracts [structured facts](llm_extracted_facts.json).
2. The decision model gets the source and the facts, each under its own label, and asks one question per fact.
3. Plain rules in [`route.py`](route.py) decide where each fact goes:
   - **Pass to the underwriter** if it is clearly supported.
   - **Send back to the LLM** if it is clearly unsupported, so it re-extracts that fact with the source in front of it.
   - **A person checks** if it is genuinely unclear.

## The sample

The submission says "Occasionally we do small roof repairs" and "We had a water damage claim at a job site a couple of years ago." The LLM's extraction says "Does no roofing work" and "No prior claims." Both mistakes are easy for a tired reader to miss, and both matter a great deal to a carrier.

**What we expect:** three facts go straight through, and the roofing and prior-loss facts go back to the LLM for another read. The underwriter's sheet shows the roof repairs and the past claim.

## Where it breaks

- It weighs support, not truth. If the applicant left something out, the source can't tell you.
- Long documents dilute the question. Send the relevant section, not the whole packet.
- The bars are placeholders. A high bar to pass is deliberate, because an unsupported fact that slips through costs more than a fact that gets re-checked.
