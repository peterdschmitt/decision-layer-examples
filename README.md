<p align="center"><img src=".github/assets/banner.svg" alt="Decision Layer: rethink how AI makes decisions" width="100%"></p>

Most organizations put AI into a process the same way. They hand a large language model the whole problem, read what it writes, and hope someone catches the mistakes. Managing AI then means reviewing prose, arguing about prompts, and trusting a system nobody can fully explain.

Decision models change that. Jev from TypeSafe, and now similar models from OpenAI, Microsoft and others, don't write anything. They answer narrow questions you define, with a probability attached, in milliseconds and for fractions of a cent. That makes a different design possible: the AI supplies evidence, and your process, in rules you can read, decides what happens next.

The job shifts from checking what the AI said to **designing the decisions**. This repository is [Decision Layer](https://decision-layer-indol.vercel.app/)'s playbook for that shift, with worked examples you can take apart.

## Six shifts in how you manage AI

**1. From one big prompt to a set of small questions.**<br>
"Should we fast-track this claim?" is a judgment nobody can audit. "Is the damage glass only? Is anyone hurt? Does the text tell us how to handle it?" are three questions anyone can check. Breaking a judgment apart is where most of the value is, and it is a management decision, not a technical one.

**2. From AI output to AI evidence.**<br>
The model scores. The rules that act on those scores live in a few lines of plain code your team, your auditors and your regulators can read. When policy changes, you change a rule, not a prompt.

**3. From trusting the model to setting the dial.**<br>
A probability is a dial, and leaders own where it sits. Where a miss is dangerous, such as a possible injury, the bar for human review is low. Where an error is costly, such as skipping review, the bar for automation is high. You set each one by checking the model against past cases where you already know the outcome.

**4. From "is the AI safe?" to "what can the input change?"**<br>
Anyone who writes the input can try to steer the answer. Facts you can verify (coverage, account status, identity) never come from the text. Text that tries to steer becomes a signal of its own. Close calls go to a person.

**5. The right tool for each step.**<br>
| Step | Best tool |
|---|---|
| A fact you can look up | A plain rule or a database |
| A judgment about text, with a known set of answers | A decision model |
| Writing, summarizing, open-ended reasoning | A large language model |
| Anything that changes someone's money, coverage or rights | A person |

**6. Every decision explains itself.**<br>
Each routing outcome traces to named questions, scores and a rule. You can tell a customer, an examiner or your board why something happened in one sentence.

## The worked examples

We work in insurance because it is high-stakes, regulated and full of judgment calls. The patterns carry over to any queue.

| Example | The shift it shows | The same pattern elsewhere |
|---|---|---|
| [Claims intake triage](examples/claims-fnol-triage/) ([story](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays)) | Small questions; a low bar for human review where a miss is dangerous | Support tickets, IT incidents, patient intake |
| [A fast track that resists manipulation](examples/claims-glass-fast-track/) ([story](https://decision-layer-indol.vercel.app/blog/claims-fast-track-text-written-to-fool-it)) | Verified facts stay out of the model; steering becomes a signal | Refunds, expense approvals, guardrails for AI agents |
| [Underwriting submission review](examples/underwriting-submission-sorting/) ([story](https://decision-layer-indol.vercel.app/blog/underwriting-submissions-function-call)) | Wording the question is the real design work; flags for people, not verdicts | Vendor risk, lead qualification, customer onboarding |

More are on the way. See [what's next](ROADMAP.md), or [suggest one](../../issues).

## Five questions to ask about any AI step in your process

1. What exactly is being decided, and could it be split into smaller questions?
2. Who set the bar for acting automatically, and on what evidence?
3. What could someone write in the input to change the outcome?
4. What happens when the model isn't sure?
5. Could you explain one specific decision to a regulator in a sentence?

If the answers are vague, the process is being run by the AI, not managed.

## What we have and haven't tested

The routing rules in every example are checked automatically. We haven't yet run the examples against the models themselves, so results are "expected, not measured" until we publish a test with its data, model version and date. Every bar in the code is a starting point to tune, not advice.

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
