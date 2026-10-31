# Check before it goes out

**Pairing:** an LLM writes, a decision model checks, and the LLM revises with precise instructions. **Status:** routing rules checked offline; model calls not yet run by us (expected, not measured).

## Why the pairing matters

An LLM can draft a customer letter in seconds. Left alone, it will also write "good news: your policy covers this" on a claim nobody has approved yet. Having a person read every letter takes away the speed, and having an LLM review the LLM costs a second expensive call that can be wrong in the same way.

A decision model checks the draft against the facts in milliseconds, for fractions of a cent. It also tells the LLM exactly what to fix, so the second draft is right. The LLM supplies the power and the decision model supplies the control.

## The flow

1. Your system pulls the facts from the claim file, so they come from your records and not from text.
2. The LLM drafts the letter. Use any LLM you like.
3. The decision model answers four questions about the draft, comparing it to the file:
   - Does it promise payment, coverage or an outcome the file doesn't confirm?
   - Does anything in it contradict the file?
   - Does it ask for every document the file says is needed?
   - Is the tone right for a customer who may be hurt?
4. Plain rules in [`route.py`](route.py) decide the outcome:
   - **Send** when the draft is clean.
   - **Revise** when it isn't. The LLM gets one precise instruction per problem, not a vague "try again".
   - **Person reviews** after two failed revisions.

## The sample

The [draft](llm_draft.txt) says "your policy covers this, and we will pay for the full repair." The [claim file](claim_file.json) says coverage is still under review. The draft also leaves out the photos the file needs, and it doesn't mention the customer's sore neck.

**What we expect:** the promise and contradiction checks fire, the missing-documents check fires, and the tone score comes in low. The draft goes back to the LLM with four exact fixes. The customer gets a correct letter the same day, and no adjuster had to read the bad one.

## Where it breaks

- The check is only as good as the questions. If you don't ask about a kind of mistake, it won't catch that kind of mistake.
- A draft that is subtly wrong in a way the file can't show, such as the wrong legal language for your state, still needs a person or a plain rule.
- The bars are placeholders. Tune them on past letters where you already know which ones caused problems.
