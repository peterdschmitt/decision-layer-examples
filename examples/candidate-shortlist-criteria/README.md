# Candidate shortlist: criteria with levels

**Area:** hiring, first-stage screening. **Model:** jev-1.14.0. **Status:** scoring and shortlist rules checked offline; model call not yet run by us (expected, not measured).

Full write-up: [How a recruiting company cut screening costs 88% using a decision model, without losing accuracy](https://decision-layer-indol.vercel.app/blog/jack-and-jill-coupled-llm-decision-model/).

## The process, fully automated

Thousands of candidates per open role each need a first score before anyone builds a shortlist. An LLM can do it, but it is paid to write an answer thousands of times a day. Here the decision model gives the first score to every candidate, and the LLM reads only the shortlist closely.

## The questions

One **Score** question per criterion in the role's hiring brief, all sent in one request. Each criterion has levels written in words, from lowest to highest, so the model places the candidate on a scale (it can land between two levels) instead of answering yes or no.

| Criterion (example brief) | Weight | Levels |
|---|---|---|
| Has built and led a B2B sales team | 0.4 | Never managed sellers · Ran a small team · Grew a team past 20 sellers |
| Has sold to finance buyers | 0.3 | No finance buyers · Some finance deals · Finance teams were the main buyer |
| Has worked at an early-stage company | 0.3 | Only large companies · Some startup time · Built sales from scratch at a startup |

The brief is made up. In practice the hiring team agrees the criteria per role.

## The rules

[`route.py`](route.py): each score is scaled to 0..1, weighted and summed into one first score; candidates are ranked and the top N go on to the LLM for the close review. A missing answer counts as the lowest level, and out-of-range scores are clamped.

**Expected for the sample candidate:** a VP Sales who grew a team to 22 at an accounting-software startup and sold to CFOs should land near the top on all three criteria.

## Set the dials from your own history

Build a test set from past roles: every candidate a hiring manager asked to meet, plus a fair sample of the rest. Run your current method and this one side by side and count how many of those "winners" each keeps on the shortlist. Tune the weights and the shortlist size on that, not on intuition.

## Where it breaks

- The model reads the text you send. Thin or padded profiles score accordingly.
- Criteria must be about the job. Keep protected characteristics, and anything that stands in for them, out of the state and the questions.
- This is a first sort, not a hiring decision. People decide who to meet and who to hire.
- Jack & Jill hasn't published its actual questions or weights. This is our sketch of the pattern in TypeSafe's composite-scoring guide.
