# Keep only what the source supports

**Pairing:** an LLM extracts facts, a decision model checks each fact against the source, and only supported facts move forward. **Status:** routing rules checked offline; model calls not yet run by us (expected, not measured).

## Why the pairing matters

LLMs are excellent at turning a messy document into a clean summary. They're also known to fill gaps with things that sound right. In underwriting, "no prior claims" is a dangerous thing to make up.

Re-reading every summary against the source throws away the time the LLM saved. Asking a second LLM to check costs as much again and can make the same mistake. A decision model asks one narrow yes-or-no question per fact: does the source support this? It answers in milliseconds, and the underwriter only sees facts that passed.

## The flow

1. The LLM reads the [submission](source_submission.txt) and extracts [structured facts](llm_extracted_facts.json).
2. The decision model gets the source and the facts, each under its own label, and asks one question per fact.
3. Plain rules in [`route.py`](route.py) decide where each fact goes:
   - **Pass to the underwriter** if it is clearly supported.
   - **Send back to the LLM** if it is clearly unsupported, so it re-extracts that fact with the source in front of it.
   - **A person checks** if it is genuinely unclear.

## The sample

The submission says "Occasionally we do small roof repairs" and "We had a water damage claim at a job site a couple of years ago." The LLM's extraction says "Does no roofing work" and "No prior claims." Both mistakes are easy for a tired reader to miss, and both matter a great deal to a carrier.

**What we expect:** three facts pass, and the roofing and prior-loss facts are sent back. The underwriter never sees the two made-up facts.

## Where it breaks

- It checks support, not truth. If the applicant left something out, the source can't tell you.
- Long documents dilute the question. Send the relevant section, not the whole packet.
- The bars are placeholders. A high bar to pass is deliberate, because an unsupported fact that slips through costs more than a fact that gets re-checked.
