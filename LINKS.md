# Other people's work

We link to these rather than copy them. Listing something here isn't an endorsement, and none of these people or companies is affiliated with Decision Layer.

## Official docs (TypeSafe, the maker of Jev)

- [API reference](https://docs.typesafe.ai/api.md): the request and response format these examples use
- [Question types: Choice, Score, Noul](https://docs.typesafe.ai/primitives.md)
- [Confidence and thresholds](https://docs.typesafe.ai/confidence.md)
- [Structuring the state](https://docs.typesafe.ai/concepts/state.md)
- [Example use cases, including insurance claims and risk](https://docs.typesafe.ai/concepts/use-case-map.md)
- [Known weak spots in jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- [Models and pricing](https://docs.typesafe.ai/models.md)
- [How TypeSafe trains decision models](https://docs.typesafe.ai/introduction/machine-learning-primer.md)

## Independent analysis

- Alex Molas, [Jev can't be calibrated](https://www.alexmolas.com/2026/09/23/jev-cant-be-calibrated.html): why to treat scores as rankings until you check them on your own data
- Tiantong Wu and Wei Yang Bryan Lim, [prompt-injection study of Jev](https://arxiv.org/abs/2609.28613): 510 attack cases against jev-1.13.0

## Regulators

- NAIC, [Artificial intelligence (insurance topics)](https://content.naic.org/insurance-topics/artificial-intelligence), including the December 2023 model bulletin

## Other decision models

These examples are written for Jev. Other decision models use their own request formats, so the code here won't run on them unchanged. Links checked Oct 31, 2026.

**From the maker**
- OpenAI, [Decisions API guide](https://developers.openai.com/api/docs/guides/decisions)
- Microsoft, [Introducing Microsoft-Decision-1 in Microsoft Foundry](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-decision-1-in-microsoft-foundry-for-decision-and-classific/4562742)
- Liquid AI, [d1-ultra](https://www.liquid.ai/blog/d1-ultra)
- Fastino, [GLiNER2.5-Decide](https://fastino.ai/blog/gliner-2-5-decide-open-weight-decision-model)

**Hosted on a platform, not the maker's own page**
- Base Labs Elephant-1, [on Baseten](https://www.baseten.co/library/elephant-1/)
- Laya, [on Hugging Face](https://huggingface.co/convaiinnovations/laya)
- Inception Mercury Decide, [on OpenRouter](https://openrouter.ai/inception/mercury-decide)

**Press only so far**
- Cloudflare Clef: [The Register](https://www.theregister.com/a/5300649), which reports its API is "fully Jev compatible". We haven't checked that against these examples.
- AWS Strands Decider 2B: [SiliconANGLE](https://siliconangle.com/2026/10/01/aws-debuts-strands-decider-2b-a-first-lightweight-decision-model-for-accelerate-agentic-workflows/)
