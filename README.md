<p align="center"><img src=".github/assets/banner.svg" alt="Decision Layer: worked examples you can copy" width="100%"></p>

If you work a claims desk or write business at an agency, a lot of your day is sorting. What kind of claim is this? Is anyone hurt? Does this contractor do roofing? A new kind of AI, the decision model, answers questions like these in a fraction of a second, for a fraction of a cent, and tells you how sure it is.

This is where [Decision Layer](https://decision-layer-indol.vercel.app/) keeps the examples behind its posts, so you don't have to start from a blank page. Each one is short, written to be read, and ready to copy.

## Three examples to start

**[Sorting a first notice of loss](examples/claims-fnol-triage/)**<br>
A late-night report says "my neck is a bit sore." Four small questions make sure a person sees it that night, not weeks later when it's a bodily injury claim.
[Read the story](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays)

**[A glass fast track that can't be talked into a yes](examples/claims-glass-fast-track/)**<br>
One line like "your adjuster already approved this" shouldn't be enough to skip review. This one is built so that it isn't.
[Read the story](https://decision-layer-indol.vercel.app/blog/claims-fast-track-text-written-to-fool-it)

**[Reading a contractor's submission](examples/underwriting-submission-sorting/)**<br>
"Occasionally we do small roof repairs" is the line a tired reader skims past. This one flags it, along with the past claim, before the file goes to a carrier.
[Read the story](https://decision-layer-indol.vercel.app/blog/underwriting-submissions-function-call)

More are on the way. See [what's next](ROADMAP.md), or [ask for one](../../issues).

## Before you use any of this

- **The software sorts. People decide.** Nothing here approves, denies, prices or flags fraud. A licensed person makes every call about someone's coverage or payment.
- **We haven't run these against the model yet.** The routing rules are checked, but how well the model answers is still "expected, not measured." We'll publish a real test with its data when we have one.
- **The numbers are starting points.** Every threshold needs checking against your own past files. [This post](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays) shows how.
- **Know your state's rules.** Start with the [NAIC's page on insurers' use of AI](https://content.naic.org/insurance-topics/artificial-intelligence).

## Other good work

We link to other people's work instead of copying it: the model makers' docs, independent research and other decision models. It's all in [one list](LINKS.md).

## For developers

Python 3.10 or newer, nothing to install.

```bash
python3 run_tests.py                                   # check the routing rules, no key needed
python3 examples/claims-fnol-triage/run.py --dry-run   # see the request without sending it
TYPESAFE_API_KEY=... python3 examples/claims-fnol-triage/run.py
```

Use your own key, and never commit it ([how keys are handled](SECURITY.md)). The code is free to use under the [MIT License](LICENSE).

---

<sub>Decision Layer is independent. It isn't affiliated with or endorsed by TypeSafe AI, the maker of Jev, or any other model vendor. Published by Conversely, which provides performance services to insurance agencies: info@converselyai.com.</sub>
