# Did the task succeed? A bar on the safe answer, and a backup with its own bar

**Area:** any product where AI agents run tasks for users (work platforms, back-office automation, support). **Model:** jev-1.13.0, the version Kiva wrote about. **Status:** decision rules checked offline with made-up probabilities; model call not yet run by us (expected, not measured).

Full write-up: [How a software company cut AI decision costs about 90% with a decision model](https://decision-layer-indol.vercel.app/blog/kiva-ai-decisions-decision-model/).

## The process, fully automated

An AI agent finishes a scheduled task. Before, an LLM read the agent's last message, said whether the task worked, and gave its own guess at how sure it was. Kiva found those guesses meant little: about 95% on right moves, 70% on wrong ones. Here a decision model answers one question with a probability for each answer, and code decides what the user is told.

## The question

| Question | Type | Why |
|---|---|---|
| `outcome` | Choice: succeeded, failed, needs_human | One sentence in `needs_human` ("finishing the work and then handing results to a person does not count as this") is what took Kiva's test from three wrong to none. |

## The rules

[`decide.py`](decide.py):

- **Bar on the safe answer.** The user hears "done" only when P(succeeded) clears the bar. The top answer's confidence can drop when the other answers split the rest; Kiva saw this with its document checks, where the worst attacks looked unsure.
- **Each decider keeps its own bar.** If the decision model is down, the backup is the old LLM prompt, with a higher bar, because an LLM's self-reported scores run high.
- **No probabilities, no notice.** A general LLM that returns no probabilities would fail every bar; the code holds the notice instead of sending a guess.
- **Compare before you switch.** `compare()` runs the old and new deciders on the same cases and lists what each got wrong.

## Try it

    python3 -m unittest -q test_decide   # offline, made-up probabilities
    python3 run.py --dry-run             # print the request for the sample message

## Where it breaks

- Kiva set its bars on small test sets it wrote itself, and says it still has to check them on real data. Do the same.
- A decision model judges each option on its own. For "pick the single best of many similar options", rewrite the option descriptions before you move the bar, and check case by case: an added "does not cover" line can push away cases that belong.
- Pin the version you tested and re-test before moving.
