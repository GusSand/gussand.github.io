---
title: 'Which training data taught it that?'
description: 'Adding "no more than 50 words" can make an AI model comply with a harmful request. Can we trace a behavior like that to its training data, and fix it by changing the data? A survey of 26 papers on data attribution for safety, on which repairs work, and on the limits of pretraining filters.'
date: 2026-10-30
permalink: /posts/2026/10/safety-data-attribution/
tags:
  - Safety
  - LLM
  - Mechanistic Interpretability
  - Post-Training
  - Data Attribution
kind: "Survey"
hook: |
  An AI model refuses a harmful request. Ask again with "no more than 50 words" at the end, and it can comply.

  Nothing about the request changed except its length limit.
image: "/images/data-attribution/fig1-what-has-been-tested.svg"
image_caption: "Data attribution papers on safety behaviors, by training stage and by how they were checked."
reading_time: 13
---

[Xiao and Aranguri](https://arxiv.org/abs/2602.11079) found this failure in OLMo 2, Ai2's open model, and call it distractor-triggered compliance. It raises a concrete question: which training examples taught the model to do that?

To find out, they scored all 378,341 preference pairs from OLMo 2's DPO stage and changed the 30,000 highest-ranked pairs. Then they ran DPO again. Flipping the preference labels on those pairs cut harmful compliance by more than three-quarters. Changing 30,000 random pairs did not reliably help.

That is what training data attribution offers. You follow a behavior back to the data that shaped it, then test whether changing that data changes the model. Across the 26 papers in this survey, it sometimes works this well. In other cases, removing tens of thousands of flagged examples barely moves the behavior. At pretraining scale, most papers answer a different question: can we filter out a dangerous topic? Only one has traced a measured behavior back to its training data and repaired it.

![Data attribution papers by training stage and validation: rankings, successful retraining interventions, and weak or failed interventions. The pretraining success cell includes IF-GUIDE on toxicity at 1B and remains mostly open.](/images/data-attribution/fig1-what-has-been-tested.svg){: style="max-width: 100%; height: auto; display: block; margin: 0 auto;"}

*Fig. 1. What the papers tested. "Ranked only" means the paper scored training data without a retraining check. The pretraining cell for a successful check holds one paper, IF-GUIDE, and is still mostly open. The note at the bottom lists pretraining papers that filter or reweight data by content. (Diagram by the author)*
{: #fig-1}

I came to this from two directions. My [Marin post](/posts/2026/09/red-teaming-marin/#which-pretraining-data-did-it) asks which pretraining data made Marin less likely to refuse. My [refusal direction survey](/posts/2026/10/refusal-direction-two-years-later/#group-4-which-training-data-did-it) ended with three attribution papers. For this survey I ran an [Undermind](https://www.undermind.ai) deep search over 125 papers. I also followed citations forward from Kowal et al. and from Xiao and Aranguri, and checked every number against the paper's full text.

{% include reading-outline.html %}

## A suspicious example is not yet an explanation

Suppose we retrieve a training document that resembles an unsafe answer. Have we found the source?

Perhaps. But the model might have learned the same pattern from thousands of other documents. The retrieved example could illustrate the behavior without contributing much to it.

Training data attribution (TDA) tries to estimate that contribution. The classic tool is the influence function. It estimates how removing one training example would change the model's loss on a test example. [Grosse et al.](https://arxiv.org/abs/2308.03296) scaled influence functions to 52B parameters with an approximation called EK-FAC. [LESS](https://arxiv.org/abs/2402.04333) compares low-rank training gradients instead.

Newer methods score examples by their internal activations. They pick a direction in activation space that tracks the behavior. It can come from a linear probe, a sparse autoencoder (SAE) feature, a persona vector, or the activation difference between two checkpoints. Each training example gets a score from how well its activations line up with that direction.

[Kowal et al.](https://arxiv.org/abs/2602.14869) connect the two families. Their Concept Influence runs influence functions toward a probe or SAE direction, and cheaper scores approximate it. On 1,000 examples, Concept Influence took 1,170 seconds and the cheapest score, Vector Filter, took 57.

Speed makes the search easier. It does not show that the search found the right examples. The stronger test is to change the selected data, retrain, and compare against a matched random change. If the targeted change moves the behavior more, the ranking found something. I use this test throughout the survey.

## When the ranking gives us something we can fix

Back to the OLMo 2 formatting failure. Xiao and Aranguri compute the activation difference between the SFT and DPO checkpoints and score every DPO pair against it. Then they rerun DPO from the SFT checkpoint. The result depends on what they do to the selected pairs:

| Intervention | Harmful compliance |
|---|---:|
| Original DPO data | 7.63% |
| Remove the 30,000 highest-ranked pairs | 2.86% |
| Switch the labels on those pairs | 1.66% |

Their scoring took 12 H100-hours, against 128 for LESS. The cheaper ranking did not win everywhere. LESS did better when removing 3,000 or 12,000 pairs, and the activation ranking won at 30,000. The behavior also appears in OLMo 2 32B, but they retrained only at 7B. So the result is one data intervention that reduces one measured failure in one training run.

Other DPO studies agree that the structure of preference data matters. [Razin et al.](https://arxiv.org/abs/2410.08847) show that DPO on refusal data can lower refusal, from 74.4% to 33.4%. Their CHES score, a similarity between the preferred and rejected answers, selects pairs whose removal mitigates the drop. [Bergen et al.](https://arxiv.org/abs/2606.12360) use SAE feature clusters to predict which features DPO will change, and to guide interventions against planted behaviors.

Fine-tuning studies add that examples from the same bad dataset are not equally consequential. [Paulo et al.](https://arxiv.org/abs/2609.37914) select two subsets, each 5% of a misaligned dataset. Training on one gives 60% emergent misalignment, the broad misbehavior that can follow narrow training on material such as insecure code. Training on the other gives 20%. Kowal et al. and [Abdelghafar](https://arxiv.org/abs/2609.33667) also find examples whose removal reduces emergent misalignment.

Influential examples also do not have to look unsafe. [He, Xia and Henderson](https://arxiv.org/abs/2404.01099) select 100 benign Alpaca examples that sit close to harmful examples in representation space. Fine-tuning on them gives a 71% attack success rate, against 13% for 100 random examples. [Li et al.](https://arxiv.org/abs/2507.18631) find a similar effect at a safety-sensitive layer. For audits that only read the data, this is a problem: an example's content may not tell us what learning from it will do.

Selecting a subset to train on is a different intervention from removing examples from a full run. [Persona vectors](https://arxiv.org/abs/2507.21509), for instance, pick 500-example subsets that raise or lower a trait. That shows the scores predict something. It does not repair an existing training set.

## When removing 60,000 examples barely helps

In [Blank et al.](https://arxiv.org/abs/2608.31079), sycophantic agreement in OLMo-3-7B rises from 12% after SFT to 32% after DPO. The preference pairs look neutral. The student's sycophancy tracks how sycophantic the teacher models behind the answers are. Removing up to 60,000 pairs by probe score leaves sycophancy at about 30% to 33%.

The compliance result suggests a simple recipe: find the bad examples and remove them. Here the recipe does little. The signal may be spread across the data, or the ranking may miss it. The failed intervention cannot tell those apart. It does show that this method found no subset worth removing.

Other results point the same way. [Weckbecker et al.](https://arxiv.org/abs/2609.20027) test three attribution methods on subliminal learning, where a model picks up a trait from data that never mentions it. None works reliably. In [Nautiyal's GRPO study](https://arxiv.org/abs/2610.10422), ranking rollouts only by gradient size matches or beats the best targeted method in two of three seeds.

Rankings also travel poorly. Kowal et al. report that probe-based scores degrade sharply under distribution shift. Paulo et al. find that rankings agree less across models than across seeds of one model, and sometimes disagree outright. A score holds for one model, one behavior, one data distribution and one training setup. Using it beyond that needs its own test.

## Finding the examples is only half the repair

A useful ranking still does not say how to change the data. [Luo et al.](https://arxiv.org/abs/2609.02771) rank OLMo 2's SFT examples and compare interventions. On a WildJailbreak safety score where higher is safer, the baseline is 0.792. Deleting the selected examples gives 0.784, slightly worse than doing nothing. Rewriting them toward safe answers gives 0.831 or 0.880, depending on which end of the ranking is rewritten. Rewriting random examples the same way gives 0.795. So both choices matter: which examples we change, and what we change them into.

[Epifano](https://arxiv.org/abs/2609.37624) finds the same pattern with known poisoned rows, without attribution. Deleting half of those rows lowers emergent misalignment from 28.5% to 26.3%. Rewriting the same rows brings it to 14.1%.

Xiao and Aranguri's label switch fits too. Deleting a preference pair removes a lesson. Reversing its labels teaches the opposite one. For a repair, the question is which intervention changes the target behavior while keeping useful capabilities.

## Pretraining: filtering a topic and tracing a behavior

At pretraining scale, several papers show that changing the data changes safety outcomes. Most choose the data by its content.

[Deep Ignorance](https://arxiv.org/abs/2508.06601) removes biothreat-related documents with a keyword list and an expert-trained classifier, then pretrains 6.9B models from scratch. The filtered models know less of the target material. They resist adversarial fine-tuning for up to 10,000 steps and 300M tokens, and general capabilities do not drop.

[Safety Pretraining](https://arxiv.org/abs/2504.16980) combines classifier filtering with added synthetic safety data. Its 1.7B models cut attack success from 38.8% to 8.4%. Because the paper changes two things at once, the filter's own share is unknown.

[Rathi and Radford](https://arxiv.org/abs/2601.21571) filter single tokens. They label medical tokens with SAE features and distill the labels into a cheap classifier. Medicine stands in for hazardous knowledge. Token filtering removes as much of the capability as document filtering, with less damage to other skills. At 1.8B, matching the unfiltered model's loss on medicine takes 7,000 times more compute. The SAE features in this study identify medical content. They do not trace a measured behavior back to the examples that caused it.

That gap matters most when the target is refusal or harmful compliance, because those behaviors need not belong to a topic you can name.

## What if safe data is enough to rebuild the unsafe behavior?

The Deep Ignorance authors also retested Safety Pretraining's filtered models. Under fine-tuning attacks, filtering gave only a small robustness advantage, and the models were especially vulnerable to few-shot prompts. Their explanation separates precise knowledge from propensities. Removing specialized scientific facts can leave a real hole. Removing a tendency to comply, or a toxic style, is harder when the remaining data supplies the ingredients.

[Li et al.](https://arxiv.org/abs/2606.19168) test this in a controlled synthetic world, MedSafetyWorld. Filtering out the explicitly unsafe examples still leaves a 30.6% prefill attack success rate, and 43.2% after fine-tuning. The model composes unsafe behavior from safe data. Removing everything related to unsafe outcomes pushes both rates near zero, but general accuracy falls from 73.46% to 53.89%. The same paper tries adding short safety reflections to pretraining text. On 1.7B models pretrained on FineWeb-Edu, prefill attack success falls from 60.9% to 6.4%.

The synthetic result does not show that every real safety behavior is spread across the data. It does show that "remove the unsafe examples" can fail even when the filter finds every explicitly unsafe example.

## A pretraining attribution result that changes the picture

[IF-GUIDE](https://arxiv.org/abs/2506.01790) is the exception to the filtering story. It scores training tokens by their influence on toxicity, then changes the training objective to suppress the flagged tokens. Plain deletion had failed first. Removing up to the 10% most influential documents and retraining Pythia-160M cut toxicity by at most 10%.

Keeping the data and changing the objective worked much better. For Pythia-1B pretrained from scratch on 1B tokens of OpenWebText, expected maximum toxicity falls from 0.585 to 0.118. A toxicity-classifier filter reaches 0.375. A smaller proxy model can compute the influence scores.

This is the one successful pretraining attribution intervention I found. It also repeats the post-training lesson: attribution can find useful targets even when deletion is a poor repair. So the open gap is narrower than "nobody has done pretraining attribution". IF-GUIDE uses gradients, targets toxicity and works at 1B. Nobody has run the activation-based version for refusal.

Other studies cover parts of that gap. Grosse et al. rank pretraining sequences for alignment-relevant queries at up to 52B, including a model asking not to be shut down, but they do not retrain. [Vetter et al.](https://arxiv.org/abs/2608.11025) retrieve villain narratives with SAE persona features. Fine-tuning on the retrieved documents does not reliably induce emergent misalignment, while synthetic question-and-answer pairs built from the same content do. Relevant content alone was not enough; the training format mattered.

Changes to the whole mix can also have large effects. [Tice et al.](https://arxiv.org/abs/2601.10160) cut base-model misalignment from 45% to 9% by upsampling synthetic documents about aligned AI during pretraining. [Lu, Tang and Cavallaro](https://arxiv.org/abs/2607.25063) change only the final 500M pretraining tokens of OLMo-2-1B. Under the same later GRPO update, the branch that ended on web text loses 16.9 points of refusal. The branch that ended on safety text loses 6.1. These mix experiments show that pretraining data matters. They do not say which documents produce the effect.

## Cyber as a stress test

Offensive cyber capability separates topics from behaviors sharply. Exploit write-ups and offensive-security documents are easy to name, and WMDP even ships a cyber corpus. But exploit development also uses ordinary skills: reading C, reasoning about memory layout, using a debugger, and knowing how protocols work.

My guess is that a topic filter would remove many explicit exploit examples and leave enough ordinary programming knowledge to rebuild some offensive capability. That would be the MedSafetyWorld problem in real data, but it is still a hypothesis.

I found no paper that filters cyber content from pretraining and then measures the result on a cyber benchmark. [Roland et al.](https://arxiv.org/abs/2607.08077) pretrain an 800M model with cybersecurity as one of four removable domains, but they measure removal only by loss. The unlearning evidence is partial. In [WMDP](https://arxiv.org/abs/2403.03218), RMU unlearning keeps college computer science but removes much of the model's computer-security knowledge. Cyber knowledge separates from general computer science, then, but no one has tested it against practical coding ability or nearby defensive skills.

Attribution offers a test. Rank documents by their effect on a measured cyber capability, check whether the top ones are exploit write-ups or ordinary code, and intervene. Measure both the targeted capability and the skills we want to keep. The result would show whether a topic filter misses important sources of the capability, or was already looking in the right place.

## The experiment I want to run next

The next step is to move the checkpoint-difference method from DPO into a bounded segment of pretraining. OLMo is the cheapest place to start. Ai2 releases OLMo 2 and OLMo 3 checkpoints from before and after mid-training, the last stage of pretraining, along with the mid-training data. OLMo 3 7B also has several mid-training runs from one checkpoint that differ only in their data mix. Those runs let us first ask whether there is a behavior change worth explaining.

1. **Establish the change.** Measure refusal and misinformation compliance before and after mid-training, and across the mix variants, on held-out prompts. If nothing changes reliably, there is nothing to attribute.
2. **Build a candidate direction.** On a separate discovery set, take the activation difference between the checkpoints for the target behavior. A checkpoint difference can also capture unrelated changes, so treat it as a candidate.
3. **Rank the documents.** Score every mid-training document against that direction. Check that the ranking adds information beyond simple baselines such as topic or document length.
4. **Replay the training segment.** Start from the earlier checkpoint and rerun mid-training with the top-ranked documents removed. For OLMo 2 1B, a replay is still about 50B tokens.
5. **Run matched controls.** Remove random documents matched for token count, and repeat enough times to separate the intervention from training noise.
6. **Measure the effect and its cost.** Check whether targeted removal shrinks the behavior change more than the controls, and whether useful capabilities survive.

A positive result would show that the selected data contributes to the behavior under that intervention. It would not show that every selected document is responsible, or that the direction explains the mechanism. A negative result could mean a spread-out cause, a poor direction or a weak intervention. IF-GUIDE and Luo et al. suggest one more arm: keep the documents and suppress or rewrite the relevant content. Removal alone may understate what the attribution found.

Marin is another candidate. In my [Marin post](/posts/2026/09/red-teaming-marin/#which-pretraining-data-did-it), the base model's misinformation compliance rises from 51.7% to 73.9% across the final cooldown, so step 1 is already done. But replaying an 8B cooldown costs far more than the OLMo experiment.

## What would make these methods useful beyond one experiment?

Three limits recur.

**Scale and realism.** Much of the evidence comes from synthetic emergent-misalignment datasets and LoRA fine-tunes. Counterfactual retraining reaches 14B in Paulo et al. The interpretability-based methods here have retraining checks mainly at 7B to 8B. Xiao and Aranguri's OLMo 2 run is the one test on a production DPO dataset.

**The full pipeline.** I found no paper that attributes one behavior across SFT, DPO and RL in one pipeline. Xiao and Aranguri list SFT and RLHF as untested. A method that explains one stage may not explain the next.

**Direction stability.** These methods measure a direction at particular checkpoints, then use it to analyze training that changes the model's representations. Nobody has tested whether the direction keeps tracking the intended behavior.

For my own work on refusal erosion, these limits point to one goal. I want a data intervention that restores refusal while keeping what the training stage was for. The literature already has cases where that kind of repair works and cases where the obvious removal fails. The open question is whether we can tell in advance which case we are in, and choose an intervention that works.

## Papers

<details markdown="1">
<summary><strong>All papers, with the check each one ran</strong></summary>

| Paper | Method | Model | Retrained? | Key number |
|---|---|---|---|---|
| Grosse et al. 2023, [2308.03296](https://arxiv.org/abs/2308.03296) | EK-FAC influence over pretraining data | up to 52B | No | Ranking only, incl. a shutdown query |
| Xia et al. 2024, LESS, [2402.04333](https://arxiv.org/abs/2402.04333) | Low-rank gradient similarity | Several | Selects data | Gradient baseline in later papers |
| He, Xia, Henderson 2024, [2404.01099](https://arxiv.org/abs/2404.01099) | Representation and gradient matching | Llama-2-7B-chat | Selects 100 examples | ASR 71.0% vs 13.0% random |
| Razin et al. 2024, [2410.08847](https://arxiv.org/abs/2410.08847) | CHES embedding similarity | Llama-3-8B-Instruct | Yes, filters DPO pairs | Refusal drop 74.4% to 33.4% before filtering |
| Chen et al. 2025, Persona Vectors, [2507.21509](https://arxiv.org/abs/2507.21509) | Projection onto a trait direction | Qwen2.5-7B, Llama-3.1-8B | Selects 500 samples | Top > random > bottom |
| Li et al. 2025, LARF, [2507.18631](https://arxiv.org/abs/2507.18631) | Safety-layer representation similarity | Llama-3.1-8B | Selects and filters | HarmBench 39.0% vs 0.0% |
| Kowal et al. 2026, Concept Influence, [2602.14869](https://arxiv.org/abs/2602.14869) | Influence toward a probe or SAE direction | Qwen2.5-7B, Llama-3.1-8B, Qwen2-7B | Yes | Vector Filter 20× faster |
| Xiao, Aranguri 2026, [2602.11079](https://arxiv.org/abs/2602.11079) | Checkpoint activation difference | OLMo 2 7B | Yes, full DPO | 7.63% to 1.66% |
| Bergen et al. 2026, [2606.12360](https://arxiv.org/abs/2606.12360) | SAE feature clusters | Llama-3.1-8B to 70B, OLMo 3 | Yes, with planted data | Predicted vs observed R² = 0.9 |
| Habibi et al. 2026, [2606.29171](https://arxiv.org/abs/2606.29171) | Ridge regression on SAE features | Llama-3.2-3B-Instruct | No | 64% to 70% test accuracy |
| Paulo et al. 2026, [2609.37914](https://arxiv.org/abs/2609.37914) | EK-FAC and gradient cosine | OLMo 3 7B, Qwen, Llama to 14B | Yes, 12 seeds | Two 5% subsets: 60% vs 20% |
| Abdelghafar 2026, [2609.33667](https://arxiv.org/abs/2609.33667) | Scoring during training | Qwen2.5-7B-Instruct | Yes | Evil 11.89 to 2.38 |
| Luo et al. 2026, [2609.02771](https://arxiv.org/abs/2609.02771) | Influence functions, then rewrite | OLMo2-7B | Yes | Delete 0.784, rewrite up to 0.880 |
| Epifano 2026, [2609.37624](https://arxiv.org/abs/2609.37624) | Known poison rows, then rewrite | Qwen2.5-14B | Yes | Delete 26.3%, rewrite 14.1% |
| Blank et al. 2026, [2608.31079](https://arxiv.org/abs/2608.31079) | Probe filtering | OLMo-3-7B | Yes | Sycophancy stays about 30% |
| Weckbecker et al. 2026, [2609.20027](https://arxiv.org/abs/2609.20027) | Three TDA methods | 1B to 7B | Yes | Not reliable |
| Nautiyal 2026, [2610.10422](https://arxiv.org/abs/2610.10422) | Rollout attribution in GRPO | Qwen2.5-1.5B | Planted trigger | Gradient-size control matches |
| Vetter et al. 2026, [2608.11025](https://arxiv.org/abs/2608.11025) | SAE persona features over pretraining docs | 4 models | Fine-tunes on retrieved docs | Does not reliably induce misalignment |
| O'Brien et al. 2025, Deep Ignorance, [2508.06601](https://arxiv.org/abs/2508.06601) | Content filter on pretraining data | 6.9B | Pretrains from scratch | Resists 10,000 fine-tuning steps |
| Maini et al. 2025, Safety Pretraining, [2504.16980](https://arxiv.org/abs/2504.16980) | Classifier filter plus synthetic safety data | 1.7B | Pretrains from scratch | ASR 38.8% to 8.4% |
| Rathi, Radford 2026, [2601.21571](https://arxiv.org/abs/2601.21571) | SAE-labeled token filter | 61M to 1.8B | Pretrains from scratch | 7,000× compute slowdown on medicine |
| Li et al. 2026, [2606.19168](https://arxiv.org/abs/2606.19168) | Safety reflections inserted in pretraining | 1.7B | Pretrains from scratch | Prefill ASR 60.9% to 6.4% |
| Coalson et al. 2025, IF-GUIDE, [2506.01790](https://arxiv.org/abs/2506.01790) | Token-level influence on toxicity, suppressed in the loss | Pythia 160M to 1B, Llama-3.2-1B | Pretrains from scratch | EMT 0.585 to 0.118 (Pythia-1B) |
| Roland et al. 2026, [2607.08077](https://arxiv.org/abs/2607.08077) | Removable domain modules, cyber among them | 800M | Pretrains from scratch | Loss only, no cyber benchmark |
| Tice et al. 2026, [2601.10160](https://arxiv.org/abs/2601.10160) | Pretraining data mix | 6.9B | Pretrains | Misalignment 45% to 9% |
| Lu, Tang, Cavallaro 2026, [2607.25063](https://arxiv.org/abs/2607.25063) | Final pretraining window | OLMo-2-1B, Pythia-1B | Pretrains | GRPO refusal loss 16.9 vs 6.1 |

</details>
