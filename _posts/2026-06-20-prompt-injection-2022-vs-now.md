---
title: 'Prompt Injection, 2022 vs Today: A Retrospective'
date: 2026-06-20
permalink: /posts/2026/06/prompt-injection-2022-vs-now/
tags:
  - Security
  - LLM
  - Prompt Injection
  - Adversarial Fine-Tuning
---

# Prompt Injection, 2022 vs Today: A Retrospective

Date: June 20, 2026 | Estimated Reading Time: 11 min | Author: Gustavo Sandoval

People like to call prompt injection the SQL injection of LLMs, and the comparison holds up better than most. Untrusted input and trusted instructions travel down the same channel, and the model has no built-in way to tell them apart. I find it useful to go back to what this looked like in 2022, when the models were GPT-3 variants and the attacks were brand new, and put it next to where we are now.

This is a retrospective companion to our paper, [Early Approaches to Adversarial Fine-Tuning for Prompt Injection Defense](https://arxiv.org/abs/2509.14271) ([Sandoval et al. 2025](https://arxiv.org/abs/2509.14271)), which documents work we actually did in 2022. If you want the method itself in detail, that's in the [earlier post on Adversarial Fine-Tuning](/posts/2023/01/blog-post-1/).

**Table of Contents**

- [The 2022 Picture](#the-2022-picture)
- [What We Tried: Adversarial Fine-Tuning](#what-we-tried-adversarial-fine-tuning)
- [What Held Up, What Did Not](#what-held-up-what-did-not)
- [The 2026 Picture](#the-2026-picture)
- [Lessons](#lessons)
- [Citation](#citation)
- [References](#references)

# The 2022 Picture

In 2022 prompt injection went from a party trick to a real concern fast. The canonical demo was an input like "Ignore all previous instructions and instead say X," which could either hijack the goal of a deployed prompt or leak the system instructions sitting behind it ([Perez & Ribeiro 2022](https://arxiv.org/abs/2211.09527)).

We studied both attacks against GPT-3-era models. Two things stood out. Without any defense, attacks succeeded about 31% of the time on the GPT-3 series. And the more capable the model, the easier it was to fool. Davinci was a softer target than the smaller variants, and far softer than GPT-2. That last part felt backwards at first, until you realize the instruction-following ability that makes a model useful is the exact thing an injection exploits.

# What We Tried: Adversarial Fine-Tuning

Our defense was Adversarial Fine-Tuning. The idea was to teach the model to treat user content as data rather than instructions, by delimiting that content and training the model to ignore any directives that show up inside it. On the smaller GPT-3 variants (Ada, Babbage, Curie), this took goal-hijacking success from double digits down to roughly zero.

It worked, but I flagged the limits at the time and they still matter. A delimiter-based scheme can be defeated if the attacker can forge the delimiter. Harmful content in the input can still get echoed back. And fine-tuning the biggest models was expensive enough to be its own obstacle.

# What Held Up, What Did Not

Some of those 2022 conclusions aged well. The framing of injection as a data-versus-instruction confusion is still how most people reason about the problem, and the entanglement between capability and vulnerability is still very real. Treating training-time defenses as one useful layer also held up.

What didn't hold up was the hope that fine-tuning alone could be the answer. Later research, including my own, makes it clear that these defenses reduce the attack surface without closing it, and that any single-layer defense tends to be brittle once an adversary adapts.

# The 2026 Picture

Today's version of the problem is bigger and less comfortable. The threat moved past direct injection to indirect injection, where the malicious instructions are planted in content the model retrieves, like a web page, a document, or an email, and then fire when an LLM-integrated app reads them ([Greshake et al. 2023](https://arxiv.org/abs/2302.12173)). Once you give a model tools, the blast radius stops being a bad sentence and starts being real actions in the world.

The defensive side has converged on layering rather than a single fix. Instruction hierarchies, task-specific fine-tuning, input and output filtering, and constitutional-style constraints get stacked together, with no one technique trusted to carry the load. The 2022 work fits in there as an early entry on the training-time side of that stack.

# Lessons

Three things I'd carry forward. Evaluate against adaptive attacks, not just the fixed prompt you happened to test, because a defense that stops yesterday's attack often falls to a mutated one. Assume defense in depth, since the whole history of this problem is single-layer defenses getting bypassed. And remember that capability and vulnerability move together, which means security has to be part of the design instead of something you bolt on after making the model more powerful.

# Citation

Cited as:
> Sandoval, Gustavo. (Jun 2026). "Prompt Injection, 2022 vs Today: A Retrospective". https://gussand.github.io/posts/2026/06/prompt-injection-2022-vs-now/.

Or

```
@article{sandoval2026promptretrospective,
  title   = "Prompt Injection, 2022 vs Today: A Retrospective",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jun",
  url     = "https://gussand.github.io/posts/2026/06/prompt-injection-2022-vs-now/"
}
```

# References

[1] Sandoval, Fenchenko, and Chen. ["Early Approaches to Adversarial Fine-Tuning for Prompt Injection Defense: A 2022 Study of GPT-3 and Contemporary Models"](https://arxiv.org/abs/2509.14271). arXiv preprint arXiv:2509.14271 (2025).

[2] Perez and Ribeiro. ["Ignore Previous Prompt: Attack Techniques For Language Models"](https://arxiv.org/abs/2211.09527). NeurIPS ML Safety Workshop 2022.

[3] Greshake et al. ["Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"](https://arxiv.org/abs/2302.12173). AISec 2023.
