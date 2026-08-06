---
title: 'Red-Teaming Language Models, Part 2: What Holds on Defense'
description: 'Part 2 of three. The best-documented defensive result, why layered safeguards can be peeled apart one classifier at a time, the adaptive-attack result that breaks most published defenses, and why agents are the current worst case.'
date: 2026-07-29
permalink: /posts/2026/07/red-teaming-language-models-defense/
tags:
  - Security
  - LLM
  - Red Teaming
  - Evaluation
  - Jailbreak
  - Open Weights
---

Date: July 29, 2026 \| Estimated Reading Time: 5 min \| Author: Gustavo Sandoval

Series: [Part 1](/posts/2026/07/red-teaming-language-models/) &mdash; Process & Measurement &middot; **Part 2** &mdash; What Holds on Defense &middot; [Part 3](/posts/2026/07/red-teaming-language-models-open-weights/) &mdash; Open Weights

This is the second of three parts. [Part 1](/posts/2026/07/red-teaming-language-models/) covered the converged red-teaming process, how attacks are built, and why reported attack success rates are so often not comparable. Here I ask the question that motivates the whole exercise: once you can run a red team and measure it, does any defense actually hold against a determined adversary? Everything here assumes you control the inference path. [Part 3](/posts/2026/07/red-teaming-language-models-open-weights/) is what happens when you do not.

Keep one point from Part 1 in view: an attack success rate is a property of the adversary you chose, not of the model alone.

[&larr; Part 1: Process and Measurement](/posts/2026/07/red-teaming-language-models/)

{% include reading-outline.html %}

<details markdown="1" open>
<summary><strong>Table of Contents</strong></summary>

- [What Holds on Defense](#what-holds-on-defense)
  - [The Strong Positive Result](#the-strong-positive-result)
  - [Attacking the Pipeline, Not the Model](#attacking-the-pipeline-not-the-model)
  - [The Strong Negative Result](#the-strong-negative-result)
  - [Agents Are the Current Worst Case](#agents-are-the-current-worst-case)
- [Continue to Part 3: Open Weights &rarr;](/posts/2026/07/red-teaming-language-models-open-weights/)
- [Citation](#citation)
- [References](#references)

</details>

# What Holds on Defense

## The Strong Positive Result

Anthropic's Constitutional Classifiers is the best-documented defensive red-team protocol published ([Sharma et al. 2025](https://arxiv.org/abs/2501.18837)). Input and output classifiers are trained on synthetic data generated from an explicit constitution and layered so that no single component carries the load. The red team ran as a bug bounty: 800 applications, 405 invited, an estimated 183 active participants, bounties up to $15K per report and $95K paid out. Success was graded by a multi-stage rubric pipeline anchored to helpful-only baseline outputs.

Over an estimated 3,000 hours of red teaming, no universal jailbreak was found. The classifier-guarded system refused over 95% of held-out jailbreak attempts against 14% for the unguarded baseline, at an absolute 0.38% increase in production-traffic refusals and 23.7% inference overhead. That last pair of numbers is why the result matters commercially.

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-constitutional-classifiers-tradeoffs.jpg" width="1086" height="521" alt="Three-panel comparison of attack success rate on held-out jailbreaks, refusal rate on claude.ai traffic, and relative inference cost, for no classifiers, prompted Claude 3.5 Sonnet variants, and Constitutional Classifiers" style="width:100%;height:auto;display:block" /></div>

*Fig. 1. Constitutional Classifiers (green) take held-out jailbreak success from 86% to about 4% at 123% inference cost and 1.5% refusals, where prompting Claude 3.5 Sonnet for the same robustness costs 190 to 200% and refuses up to 2.7% of real traffic. (Image source: [Sharma et al. 2025](https://arxiv.org/abs/2501.18837))*

The near-miss is the part I'd point people to. One report initially looked like a universal jailbreak. It turned out to be an implementation error that let participants receive up to 128 tokens *after* the output classifier had already flagged the content: a flaw in the deployment, by Anthropic's own description, not in the classifier. The lesson generalizes: attackers target the weakest component, and the weakest component is often the harness. **Red team the deployment and the evaluation protocol, not only the model.**

The 2026 successor keeps the constitutional approach but rebuilds the pipeline around it, most importantly with exchange classifiers that see a response in its full conversational context rather than in isolation, reaching a 40x cost reduction and a 0.05% refusal rate on production traffic ([Cunningham et al. 2026](https://arxiv.org/abs/2601.04603)). The counterpoints arrived just as quickly: adversarial fine-tuning that evades classifiers above 99% while costing under 5% on reasoning benchmarks, against the 25%-plus capability damage earlier fine-tuning attacks paid, though it needs fine-tuning API access to land ([Sel et al. 2026](https://arxiv.org/abs/2603.29038)), and the two results in the next section. This exchange is still live.

## Attacking the Pipeline, Not the Model

The near-miss above generalizes into a method. McKenzie and colleagues built an open-source defense-in-depth pipeline, with few-shot-prompted input and output classifiers, that beat ShieldGemma, the best open-weight safeguard model they tested, and drove attack success to 0% on ClearHarm, a dataset of unambiguously catastrophic misuse queries ([McKenzie et al. 2025](https://arxiv.org/abs/2506.24068)). Then they attacked it in stages.

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-stack-pipeline-attack.jpg" width="1640" height="760" alt="Left: schematic of a query carrying an input-classifier jailbreak and instructing the model to repeat an output-classifier jailbreak, passing both filters. Right: attack success rate versus attacks per example, with PAP flat at zero against the defended pipeline and STACK rising to about 70 percent" style="width:100%;height:auto;display:block" /></div>

*Fig. 2. The staged attack: the query carries a jailbreak for the input classifier and makes the model repeat one for the output classifier, so the response smuggles its own key past the final filter. PAP stays flat at 0%; STACK reaches about 70%. (Image source: [McKenzie et al. 2025](https://arxiv.org/abs/2506.24068))*

The staging is the whole idea. Find a universal jailbreak for the input classifier, use a persuasion attack to get the model itself to comply, then find a universal jailbreak string for the output classifier and have the model *repeat* it, so the response carries its own key past the final filter. Each component is attacked separately and the results are concatenated. On ClearHarm that took the pipeline from 0% to 71%. A transfer version, with both classifier jailbreaks developed against a proxy pipeline the attackers assembled themselves, still landed 33%, needing only the forty persuasion queries against the target itself.

Two things follow. Layering safeguards multiplies robustness only if the attacker has to beat the layers simultaneously; if they can be attacked one at a time, you have made the attack longer rather than harder. And an end-to-end evaluation, which is how both a bug bounty and a benchmark measure a pipeline, cannot tell those two situations apart. Their mitigations are cheap and worth copying: return identical refusals regardless of which stage fired, and keep running a query through the remaining stages after an early reject, so neither the wording nor the latency tells the attacker which component they still need to beat.

Then, in February 2026, the harder result. Boundary Point Jailbreaking is fully black-box and uses a single bit per query (flagged or not flagged) with no classifier scores or gradients ([Davies et al. 2026](https://arxiv.org/abs/2602.15001)). Its trick addresses what makes attacking a strong defense so hard: almost every candidate attack fails, so almost every query returns no usable signal. Instead of optimizing directly against a target, it builds a curriculum of easier intermediate targets and evaluates candidates at "boundary points" chosen to be maximally sensitive to small changes in attack strength.

Both labs verified it in hedged terms: the first fully automated black-box attack either is aware of to clear their universal-jailbreak bar, and the first to beat GPT-5's input classifier without human seed attacks. On biological-misuse questions it moved the average rubric score from 0% to 25.5% against the classifiers guarding Claude Sonnet 4.5 (68% with basic elicitation), and from 0% to 75.6% against GPT-5's input classifier. One scope caveat: what BPJ automates is the attack on the *classifiers*; in both settings the authors used a human-found jailbreak to get past the model's own refusals.

The authors are careful about what this overturns, and so am I. It took months of effort and ran on accounts exempt from the usual flagging bans, where Constitutional Classifiers is designed against attackers with less time. But the dollar costs are what I would put in front of a security team: $330 and 660,000 queries for the Constitutional Classifiers setting, $210 and 800,000 for GPT-5's, a rounding error against the $95K bounty. A defense that holds against thousands of hours of human effort can still fall to a script that runs overnight, because they measure different adversaries.

The defensive reading: those 660,000 queries generated an enormous number of flags. Nothing about any single interaction gave the attack away, but the *campaign* was loud. That points at a control the literature underweights, batch-level monitoring across interactions, rather than one more classifier inside a single request.

## The Strong Negative Result

Now the bad news.

Nasr, Carlini, and colleagues took twelve recent defenses against jailbreaks and prompt injections, and systematically tuned gradient, reinforcement learning, search, and human attacks against each one's specific design ([Nasr et al. 2025](https://arxiv.org/abs/2510.09023)).

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-adaptive-attacks-12-defenses.jpg" width="1122" height="354" alt="Bar chart of twelve defenses showing low static attack success rates and high adaptive attack success rates" style="width:100%;height:auto;display:block" /></div>

*Fig. 3. Twelve defenses under static (green) versus tuned adaptive (orange) attack: several that report 0% under static attack land between 71% and 99% once the attack is tuned against them. (Image source: [Nasr et al. 2025](https://arxiv.org/abs/2510.09023))*

Most of the twelve were bypassed above 90%, and the majority had originally reported near-zero. The rule worth memorizing: defenses that report near-zero attack success rates on public benchmarks are often among the easiest to break once novel attacks are attempted.

Note the rightmost bar in that figure. In their human red-teaming setting, the static attack succeeded on nothing and human attackers succeeded on everything. If your evaluation is a fixed corpus of published attack strings, you have measured your defense against a threat model in which the adversary does not adapt, and no such adversary exists.

IBM adds a budget corollary: fine-tuned BERT and DeBERTa classifiers generalize to new datasets competitively with, sometimes better than, more expensive open and closed guardrails ([Zizzo et al. 2025](https://arxiv.org/abs/2502.15427)).

## Agents Are the Current Worst Case

The Gray Swan and UK AISI public competition produced the numbers in this post that worry me most ([Zou et al. 2025](https://arxiv.org/abs/2507.20526)). Across 44 realistic deployment scenarios and 22 frontier models, almost 2,000 participants made approximately 1.8 million attack attempts and produced over 62,000 successful elicitations of targeted policy violations. Every model experienced repeated successful attacks across every target behavior: a 100% behavior-level attack success rate.

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-agent-asr-by-model.jpg" width="1115" height="504" alt="Per-challenge attack success rate by model, ranging from 6.7 percent down to 1.5 percent" style="width:100%;height:auto;display:block" /></div>

*Fig. 4. Per-challenge attack success by model runs 6.7% down to 1.5%, yet every model hit a 100% behavior-level rate over the competition, because attackers retry. (Image source: [Zou et al. 2025](https://arxiv.org/abs/2507.20526))*

This figure is the cleanest illustration of the estimand point from earlier. The per-challenge rate runs from 6.7% for the weakest model to 1.5% for the strongest. The behavior-level rate, meaning whether a behavior was ever elicited on that model at any point in the competition, is 100% for all 22. Neither number is wrong. Report the first and your agent looks respectable; report the second and it looks undefended. Only the second describes what happens when someone attacks you, and only the first is what most evaluations publish.

Three findings from that competition should change how people plan. Indirect prompt injection was roughly five times more effective than direct injection, 27.1% against 5.7%. Robustness barely correlated with model size, capability, or inference-time compute, so you cannot buy your way out by scaling. And attacks transferred readily across models and tasks, so failures are correlated across vendors and defense-by-model-diversity does not work either.

Everything above assumes you control the inference path. [**Part 3: What Changes When You Ship Open Weights**](/posts/2026/07/red-teaming-language-models-open-weights/) is what happens when you give that up.

# Citation

Cited as:
> Sandoval, Gustavo. (Jul 2026). "Red-Teaming Language Models, Part 2: What Holds on Defense". https://gussand.github.io/posts/2026/07/red-teaming-language-models-defense/.

Or

```
@article{sandoval2026redteaming2,
  title   = "Red-Teaming Language Models, Part 2: What Holds on Defense",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jul",
  url     = "https://gussand.github.io/posts/2026/07/red-teaming-language-models-defense/"
}
```

# References

[1] Sharma et al. ["Constitutional Classifiers: Defending against Universal Jailbreaks across Thousands of Hours of Red Teaming"](https://arxiv.org/abs/2501.18837). arXiv preprint arXiv:2501.18837 (2025).

[2] Cunningham et al. ["Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks"](https://arxiv.org/abs/2601.04603). arXiv preprint arXiv:2601.04603 (2026).

[3] Sel et al. ["Trojan-Speak: Bypassing Constitutional Classifiers with No Jailbreak Tax via Adversarial Finetuning"](https://arxiv.org/abs/2603.29038). arXiv preprint arXiv:2603.29038 (2026).

[4] McKenzie, Hollinsworth, Tseng, Davies, Casper, Tucker, Kirk, and Gleave. ["STACK: Adversarial Attacks on LLM Safeguard Pipelines"](https://arxiv.org/abs/2506.24068). arXiv preprint arXiv:2506.24068 (2025).

[5] Davies, Giglemiani, Lau, Winsor, Irving, and Gal. ["Boundary Point Jailbreaking of Black-Box LLMs"](https://arxiv.org/abs/2602.15001). arXiv preprint arXiv:2602.15001 (2026).

[6] Nasr, Carlini, Sitawarin, et al. ["The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections"](https://arxiv.org/abs/2510.09023). arXiv preprint arXiv:2510.09023 (2025).

[7] Zizzo et al. ["Adversarial Prompt Evaluation: Systematic Benchmarking of Guardrails Against Prompt Input Attacks on LLMs"](https://arxiv.org/abs/2502.15427). arXiv preprint arXiv:2502.15427 (2025).

[8] Zou et al. ["Security Challenges in AI Agent Deployment: Insights from a Large Scale Public Competition"](https://arxiv.org/abs/2507.20526). arXiv preprint arXiv:2507.20526 (2025).
