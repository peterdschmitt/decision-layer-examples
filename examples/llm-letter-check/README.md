# Draft and decide: a claim letter

**In tandem:** the LLM drafts, the decision model scores the draft against the claim file, and those scores direct the LLM's next draft. **Status:** routing rules checked offline; model calls not yet run by us (expected, not measured).

## Why the two work better together

An LLM can write a warm, clear customer letter in seconds. What it doesn't have is a fast, cheap way to judge its own draft against the facts of a specific claim. A decision model does exactly that, in milliseconds and for fractions of a cent, and it answers in scores that can be turned straight into instructions.

So the two loop. The LLM brings the writing. The decision model brings precise direction: remove this promise, correct that fact, ask for the photos, acknowledge the injury. A second draft shaped by four exact directions lands right, and a letter that once needed an adjuster's afternoon goes out the same day. Neither model gets there alone.

## The flow

1. Your system pulls the facts from the claim file, so they come from your records and not from text.
2. The LLM drafts the letter. Use any LLM you like.
3. The decision model answers four questions about the draft against the file:
   - Does it promise payment, coverage or an outcome the file doesn't confirm?
   - Does anything in it contradict the file?
   - Does it ask for every document the file says is needed?
   - Is the tone right for a customer who may be hurt?
4. Plain rules in [`route.py`](route.py) decide the outcome:
   - **Send** when the draft is clean.
   - **Revise** when it isn't. The LLM gets one precise direction per issue, not a vague "try again".
   - **Person reviews** after two failed revisions.

## The sample

The [draft](llm_draft.txt) says "your policy covers this, and we will pay for the full repair." The [claim file](claim_file.json) says coverage is still under review. The draft also leaves out the photos the file needs, and it doesn't mention the customer's sore neck.

**What we expect:** the promise, contradiction and missing-documents questions come back yes, and the tone score comes in low. The LLM gets four exact directions and writes the second draft. The customer gets a correct letter the same day.

## Where it breaks

- The direction is only as good as the questions. If you don't ask about something, the decision model can't steer the LLM on it.
- A draft that is subtly wrong in a way the file can't show, such as the wrong legal language for your state, still needs a person or a plain rule.
- The bars are placeholders. Tune them on past letters where you already know which ones caused problems.
