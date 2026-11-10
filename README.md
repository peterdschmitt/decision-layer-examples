<p align="center"><img src=".github/assets/banner.svg" alt="Decision Layer: the tractor and the hydraulics" width="100%"></p>

Most companies bolt an LLM onto a process and get output that someone still has to check. The writing gets faster, the review queue gets longer, and the numbers that matter barely move.

Couple the same LLM with a decision model and the output changes from **something to check** into **something to act on**. That's what makes AI pay off at scale: whole processes that run end to end on their own, with decisions that are faster, cheaper and defensible.

Decision models, such as Jev from TypeSafe and now similar models from OpenAI, Microsoft and others, answer narrow questions you define, with a probability, in milliseconds and for fractions of a cent. An LLM reads, reasons and writes. Neither one gets a process to full automation alone. Together they do.

## The tractor and the hydraulics

A tractor on its own can drive across a field and pull a load. Add hydraulics and it becomes something else: a machine that digs a trench in minutes, lifts loads no crew could move, and does it with a touch of a lever. The tractor didn't get a bigger engine. The hydraulics multiplied what it could do.

An LLM is the tractor: a capable, general machine that can read, draft and reason about almost anything. A decision model is the hydraulics. It takes on the heavy lifting of judgment at a scale an LLM can't reach on its own, call after call, each one in milliseconds and for a fraction of a cent. Together they move workloads that neither could move alone.

## What changes

- **Less slop.** Work leaves the process with the answers that make it actionable, not with a request for review.
- **Legitimate outcomes.** Every action traces to named questions, a probability and a rule you can show a customer, an examiner or your board.
- **Speed to accurate action.** Answers take milliseconds, so work moves the moment it's ready, and only real doubt reaches a person.
- **A fraction of the cost.** Each answer costs fractions of a cent, so the process scales without adding reviewers.

## Five ways to put them to work

**1. Write and send.**<br>
The LLM writes the letter, reply or notice. The decision model answers a few questions about it against the record. When every answer clears its bar, it's sent. *Process: customer correspondence, fully automated.*

**2. Read and route.**<br>
The LLM reads a long document and builds the summary. The decision model judges each fact against the source. When every fact holds, the file moves to its next stage. *Process: intake, fully automated.*

**3. Propose and choose.**<br>
The LLM lays out the possible next steps for a case. The decision model scores each against policy and the situation and chooses. *Process: case handling, fully automated for clear cases.*

**4. Sort and solve.**<br>
The decision model sorts every incoming item in milliseconds. The LLM works the ones that need reasoning, with a pointed question instead of the whole problem. *Process: high-volume queues, end to end.*

**5. Plan and pace.**<br>
An LLM agent plans and works through a multi-step task. At each step the decision model answers whether to go on, pause or hand off. *Process: multi-step work run by agents, with confidence at every step.*

## What changes for leaders

- **You design decisions, not prompts.** Break each judgment into narrow questions anyone can audit.
- **You set the dials.** Each bar decides how much runs on its own. Set it by testing against past cases where you know the outcome, then lower it as the record earns trust.
- **You measure automation, not activity.** Track the share of work that runs straight through, the time to action, and the error rate on what ran on its own.
- **A person makes the calls that change someone's money, coverage or rights.** Everything else can run.

## The worked examples

We work in insurance because it is high-stakes, regulated and full of judgment calls. The patterns carry over to any process.

**The two in tandem**

**[Claim status letters, fully automated](examples/claim-letters-automated/)**<br>
The LLM writes every letter. The decision model answers four questions about it against the claim file. Letters that clear every bar are sent with no one in between.

**[Submission intake, fully automated to market](examples/submission-intake-automated/)**<br>
The LLM builds the fact sheet from each submission. The decision model judges every fact against the source. Sheets where every fact holds go straight to carriers.

**[Candidate shortlist: criteria with levels](examples/candidate-shortlist-criteria/)** ([story](https://decision-layer-indol.vercel.app/blog/jack-and-jill-coupled-llm-decision-model/))<br>
The decision model gives every candidate a first score against the role's criteria; the LLM reads only the shortlist. "Sort and solve" for hiring.

**[AI endpoint inventory](examples/ai-endpoint-inventory/)** ([story](https://decision-layer-indol.vercel.app/blog/harness-ai-api-inventory-decision-model/))<br>
The decision model decides; an LLM explains the positives and handles only the unsure band, where every error sat in testing.

**[Customer profile checks with an unsure zone](examples/profile-check-unsure-zone/)**<br>
The decision model checks every profile; only its unsure zone goes to an LLM. Includes a check that the decision model says it is unsure when it is wrong.

**Building blocks: how to write the decision model's questions**

**[Claims intake triage](examples/claims-fnol-triage/)** ([story](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays))<br>
Small questions, and a low bar for human review where a miss is dangerous. The decision-model side of "sort and solve."

**[A fast track that resists manipulation](examples/claims-glass-fast-track/)** ([story](https://decision-layer-indol.vercel.app/blog/claims-fast-track-text-written-to-fool-it))<br>
Verified facts stay out of the model, and attempts to steer it become a signal. The same defense matters when the text being judged was written by an LLM.

**[Underwriting submission review](examples/underwriting-submission-sorting/)** ([story](https://decision-layer-indol.vercel.app/blog/underwriting-submissions-function-call))<br>
Wording the question is the real design work, and the model raises flags for people rather than giving verdicts.

See [what's next](ROADMAP.md), or [suggest one](../../issues).

## Five questions to ask about any AI step in your process

1. Is the output something to act on, or something someone still has to check?
2. Which judgments stand between that output and action, and could each be a narrow question?
3. Who sets the bar for acting on its own, and on what evidence?
4. What share of the work runs straight through today, and what would it take to double it?
5. Could you explain any single automated action to a regulator in a sentence?

## What we have and haven't tested

The routing rules in every example are checked automatically. We haven't yet run the examples against the models themselves, and we make no speed or cost claims beyond the vendors' published pricing, so results are "expected, not measured" until we publish a test with its data, model version and date. Every bar in the code is a starting point to tune, not advice.

## Other good work

We link to other people's work rather than copy it: the model makers' docs, independent research and other decision models. It's all in [one list](LINKS.md).

## For builders

Python 3.10 or newer, nothing to install.

```bash
python3 run_tests.py                                   # check the routing rules, no key needed
python3 examples/claims-fnol-triage/run.py --dry-run   # see the request without sending it
TYPESAFE_API_KEY=... python3 examples/claims-fnol-triage/run.py
```

Use your own key and never commit it ([how keys are handled](SECURITY.md)). The code is free to use under the [MIT License](LICENSE).

---

<sub>Decision Layer is independent. It isn't affiliated with or endorsed by TypeSafe AI, the maker of Jev, or any other model vendor. Published by Conversely: info@converselyai.com.</sub>
