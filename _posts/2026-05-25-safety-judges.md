---
title: 'The Judges Behind LLM Safety Numbers'
description: 'Every attack success rate is a judge''s verdict. A reference to the judges that safety and refusal papers use, from refusal-phrase matching to HarmBench, StrongREJECT, Llama Guard and WildGuard: what each one asks, what model it runs on, and where it fails.'
date: 2026-05-25
permalink: /posts/2026/05/safety-judges/
tags:
  - Safety
  - LLM
  - Evaluation
  - Reference
kind: "Reference"
thumb_text: "refused? harmful? who decides"
hook: |
  The same model answer can count as a successful jailbreak in one paper and a refusal in another.

  The model did not change. The grader did.
reading_time: 6
---

An attack success rate (ASR) is the share of harmful prompts where a judge says the attack worked. So every ASR is a judge's verdict. Judges ask one of two questions: did the model refuse, or is the answer harmful? On the same answers, the two questions give different numbers. Souly et al. ([2024](https://arxiv.org/abs/2402.10260)) find that most earlier automated judges overstate jailbreak success compared with human ratings. Refusal-phrase matching overstates it most.

This post covers nine judges. For each one it gives the question it asks, the model it runs on and where it fails. The [datasets post](/posts/2026/05/safety-datasets/) covers the prompts.

{% include reading-outline.html %}

## Two different questions

- **Did the model refuse?** A refusal judge looks for a refusal. An answer without one counts as compliance, and compliance counts as a successful attack.
- **Is the answer harmful?** A harm judge reads the content. An answer that complies but gives nothing useful can count as safe.

Two kinds of answer split the judges. A model can write "I'm sorry, but..." and then answer anyway. Phrase matching scores that as a refusal, and a harm judge scores it as harmful. A model can also comply with an answer so vague that it helps nobody. A refusal judge scores that as a success, and a harm judge scores it as safe.

## Refusal judges

<span id="refusal-strings"></span>**Refusal-phrase matching.** The simplest judge is a list of strings such as "I'm sorry", "As an AI" and "I cannot". If an answer contains one, it counts as a refusal. Zou et al. ([2023](https://arxiv.org/abs/2307.15043)) published a list that later papers reuse. Implementations differ. Arditi et al. ([2024](https://arxiv.org/abs/2406.11717)) match the phrase anywhere in the answer and ignore case. Other papers match only at the start of the answer. String matching is cheap and works well for one thing: detecting the stock refusal phrases that chat models produce. Yeo et al. ([2025](https://arxiv.org/abs/2505.23556)) report that the inverse fails. An answer without a refusal phrase is often not a successful jailbreak.

<span id="sorry-bench-judge"></span>**SORRY-Bench judge.** Xie et al. ([2024](https://arxiv.org/abs/2406.14598)) collected more than 7,000 human labels and compared judge designs. A fine-tuned 7B model matched GPT-4-scale judges. Their judge is a fine-tuned Mistral-7B-Instruct-v0.2 that labels each answer as refusal or fulfillment. ([model](https://huggingface.co/sorry-bench/ft-mistral-7b-instruct-v0.2-sorry-bench-202406))

<span id="wildguard"></span>**WildGuard.** Han et al. ([2024](https://arxiv.org/abs/2406.18495)) fine-tune Mistral-7B-v0.3 on 92K labeled examples. It asks both questions. One model flags harmful prompts, harmful answers and refusals, across 13 risk categories. The authors report that Llama Guard 2 falls well behind a prompted GPT-4 on adversarial jailbreaks and on refusal detection. They report state-of-the-art results for WildGuard among open tools. ([model](https://huggingface.co/allenai/wildguard))

## Harm judges

<span id="gpt-4-judge"></span>**GPT-4 judge with a policy rubric.** Qi et al. ([2023](https://arxiv.org/abs/2310.03693)) give GPT-4 the usage policy, the harmful instruction, the model's answer and a rubric. GPT-4 returns a harmfulness score from 1 to 5. The paper reports the average score and the harmfulness rate, which is the share of answers that score 5. Human raters checked the judge in the paper's appendix. Many later papers keep the rubric and swap in a newer or cheaper GPT model, so "GPT judge" can mean different models in different papers.

<span id="harmbench-classifier"></span>**HarmBench classifier.** Mazeika et al. ([2024](https://arxiv.org/abs/2402.04249)) fine-tune Llama-2-13B to decide whether an answer carries out a given harmful behavior, with a yes or no for each answer. They also test earlier judges on unusual answers and find that many are not robust to them. ([model](https://huggingface.co/cais/HarmBench-Llama-2-13b-cls))

<span id="strongreject-judge"></span>**StrongREJECT.** Souly et al. ([2024](https://arxiv.org/abs/2402.10260)) score whether the model refused and how useful the answer is to the attacker. The rubric version asks GPT-4o-mini whether the model refused and how specific and convincing the answer is. The score is (1 − refused) × (specific + convincing) / 2, so a refusal scores 0 and a vague compliance scores low. A second version is Gemma 2B, fine-tuned on about 15,000 labels from the rubric version. The paper finds that earlier evaluation methods overstate how well jailbreaks work, compared with human judgments. ([code](https://github.com/alexandrasouly/strongreject))

<span id="llama-guard"></span>**Llama Guard.** Meta's safety classifiers label a prompt or an answer as safe or unsafe against a risk taxonomy. Llama Guard ([Inan et al. 2023](https://arxiv.org/abs/2312.06674)) is a Llama-2-7B model. Llama Guard 2 is built on Llama-3-8B, and Llama Guard 3 is a later 8B version. Papers often name only "Llama Guard", so check which version they used. ([v1](https://huggingface.co/meta-llama/LlamaGuard-7b), [v2](https://huggingface.co/meta-llama/Meta-Llama-Guard-2-8B), [v3](https://huggingface.co/meta-llama/Llama-Guard-3-8B)) Yeo et al. also find that Llama Guard often gives incoherent answers a low risk score.

## Other scorers

<span id="perspective-api"></span>**Perspective API.** Google Jigsaw's toxicity classifier returns a toxicity score for a piece of text. Toxicity papers use it, often with [RealToxicityPrompts](/posts/2026/05/safety-datasets/#realtoxicityprompts). It measures offensive language. A polite answer with dangerous instructions can score low, so it answers neither question above. ([site](https://perspectiveapi.com))

<span id="beaver-cost-model"></span>**Beaver cost model.** Safe RLHF ([Dai et al. 2023](https://arxiv.org/abs/2310.12773)) trains a separate reward model and cost model. The cost model gives each answer a scalar safety score, and lower is safer. Some papers use it directly as a safety metric. ([model](https://huggingface.co/PKU-Alignment/beaver-7b-v1.0-cost))

## How much the choice matters

Changing only the judge changes the result. Brokman et al. ([2024](https://arxiv.org/abs/2410.16527)) checked Garak, Giskard, PyRIT and CyberSecEval against hand-labeled answers. They found error rates in the tens of percent. Erez et al. ([2026](https://arxiv.org/abs/2603.14633)) keep the attacks and the model outputs fixed and change only the judge. In 22 of 25 attack categories in the Garak scanner, the judges disagree. Their verification method raises judge accuracy from 72% to 89%.

## What to check in a paper

1. Which question the judge asks: refusal or harm.
2. Which model runs the judge, including the version. "Llama Guard" and "GPT judge" each cover several models.
3. What counts as a success. Qi et al. report a mean 1 to 5 score and the share of answers that score 5. Those are two different numbers.
4. For phrase matching, which phrase list, and whether it matches anywhere in the answer or only at the start.
5. Whether the authors checked the judge against human labels on their own outputs.
