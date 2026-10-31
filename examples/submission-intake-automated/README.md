# Submission intake, fully automated to market

**LLM + decision model:** the LLM reads each submission and builds the fact sheet, the decision model judges each fact against the source, and sheets where every fact holds go straight to carriers. **Status:** routing rules checked offline; model calls not yet run by us (expected, not measured).

## The process change

**Today:** an account manager reads every submission, builds the fact sheet by hand and sends it to market. On a busy week, files wait days.

**With an LLM alone:** the sheet is built in seconds, and the account manager still re-reads the whole submission to see which parts are safe to send. The work moves from typing to checking. The numbers don't move.

**With an LLM and a decision model together:** the LLM builds the sheet. The decision model judges every fact against the source, one narrow question each, in milliseconds. Sheets where every fact holds go to carriers with no one in between. When something doesn't hold, a person sees only that fact, not the whole file.

That's the shift from output to check to output to act on. Intake can run end to end on its own, and the account manager's time goes to the facts that need judgment.

## The flow

1. The LLM reads the [submission](source_submission.txt) and builds a [fact sheet](llm_extracted_facts.json).
2. The decision model gets the source and the facts, each under its own label, and asks one question per fact: does the source support it?
3. Plain rules in [`route.py`](route.py) act on the answers:
   - **Send to market** when every fact clears the bar.
   - **Person confirms facts** otherwise, showing only the facts in doubt.

## The sample

The submission says "Occasionally we do small roof repairs" and "We had a water damage claim at a job site a couple of years ago." The sheet says "Does no roofing work" and "No prior claims."

**What we expect:** three facts clear the bar. The account manager is shown two lines, roofing and prior losses, confirms them in a minute, and the file goes out the same day with the right facts.

## What leaders should measure

- **Straight-through rate:** the share of submissions that reach carriers with no one touching them.
- **Time to market:** from submission received to submission sent.
- **Carrier pushback:** the share of submissions that carriers send back for wrong or missing facts.

## Where it breaks

- The decision model judges whether the source supports a fact, not whether the applicant told the truth.
- Long packets dilute the question. Send the section that matters, not the whole packet.
- The bar is a placeholder. A high bar is deliberate: a wrong fact that reaches a carrier costs more than a minute of someone's time.
