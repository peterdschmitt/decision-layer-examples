# Claim status letters, fully automated

**LLM + decision model:** the LLM writes every letter, the decision model answers four questions about it against the claim file, and letters that clear every bar are sent with no one in between. **Status:** routing rules checked offline; model calls not yet run by us (expected, not measured).

## The process change

**Today:** an adjuster writes or reviews every status letter. Letters wait for someone's afternoon, customers call to ask what's happening, and the adjuster's time goes to correspondence instead of claims.

**With an LLM alone:** letters get written in seconds, and someone still reads every one before it goes out, because nobody can tell which drafts are safe. The work moves from writing to checking. The numbers don't move.

**With an LLM and a decision model together:** the LLM writes the letter. The decision model answers four narrow questions about it against the claim file, in milliseconds and for fractions of a cent. When every answer clears its bar, the letter goes out on its own. The output stops being something to check and becomes something to act on.

The goal is full automation with confidence. You choose the bars, so you choose how much runs on its own and how much reaches a person. Every letter that goes out carries a record of why: four questions, four answers and the rule that sent it.

## The flow

1. Your system pulls the facts from the claim file, so they come from your records.
2. The LLM writes the letter. Use whichever LLM you like.
3. The decision model answers four questions about the letter against the file:
   - Does it promise payment, coverage or an outcome the file doesn't confirm?
   - Does anything in it contradict the file?
   - Does it ask for every document the file says is needed?
   - Is the tone right for a customer who may be hurt?
4. Plain rules in [`route.py`](route.py) act on the answers:
   - **Send automatically** when every answer clears its bar.
   - **Adjuster sends** otherwise, with the specific reasons on top.

## The sample

The [letter](llm_draft.txt) says "your policy covers this, and we will pay for the full repair." The [claim file](claim_file.json) says coverage is still under review.

**What we expect:** this one goes to the adjuster, marked "promises coverage the file doesn't confirm," "doesn't ask for the photos" and "tone." A letter that matches the file goes out on its own the moment it's written.

## What leaders should measure

- **Automation rate:** the share of letters sent with no one touching them.
- **Time to letter:** from claim event to letter in the customer's hands.
- **Error rate on automated letters:** sampled after the fact. This is how you earn the right to lower the bars.

## Where it breaks

- The decision model answers only the questions you ask. A kind of error you don't ask about won't stop a letter.
- Some requirements can't be read from the file, such as the exact legal wording your state requires. Keep those in templates or plain rules.
- The bars are placeholders. Set them on past letters where you already know which ones caused problems.
