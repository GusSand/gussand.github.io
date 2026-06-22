---
title: 'Mechanistic Interpretability as a Security Tool'
date: 2026-06-22
permalink: /posts/2026/06/mech-interp-for-security/
tags:
  - Security
  - LLM
  - Mechanistic Interpretability
  - Steering
---

# Mechanistic Interpretability as a Security Tool

Date: June 22, 2026 | Estimated Reading Time: 10 min | Author: Gustavo Sandoval

Mechanistic interpretability usually gets pitched as a science project, a way to understand in principle what's happening inside a neural network. I want to make a narrower, more practical case for it: interpretability as a security tool. If you can find where a model decides to do something unsafe, you can often fix it right there, cheaply, without retraining the whole thing.

This is the thread running through my recent work, and the clearest example is our paper [Surgical Repair of Insecure Code Generation in LLMs](https://arxiv.org/abs/2604.16697) ([Sandoval et al. 2026](https://arxiv.org/abs/2604.16697)).

**Table of Contents**

- [The Usual Security Loop](#the-usual-security-loop)
- [What Interpretability Adds](#what-interpretability-adds)
- [A Worked Example: Insecure Code](#a-worked-example-insecure-code)
- [Steering as an Intervention](#steering-as-an-intervention)
- [Limits and Risks](#limits-and-risks)
- [Where This Goes](#where-this-goes)
- [Citation](#citation)
- [References](#references)

# The Usual Security Loop

The standard way to make a model behave is data and training. Collect examples of good and bad behavior, fine-tune, evaluate, repeat. It works, but it's blunt. You're moving billions of parameters to fix a behavior whose cause you never actually located, and you pay for that in compute, in damage to unrelated capabilities, and in not really knowing whether the fix is robust or just papered over.

# What Interpretability Adds

Interpretability changes the unit of analysis from the model's behavior to the model's computation. Instead of asking what the model did, you ask which internal parts produced it. That buys you two things. You can tell a knowledge deficit ("the model never learned this") apart from a deployment failure ("the model knows but doesn't act on it"), and those need completely different fixes. And once you know where the responsible computation lives, you can edit activations there with steering vectors or representation engineering ([Turner et al. 2023](https://arxiv.org/abs/2308.10248); [Zou et al. 2023](https://arxiv.org/abs/2310.01405)) instead of retraining.

# A Worked Example: Insecure Code

In the Surgical Repair work, interpretability did real diagnostic work rather than decoration. We showed that insecure code generation isn't a knowledge deficit, because the model can explain the exact vulnerability it just wrote. Tracing the security-relevant representations, we found they're present from the early layers but go inert until the final one, where the pressure to produce well-formatted output overrides them. That gap between knowing and doing is the Format-Reliability Gap, and it's the kind of distinction the data-and-training loop can't see, because from the outside the model just looks like it doesn't understand security. The full diagnosis is in the [dedicated post](/posts/2026/06/format-reliability-gap/).

# Steering as an Intervention

Once you've localized the failure, the fix can be surgical. A per-vulnerability steering vector re-asserts the security signal at the layer where it gets suppressed, and that cuts insecure generation by up to 74% with almost no overhead and no fine-tuning run. The general point is bigger than one paper: a cause that lives in one place admits a cheap fix in that same place, which is exactly the property you want from something you intend to deploy.

# Limits and Risks

I don't want to pretend this is a cure-all. The same tools cut both ways, since a method for finding and steering a behavior is also a method an adversary can use to find and steer it. Localization can be partial, and not every unsafe behavior is going to be as cleanly single-layer as this one was. And steering can be evaded or can drift, so interventions need testing against adaptive inputs, not just the cases that motivated them.

# Where This Goes

The framing I keep coming back to is a loop. Measure a security failure empirically, the way we did in the Lost at C user study. Locate it inside the model with interpretability. Then intervene at the source and measure again. Each stage feeds the next. Interpretability is the part that turns "the model is unsafe" into "here is the component responsible, and here is a cheap fix," and that's what makes it a tool rather than just a microscope.

# Citation

Cited as:
> Sandoval, Gustavo. (Jun 2026). "Mechanistic Interpretability as a Security Tool". https://gussand.github.io/posts/2026/06/mech-interp-for-security/.

Or

```
@article{sandoval2026mechinterpblog,
  title   = "Mechanistic Interpretability as a Security Tool",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jun",
  url     = "https://gussand.github.io/posts/2026/06/mech-interp-for-security/"
}
```

# References

[1] Sandoval et al. ["Surgical Repair of Insecure Code Generation in LLMs: From Mechanistic Diagnosis to Deployment-Ready Intervention"](https://arxiv.org/abs/2604.16697). arXiv preprint arXiv:2604.16697 (2026).

[2] Sandoval et al. ["Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants"](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval). USENIX Security 2023.

[3] Turner et al. ["Activation Addition: Steering Language Models Without Optimization"](https://arxiv.org/abs/2308.10248). arXiv preprint arXiv:2308.10248 (2023).

[4] Zou et al. ["Representation Engineering: A Top-Down Approach to AI Transparency"](https://arxiv.org/abs/2310.01405). arXiv preprint arXiv:2310.01405 (2023).
