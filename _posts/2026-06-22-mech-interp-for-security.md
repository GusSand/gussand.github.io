---
title: 'Mechanistic Interpretability as a Security Tool'
description: 'Interpretability is usually pitched as a science project. The narrower, more useful case: if you can find where a model decides to do something unsafe, you can often fix it there, cheaply, instead of retraining around it. A tour of where behavior lives inside a model, what it costs to reach in, and why the same tools cut both ways.'
date: 2026-06-22
permalink: /posts/2026/06/mech-interp-for-security/
tags:
  - Security
  - LLM
  - Mechanistic Interpretability
  - Steering
---

Date: June 22, 2026 \| Estimated Reading Time: 12 min \| Author: Gustavo Sandoval

In May 2024, Anthropic put out a version of Claude that could not stop talking about the Golden Gate Bridge. Ask it for a banana bread recipe and it would work the bridge into the ingredients. Ask it to write a business email and the fog would roll in. It was funny, it was briefly a meme, and it was made by turning a single knob. The researchers had located an internal feature that fired on the concept "Golden Gate Bridge," clamped its value high, and let the model run ([Templeton et al. 2024](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)).

The joke is also the whole argument I want to make. If a behavior corresponds to something you can point at inside the network, you can reach in and change it without retraining anything. Golden Gate Claude is a toy. The security version is not: if the thing you can point at is "write the SQL query with string concatenation instead of a parameterized statement," then pointing at it is the beginning of a fix.

Mechanistic interpretability usually gets pitched as a science project, a way to understand in principle what a neural network is doing. I want to make a narrower and more practical case. Used as a security tool, interpretability answers a specific question that black-box testing cannot: not *whether* the model does something unsafe, but *where inside it* the decision to do so gets made. Once you have that location, some fixes get much cheaper. This is the thread running through my recent work, and the clearest example is our paper [Surgical Repair of Insecure Code Generation in LLMs](https://arxiv.org/abs/2604.16697) ([Sandoval et al. 2026](https://arxiv.org/abs/2604.16697)).

**Table of Contents**

- [The Usual Security Loop](#the-usual-security-loop)
- [What Interpretability Changes](#what-interpretability-changes)
- [Where Does a Behavior Live?](#where-does-a-behavior-live)
- [Reading vs. Writing](#reading-vs-writing)
- [A Worked Example: Insecure Code](#a-worked-example-insecure-code)
- [The Same Tools Cut Both Ways](#the-same-tools-cut-both-ways)
- [Where the Microscope Lies](#where-the-microscope-lies)
- [Does the Fix Survive?](#does-the-fix-survive)
- [Where This Goes](#where-this-goes)
- [Citation](#citation)
- [References](#references)

# The Usual Security Loop

The standard way to make a model behave is data and training. Collect examples of good and bad behavior, fine-tune on the good, evaluate, and repeat until the numbers look acceptable. It works, and for many problems it is the right tool. But it is blunt in a specific way: you are moving billions of parameters to correct a behavior whose cause you never located. You pay for that in compute, in collateral damage to unrelated capabilities that gradient descent had no reason to preserve, and in a subtler way that should worry a security team most, because you never learn whether you fixed the cause or just covered the symptom, which is the difference between a defense and a coincidence.

The security literature has learned to distrust that last part. A defense that reports near-zero attack success on the cases it was tuned against, and then falls over when someone attacks it adaptively, is a pattern common enough that I gave it [its own treatment elsewhere](/posts/2026/07/red-teaming-language-models/). Training against a behavior you cannot locate is how you end up there.

# What Interpretability Changes

Interpretability changes the unit of analysis from the model's behavior to the model's computation. Instead of asking what the model did, you ask which internal parts produced it. That shift buys two things that matter for security.

The first is a diagnosis you cannot get from the outside. A model that writes insecure code might be failing for opposite reasons: it never learned the secure pattern, or it knows the secure pattern perfectly well and does not deploy it under the conditions that matter. From the outside those look identical, a wrong answer either way. Inside, they are different failures with different fixes, and only one of them is a knowledge problem. Telling them apart is most of the value.

The second is that once you know where the responsible computation lives, you can edit it directly. Two lines of work established that model behavior can be steered by adding a vector to its activations rather than by retraining: activation addition, which reads a direction off a few contrastive prompts and adds it back at inference ([Turner et al. 2023](https://arxiv.org/abs/2308.10248)), and representation engineering, which treats these directions as a general control surface for high-level concepts like honesty and harmfulness ([Zou et al. 2023](https://arxiv.org/abs/2310.01405)). The intervention costs a forward-pass addition and no gradient steps. That is the property you want from something you intend to run in production.

# Where Does a Behavior Live?

If the plan is to reach in and change something, the obvious question is what "something" is. The field has found behavior localized at three grains, and they are worth keeping distinct because they cost different amounts to find and admit different interventions.

![](/images/mech-interp/fig1-three-grains.svg)
*Fig. 1. The three grains at which a behavior can be localized. Use the coarsest one that still separates what you want to change from what you want to keep. (Diagram by the author)*

**A direction.** The cleanest result in this genre is that refusal, the thing that makes a chat model decline a harmful request, is mediated by a single direction in activation space ([Arditi et al. 2024](https://arxiv.org/abs/2406.11717)). Across thirteen open-weight chat models, adding that one direction makes the model refuse harmless requests, and erasing it makes the model comply with harmful ones. A behavior that safety training spends enormous effort installing turns out to hang on a one-dimensional thread. That is a gift to a defender who wants to strengthen it and, as I will get to, a gift to an attacker who wants to cut it.

**A feature.** Directions found from a handful of prompts are coarse. Sparse autoencoders push for something finer: train a wide, sparse dictionary on a model's activations and recover thousands of features that each fire on a specific, human-nameable concept ([Bricken et al. 2023](https://transformer-circuits.pub/2023/monosemantic-features/index.html)), then scale the same recipe to a production model and get millions, including features for concepts like insecure code, deception, and backdoors ([Templeton et al. 2024](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)). The Golden Gate feature came from here. So did the demonstration that clamping a feature reliably moves behavior, which is the part a security team should care about.

**A circuit.** The most demanding grain is a subgraph of attention heads and MLPs that implements an algorithm. The canonical example reverse-engineered how GPT-2 small identifies an indirect object, tracing a specific set of heads that copy, inhibit, and move information to complete "When John and Mary went to the store, John gave a drink to ___" ([Wang et al. 2022](https://arxiv.org/abs/2211.00593)). Circuit-level understanding is expensive and does not yet scale to frontier models, but it is the only grain that tells you *why* a behavior happens rather than just *where* its signature sits.

For security the useful move is usually the cheapest grain that supports the intervention you need. You do not need a full circuit to strengthen refusal if refusal is a direction. You reach for the finer tools when the coarse ones cannot separate the behavior you want to change from the one you want to keep.

# Reading vs. Writing

There is a second axis that matters more than the grain, and it splits interpretability's two security uses cleanly. You can *read* the model's internal state to decide whether something is happening, or you can *write* to it to change what happens. Detection and control are different jobs with different failure modes.

Reading is monitoring. The strongest demonstration is that a simple linear probe, trained on activations, can catch a backdoored model in the act: Anthropic planted sleeper-agent behavior in a model and found that a probe asking essentially "are you about to do something dangerous" flagged the defection with near-perfect separation, even though the behavior was invisible from the model's outputs until the trigger fired ([MacDiarmid et al. 2024](https://www.anthropic.com/research/probes-catch-sleeper-agents)). A probe is cheap, it runs alongside inference, and it fails safe: a false positive costs you a refusal, not a breach.

Writing is steering, and it is the same operation as the Golden Gate knob pointed at something you care about. Reading tells you a request is heading somewhere bad. Writing tries to stop it from getting there. The two compose: a probe that fires can gate whether a steering vector gets applied, so the intervention only touches the inputs that need it and leaves normal traffic alone. That gating matters, because the cost of steering is almost never zero, and applying it to everything is how you break the capabilities you were trying to protect.

![](/images/mech-interp/fig2-read-vs-write.svg)
*Fig. 2. Reading the model's state to monitor, versus writing to it to steer. A probe can gate when the steering vector fires, so the intervention only touches inputs that need it. (Diagram by the author)*

# A Worked Example: Insecure Code

Here is where the diagnosis earns its keep. In the [Lost at C](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval) user study we established that assistant-written code carries real vulnerabilities into programs written by real people ([Sandoval et al. 2023](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval)). The obvious reading is a knowledge deficit: the model does not know secure patterns. That reading is wrong, and interpretability is how we know it is wrong.

In the Surgical Repair work, the model can explain the exact vulnerability it just wrote, in detail, when you ask it to review its own output. The knowledge is there. Tracing the security-relevant representations through the network, we found them present from the early layers and then going inert at the very end, where the pressure to emit well-formatted, plausible-looking code overrides them. The model knows the code is unsafe and writes it anyway, because at the layer where the token is chosen, "looks like correct code" wins over "is secure." That gap between knowing and doing is the [Format-Reliability Gap](/posts/2026/06/format-reliability-gap/), and it is exactly the distinction the data-and-training loop cannot see, because from the outside the model just looks ignorant.

![](/images/mech-interp/fig3-format-reliability-gap.svg)
*Fig. 3. The Format-Reliability Gap, drawn schematically: the security signal is computed early and held across the network, then collapses at the final layer as output-format pressure takes over. The measured curves are in [Sandoval et al. 2026](https://arxiv.org/abs/2604.16697). (Diagram by the author)*

This is not a new idea in code security specifically. SVEN showed years earlier that you can steer a code model's security behavior with a small learned control, a set of continuous prefixes that raise or lower the rate of secure output without changing the model's weights ([He and Vechev 2023](https://arxiv.org/abs/2302.05319)). What the mechanistic diagnosis adds is the reason it works and where to apply it: the signal is already computed, it is being suppressed late, and re-asserting it at that layer is a local edit rather than a retrain.

# The Results

Once the failure is localized, the fix can be surgical. A per-vulnerability steering vector re-asserts the security signal at the layer where it gets suppressed. In our evaluation that cuts insecure generation by up to 74%, with almost no inference overhead and no fine-tuning run at all. The vectors are per-CWE, so the intervention is scoped to the vulnerability class it was built for rather than being a blunt "be more secure" push that would degrade unrelated generation.

![](/images/mech-interp/fig4-steering-result.svg)
*Fig. 4. Re-asserting the signal at the layer where it collapses cuts insecure generations by up to 74% relative to baseline, shown normalized, at a forward-pass addition and no fine-tuning. (Chart by the author; result from [Sandoval et al. 2026](https://arxiv.org/abs/2604.16697))*

That number matters less than its shape. A cause that lives in one place admits a cheap fix in that same place, and you can measure the fix against the same localized signal you used to find the cause. That closes a loop the black-box process leaves open. You are no longer hoping the retrain fixed the right thing. You located the thing, you edited it, and you re-measured it in the same coordinates.

# The Same Tools Cut Both Ways

I do not want to oversell this, because the honesty is load-bearing. A method for finding and steering a behavior is also a method for finding and steering it in the other direction, and the interpretability literature is candid about it.

The refusal direction is the sharpest example. The same one-dimensional result that lets a defender reinforce refusal is, read backwards, a recipe for removing it: erase the direction and an aligned open-weight model stops refusing, at the cost of a rank-one weight edit and no training data ([Arditi et al. 2024](https://arxiv.org/abs/2406.11717)). This is now a standard jailbreak for open weights. SVEN's authors made the symmetry explicit in the other domain, using the same prefix mechanism to *harden* a code model and to *attack* it, driving its secure-output rate down on demand ([He and Vechev 2023](https://arxiv.org/abs/2302.05319)). Steering is a control surface, and control surfaces do not have a preferred sign.

![](/images/mech-interp/fig5-dual-use.svg)
*Fig. 5. A located behavior is dual-use. The refusal direction a defender adds to strengthen refusal is, negated, a rank-one jailbreak. (Diagram by the author, following [Arditi et al. 2024](https://arxiv.org/abs/2406.11717))*

The practical consequence is that publishing a localized defense can hand an attacker a differentiable map of what to disable. It is the same tension that runs through open-weight release generally, which I take up [in the red-teaming series](/posts/2026/07/red-teaming-language-models-open-weights/): the more precisely you characterize where safety lives, the more precisely someone else can remove it.

# Where the Microscope Lies

Interpretability has its own file of negative results, and the security-relevant ones are worth knowing before you bet a defense on any of this.

![](/images/mech-interp/fig6-negative-results.svg)
*Fig. 6. Four security-relevant interpretability results that failed, got complicated, or turned out to measure the tool instead of the model. (Diagram by the author; sources in the text)*

Steering, the write operation this whole post leans on, is less reliable than the clean demos suggest. A systematic study of steering vectors found high variance across prompts and poor generalization out of distribution, with interventions that work on the examples used to build them failing or reversing elsewhere ([Tan et al. 2024](https://arxiv.org/abs/2407.12404)). A steering-based defense tuned on the cases that motivated it is exactly the kind of thing that looks solid in a paper and slips in deployment.

The reading side has taken hits too. Sparse autoencoders are the flagship of the features grain, and the obvious security use is detection: train the dictionary, watch for the harmful feature. When someone benchmarked that against a plain linear probe on the same activations, the autoencoder did not win, and a simple probe matched or beat it across a battery of concepts ([Kantamneni et al. 2025](https://arxiv.org/abs/2502.16681)). The expensive tool did not buy detection performance over the cheap one.

Even the cleanest result in this post has been complicated. The single-direction refusal finding that makes refusal look like a solved knob turns out to be incomplete: refusal is carried by more than one direction, and ablating the one you found has side effects and misses the refusal that routes elsewhere ([Joad et al. 2026](https://arxiv.org/abs/2602.02132)). The knob is real. It is not the whole mechanism.

The oldest caution is the one most worth keeping, because it predates language models. A probe that reads a concept off activations at high accuracy may be measuring its own capacity to fit a label rather than a feature the model actually uses. The fix is a control task: train the same probe on random labels, and trust the result only to the extent the real task beats the random one ([Hewitt and Liang 2019](https://arxiv.org/abs/1909.03368)). A monitoring probe that has not cleared that bar is telling you about the probe, not the model.

None of this retires interpretability as a security tool. It sets the evidentiary bar. A located behavior is a hypothesis, and the intervention built on it is a defense that has to be red-teamed like any other, not trusted because it arrived with a mechanism attached.

# Does the Fix Survive?

The uncomfortable question for any interpretability-based fix is whether it deleted the behavior or merely hid it. Behavioral evidence cannot tell the two apart, and this is not hypothetical. Unlearning methods that report a capability removed, evaluated the standard way on benchmarks like WMDP ([Li et al. 2024](https://arxiv.org/abs/2403.03218)), can often have that capability restored with a small amount of fine-tuning, sometimes on the order of a dozen or so steps ([Che et al. 2025](https://arxiv.org/abs/2502.05209)). The knowledge was suppressed, not deleted. A steering vector that re-asserts a security signal is on firmer ground than an unlearning claim, because it is an additive intervention with an explicit mechanism rather than a claim of absence, but the general caution stands: an intervention that looks perfect on the cases that motivated it can be evaded, drift, or fail to compose with the next one.

So the interventions in this post need the same treatment I would demand of any defense. Test them against adaptive inputs, not only the cases that inspired them. Report where they fail, not just where they hold. Localization can be partial, and not every unsafe behavior will be as cleanly single-layer as the Format-Reliability Gap turned out to be. Interpretability makes the fix cheaper and the diagnosis sharper; it does not exempt the result from being red-teamed.

# Where This Goes

The framing I keep coming back to is a loop, and it is the same loop whether the target is insecure code, a jailbreak, or a backdoor. Measure the failure empirically, the way [Lost at C](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval) measured insecure code in a controlled study. Locate it inside the model with interpretability, at the coarsest grain that separates it from what you want to keep. Intervene at the source, with a probe that reads or a vector that writes. Then measure again, in the same coordinates, and check the fix against an adversary rather than against the motivating example. Each stage feeds the next, and the interpretability stage is the one that turns "the model is unsafe" into "here is the component responsible, and here is a cheap fix I can verify."

![](/images/mech-interp/fig7-loop.svg)
*Fig. 7. The loop interpretability closes: measure a failure, locate it, intervene at the source, re-measure against an adversary, and feed the result back. (Diagram by the author)*

The near-term future of this is monitoring in production, where cheap probes gate expensive interventions on live traffic, and the longer-term future pushes the same question earlier, into pretraining, where the most durable interventions seem to live. But the core claim is small and I want to keep it small: interpretability is not only a microscope for understanding models in principle. Pointed at a located failure, it is a wrench.

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

[1] Templeton, Conerly, Marcus, et al. ["Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet"](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html). Transformer Circuits (2024).

[2] Sandoval et al. ["Surgical Repair of Insecure Code Generation in LLMs: From Mechanistic Diagnosis to Deployment-Ready Intervention"](https://arxiv.org/abs/2604.16697). arXiv preprint arXiv:2604.16697 (2026).

[3] Turner, Thiergart, Udell, et al. ["Activation Addition: Steering Language Models Without Optimization"](https://arxiv.org/abs/2308.10248). arXiv preprint arXiv:2308.10248 (2023).

[4] Zou, Phan, Chen, et al. ["Representation Engineering: A Top-Down Approach to AI Transparency"](https://arxiv.org/abs/2310.01405). arXiv preprint arXiv:2310.01405 (2023).

[5] Arditi, Obeso, Syed, et al. ["Refusal in Language Models Is Mediated by a Single Direction"](https://arxiv.org/abs/2406.11717). NeurIPS 2024.

[6] Bricken, Templeton, Batson, et al. ["Towards Monosemanticity: Decomposing Language Models With Dictionary Learning"](https://transformer-circuits.pub/2023/monosemantic-features/index.html). Transformer Circuits (2023).

[7] Wang, Variengien, Conmy, Shlegeris, and Steinhardt. ["Interpretability in the Wild: a Circuit for Indirect Object Identification in GPT-2 small"](https://arxiv.org/abs/2211.00593). ICLR 2023.

[8] MacDiarmid, Maxwell, Schiefer, et al. ["Simple probes can catch sleeper agents"](https://www.anthropic.com/research/probes-catch-sleeper-agents). Anthropic (2024).

[9] Sandoval, Fenchenko, Pearce, et al. ["Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants"](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval). USENIX Security 2023.

[10] He and Vechev. ["Large Language Models for Code: Security Hardening and Adversarial Testing"](https://arxiv.org/abs/2302.05319). ACM CCS 2023.

[11] Tan, Chanin, Lynch, et al. ["Analyzing the Generalization and Reliability of Steering Vectors"](https://arxiv.org/abs/2407.12404). NeurIPS 2024.

[12] Kantamneni, Engels, Rajamanoharan, Tegmark, and Nanda. ["Are Sparse Autoencoders Useful? A Case Study in Sparse Probing"](https://arxiv.org/abs/2502.16681). arXiv preprint arXiv:2502.16681 (2025).

[13] Joad, Hawasly, Boughorbel, Durrani, and Sencar. ["There Is More to Refusal in Large Language Models than a Single Direction"](https://arxiv.org/abs/2602.02132). arXiv preprint arXiv:2602.02132 (2026).

[14] Hewitt and Liang. ["Designing and Interpreting Probes with Control Tasks"](https://arxiv.org/abs/1909.03368). EMNLP 2019.

[15] Li, Pan, Lin, et al. ["The WMDP Benchmark: Measuring and Reducing Malicious Use With Unlearning"](https://arxiv.org/abs/2403.03218). ICML 2024.

[16] Che, Casper, Kirk, et al. ["Model Tampering Attacks Enable More Rigorous Evaluations of LLM Capabilities"](https://arxiv.org/abs/2502.05209). arXiv preprint arXiv:2502.05209 (2025).
