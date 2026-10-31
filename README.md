# Decision Layer worked examples

> **Unofficial.** This repository is made by [Decision Layer](https://decision-layer-indol.vercel.app/), an independent blog and podcast. It is not affiliated with, endorsed by or sponsored by TypeSafe AI or any other model vendor. "Jev" and other product names belong to their owners.

Copyable, worked examples of **decision models** (Jev and similar "System One" models) doing real operations work. We start with the lane we know best: **insurance claims and underwriting**.

Each example is a small folder with:

| File | What it is |
|---|---|
| `README.md` | The problem, the questions we ask, why they are worded that way, and where it breaks |
| `sample_input.txt` | A made-up input (never real customer data) |
| `request.py` | Builds the request body: the state and the questions |
| `route.py` | Turns the model's answers into a queue, in plain code you can read |
| `test_route.py` | Offline checks of the routing rules, using made-up answers |
| `run.py` | Sends the request to the API (needs your own key) and prints the queue |

## The examples

| Example | Area | Write-up |
|---|---|---|
| [First notice of loss triage](examples/claims-fnol-triage/) | Claims | [Labels, not essays](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays) |
| [Glass fast track that resists planted text](examples/claims-glass-fast-track/) | Claims | [Text written to fool it](https://decision-layer-indol.vercel.app/blog/claims-fast-track-text-written-to-fool-it) |
| [Commercial submission sorting](examples/underwriting-submission-sorting/) | Underwriting | [A function call for underwriters](https://decision-layer-indol.vercel.app/blog/underwriting-submissions-function-call) |

More are listed in [ROADMAP.md](ROADMAP.md). For other people's work, see [LINKS.md](LINKS.md). We link to it rather than copy it.

## What has and hasn't been tested

Be clear-eyed about this:

- **The routing code is tested offline.** `test_route.py` feeds made-up answers into `route.py` and checks the queue. That proves the rules do what they say. It says nothing about how well the model answers.
- **The model calls have not been run by us yet.** The request format follows TypeSafe's [API reference](https://docs.typesafe.ai/api.md). Each example's README says "expected, not measured" until we publish a real run with its data, code, model version and date.
- **Every threshold is a placeholder.** Set yours by checking the model against past files where you already know the answer. The [claims intake write-up](https://decision-layer-indol.vercel.app/blog/claims-intake-labels-not-essays) shows how.

## Ground rules for insurance use

- The model **sorts and flags**. A licensed person makes every decision that changes someone's coverage, price or payment.
- No approvals, denials, prices or fraud scores come from these examples.
- No protected traits as inputs, and nothing that stands in for them.
- Check your state's rules. The NAIC adopted a [model bulletin on insurers' use of AI](https://content.naic.org/insurance-topics/artificial-intelligence) in December 2023, and states decide how to apply it.

## Run it

Python 3.10 or newer. No packages to install.

```bash
# Offline: check the routing rules (no key needed)
python3 run_tests.py

# Show the request an example would send, without sending it
python3 examples/claims-fnol-triage/run.py --dry-run

# Send it for real with your own key
export TYPESAFE_API_KEY=...   # your key; never commit it
python3 examples/claims-fnol-triage/run.py
```

The key is read only from the `TYPESAFE_API_KEY` environment variable. Nothing in this repo prints, logs or stores it. See [SECURITY.md](SECURITY.md).

## Using these examples

Code is under the [MIT License](LICENSE). Take it, change it, ship it. A link back to Decision Layer is appreciated, not required. Found a mistake? Open an issue.

Published by Conversely, which provides performance services to insurance agencies. Contact: info@converselyai.com.
