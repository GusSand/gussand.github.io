---
title: 'Red-Teaming Language Models, Part 2: What Holds on Defense, and Open Weights'
description: 'Part 2: the defenses that survive a determined adversary, why layered safeguards can be peeled apart one at a time, and how the entire red-teaming order inverts once you ship open weights.'
date: 2026-07-29
permalink: /posts/2026/07/red-teaming-language-models-defense-open-weights/
tags:
  - Security
  - LLM
  - Red Teaming
  - Evaluation
  - Jailbreak
  - Open Weights
---

Date: July 29, 2026 \| Estimated Reading Time: 16 min \| Author: Gustavo Sandoval

This is Part 2 of two. [Part 1](/posts/2026/07/red-teaming-language-models/) covered the converged red-teaming process, how attacks are actually built, and why reported attack success rates are so often not comparable across papers. Here I take up the two questions that matter once you have a process and can measure it: which defenses actually hold against a determined adversary, and how the whole order of operations inverts when you ship the weights instead of an API.

One point from Part 1 carries everything below: an attack success rate is a property of the adversary you chose, not of the model alone. It is worth keeping in view.

{% include reading-outline.html %}

<details markdown="1" open>
<summary><strong>Table of Contents</strong></summary>

- [&larr; Part 1: Process and Measurement](/posts/2026/07/red-teaming-language-models/)
- [What Holds on Defense](#what-holds-on-defense)
  - [The Strong Positive Result](#the-strong-positive-result)
  - [Attacking the Pipeline, Not the Model](#attacking-the-pipeline-not-the-model)
  - [The Strong Negative Result](#the-strong-negative-result)
  - [Agents Are the Current Worst Case](#agents-are-the-current-worst-case)
- [Open Weights Changes the Order](#open-weights-changes-the-order)
  - [Measuring Any of This Is Its Own Problem](#measuring-any-of-this-is-its-own-problem)
  - [Moving the Intervention Into Pretraining](#moving-the-intervention-into-pretraining)
  - [Or Put the Capability in a Detachable Part](#or-put-the-capability-in-a-detachable-part)
  - [A Priority List](#a-priority-list)
- [Access, Disclosure, Governance](#access-disclosure-governance)
- [Open Problems](#open-problems)
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

# Open Weights Changes the Order

Everything above assumes you control the inference path. If you ship weights, you do not, and the standard process needs reordering.

![](/images/red-teaming/fig6-open-weights-cut.svg)
*Fig. 5. Where a safeguard lives determines whether it survives release: deployment-layer defenses are never shipped and post-training alignment is cheap to strip, so only what is baked in during pretraining crosses the line intact. (Diagram by the author; costs from [Zhan et al. 2023](https://arxiv.org/abs/2311.05553), [Lermen et al. 2023](https://arxiv.org/abs/2310.20624), [Qi et al. 2024](https://arxiv.org/abs/2310.03693) and [Bhardwaj & Poria 2023](https://arxiv.org/abs/2310.14303))*

The organizing insight is that once weights ship, the entire refusal layer is a soft target and every deployment-layer defense is optional for the adversary. Constitutional Classifiers works because Anthropic controls the inference path. An open-weights team does not.

The corollary reorders the standard process: **red teaming your aligned checkpoint characterizes a configuration no adversary will use.** Four independent results price the removal of alignment, and the prices are not serious money.

| Work | Target | Attacker budget | Result |
|---|---|---|---|
| [Qi et al. 2024](https://arxiv.org/abs/2310.03693) | GPT-3.5 Turbo | 10 examples, under $0.20 via the fine-tuning API | Guardrails jailbroken; responsive to nearly any harmful instruction |
| [Bhardwaj & Poria 2023](https://arxiv.org/abs/2310.14303) | ChatGPT, open models | 100 samples | 88% attack success on ChatGPT, over 91% on open models |
| [Lermen et al. 2023](https://arxiv.org/abs/2310.20624) | Llama 2-Chat 70B | LoRA on one GPU, under $200 | About 1% refusal across two benchmarks |
| [Zhan et al. 2023](https://arxiv.org/abs/2311.05553) | GPT-4 | 340 examples, under $245 | RLHF protections removed, up to 95% success |

Qi et al. add the finding that should worry anyone operating a fine-tuning API rather than attacking one: the same degradation shows up after fine-tuning on entirely *benign* instruction data, with no adversarial intent anywhere in the pipeline. Any red-team result against the aligned checkpoint has a shelf life of roughly one afternoon of attacker GPU time.

What follows is that white-box red teaming that stops short of fine-tuning studies a weaker adversary than the real one ([Wang et al. 2025](https://arxiv.org/abs/2506.05376)). For open weights, "adaptive" must include a fine-tuning arm, not just prompt-space search.

The same problem hits labs that ship nothing but a guard. The transfer half of the staged attack [above](#attacking-the-pipeline-not-the-model) trained against a proxy pipeline built from open-weight safeguard models, then worked a third of the time on a target it had never queried. Publishing a safeguard model hands every attacker a differentiable stand-in for your defense, which is why that paper recommends keeping safeguards closed or trained on non-public data. The argument is sound and points the wrong way for a field that depends on open artifacts (ShieldGemma, Llama Guard) to reproduce anything, and I don't think anyone has a good answer yet.

## Measuring Any of This Is Its Own Problem

Before the interventions, the instruments, because the evaluation methodology here is in worse shape than the defenses are. Qi, Wei, Carlini, and colleagues make the case directly: evaluating durable safeguards is *itself* exceedingly difficult, and standard evaluations mislead readers into thinking safeguards are more durable than they are ([Qi, Wei, Carlini, et al. 2024](https://arxiv.org/abs/2412.07097)). Cabin claims to constrained threat models rather than stating general resistance. If you read one thing before designing an open-weights evaluation, read that one.

Three concrete instruments have arrived since. **Model tampering attacks**, which modify latents or weights rather than only inputs, empirically predict and conservatively bound the success of held-out input-space attacks, which makes them a strictly better evaluation primitive for open weights ([Che et al. 2025](https://arxiv.org/abs/2502.05209)); the same paper finds state-of-the-art unlearning undone within 16 steps of fine-tuning. **The Safety Gap Toolkit** measures the gap between a model with safeguards intact and the same model stripped, across Llama-3 and Qwen-2.5 from 0.5B to 405B, and the gap *widens* with scale ([Dombrowski et al. 2025](https://arxiv.org/abs/2507.11544)): the problem gets worse exactly as your model gets more useful. **TamperBench** standardizes the comparison across 21 open-weight models and nine tampering threats, and finds jailbreak-tuning the most severe of the set ([Hossain et al. 2026](https://arxiv.org/abs/2602.06911)). The durability literature has been uncomparable across papers for two years; this is what fixes it.

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-safety-gap-scaling.jpg" width="650" height="472" alt="Effective dangerous capabilities versus model size, with the original model flat near zero and the harmful fine-tune rising with scale, the shaded area between them labeled the safety gap" style="width:100%;max-width:650px;height:auto;display:block;margin:0 auto" /></div>

*Fig. 6. The safety gap: the released model's dangerous capability (black) stays under 0.15 at every scale, but a 51-sample harmful fine-tune (teal) rises from 0.33 at 1B to 0.69 at 405B. The shaded area is risk no evaluation of the released checkpoint can see. (Image source: [Dombrowski et al. 2025](https://arxiv.org/abs/2507.11544))*

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-safety-gap-compliance-vs-accuracy.jpg" width="616" height="592" alt="Accuracy versus compliance rate for Llama models from 1B to 405B, showing fine-tuned and refusal-ablated variants moving to high compliance with almost no accuracy loss" style="width:100%;max-width:616px;height:auto;display:block;margin:0 auto" /></div>

*Fig. 7. Fine-tuning on 50 benign or 51 harmful examples, or ablating the refusal direction (orange), pushes compliance from near 0 toward 1.0 while accuracy stays within a point or two: no trade-off for the attacker to manage. (Image source: [Dombrowski et al. 2025](https://arxiv.org/abs/2507.11544))*

## Moving the Intervention Into Pretraining

The strongest 2025 result on this is Deep Ignorance, which filters dual-use content out of the *pretraining* data rather than removing capability afterwards ([O'Brien et al. 2025](https://arxiv.org/abs/2508.06601)).

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-deep-ignorance-tamper.jpg" width="1021" height="506" alt="General capability unchanged by filtering, and biothreat proxy capability staying below baseline under adversarial fine-tuning" style="width:100%;height:auto;display:block" /></div>

*Fig. 8. Left: filtering leaves general capability essentially unchanged. Right: under adversarial fine-tuning up to 300M tokens, filtered models (orange, blue) stay below the unfiltered baseline (grey) rather than converging to it. (Image source: [O'Brien et al. 2025](https://arxiv.org/abs/2508.06601))*

Filtered 6.9B models stay tamper-resistant up to 10,000 steps of adversarial fine-tuning on 305M tokens, over an order of magnitude better than the post-training baselines they ran, which were circuit breaking and circuit breaking plus latent adversarial training. They declined to run TAR ([Tamirisa et al. 2024](https://arxiv.org/abs/2408.00761)) on cost grounds, noting that the second baseline is algorithmically close to it. The filtering pipeline costs under 1% of total training FLOPs, with no observed degradation to unrelated capabilities. That combination is not available anywhere else in the literature.

Three caveats matter more than the headline. **Filtering yields ignorance, not safety**: filtered models still use the information when it is supplied in context, through search-tool augmentation or retrieval. Circuit-breaking does block in-context retrieval on its own, but no model in their study resisted the *combined* fine-tuning plus in-context-retrieval attack. **Filtering may not survive composition**: in a controlled synthetic medical world, models still compose benign facts into unsafe behavior they were never shown, and filtering hard enough to prevent it costs real general capability, 73.5% down to 53.9% in their setup ([Li et al. 2026](https://arxiv.org/abs/2606.19168)). **Neither stage is sufficient alone**: in that same work, pretraining-stage alignment on its own leaves a 91.5% prefill-attack success rate, post-training alone gets to 25.2%, and the two together reach 8.5%. Their conclusion is the one to take: pretraining alignment is not self-sufficient without matching post-training. Budget for both stages or neither.

The open question I find most interesting here: every existing tamper-resistance protocol is behavioral, so it cannot distinguish *verified deletion* from *elicitation difficulty*, whether the capability is gone or merely hard to reach. Deep Ignorance released 18 matched model artifacts expressly to enable that kind of causal study, and as far as I know nobody has run the mechanistic version yet.

I have a stake in this question. In our own unlearning work, a method reporting complete suppression of a target behavior could be substantially reverted with a few dozen samples, which is what you would expect if the knowledge were gated rather than removed. It is the same pattern I keep running into in code security, where a model can identify a vulnerability it just wrote. Che et al. report the same thing at benchmark scale, 16 fine-tuning steps to undo state-of-the-art unlearning, so this is not an artifact of our setup. Behavioral evidence of absence is weak evidence, and the whole tamper-resistance literature currently rests on it.

## Or Put the Capability in a Detachable Part

Filtering's weak point is labels. Deciding what counts as dual-use content is expensive at the scale of a pretraining corpus, and because larger models are more sample-efficient, a small fraction of mislabeled content can hand the capability back. Filter 99% of the virology and the remaining 1% may be enough.

A different line of work stops trying to keep the capability out and instead decides *where in the weights* it is allowed to live. Gradient routing uses data-dependent masks so that examples from a target domain only update a chosen subset of parameters, localizing the capability by construction so you can delete the subset afterwards ([Cloud et al. 2024](https://arxiv.org/abs/2410.04332)). Selective Gradient Masking sharpens this and tests behavior under label noise ([Shilov et al. 2025](https://arxiv.org/abs/2512.05648)). It beats data filtering on the retain/forget trade-off precisely when labels are wrong, and it needs seven times more fine-tuning steps than RMU-style unlearning to climb back to baseline on the forget set. The second number is the interesting one, because it is a tamper-resistance claim rather than a suppression claim.

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-sgtm-retain-forget.jpg" width="1091" height="558" alt="Two panels of forget loss on biology versus retain loss, with SGTM dominating strict filtering, weak filtering and no filtering, on general knowledge and on related knowledge" style="width:100%;height:auto;display:block" /></div>

*Fig. 9. The retain/forget trade-off with biology as the target capability; best curves sit top-left. SGTM (orange) dominates both filtering baselines, and holds most of its margin in the hard right-panel case where retain domains overlap the forget domain and mislabeled data concentrates. (Image source: [Shilov et al. 2025](https://arxiv.org/abs/2512.05648))*

The version that made me reconsider the release decision entirely is GRAM, from AE Studio with Anthropic ([Roland et al. 2026](https://arxiv.org/abs/2607.08077)). Each MLP block gets small auxiliary modules, one per sensitive domain. There is no learned router and no per-token routing; gradient routing sends updates to modules according to the data label, so the core weights carry general knowledge and each auxiliary module carries one capability. Delete a module at inference and that capability goes with it.

The results are stronger than I expected from a first paper. A single training run approximates a whole family of separately filtered models: at 26M parameters it matched five individually filtered models, and at 800M it gave capability removal comparable to filtering across virology, cybersecurity, nuclear physics, and specialized code, at a fifth of the training compute, since filtering has to pay for a separate run per capability profile. It holds from 50M to 5B parameters, with isolation getting *better* as models grow. Modules compose, sixteen configurations from four modules, where stacking LoRA adapters degraded. And with half the training data left unlabeled it beat both filtering and LoRA, which is the realistic setting given that labeling was the original problem.

The number I would look at first, though, is the rightmost group below.

<div style="background:#fff;padding:10px;border-radius:8px;margin:1.2em 0"><img src="/images/red-teaming/paper-gram-elicited-forget.png" width="1450" height="300" alt="Bar chart comparing filtering, GRAM, FT-LoRA, FT-Full and MaxEnt on core, retain, forget and elicited-forget compute ratio" style="width:100%;height:auto;display:block" /></div>

*Fig. 10. Five ways to remove a capability from an 800M model (lower Forget and Elicit is better; Elicit is Forget re-measured after adversarial fine-tuning). MaxEnt has the best Forget at 0.46 but the worst Elicit at 0.91, the capability comes back; GRAM goes 0.54 to 0.63, tracking data filtering's 0.53 to 0.58. (Image source: [Roland et al. 2026](https://arxiv.org/abs/2607.08077))*

This matters beyond the efficiency win. Every release decision in this post has been binary: ship the weights or do not. Modular pretraining makes "ship the model without the virology module" a coherent thing to do, and nearly free once you have trained once. The most consequential and least reversible step in the pipeline gets intermediate settings.

I would not oversell it, and neither do the authors: it is preliminary, clean separation may be impossible when a target capability overlaps a desired one, the scaling trends were verified only to 5B, and they cannot yet say *why* GRAM composes more reliably than stacked LoRA. My own reservation is narrower. The elicited-forget numbers above are real evidence the capability does not come back easily, but they come from fine-tuning on 512 sequences, roughly half a million tokens, where Deep Ignorance's comparable claim was tested to 305M, three orders of magnitude more. What has been shown is that a detachable capability resists a *brief* attack about as well as filtering does, which is encouraging and is not the same as tamper resistance.

The framing I have found most useful for organizing all of this is Siddiqui and colleagues' argument that **capability control is a separate goal from alignment** ([Siddiqui et al. 2026](https://arxiv.org/abs/2602.05164)). Alignment is preference-driven and context-dependent; capability control is about hard operational limits that hold under adversarial elicitation. They sort the mechanisms into three layers, data, learning, and system, note that each fails characteristically when used alone, and land on defense in depth across the stack. Their listed open challenges are the same two that keep appearing in this post: knowledge is dual-use, and capabilities recombine compositionally.

Two adjacent papers need the inference path you lose on release, so they are the right idea in the wrong threat model for open weights but directly usable if you host: least-privilege language models, which shrink the model's reachable internal computation with a rank-indexed knob ([Rauba et al. 2026](https://arxiv.org/abs/2601.23157)), and a position paper recasting the dual-use dilemma as an authorization problem ([Wybitul 2025](https://arxiv.org/abs/2505.09341)).

**The answer keeps being in pretraining.** Filter the data, or route the gradients, or both. Every intervention in this section that survives contact with someone who has your weights is one you made before training finished; everything added afterwards is either cheap to strip or optional for the adversary. I would not defend that as a law, and Li et al.'s compositional-reconstruction result is a real crack in it, but nothing in the current literature contradicts it, and it is a better planning heuristic than the order most teams work in.

## A Priority List

The ordering is mine; the individual items are claims other people have made, and each points at its source.

The first three have since been formalized. Paskov, Rodriguez, Dev, and Casper propose four *proportional evaluation* requirements and review every open-weight family released between 2025 and April 2026: of 37, exactly one satisfies all four, and most satisfy none ([Paskov et al. 2026](https://arxiv.org/abs/2606.19890)). Almost nobody is doing this.

If you are building an open-weights model, in order:

1. **Re-baseline the threat model on a fine-tuning adversary,** not a gradient-suffix one; every other priority follows ([Wang et al. 2025](https://arxiv.org/abs/2506.05376); [Che et al. 2025](https://arxiv.org/abs/2502.05209)).
2. **Run dangerous-capability evaluations on the base model, before alignment.** Refusal is removable, so what matters at release is what the base model knows. The [Safety Gap Toolkit](https://arxiv.org/abs/2507.11544) is the instrument.
3. **Measure marginal uplift, not absolute harm:** what your model adds over what is already openly available, which most risk assessments do not measure ([Kapoor et al. 2024](https://arxiv.org/abs/2403.07918)).
4. **Treat the release decision as the top-level control and document it,** including the dissent. It is the only irreversible step. Anthropic faced the adjacent problem in 2022 and, with no community norms to appeal to, made the call in a vacuum ([Ganguli et al. 2022](https://arxiv.org/abs/2209.07858)).
5. **Move the intervention into pretraining,** filtering data ([O'Brien et al. 2025](https://arxiv.org/abs/2508.06601)) or routing gradients so the capability is detachable ([Roland et al. 2026](https://arxiv.org/abs/2607.08077)), the only idea that gives item 4 graded options.
6. **Do the cheap, demonstrated adversarial training.** R2D2 took a Zephyr-recipe model to 5.9% GCG attack success in 16 GPU-hours, against 30%+ for the Llama 2 chat models ([Mazeika et al. 2024](https://arxiv.org/abs/2402.04249)).
7. **Build and validate the judge before scaling attacks.** Hand-label a few hundred completions, then automate; this is where most teams waste the most money.
8. **Red team adaptively, or not at all,** with a fine-tuning arm ([Nasr et al. 2025](https://arxiv.org/abs/2510.09023)).
9. **Publish the eval suite and attack data with a datasheet,** so downstream fine-tuners can tell whether their derivative is worse than the original ([Qi, Wei, Carlini, et al. 2024](https://arxiv.org/abs/2412.07097); [Hossain et al. 2026](https://arxiv.org/abs/2602.06911)).
10. **Ship reference deployment-layer guardrails you cannot enforce,** with a documented benign false-positive rate, and say in the model card that model-level and system-level safety are different claims.

If you only do three: base-model capability evaluation before alignment, judge validation before attack scaling, and a real coordinated-disclosure policy.

# Access, Disclosure, Governance

Three things belong in any program that accepts external findings. A legal and technical **safe harbor**, since accounts have been suspended mid-research without appeal and the good-faith call should not be the company's alone ([Longpre et al. 2024](https://arxiv.org/abs/2403.04893)). A **standardized flaw report** carrying reporter identity, system versions, a reproducibility session ID, the policy mapping, and statistical validity metrics ([Longpre et al. 2025](https://arxiv.org/abs/2503.16861)). And **disclosure coordination**, because flaws transfer across providers, so single-vendor disclosure leaves correlated vulnerabilities unaddressed elsewhere. One idea worth copying from cyber: treat unpatchable AI vulnerabilities as **classes** (like CWE) with implementations as **instances** (like CVE) ([Sinha et al. 2025](https://arxiv.org/abs/2509.11398)).

# Open Problems

**Agentic and environment-level red teaming has no published methodology.** Scale AI calls for investment in sandboxes and real environments of the kind capability research already builds: modeling world state (saving a password is safe on a personal machine, not on a public one), classifying harm at the trajectory level rather than the response level, monitoring the user rather than only the output, and red-teaming the monitor itself. Nobody has published a worked methodology, and agents are already the empirical worst case, so this is the largest process-level hole in the field.

**Prompt difficulty is uncalibrated across risk categories.** Cross-category attack success comparison is currently close to meaningless, because differences reflect how hard the prompts happen to be rather than differential susceptibility. It is the equivalent of comparing scores on a novice test and a graduate test and concluding something about the students.

**Marginal uplift measurement is ad hoc.** Ten minutes of web search per behavior is the only concrete instrument in the corpus, and it is a rough proxy. Open-weights release decisions currently hinge on a quantity nobody measures rigorously.

**Evaluator reliability is a mechanistic interpretability target, and nobody is treating it as one.** Rule-based detectors fail on one-character mismatches and on negation. LLM judges fail on rubric misreading and are themselves attackable. Both failure classes look representational to me: the judge encodes the right distinction and fails to act on it. Whether an activation probe read off a judge's internals could outperform the judge's own output head is, as far as I can tell, untested, and it is cheap to try.

A closing note on shelf life. The two most decision-relevant papers cited here are both from 2026, and the strongest defensive result and its strongest counterattack were published within months of each other. Verdicts in this area go stale in about a month. Re-check before you rely on any of it, including this.

# Citation

Cited as:
> Sandoval, Gustavo. (Jul 2026). "Red-Teaming Language Models, Part 2: What Holds on Defense, and Open Weights". https://gussand.github.io/posts/2026/07/red-teaming-language-models-defense-open-weights/.

Or

```
@article{sandoval2026redteaming2,
  title   = "Red-Teaming Language Models, Part 2: What Holds on Defense, and Open Weights",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jul",
  url     = "https://gussand.github.io/posts/2026/07/red-teaming-language-models-defense-open-weights/"
}
```

# References

[1] Ganguli et al. ["Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned"](https://arxiv.org/abs/2209.07858). arXiv preprint arXiv:2209.07858 (2022).

[2] Mazeika et al. ["HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal"](https://arxiv.org/abs/2402.04249). ICML 2024.

[3] Sharma et al. ["Constitutional Classifiers: Defending against Universal Jailbreaks across Thousands of Hours of Red Teaming"](https://arxiv.org/abs/2501.18837). arXiv preprint arXiv:2501.18837 (2025).

[4] Cunningham et al. ["Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks"](https://arxiv.org/abs/2601.04603). arXiv preprint arXiv:2601.04603 (2026).

[5] Sel et al. ["Trojan-Speak: Bypassing Constitutional Classifiers with No Jailbreak Tax via Adversarial Finetuning"](https://arxiv.org/abs/2603.29038). arXiv preprint arXiv:2603.29038 (2026).

[6] McKenzie, Hollinsworth, Tseng, Davies, Casper, Tucker, Kirk, and Gleave. ["STACK: Adversarial Attacks on LLM Safeguard Pipelines"](https://arxiv.org/abs/2506.24068). arXiv preprint arXiv:2506.24068 (2025).

[7] Davies, Giglemiani, Lau, Winsor, Irving, and Gal. ["Boundary Point Jailbreaking of Black-Box LLMs"](https://arxiv.org/abs/2602.15001). arXiv preprint arXiv:2602.15001 (2026).

[8] Nasr, Carlini, Sitawarin, et al. ["The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections"](https://arxiv.org/abs/2510.09023). arXiv preprint arXiv:2510.09023 (2025).

[9] Zizzo et al. ["Adversarial Prompt Evaluation: Systematic Benchmarking of Guardrails Against Prompt Input Attacks on LLMs"](https://arxiv.org/abs/2502.15427). arXiv preprint arXiv:2502.15427 (2025).

[10] Zou et al. ["Security Challenges in AI Agent Deployment: Insights from a Large Scale Public Competition"](https://arxiv.org/abs/2507.20526). arXiv preprint arXiv:2507.20526 (2025).

[11] Wang, Knight, Kritz, Primack, and Michael. ["A Red Teaming Roadmap Towards System-Level Safety"](https://arxiv.org/abs/2506.05376). arXiv preprint arXiv:2506.05376 (2025).

[12] Longpre, Kapoor, Klyman, et al. ["A Safe Harbor for AI Evaluation and Red Teaming"](https://arxiv.org/abs/2403.04893). ICML 2024.

[13] Longpre, Klyman, Appel, et al. ["In-House Evaluation Is Not Enough: Towards Robust Third-Party Flaw Disclosure for General-Purpose AI"](https://arxiv.org/abs/2503.16861). arXiv preprint arXiv:2503.16861 (2025).

[14] Sinha et al. ["From Firewalls to Frontiers: AI Red-Teaming is a Domain-Specific Evolution of Cyber Red-Teaming"](https://arxiv.org/abs/2509.11398). arXiv preprint arXiv:2509.11398 (2025).

[15] O'Brien, Casper, Anthony, et al. ["Deep Ignorance: Filtering Pretraining Data Builds Tamper-Resistant Safeguards into Open-Weight LLMs"](https://arxiv.org/abs/2508.06601). arXiv preprint arXiv:2508.06601 (2025).

[16] Li, Tang, Xu, Ye, and Lyu. ["Beyond Safe Data: Pretraining-Stage Alignment with Regular Safety Reflection"](https://arxiv.org/abs/2606.19168). arXiv preprint arXiv:2606.19168 (2026).

[17] Zhan, Fang, Bindu, et al. ["Removing RLHF Protections in GPT-4 via Fine-Tuning"](https://arxiv.org/abs/2311.05553). NAACL 2024.

[18] Lermen, Rogers-Smith, and Ladish. ["LoRA Fine-tuning Efficiently Undoes Safety Training in Llama 2-Chat 70B"](https://arxiv.org/abs/2310.20624). arXiv preprint arXiv:2310.20624 (2023).

[19] Qi, Zeng, Xie, et al. ["Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!"](https://arxiv.org/abs/2310.03693). ICLR 2024.

[20] Bhardwaj and Poria. ["Language Model Unalignment: Parametric Red-Teaming to Expose Hidden Harms and Biases"](https://arxiv.org/abs/2310.14303). arXiv preprint arXiv:2310.14303 (2023).

[21] Qi, Wei, Carlini, Huang, Xie, He, Jagielski, Nasr, Mittal, and Henderson. ["On Evaluating the Durability of Safeguards for Open-Weight LLMs"](https://arxiv.org/abs/2412.07097). ICLR 2025.

[22] Che, Casper, Kirk, Satheesh, Slocum, McKinney, et al. ["Model Tampering Attacks Enable More Rigorous Evaluations of LLM Capabilities"](https://arxiv.org/abs/2502.05209). arXiv preprint arXiv:2502.05209 (2025).

[23] Dombrowski, Bowen, Gleave, and Cundy. ["The Safety Gap Toolkit: Evaluating Hidden Dangers of Open-Source Models"](https://arxiv.org/abs/2507.11544). arXiv preprint arXiv:2507.11544 (2025).

[24] Hossain, Tseng, Pandey, Vajpayee, Kowal, Nonta, et al. ["TamperBench: Systematically Stress-Testing LLM Safety Under Fine-Tuning and Tampering"](https://arxiv.org/abs/2602.06911). arXiv preprint arXiv:2602.06911 (2026).

[25] Tamirisa, Bharathi, Phan, Zhou, Gatti, Suresh, et al. ["Tamper-Resistant Safeguards for Open-Weight LLMs"](https://arxiv.org/abs/2408.00761). ICLR 2025.

[26] Kapoor, Bommasani, Klyman, Longpre, Ramaswami, Cihon, et al. ["On the Societal Impact of Open Foundation Models"](https://arxiv.org/abs/2403.07918). ICML 2024.

[27] Paskov, Rodriguez, Dev, and Casper. ["Open Weight AI Models Require Proportional Evaluation Approaches"](https://arxiv.org/abs/2606.19890). arXiv preprint arXiv:2606.19890 (2026).

[28] Cloud, Goldman-Wetzler, Wybitul, Miller, and Turner. ["Gradient Routing: Masking Gradients to Localize Computation in Neural Networks"](https://arxiv.org/abs/2410.04332). arXiv preprint arXiv:2410.04332 (2024).

[29] Shilov, Cloud, Gema, Goldman-Wetzler, Panickssery, Sleight, et al. ["Beyond Data Filtering: Knowledge Localization for Capability Removal in LLMs"](https://arxiv.org/abs/2512.05648). arXiv preprint arXiv:2512.05648 (2025).

[30] Roland, Cubuktepe, Martinez, Servaes, Pepper, Vaiana, de Lucena, Rosenblatt, Foote, Anil, and Cloud. ["Modular Pretraining Enables Access Control"](https://arxiv.org/abs/2607.08077). arXiv preprint arXiv:2607.08077 (2026).

[31] Siddiqui, Triantafillou, Krueger, and Weller. ["Position: Capability Control Should be a Separate Goal From Alignment"](https://arxiv.org/abs/2602.05164). arXiv preprint arXiv:2602.05164 (2026).

[32] Rauba, Seputis, Vanagas, and van der Schaar. ["No More, No Less: Least-Privilege Language Models"](https://arxiv.org/abs/2601.23157). arXiv preprint arXiv:2601.23157 (2026).

[33] Wybitul. ["Access Controls Will Solve the Dual-Use Dilemma"](https://arxiv.org/abs/2505.09341). arXiv preprint arXiv:2505.09341 (2025).
