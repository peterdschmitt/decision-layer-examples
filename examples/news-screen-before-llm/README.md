# Screen what the LLM reads, and check that screening pays

**Area:** any team whose LLM reads a pile of documents before it writes: news briefings, research digests, search results, inbox summaries. **Model:** jev-1.13.0 in the request (Currents used TypeSafe's Jev through typesafe-sdk 0.6.0; any decision model that takes a yes/no question works). **Status:** screening and cost rules checked offline with made-up articles, probabilities and prices; model call not yet run by us (expected, not measured).

Full write-up: How a news search company cut what its LLM reads 16% with a decision model (draft, Decision Layer, Nov. 12, 2026).

## The process

The decision model reads each article's headline and summary and answers one question: is this real reporting about the topic? Articles at or above the bar go to the LLM, which writes the briefing. The rest are dropped before the LLM reads them. If the decision model is down, the article is kept, as before.

Currents News API ran this on 2,000 live articles. At a 0.70 bar the LLMs read 16-18% less text, and blind AI judges found five of six quality comparisons too close to call. By Currents' own price math, screening paid in front of Claude Sonnet 4.6 but would lose money in front of a cheap LLM such as GPT-5 Mini.

## The rules

[`screen.py`](screen.py):

- **`screen`** / **`screen_then_brief`**: drop what falls below the bar; the LLM writes from the rest.
- **`net_saving`** / **`screening_pays`**: what the LLM no longer reads, at its price, minus what the screening costs.
- **`break_even_llm_price`**: the lowest LLM price at which screening stops losing money.
- **`bar_report`**: the share dropped at each bar. Check quality at the bar you choose.

## Try it

    python3 -m unittest -q test_screen   # offline, made-up numbers
    python3 run.py                       # offline run: the expensive LLM saves, the cheap one loses
    python3 run.py --dry-run             # print the request for the first article
    python3 run.py --live                # ask the decision model; needs TYPESAFE_API_KEY

## Where it breaks

- Precise searches return mostly on-topic articles, so there may be little to drop. Count the noise first.
- The screening request repeats the question for every article, so it can be longer than the summary it screens. Price it before you build.
- A higher bar saves more and risks dropping an article that mattered. Currents judged quality only at 0.70. Use a lower bar when a miss is costly.
