<p align="center"><img src=".github/assets/banner.svg" alt="Decision Layer: the tractor and the hydraulics" width="100%"></p>

Language models can read, reason and write about almost anything. Decision models, such as Jev from TypeSafe and now similar models from OpenAI, Microsoft and others, do something different. They answer narrow questions you define with a probability, in milliseconds and for fractions of a cent.

Each one alone is useful. Working together, they change what a process can do.

## The tractor and the hydraulics

A tractor on its own can drive across a field and pull a load. Add hydraulics and it becomes something else: a machine that digs a trench in minutes, lifts loads no crew could move, and does it with a touch of a lever. The tractor didn't get a bigger engine. The hydraulics multiplied what it could do.

An LLM is the tractor: a capable, general machine that can read, draft and reason about almost anything. A decision model is the hydraulics. It takes on the heavy lifting of judgment at a scale an LLM can't touch on its own, call after call, each one in milliseconds and for a fraction of a cent. Together they move workloads that neither could move alone.

**In tandem, each makes the other more useful.** The LLM gives the decision model rich material to judge: drafts, options, facts pulled from long documents, plans. The decision model gives the LLM fast, precise direction: which option, which facts, what to fix, when to go and when to hand off. The loop between them turns AI work into action. The results:

- **Less slop.** The LLM's work is shaped by sharp, fast judgments as it goes, not reviewed afterwards.
- **More legitimate outcomes.** Each action traces to named questions, a score and a rule you can show a customer, an examiner or your board.
- **Faster to the right action.** Judgments take milliseconds, so good work moves at once and only real doubt waits for a person.
- **A fraction of the cost.** Most judgments cost fractions of a cent, so the LLM's power goes where it matters.

This repository is [Decision Layer](https://decision-layer-indol.vercel.app/)'s playbook for that pairing, with worked examples you can take apart.

## Five ways they work in tandem

**1. Draft and decide.**<br>
The LLM drafts the claim letter, customer reply or recommendation. The decision model scores it against the file in milliseconds: promises, facts, missing requests, tone. Those scores become exact directions for the LLM's next draft, and the right letter goes out the same day.

**2. Read and weigh.**<br>
The LLM reads a long document and lays out the facts. The decision model weighs each fact against the source. Together they hand an underwriter a fact sheet that's ready to act on.

**3. Propose and choose.**<br>
The LLM proposes several possible next steps. The decision model scores each against policy and the situation and chooses. The LLM brings the range of options, and the decision model makes the call fast.

**4. Sort and solve.**<br>
The decision model sorts every case in milliseconds. The LLM takes the hard ones, with a pointed question instead of the whole problem. Volume moves at decision-model speed, and the LLM's reasoning goes where it counts.

**5. Plan and pace.**<br>
An LLM agent plans and works through a multi-step task. At each step the decision model sets the pace: go on, pause, or hand off to a person. The agent moves quickly because each step gets a fast judgment.

## What changes for leaders

- **You design decisions, not prompts.** Break a judgment into questions anyone can audit.
- **You own the dial.** Each probability has a bar for acting on its own, set by checking against past cases where you know the outcome. Low where a miss is dangerous, high where an error is costly.
- **You decide what input can change.** Facts you can verify never come from text someone else wrote.
- **A person makes the call that changes someone's money, coverage or rights.** The pairing gets the right cases to them faster, with the evidence attached.

## The worked examples

We work in insurance because it is high-stakes, regulated and full of judgment calls. The patterns carry over to any process.

**The two in tandem**

**[Draft and decide: a claim letter](examples/llm-letter-check/)**<br>
The LLM drafts a claim letter. The decision model scores it against the claim file, and its scores give the LLM four exact directions for the next draft. The customer gets a correct letter the same day.

**[Read and weigh: an underwriting fact sheet](examples/llm-fact-check/)**<br>
The LLM reads a contractor's submission and lays out the facts. The decision model weighs each one against the source, and the two facts the source doesn't support go back to the LLM for another read. The underwriter gets a sheet that's ready to act on.

**Building blocks: how to write the decision model's questions**

**[Claims intake triage](examples/claims-fnol-triage/)** ([story](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays))<br>
Small questions, and a low bar for human review where a miss is dangerous. The decision-model side of "sort and solve."

**[A fast track that resists manipulation](examples/claims-glass-fast-track/)** ([story](https://decision-layer-indol.vercel.app/blog/claims-fast-track-text-written-to-fool-it))<br>
Verified facts stay out of the model, and attempts to steer it become a signal. The same defense matters when the text being judged was written by an LLM.

**[Underwriting submission review](examples/underwriting-submission-sorting/)** ([story](https://decision-layer-indol.vercel.app/blog/underwriting-submissions-function-call))<br>
Wording the question is the real design work, and the model raises flags for people rather than giving verdicts.

See [what's next](ROADMAP.md), or [suggest one](../../issues).

## Five questions to ask about any AI step in your process

1. Where could a fast, cheap judgment multiply what your LLM already does?
2. Could that judgment be split into small questions anyone can audit?
3. Who set the bar for acting automatically, and on what evidence?
4. What happens when the AI isn't sure?
5. Could you explain one specific action to a regulator in a sentence?

If the answers are vague, the AI is running the process instead of you.

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
