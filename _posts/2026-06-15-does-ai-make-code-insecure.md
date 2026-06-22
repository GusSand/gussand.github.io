---
title: 'Does AI Make You Write Insecure Code? A User Study'
date: 2026-06-15
permalink: /posts/2026/06/does-ai-make-code-insecure/
tags:
  - Security
  - LLM
  - Code Assistants
  - User Study
---

# Does AI Make You Write Insecure Code? A User Study

Date: June 15, 2026 | Estimated Reading Time: 9 min | Author: Gustavo Sandoval

When Copilot and Codex showed up in everyone's editor, the security community had a fast and fair reaction. A model trained on a huge pile of public code is going to suggest some of the bad patterns in that pile, and people are going to accept them. There was even evidence for the worry. When you looked at what Copilot generated on its own, a meaningful fraction of it contained weaknesses ([Pearce et al. 2022](https://arxiv.org/abs/2108.09293)).

But that left the question I actually cared about. A model's raw output and the code a person ships after working with that model are two different things. So we ran a study instead of arguing about it: [Lost at C](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval), at USENIX Security '23 ([Sandoval et al. 2023](https://arxiv.org/abs/2208.09727)). This post is the short version, caveats included.

**Table of Contents**

- [Why This Question Is Hard](#why-this-question-is-hard)
- [Study Design](#study-design)
- [Results](#results)
- [Caveats and Interpretation](#caveats-and-interpretation)
- [Takeaways](#takeaways)
- [Citation](#citation)
- [References](#references)

# Why This Question Is Hard

It's easy to slide between two claims that aren't the same thing. One is that AI assistants generate insecure code, which is a statement about what the model emits. The other is that AI assistants make developers ship more insecure code, which is a statement about the whole human-plus-model system.

The gap between them is the human. People edit, reject, and rewrite suggestions, and plenty of bugs a model proposes never make it into the final program. If you want to say anything about the second claim, you can't just grade model output. You need real people writing real code, a task where security actually bites, and a control group to compare against. That's what we set up.

# Study Design

We recruited 58 student programmers and asked each of them to implement a singly-linked "shopping list" in C. Both choices were on purpose. C is where the scary bugs live: manual memory management, pointer arithmetic, array indexing, and the buffer overflows and use-after-frees that come with them. If an assistant is going to steer people into serious vulnerabilities, this is the setting where you'd expect to see it.

Half the participants worked with an LLM assistant and half worked without one. Then we went through the code everyone actually produced and counted the critical security bugs in each group.

# Results

Here's the part that surprised people. The assisted group introduced critical security bugs at a rate no more than 10% above the control group. In this task the assistant was basically security-neutral. It didn't trigger the collapse you might predict from "the model suggests vulnerabilities."

I think that's the honest, slightly unsatisfying middle ground. The raw generations can absolutely contain vulnerabilities, which lines up with [Pearce et al. (2022)](https://arxiv.org/abs/2108.09293). And yet the code people shipped with the model in the loop wasn't meaningfully worse than what they wrote alone.

# Caveats and Interpretation

One study doesn't close the book, and how you read it depends entirely on the limits:

- C punishes everyone. The baseline bug rate is high whether or not you have an assistant, and a high common-mode error rate can swallow the difference between the two groups.
- These were students, and a shopping list is not a payment system. Both the population and the stakes are a step removed from production.
- "No worse than control" is not "safe." Both groups wrote plenty of bugs. We measured the marginal effect of the assistant, not the absolute safety of the code.
- It's one task in one language. Move to a web backend where injection and auth bugs dominate and the answer could flip.

# Takeaways

The reason to run a study like this is to drag the conversation off of vibes and onto numbers. Once you do, the better questions get sharper. Not "is AI good or bad for security," but which tasks, which languages, and which failure modes actually move when a model joins the work.

That's the question my later work chases. Instead of just measuring whether models write insecure code, I want to know why they do it and then fix it at the source, which is what I get into in the [post on the Format-Reliability Gap](/posts/2026/06/format-reliability-gap/).

# Citation

Cited as:
> Sandoval, Gustavo. (Jun 2026). "Does AI Make You Write Insecure Code? A User Study". https://gussand.github.io/posts/2026/06/does-ai-make-code-insecure/.

Or

```
@article{sandoval2026lostatcblog,
  title   = "Does AI Make You Write Insecure Code? A User Study",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jun",
  url     = "https://gussand.github.io/posts/2026/06/does-ai-make-code-insecure/"
}
```

# References

[1] Sandoval et al. ["Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants"](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval). USENIX Security 2023. | [arXiv:2208.09727](https://arxiv.org/abs/2208.09727)

[2] Pearce et al. ["Asleep at the Keyboard? Assessing the Security of GitHub Copilot's Code Contributions"](https://arxiv.org/abs/2108.09293). IEEE S&P 2022.
