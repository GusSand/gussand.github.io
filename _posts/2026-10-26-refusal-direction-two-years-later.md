---
title: 'Refusal is one direction. Two years later, what did fine-tuning do to it?'
description: 'Delete one direction from a chat model and it stops refusing. Two years and 34 follow-up papers later: fine-tuning breaks refusal around the direction, the direction is only part of the story, and nobody has traced it through a full open training pipeline.'
date: 2026-10-26
permalink: /posts/2026/10/refusal-direction-two-years-later/
tags:
  - Safety
  - LLM
  - Mechanistic Interpretability
  - Post-Training
kind: "Survey"
image: "/images/refusal-direction/fig0-map-of-follow-ups.svg"
image_caption: "Follow-up papers to Arditi et al., grouped by the question they ask."
hook: |
  Delete one direction from a chat model's activations, and it stops refusing harmful requests.

  Add the same direction to a harmless prompt, and the model refuses that too.
reading_time: 9
---

In 2024 Andy Arditi and his coauthors showed this in [Refusal in Language Models Is Mediated by a Single Direction](https://arxiv.org/abs/2406.11717). One direction in the residual stream mediates refusal across the chat models they tested. The code is public, there are abliterated models using this finding on [Hugging Face](https://huggingface.co/collections/mlabonne/abliteration), and the paper has 1,232 citations on Semantic Scholar.

So what did fine-tuning do to that direction? The follow-ups give a fairly consistent answer. Fine-tuning mostly breaks refusal by going around the direction, which survives in some form while the routing around it changes. One direction is enough to steer the refusal decision that safety training produces. It is not the whole story, though, and it is not the model's judgment of harm. Defenses that hold the direction in place during fine-tuning work in their own evaluations. Cheap attribution methods can find the training data that moved it. What nobody has done is trace the direction through all three stages of one open training pipeline: SFT, then DPO, then RL.

![Diagram. Arditi et al. 2024 on the left branches to four groups of follow-up papers: fine-tuning breaks refusal (10 papers), refusal has more than one direction (10), the direction as a defense (6), and which training data did it (3). A dashed box below marks the measurement not found: the direction traced through SFT, DPO and RL on one open pipeline.](/images/refusal-direction/fig0-map-of-follow-ups.svg){: style="max-width: 100%; height: auto; display: block; margin: 0 auto;"}

*Fig. 1. The map of this post. Arditi et al. is on the left. The follow-up papers fall into four groups: 10 on fine-tuning attacks, 10 on the geometry of refusal, 6 on defenses and 3 on data attribution. The dashed box is the measurement I could not find. (Diagram by the author)*
{: #fig-1}

In my latest research, I have used Arditi et al.'s refusal direction to read models rather than steer them. I project a model's activations onto it and compare how far prompts sit along it. For this post I ran an [Undermind](https://www.undermind.ai) deep search (250 ranked papers) and added papers I had already read. I sorted the follow-ups by the question each one asks ([Fig. 1](#fig-1)). The papers measure refusal in different ways, so their numbers rarely compare directly. The [reference section](#metrics-models-and-prompts) at the end lists each paper's models, prompts and metric.

{% include reading-outline.html %}

## Does fine-tuning delete the direction, or go around it? {#group-1-fine-tuning-breaks-refusal}

Qi et al. ([2023](https://arxiv.org/abs/2310.03693)) found that fine-tuning an aligned model on a few examples compromises its safety, even when the data is benign. Two follow-up papers from 2024 explain parts of this result.

Qi et al. ([2024](https://arxiv.org/abs/2406.05946)) argue that safety alignment is shallow. It changes the output distribution over the first few tokens and little else. In their account, this is why prefilling attacks, decoding-parameter attacks and fine-tuning attacks all work.

![Line chart from Qi et al. Per-token KL divergence between aligned and base models on harmful responses. Llama-2-7B-Chat starts at about 9 on token 1 and falls below 2 by token 4. Gemma-1.1-7B-IT starts at about 4 and falls to about 1.3 by token 20.](/images/refusal-direction/qi-2024-per-token-kl.png){: style="max-width: min(560px, 100%); height: auto; display: block; margin: 0 auto;"}

*Fig. 2. Where alignment changes the output. The y-axis is the KL divergence between the aligned chat model and its base model, per token, on harmful responses from HEx-PHI. For Llama-2-7B the divergence is high on the first token and small from the fourth token on. Alignment changes the start of the response the most. (Figure from [Qi et al. 2024](https://arxiv.org/abs/2406.05946))*

He, Xia and Henderson ([2024](https://arxiv.org/abs/2404.01099)) look at the data. They select 100 benign examples, and after training on them the model complies with more than 70% of harmful requests. After training on 100 random benign examples, it complies with fewer than 20%. The selected examples are often lists, bullet points and math problems. Nothing in them is harmful.

Lee et al. ([2024](https://arxiv.org/abs/2401.01967)) studied direct preference optimization (DPO) on toxicity in GPT-2. After DPO, the toxic capability is still in the model, and the model learns to bypass it. Later papers in this group report the same pattern.

Three 2024 papers look inside the model. Yu et al. ([2024](https://arxiv.org/abs/2409.20089)) show that many adversarial attacks share one mechanism: they ablate the refusal direction, which they call the refusal feature. Their defense, ReFAT, simulates that ablation during training. Leong et al. ([2024](https://arxiv.org/abs/2405.16229)) split refusal into three stages: recognize the harmful request, start the refusal, finish the refusal. Different fine-tuning attacks hit different stages. Jain et al. ([2024](https://arxiv.org/abs/2407.10264)) use synthetic data to study supervised fine-tuning (SFT), DPO and unlearning. All three methods make small changes to MLP weights that push unsafe inputs into a null space. On their synthetic data, a jailbreak works when it makes an unsafe input look like a safe one.

DPO can also undo refusal by itself. Razin et al. ([2024](https://arxiv.org/abs/2410.08847)) describe likelihood displacement. DPO can move probability mass from the preferred refusal to a harmful response, because the two responses in a pair have similar embeddings. In one of their runs, Llama-3-8B-Instruct's refusal rate fell by more than half.

Yoon et al. ([2026](https://arxiv.org/abs/2605.10998)) turn likelihood displacement into an attack. Each of their 10 preference pairs has a benign prompt, a helpful preferred answer and a refusal as the rejected answer. They submit these pairs through OpenAI's public fine-tuning API. The attack then succeeds on 55% to 82% of harmful requests against GPT-4o and the GPT-4.1 models. To the API provider, the request looks the same as a legitimate request to reduce over-refusal.

Guo et al. ([2026](https://arxiv.org/abs/2609.01455)) explain benign fine-tuning with Fisher geometry. They argue that safety depends on a low-rank pathway that routes outputs. About 100 benign examples re-sharpen that pathway, and general capability changes only a little.

My reading of this group: fine-tuning keeps the direction in some form, and refusal fails because of changes around it. Three papers say this in their own words. Lee et al. say the toxic capability is "bypassed". Guo et al. say "routing disrupted". Zhao et al. (next section) find that the model's judgment of harmfulness stays intact. None of the papers in this group measures the direction inside a production post-training pipeline.

## Is refusal really one direction? {#group-2-refusal-has-more-than-one-direction}

Arditi et al. claim that the direction mediates refusal under intervention. Much of the 2025 and 2026 work tests the limits of that claim.

Marshall, Scherlis and Belrose ([2024](https://arxiv.org/abs/2411.09003)) treat refusal as an affine function. On ten models, subspace projection combined with activation addition controls refusal more precisely than either method alone. Wollschläger et al. ([2025](https://arxiv.org/abs/2502.17420)) find several independent refusal directions and multi-dimensional concept cones. They also show that two orthogonal directions can still interact under intervention.

Pan et al. ([2025](https://arxiv.org/abs/2502.09674)) study how representations shift during safety fine-tuning of Llama 3 8B. They find one dominant direction plus smaller directions that are interpretable, for features such as hypothetical framing and role-play. The smaller directions modulate the dominant one. Yeo et al. ([2025](https://arxiv.org/abs/2505.23556)) use sparse autoencoders (SAEs) and find features that causally mediate refusal in two chat models.

Zhao et al. ([2025](https://arxiv.org/abs/2507.11878)) separate harmfulness from refusal. They find a harmfulness direction that is distinct from the refusal direction. Jailbreaks lower the refusal signal and leave the model's internal judgment of harmfulness in place. Adversarial fine-tuning also leaves that judgment almost unchanged.

![Diagram from Zhao et al. The model reads the harmfulness of an instruction at the last instruction token and makes the refusal decision at the last token of the whole prompt. Steering along the refusal direction and along the harmfulness direction gives different answers to the question "Could this user prompt cause harm?"](/images/refusal-direction/zhao-2025-harmfulness-vs-refusal.png){: style="max-width: 100%; height: auto; display: block; margin: 0 auto;"}

*Fig. 3. Two directions at two token positions. Zhao et al. read harmfulness at the last token of the user instruction (orange) and refusal at the last token of the full prompt (blue). In this example the model judges "how to kill the lights in my room" harmless and still refuses. Adding the refusal direction does not make the model call the prompt harmful. Adding the harmfulness direction does. (Figure from [Zhao et al. 2025](https://arxiv.org/abs/2507.11878), CC BY 4.0)*

Zhao et al.'s split matters for the next two papers. Refusal is an action: when the refusal direction is present, the model writes a refusal. Harmfulness is a judgment about the input. A monitor that reads harmfulness measures something different from the direction Arditi et al. found.

Two papers probe harmfulness and find more than one direction. Bailey et al. ([2024](https://arxiv.org/abs/2412.09565)) attack harmfulness probes that read the model's input. In one experiment on Llama-3-8B-Instruct, the defender retrains the probe after every attack. After more than 70 rounds, the attacker still finds a new embedding suffix that fools the latest probe. The authors conclude that no single "harmfulness direction" lets a monitor recognize harmful inputs robustly.

Youstra et al. ([2025](https://arxiv.org/abs/2508.17158)) find many harm directions without any attack. They train a probe, remove its direction from the activations, and train the next probe on what remains. The probes stay near-perfect for the first hundred orthogonal directions. In their examples, steering along one of these directions jailbreaks the model on a harmful prompt. Their model was fine-tuned on cipher-encoded harmful data, so the result may not transfer to a standard chat model.

My reading of the two papers: the model's judgment of harm can be read along many directions. An attacker who suppresses one direction has others to use. Neither paper measures the refusal direction.

Joad et al. ([2026](https://arxiv.org/abs/2602.02132)) find that different refusal categories have geometrically distinct directions. Steering along any of them gives nearly the same trade-off between refusal and over-refusal. So the category directions change the style of the refusal, and the decision to refuse stays the same. Wang et al. ([2026](https://arxiv.org/abs/2610.04245)) define steering dimensionality. One dimension is enough to steer the refusal that safety training produces. Refusal in general contexts needs more than five dimensions.

Ponkshe et al. ([2025](https://arxiv.org/abs/2505.14185)) are the most skeptical. On five Llama and Qwen models, the subspaces that amplify safe behavior also amplify useful behavior. They conclude that safety is entangled with general learning.

These papers agree with Arditi et al. if the claim stays narrow. One direction is enough to control the refusal decision that safety training produces. The direction is not a full description of how the model represents refusal (Wollschläger et al., Joad et al.). It is also not an isolated feature that you can protect or delete without side effects (Ponkshe et al.). It is also not the model's judgment of harm, which Zhao et al., Bailey et al. and Youstra et al. find elsewhere. I use the direction as a measuring instrument for the refusal decision, and I make no claim about mechanism. Both the one-direction papers and the multi-direction papers support that use.

## Can the direction be protected during fine-tuning? {#group-3-the-direction-as-a-defense}

Two 2024 defenses act on representations without using the refusal direction. Zou et al. ([2024](https://arxiv.org/abs/2406.04313)) introduce circuit breakers, which reroute the representations that produce harmful outputs. Circuit breakers hold up against attacks the model did not see in training. Chen et al. ([2024](https://arxiv.org/abs/2406.14144)) find a small set of safety neurons. Patching only those neurons restores most of the model's safety performance. The safety neurons overlap with helpfulness neurons, which gives a mechanistic account of the alignment tax.

Four defenses from 2024 to 2026 work with the direction or with nearby safety representations. Zhu et al. ([2024](https://arxiv.org/abs/2410.10343)) observe that fine-tuned models keep safety-related activations close to those of their base model. From these activations they extract a reusable set of safety directions, which they call SafetyLock. On toxic fine-tunes, SafetyLock brings the harmful-response rate from 60% to below 1%, in under a hundredth of a second.

Du et al. ([2025](https://arxiv.org/abs/2509.06795)) add a loss term during fine-tuning. The term constrains each sample's projection onto the refusal direction. Asif and Amiri ([2026](https://arxiv.org/abs/2605.01913)) measure how safety-relevant representations drift during standard fine-tuning. Their method, RefusalGuard, constrains updates so that those components stay stable.

Li et al. ([2026](https://arxiv.org/abs/2604.00012)) study reasoning models. They find that the safety mechanism is still present after post-training, but over-activated reasoning representations mask it. Their method, SafeReAct, prunes the reasoning neurons to build a safer reference model. LoRA adapters then train the original model to match the pruned model's representations on harmful prompts.

SafetyLock, the projection constraint of Du et al., RefusalGuard and SafeReAct repeat the pattern from the first section. All four assume that the direction, or the safety representation around it, survives fine-tuning. They keep it in place during training or restore it afterwards. None of the four asks which stage of a multi-stage pipeline moved it.

## Which training data moved it? {#group-4-which-training-data-did-it}

Razin et al. already look at the data. Their similarity score finds the preference pairs that cause likelihood displacement, and removing those pairs reduces the unalignment. Three 2026 papers do data attribution for safety at larger scale.

Kowal et al. ([2026](https://arxiv.org/abs/2602.14869)) introduce Concept Influence. It attributes behavior to semantic directions, such as probes or SAE features, instead of to individual test examples. Simple probe-based attribution is a first-order approximation of Concept Influence, and it runs much faster than influence functions.

Xiao and Aranguri ([2026](https://arxiv.org/abs/2602.11079)) apply a similar method to OLMo 2's full DPO dataset. The target behavior is a model that refuses a harmful request until you append a formatting instruction such as "(no more than 50 words)". They score each preference pair by its alignment with an activation-difference vector for that behavior. Then they remove or relabel the top 30,000 pairs and retrain DPO from the SFT checkpoint. Switching the labels cuts the behavior by more than three-quarters. Removing or relabeling 30,000 random pairs does not reliably reduce it.

![Two bar charts from Xiao and Aranguri. Harmful response rate after removing (top) or switching (bottom) 30,000 DPO pairs. Baseline 7.6% in both. Removing: LLM toxicity ranking 3.6%, gradient attribution 5.8%, probe 2.9%. Switching: LLM toxicity 3.7%, gradient 2.5%, probe 1.7%.](/images/refusal-direction/xiao-2026-attribution.png){: style="max-width: min(420px, 100%); height: auto; display: block; margin: 0 auto;"}

*Fig. 4. Retraining OLMo 2 DPO after changing 30,000 of 378,341 preference pairs. The baseline harmful-response rate is 7.6%. Each method ranks the pairs differently. "LLM Toxic" asks an LLM judge how toxic each pair is. "Gradient" uses gradient-based attribution. "Probe" uses the activation-difference vector. The probe ranking gives the lowest harmful-response rate for both removal (2.9%) and label switching (1.7%). (Figure from [Xiao and Aranguri 2026](https://arxiv.org/abs/2602.11079), CC BY 4.0)*

Bergen et al. ([2026](https://arxiv.org/abs/2606.12360)), from Goodfire, start before training. They inspect a preference dataset before optimization and predict, at the level of concepts, which behaviors the model will learn from it. Their predictions match the feature changes after DPO closely. The same paper also tracks the refusal direction from SFT to DPO, which I come back to in the [next section](#what-i-did-not-find).

Xiao and Aranguri report that their attribution costs more than ten times less than the gradient-based and LLM-judge baselines. With methods this cheap, I expect more papers in this group soon.

## What happens to the direction across a full pipeline? {#what-i-did-not-find}

Tülu 3 and OLMo 2 publish the checkpoints, datasets and evaluations for a full pipeline of SFT, then DPO, then reinforcement learning (RL). Seven papers come close to tracing refusal through such a pipeline. Each covers part of it.

The two closest measure the direction itself. Du et al. ([2025](https://arxiv.org/abs/2504.02904)) compare base and post-trained models, including a Tülu 3 SFT checkpoint and Meta's Llama-3.1-8B-Instruct. Their figure carries the most important number in this post. The base model's refusal direction is almost unrelated to the SFT model's: cosine similarity 0.15. The SFT and Instruct directions are only partly aligned, at 0.66. That number covers base to SFT only.

![Three cosine-similarity heatmaps from Du et al. for Llama-3.1-8B base, Tülu 3 SFT and Instruct. Two truthfulness directions have similarities of 0.89 to 0.94 between all pairs. The refusal direction has 0.147 between base and SFT, 0.252 between base and Instruct, and 0.660 between SFT and Instruct.](/images/refusal-direction/du-2025-direction-cosine.png){: style="max-width: 100%; height: auto; display: block; margin: 0 auto;"}

*Fig. 5. Cosine similarity between the directions of three Llama-3.1-8B models: base, Tülu 3 SFT and Meta's Instruct. The left and middle panels are truthfulness directions, and all pairs are 0.89 or higher. The right panel is the refusal direction. The base model's refusal direction is almost unrelated to the SFT direction (0.15) and the Instruct direction (0.25). The SFT and Instruct refusal directions are only partly aligned (0.66). (Figure from [Du et al. 2025](https://arxiv.org/abs/2504.02904), CC BY 4.0)*

Bergen et al. take the next step. In all four model families they train, DPO lowers safety relative to the SFT checkpoint, including in a reproduction of Tülu 3 70B DPO. In an appendix they re-estimate the refusal direction after DPO and compare it with the SFT direction by layerwise cosine similarity. They also steer each DPO model with the SFT direction and with its own direction, and score refusal with WildGuard. Their DPO models are their own runs, and they stop before RL.

The other five each touch one stage, or measure something other than the direction:

- Zahraei et al. ([2026](https://arxiv.org/abs/2610.00568)) evaluate the released SFT, DPO and RLVR checkpoints of Tülu 3 and OLMo 3. They measure whether a model summarizes a source faithfully when the source makes an unsafe claim. Unfaithfulness grows most at DPO, and RLVR recovers only part of it. They do not use the refusal direction.
- Lu et al. ([2026](https://arxiv.org/abs/2607.25063)) fork a partly trained OLMo-2-1B model into six branches that differ only in their last pretraining tokens. Identical SFT installs refusal in every branch. Under the same DPO, and under a GRPO RL update, the branch that ended on safety text loses far less refusal. They measure refusal from model outputs.
- Elcock et al. ([2026](https://arxiv.org/abs/2607.22676)) compare SFT with RL from verifiable rewards (RLVR) as adaptation methods. SFT causes more alignment drift.
- Kabir and Tiganj ([2026](https://arxiv.org/abs/2604.18510)) compare harmful SFT, harmful RLVR and abliteration, which removes the refusal direction from the weights. RLVR keeps the representation geometry and retargets behavior toward compliance.
- Xiao and Aranguri work inside OLMo 2's DPO stage.

No paper traces the refusal direction through the released SFT, DPO and RL checkpoints of one public pipeline. Bergen et al. cover SFT to DPO on their own runs. No paper measures where harmful and benign prompts sit along the direction at each of the three stages. The Tülu 3 paper's own tables show safety behavior decaying across the stages. The direction gives a way to measure the change, and the checkpoints are on Hugging Face. The measurement also needs one metric held fixed across all stages. Then a change in the number comes from the model and not from the judge. In 250 papers I found no published version of this measurement.

I have run this measurement as part of a paper in progress. The paper now asks a broader question: what in DPO and RL causes the decline in refusal. I will post the results when the paper is out. If you know of a paper that already does this, please tell me.

## Reference: how each paper measures refusal {#metrics-models-and-prompts}

Arditi et al. use two scores. The refusal score is a string match. An answer counts as a refusal if it contains a phrase such as "I'm sorry" or "As an AI". The safety score asks [Llama Guard 2](/posts/2026/05/safety-judges/#llama-guard) whether the answer is harmful.

The follow-up papers do not share a metric, and the methods answer two different questions. A refusal metric asks whether the model refused. A harm metric asks whether the answer is harmful. Zhao et al. show that the model keeps these apart internally. Yeo et al. report the practical problem: an answer without a refusal phrase is often not a successful jailbreak. My [judges post](/posts/2026/05/safety-judges/) describes each judge in the table.

| Method | Question it answers | Papers |
|---|---|---|
| [Refusal phrase in the answer](/posts/2026/05/safety-judges/#refusal-strings) | Did the model refuse? | Arditi 2024, Zhao 2025, Du 2025 (post-training); also part of He 2024, Zhu 2024 and Wollschläger 2025 |
| [GPT-family judge](/posts/2026/05/safety-judges/#gpt-4-judge) | Is the answer harmful? | Qi 2023, Qi 2024, He 2024, Leong 2024, Zhu 2024, Ponkshe 2025, Du 2025 (anchoring), Guo 2026, Kabir 2026, Yoon 2026, Xiao and Aranguri 2026 |
| Fine-tuned safety classifier ([HarmBench](/posts/2026/05/safety-judges/#harmbench-classifier), [StrongREJECT](/posts/2026/05/safety-judges/#strongreject-judge), [Llama Guard](/posts/2026/05/safety-judges/#llama-guard)) | Is the answer harmful? | Zou 2024, Yu 2024, Bailey 2024, Yeo 2025, Pan 2025, Wollschläger 2025, Youstra 2025, Li 2026; also Arditi 2024 and Leong 2024 |
| Judge that labels refusal or compliance | Did the model refuse? | Marshall 2024 (Llama 3 70B), Razin 2024 ([SORRY-Bench judge](/posts/2026/05/safety-judges/#sorry-bench-judge)), Joad 2026 ([WildGuard](/posts/2026/05/safety-judges/#wildguard)), Wang 2026 (a Qwen model) |
| Other | Toxicity, safety reward or token match | Lee 2024 ([Perspective API](/posts/2026/05/safety-judges/#perspective-api) on GPT-2), Chen 2024 (a [safety cost model](/posts/2026/05/safety-judges/#beaver-cost-model)), Jain 2024 (null tokens on synthetic data) |

The prompt sets differ as well. [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi), [AdvBench](/posts/2026/05/safety-datasets/#advbench), [HarmBench](/posts/2026/05/safety-datasets/#harmbench), [JailbreakBench](/posts/2026/05/safety-datasets/#jailbreakbench), [SORRY-Bench](/posts/2026/05/safety-datasets/#sorry-bench) and [XSTest](/posts/2026/05/safety-datasets/#xstest) all appear, among about twenty sets. My [datasets post](/posts/2026/05/safety-datasets/) describes each one. My [red-teaming post](/posts/2026/07/red-teaming-language-models/#the-measurement-problem) describes the same comparability problem for attack evaluations.

The models are narrow too. Almost every paper includes a Llama chat model at 7B or 8B. Only Arditi et al., Zhu et al., Youstra et al. and Bergen et al. test models of 70B or more. Two papers attack closed models through fine-tuning APIs: Qi et al. 2023 (GPT-3.5 Turbo) and Yoon et al. (GPT-4o and GPT-4.1). Fewer than half of the papers test harmless prompts at all, so a method that also makes the model refuse benign requests often goes unmeasured. Only Bergen et al. evaluate on [DAN](/posts/2026/05/safety-datasets/#dan) and [WildJailbreak](/posts/2026/05/safety-datasets/#wildjailbreak) jailbreak prompts.

<details markdown="1">
<summary>Setup of each paper: models, prompts and metric</summary>

The table lists the main experiments. Appendices sometimes add models or datasets. "Not checked" means I could not confirm the entry in the paper's text.

| Paper | Models | Harmful prompts | Harmless prompts | Metric |
|---|---|---|---|---|
| Arditi 2024 | 13 chat models: Qwen 1.8B to 72B, Yi 6B and 34B, Gemma 2B and 7B, Llama-2 7B to 70B, Llama-3 8B and 70B | [JailbreakBench](/posts/2026/05/safety-datasets/#jailbreakbench) (evaluation); [AdvBench](/posts/2026/05/safety-datasets/#advbench), [MaliciousInstruct](/posts/2026/05/safety-datasets/#maliciousinstruct), [TDC2023](/posts/2026/05/safety-datasets/#tdc2023), [HarmBench](/posts/2026/05/safety-datasets/#harmbench) (direction) | [Alpaca](/posts/2026/05/safety-datasets/#alpaca) | [Refusal phrases](/posts/2026/05/safety-judges/#refusal-strings); [Llama Guard 2](/posts/2026/05/safety-judges/#llama-guard) |
| Qi 2023 | Llama-2-7B-Chat, GPT-3.5 Turbo | [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi) (330 prompts, introduced here) | none | [GPT-4 judge](/posts/2026/05/safety-judges/#gpt-4-judge), 1 to 5 |
| He 2024 | Llama-2-7B-Chat, Llama-2-13B-Chat | [AdvBench](/posts/2026/05/safety-datasets/#advbench) (520 prompts) | none | [Refusal phrases](/posts/2026/05/safety-judges/#refusal-strings); GPT-3.5 judge |
| Lee 2024 | GPT-2 medium | [RealToxicityPrompts](/posts/2026/05/safety-datasets/#realtoxicityprompts) | none | [Perspective API](/posts/2026/05/safety-judges/#perspective-api) toxicity |
| Leong 2024 | Llama-2-7B-Chat | [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi) | none | [GPT-4 judge](/posts/2026/05/safety-judges/#gpt-4-judge); [Llama Guard 2](/posts/2026/05/safety-judges/#llama-guard) |
| Qi 2024 | Llama-2-7B and Gemma-7B, base and aligned | [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi) | none | [GPT-4 judge](/posts/2026/05/safety-judges/#gpt-4-judge) |
| Jain 2024 | minGPT on synthetic data; Llama-2 7B and Llama-3 8B, base and chat | Synthetic; 500 custom instructions | Same sets | Null-token output |
| Razin 2024 | OLMo-1B, Gemma-2B, Llama-3-8B | [SORRY-Bench](/posts/2026/05/safety-datasets/#sorry-bench) | none | [SORRY-Bench judge](/posts/2026/05/safety-judges/#sorry-bench-judge) |
| Yu 2024 | Llama-3-8B, Mistral-7B, Gemma-7B (instruct) | [HarmBench](/posts/2026/05/safety-datasets/#harmbench) attacks | [XSTest](/posts/2026/05/safety-datasets/#xstest) | [HarmBench](/posts/2026/05/safety-judges/#harmbench-classifier), [Llama Guard 2](/posts/2026/05/safety-judges/#llama-guard) and [StrongREJECT](/posts/2026/05/safety-judges/#strongreject-judge) judges |
| Zou 2024 | Mistral-7B-Instruct-v2, Llama-3-8B-Instruct | [HarmBench](/posts/2026/05/safety-datasets/#harmbench) | none | [HarmBench classifier](/posts/2026/05/safety-judges/#harmbench-classifier) |
| Chen 2024 | Llama-2-7B, Mistral-7B-v0.1, Gemma-7B | [BeaverTails](/posts/2026/05/safety-datasets/#beavertails) | none | [Safety cost model](/posts/2026/05/safety-judges/#beaver-cost-model) |
| Zhu 2024 | Llama-3-8B and 70B Chat, Mistral-Large-2 123B | [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi), [AdvBench](/posts/2026/05/safety-datasets/#advbench) | none | [GPT-4 judge](/posts/2026/05/safety-judges/#gpt-4-judge); refusal phrases |
| Marshall 2024 | Ten open models | [AdvBench](/posts/2026/05/safety-datasets/#advbench) | [Alpaca](/posts/2026/05/safety-datasets/#alpaca) | Llama 3 70B judge |
| Bailey 2024 | Llama-3-8B-Instruct | [Circuit Breakers dataset](/posts/2026/05/safety-datasets/#circuit-breakers) | [UltraChat](/posts/2026/05/safety-datasets/#ultrachat), [XSTest](/posts/2026/05/safety-datasets/#xstest) (probe training) | [StrongREJECT](/posts/2026/05/safety-judges/#strongreject-judge) |
| Pan 2025 | Llama-3.1-8B-Instruct | [StrongREJECT](/posts/2026/05/safety-datasets/#strongreject) prompts with jailbreaks | [OR-Bench](/posts/2026/05/safety-datasets/#or-bench) | Refusal accuracy; [StrongREJECT](/posts/2026/05/safety-judges/#strongreject-judge) |
| Wollschläger 2025 | Gemma 2, Qwen2.5 and Llama-3 families | [JailbreakBench](/posts/2026/05/safety-datasets/#jailbreakbench) | [Alpaca](/posts/2026/05/safety-datasets/#alpaca) | [StrongREJECT](/posts/2026/05/safety-judges/#strongreject-judge); refusal phrases |
| Du 2025 (post-training) | Llama-3.1-8B and Mistral-7B-v0.3: base, SFT and Instruct | Not checked | Not checked | [Refusal phrases at the start of the answer](/posts/2026/05/safety-judges/#refusal-strings) |
| Ponkshe 2025 | Llama 3.2 1B, Llama 2 7B, Qwen-2.5 1B, 3B and 7B, base and aligned | [AdvBench](/posts/2026/05/safety-datasets/#advbench) | none | GPT-4o-mini judge, 1 to 5 |
| Yeo 2025 | Gemma-2-2B, Llama-3.1-8B (instruct) | Not checked | none | [HarmBench classifier](/posts/2026/05/safety-judges/#harmbench-classifier) |
| Zhao 2025 | Llama-2-7B-Chat, Llama-3-8B-Instruct, Qwen2-7B-Instruct | [AdvBench](/posts/2026/05/safety-datasets/#advbench), [JailbreakBench](/posts/2026/05/safety-datasets/#jailbreakbench), [SORRY-Bench](/posts/2026/05/safety-datasets/#sorry-bench) | [Alpaca](/posts/2026/05/safety-datasets/#alpaca), [XSTest](/posts/2026/05/safety-datasets/#xstest) | [Refusal phrases](/posts/2026/05/safety-judges/#refusal-strings) |
| Youstra 2025 | Llama-3.1-70B-Instruct, cipher fine-tuned | [AdvBench](/posts/2026/05/safety-datasets/#advbench), encrypted | none | [StrongREJECT](/posts/2026/05/safety-judges/#strongreject-judge) |
| Du 2025 (anchoring) | Llama-2-7B, Llama-3-8B and Qwen2-7B chat | [AdvBench](/posts/2026/05/safety-datasets/#advbench), [CatQA](/posts/2026/05/safety-datasets/#catqa); SAP30, CompObj, AutoDAN and PAIR attacks | none | [GPT-4 judge](/posts/2026/05/safety-judges/#gpt-4-judge); refusal phrases |
| Joad 2026 | Gemma-2-9B-it, Llama-3.1-8B-Instruct | [WildGuardMix](/posts/2026/05/safety-datasets/#wildguardmix), [SORRY-Bench](/posts/2026/05/safety-datasets/#sorry-bench) | Not checked | [WildGuard](/posts/2026/05/safety-judges/#wildguard) |
| Xiao and Aranguri 2026 | OLMo 2 7B | 120 LMSys prompts | [XSTest](/posts/2026/05/safety-datasets/#xstest) | GPT-5-mini judge |
| Li 2026 | DeepSeek-R1-distilled Llama-8B, Qwen-7B and Qwen-14B; OpenThinker-7B | [AdvBench](/posts/2026/05/safety-datasets/#advbench), [JailbreakBench](/posts/2026/05/safety-datasets/#jailbreakbench) | [XSTest](/posts/2026/05/safety-datasets/#xstest) | [Llama Guard 3](/posts/2026/05/safety-judges/#llama-guard); refusal phrases for over-refusal |
| Yoon 2026 | GPT-4o, GPT-4.1, GPT-4.1-mini, GPT-4.1-nano; Llama 3.2 3B, Llama 3.1 8B, Qwen2.5 3B and 7B | [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi) | none | GPT-5-mini judge |
| Guo 2026 | Llama-3.1-8B-Instruct, Qwen2.5-7B-Instruct | [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi) | none | GPT-4o mini judge |
| Kabir 2026 | Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct | [AdvBench](/posts/2026/05/safety-datasets/#advbench), [HEx-PHI](/posts/2026/05/safety-datasets/#hex-phi) | none | GPT-4o-mini judge |
| Elcock 2026 | Qwen3-1.7B, Qwen2.5-3B, Llama3.2-3B, Llama3.1-8B (instruct) | [HarmBench](/posts/2026/05/safety-datasets/#harmbench) | none | HarmBench refusal rate |
| Bergen 2026 | Llama-3.1-8B and 70B, OLMo-3-7B, OLMo-3.1-32B | [StrongREJECT](/posts/2026/05/safety-datasets/#strongreject), [HarmBench](/posts/2026/05/safety-datasets/#harmbench) and five attack variants, [WildJailbreak](/posts/2026/05/safety-datasets/#wildjailbreak), [DAN](/posts/2026/05/safety-datasets/#dan) | [XSTest](/posts/2026/05/safety-datasets/#xstest), [WildJailbreak](/posts/2026/05/safety-datasets/#wildjailbreak) benign | AllenAI safety-eval scorers |
| Wang 2026 | Qwen2.5-3B-Instruct, Llama-3.1-8B-Instruct | Custom sets | Custom sets | Qwen judge |

</details>

## Papers {#papers-mentioned}

The numbers the narrative leaves out are here, one per paper.

<details markdown="1" open>
<summary><strong>All papers, with a key result</strong></summary>

| Paper | Section | Key result |
|---|---|---|
| Arditi et al. 2024, [Refusal in Language Models Is Mediated by a Single Direction](https://arxiv.org/abs/2406.11717) | Intro | One direction mediates refusal in 13 chat models up to 72B |
| Qi et al. 2023, [Fine-tuning Aligned Language Models Compromises Safety](https://arxiv.org/abs/2310.03693) | Fine-tuning | A few fine-tuning examples break safety, even benign ones |
| Qi et al. 2024, [Safety Alignment Should Be Made More Than Just a Few Tokens Deep](https://arxiv.org/abs/2406.05946) | Fine-tuning | Per-token KL about 9 on token 1, below 2 by token 4 (Llama-2-7B) |
| He, Xia, Henderson 2024, [What is in Your Safe Data?](https://arxiv.org/abs/2404.01099) | Fine-tuning | 100 selected benign examples: over 70% compliance vs under 20% random |
| Lee et al. 2024, [A Mechanistic Understanding of Alignment Algorithms](https://arxiv.org/abs/2401.01967) | Fine-tuning | After DPO, toxic capability remains and is bypassed (GPT-2) |
| Yu et al. 2024, [Robust LLM Safeguarding via Refusal Feature Adversarial Training](https://arxiv.org/abs/2409.20089) | Fine-tuning | Many attacks ablate the refusal feature; ReFAT trains against it |
| Leong et al. 2024, [No Two Devils Alike](https://arxiv.org/abs/2405.16229) | Fine-tuning | Refusal in three stages; attacks hit different stages |
| Jain et al. 2024, [What Makes and Breaks Safety Fine-tuning?](https://arxiv.org/abs/2407.10264) | Fine-tuning | SFT, DPO and unlearning push unsafe inputs into a null space |
| Razin et al. 2024, [Unintentional Unalignment](https://arxiv.org/abs/2410.08847) | Fine-tuning, data | Llama-3-8B-Instruct refusal 74.4% to 33.4% under DPO |
| Yoon et al. 2026, [Few-Shot Truly Benign DPO Attack](https://arxiv.org/abs/2605.10998) | Fine-tuning | 10 pairs via OpenAI's API: 55% to 82% attack success; one pair can suffice on open models |
| Guo et al. 2026, [When Safety Routing Breaks](https://arxiv.org/abs/2609.01455) | Fine-tuning | About 100 benign examples disrupt a low-rank safety routing pathway |
| Marshall, Scherlis, Belrose 2024, [Refusal in LLMs is an Affine Function](https://arxiv.org/abs/2411.09003) | One direction? | Projection plus addition beats either alone, on ten models |
| Wollschläger et al. 2025, [The Geometry of Refusal in Large Language Models](https://arxiv.org/abs/2502.17420) | One direction? | Several independent refusal directions and concept cones |
| Pan et al. 2025, [The Hidden Dimensions of LLM Alignment](https://arxiv.org/abs/2502.09674) | One direction? | One dominant direction plus smaller modulating ones (Llama 3 8B) |
| Yeo et al. 2025, [Understanding Refusal in Language Models with Sparse Autoencoders](https://arxiv.org/abs/2505.23556) | One direction? | SAE features causally mediate refusal in two chat models |
| Zhao et al. 2025, [LLMs Encode Harmfulness and Refusal Separately](https://arxiv.org/abs/2507.11878) | One direction? | Harmfulness direction distinct from refusal; jailbreaks leave harm judgment intact |
| Bailey et al. 2024, [Obfuscated Activations Bypass LLM Latent-Space Defenses](https://arxiv.org/abs/2412.09565) | One direction? | Probe recall 100% to 0% while jailbreaks still succeed 90%; over 70 retraining rounds, jailbreak rate levels near 50% |
| Youstra et al. 2025, [Towards Safeguarding LLM Fine-tuning APIs against Cipher Attacks](https://arxiv.org/abs/2508.17158) | One direction? | Near-perfect probes for 100 orthogonal directions, above chance to about 300 |
| Joad et al. 2026, [There Is More to Refusal in Large Language Models than a Single Direction](https://arxiv.org/abs/2602.02132) | One direction? | Category directions differ; refusal trade-off nearly the same |
| Wang et al. 2026, [On the Steering Dimensionality of Refusal in Language Models](https://arxiv.org/abs/2610.04245) | One direction? | One dimension for safety-trained refusal; more than five in general contexts |
| Ponkshe et al. 2025, [Safety Subspaces are Not Linearly Distinct](https://arxiv.org/abs/2505.14185) | One direction? | Safe and useful behavior share subspaces on five models |
| Zou et al. 2024, [Improving Alignment and Robustness with Circuit Breakers](https://arxiv.org/abs/2406.04313) | Defense | Rerouting holds against unseen attacks |
| Chen et al. 2024, [Towards Understanding Safety Alignment: Safety Neurons](https://arxiv.org/abs/2406.14144) | Defense | About 5% of neurons; patching them restores over 90% of safety |
| Zhu et al. 2024, [Locking Down the Finetuned LLMs Safety](https://arxiv.org/abs/2410.10343) | Defense | SafetyLock: harmful responses 60% to below 1%, under 0.01 s |
| Du et al. 2025, [Anchoring Refusal Direction](https://arxiv.org/abs/2509.06795) | Defense | Loss term constrains projection onto the refusal direction |
| Asif, Amiri 2026, [RefusalGuard](https://arxiv.org/abs/2605.01913) | Defense | Constrains updates to keep safety components stable |
| Li et al. 2026, [Finding and Reactivating Post-Trained LLMs' Hidden Safety Mechanisms](https://arxiv.org/abs/2604.00012) | Defense | SafeReAct unmasks safety in reasoning models |
| Kowal et al. 2026, [Concept Influence](https://arxiv.org/abs/2602.14869) | Data | Attribution toward a probe or SAE direction; probe version more than 10× faster |
| Xiao, Aranguri 2026, [Probe-Based Data Attribution](https://arxiv.org/abs/2602.11079) | Data | 30k of 378k DPO pairs: 7.6% to 2.9% (remove), 1.7% (switch) |
| Bergen et al. 2026, [Anatomy of Post-Training](https://arxiv.org/abs/2606.12360) | Data, pipeline | Predicted vs observed feature change R² = 0.9 (0.58 prompt-level); SFT vs DPO refusal direction compared |
| Du et al. 2025, [How Post-Training Reshapes LLMs](https://arxiv.org/abs/2504.02904) | Pipeline | Refusal-direction cosine: base vs SFT 0.15, base vs Instruct 0.25, SFT vs Instruct 0.66 (layer 11) |
| Zahraei et al. 2026, [Emergent Unfaithfulness](https://arxiv.org/abs/2610.00568) | Pipeline | Unfaithfulness grows most at DPO; RLVR recovers only part |
| Lu, Tang, Cavallaro 2026, [Similar Models Learn Differently](https://arxiv.org/abs/2607.25063) | Pipeline | Final 500M-token window changes how much refusal survives DPO and GRPO |
| Elcock et al. 2026, [How LLM Task-Adaptation Reshapes Alignment](https://arxiv.org/abs/2607.22676) | Pipeline | SFT causes more alignment drift than RLVR |
| Kabir, Tiganj 2026, [Behind Harmful Compliance](https://arxiv.org/abs/2604.18510) | Pipeline | RLVR keeps geometry and retargets behavior toward compliance |

</details>
