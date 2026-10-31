---
layout: page
title: "Research"
permalink: /research/
---

---

## Research interests

My research asks why language models fail to act on what they know about safety, and what to do about it. I work on three steps: find where safe behavior breaks down inside the model, repair it without retraining, and prevent unsafe behavior from being learned in the first place.

- **Diagnosis: how safety breaks during training.** How refusal and other safe behavior erode across pretraining and post-training (SFT, DPO and RL), measured inside the model with tools such as the [refusal direction](/posts/2026/10/refusal-direction-two-years-later/).
- **Intervention: repair without retraining.** Probes and steering vectors that locate where a model's safe knowledge gets lost and push the decision back. [Insecure code generation](/posts/2026/10/models-know-the-fix/) is my first worked case, and [attention-head repair](https://arxiv.org/abs/2508.19414) of an arithmetic error is another.
- **Prevention: open-weight risk.** Which training data teaches an unsafe behavior, whether [data attribution](/posts/2026/10/safety-data-attribution/) or filtering can stop it, and how to test safeguards against attackers who hold the weights. In code models, unlearning can [hide knowledge instead of deleting it](https://openreview.net/forum?id=6WYjBeIioq).
- **Measurement: safety numbers you can trust.** Red-teaming methods, judges and benchmarks, and why one model gets different safety numbers from different evaluations.

Earlier work, which I still build on, studied how AI coding assistants affect the security of the code people write ([Lost at C](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval)) and how to defend against prompt injection.

I received my PhD from NYU and was advised by [Siddharth Garg](https://engineering.nyu.edu/faculty/siddharth-garg) and [Brendan Dolan-Gavitt](https://engineering.nyu.edu/faculty/brendan-dolan-gavitt), and a member of the [EnSuRe Research Lab](https://wp.nyu.edu/ensure_group/).

## Publications

You can also find my papers on [Google Scholar](https://scholar.google.com/citations?user=JIGI9xkAAAAJ).

{% include publications.html %}

## Collaborations

I'm always interested in collaborating with other researchers in AI safety and interpretability. Feel free to reach out if you're working on related problems.
