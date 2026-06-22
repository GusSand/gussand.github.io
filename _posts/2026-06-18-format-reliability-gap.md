---
title: 'The Format-Reliability Gap: Diagnosing and Repairing Insecure Code Generation'
date: 2026-06-18
permalink: /posts/2026/06/format-reliability-gap/
tags:
  - Security
  - LLM
  - Mechanistic Interpretability
  - Secure Code Generation
---

# The Format-Reliability Gap: Diagnosing and Repairing Insecure Code Generation

Date: June 18, 2026 | Estimated Reading Time: 10 min | Author: Gustavo Sandoval

Ask an LLM to generate a piece of code and it might hand you a SQL injection or a buffer overflow. Ask the same model, a minute later, "does this code have a vulnerability?" and it will often name the bug, explain why it's dangerous, and write the fix. So the knowledge is in there. The model just doesn't use it while it's generating.

Our 2026 preprint, [Surgical Repair of Insecure Code Generation in LLMs](https://arxiv.org/abs/2604.16697) ([Sandoval et al. 2026](https://arxiv.org/abs/2604.16697)), gives that phenomenon a name, the Format-Reliability Gap, finds where it lives inside the network, and shows that because it lives in one place you can repair it with a small, cheap intervention instead of retraining the whole model.

**Table of Contents**

- [It Is Not a Knowledge Deficit](#it-is-not-a-knowledge-deficit)
- [A Single-Layer Failure](#a-single-layer-failure)
- [Repair with Steering Vectors](#repair-with-steering-vectors)
- [Why the Framing Matters](#why-the-framing-matters)
- [Open Questions](#open-questions)
- [Citation](#citation)
- [References](#references)

# It Is Not a Knowledge Deficit

The first finding is the one everything else depends on. Insecure generation is not the model failing to know what a vulnerability is. The same model that emits the vulnerable code diagnoses it correctly when you ask directly. So the standard fix, "train on more secure code so the model learns security," is aimed at the wrong target. The model already learned. The problem is that what it knows doesn't drive what it writes.

This builds on our earlier finding that the security effect of assistants is subtler than people expected ([Sandoval et al. 2023](https://arxiv.org/abs/2208.09727)). Here we go a layer down: not whether the model writes insecure code, but the mechanism by which it does so even when it clearly knows better.

# A Single-Layer Failure

We used mechanistic interpretability to follow the security-relevant representations through the network. The picture that came out is surprisingly clean. The model registers the risky pattern in its early layers. That signal then sits there, doing nothing, through the middle of the network. At the final layer, the pressure to produce fluent, format-compliant output competes with the security signal and wins.

In other words, the model knows, carries that knowledge most of the way through, and drops it at the last step in favor of writing something that looks like correct code. The failure isn't smeared across the whole model. It's concentrated right where format gets resolved.

# Repair with Steering Vectors

A failure that lives in one place can be fixed in one place. Instead of retraining, we build a steering vector for each vulnerability type, a direction we add to the model's internal activations that re-asserts the security signal exactly where it was getting crowded out. This follows the activation-steering and representation-engineering line of work ([Turner et al. 2023](https://arxiv.org/abs/2308.10248); [Zou et al. 2023](https://arxiv.org/abs/2310.01405)), pointed at the security failure mode.

It works well. Insecure generation drops by up to 74%, with almost no added cost and no fine-tuning run. The intervention is targeted enough that general code quality holds, so you don't end up with a model that refuses or rewrites everything in the name of safety.

# Why the Framing Matters

Most "make the model write secure code" pipelines treat the model as a black box and throw more data at it. Calling insecure generation a localized, mechanistic failure changes what you can do about it. You can diagnose it precisely, point at the layer responsible, and fix it cheaply. "Deployment-ready" is in the subtitle on purpose, since the overhead is low enough to actually run.

# Open Questions

I don't want to oversell a single paper. A few things I still want to know: how stable the single-layer story is across architectures and scales, whether per-vulnerability vectors can be combined without stepping on each other when several risks show up at once, and how well steering holds up against inputs designed specifically to evade it.

# Citation

Cited as:
> Sandoval, Gustavo. (Jun 2026). "The Format-Reliability Gap: Diagnosing and Repairing Insecure Code Generation". https://gussand.github.io/posts/2026/06/format-reliability-gap/.

Or

```
@article{sandoval2026surgicalblog,
  title   = "The Format-Reliability Gap: Diagnosing and Repairing Insecure Code Generation",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jun",
  url     = "https://gussand.github.io/posts/2026/06/format-reliability-gap/"
}
```

# References

[1] Sandoval et al. ["Surgical Repair of Insecure Code Generation in LLMs: From Mechanistic Diagnosis to Deployment-Ready Intervention"](https://arxiv.org/abs/2604.16697). arXiv preprint arXiv:2604.16697 (2026).

[2] Sandoval et al. ["Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants"](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval). USENIX Security 2023.

[3] Turner et al. ["Activation Addition: Steering Language Models Without Optimization"](https://arxiv.org/abs/2308.10248). arXiv preprint arXiv:2308.10248 (2023).

[4] Zou et al. ["Representation Engineering: A Top-Down Approach to AI Transparency"](https://arxiv.org/abs/2310.01405). arXiv preprint arXiv:2310.01405 (2023).
