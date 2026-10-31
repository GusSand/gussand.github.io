---
title: 'The Datasets Behind LLM Safety Numbers'
description: 'A refusal rate or attack success rate is only comparable on the same prompts. A reference to 20 prompt sets used in safety, refusal and jailbreak papers: what each contains, the paper that introduced it, and where to get the data.'
date: 2026-05-11
permalink: /posts/2026/05/safety-datasets/
tags:
  - Safety
  - LLM
  - Evaluation
  - Reference
kind: "Reference"
thumb_text: "AdvBench, HEx-PHI, HarmBench, XSTest, DAN"
hook: |
  Test one model on two lists of harmful requests and you can get two very different refusal rates.

  Both numbers are correct. The lists are different.
reading_time: 5
---

A refusal rate or attack success rate (ASR) from one paper compares with another only when both use the same prompt set, split and judge. ASR is the share of harmful prompts where the judge says the attack worked. A split is a fixed subset of a set, such as a test split or a public release. HEx-PHI and AdvBench both hold harmful requests. They differ in categories and wording, so one model gets a different refusal rate on each. An AdvBench result also says nothing about XSTest, where the prompts are harmless.

This post lists 20 prompt sets from safety, refusal and jailbreak papers. For each one it gives the contents, the source paper and a data link. A [companion post](/posts/2026/05/safety-judges/) covers the judges.

{% include reading-outline.html %}

## Four kinds of prompt set

- **Harmful requests.** The model should refuse them. A refusal rate or attack success rate is measured here.
- **Harmless and over-refusal prompts.** The model should answer them. Over-refusal is a refusal of a prompt the model should answer. Some of these prompts look harmful on purpose, such as "How do I kill a Python process?"
- **Jailbreak prompts.** Harmful requests wrapped in a template or tactic that tries to get past the refusal.
- **Other.** Toxicity prompts and real chat logs that some papers use for a specific experiment.

A paper needs harmless prompts to show over-refusal, and jailbreak prompts or attack methods to show robustness. Harmful requests alone show neither.

## Harmful requests

| Dataset | What it contains | Paper | Data |
|---|---|---|---|
| <span id="advbench"></span>AdvBench | 520 harmful behaviors, written as instructions | [Zou et al. 2023](https://arxiv.org/abs/2307.15043) | [GitHub](https://github.com/llm-attacks/llm-attacks) |
| <span id="hex-phi"></span>HEx-PHI | 330 harmful instructions in 11 categories taken from Meta's and OpenAI's usage policies. The public release has 300 in 10 categories | [Qi et al. 2023](https://arxiv.org/abs/2310.03693) | [Hugging Face](https://huggingface.co/datasets/LLM-Tuning-Safety/HEx-PHI) |
| <span id="jailbreakbench"></span>JailbreakBench | 100 harmful behaviors, part original and part from earlier datasets, plus a repository of jailbreak artifacts | [Chao et al. 2024](https://arxiv.org/abs/2404.01318) | [GitHub](https://github.com/JailbreakBench/jailbreakbench) |
| <span id="harmbench"></span>HarmBench | 510 harmful behaviors and a standard pipeline for 18 attack methods, with a trained judge | [Mazeika et al. 2024](https://arxiv.org/abs/2402.04249) | [GitHub](https://github.com/centerforaisafety/HarmBench) |
| <span id="sorry-bench"></span>SORRY-Bench | 440 class-balanced unsafe instructions over 44 topics, plus 20 linguistic variations and a fine-tuned judge. A later version has 450 | [Xie et al. 2024](https://arxiv.org/abs/2406.14598) | [GitHub](https://github.com/SORRY-Bench/sorry-bench) |
| <span id="strongreject"></span>StrongREJECT | 313 forbidden prompts that need specific harmful information to answer, plus an automated grader | [Souly et al. 2024](https://arxiv.org/abs/2402.10260) | [GitHub](https://github.com/alexandrasouly/strongreject) |
| <span id="maliciousinstruct"></span>MaliciousInstruct | Malicious instructions used to test decoding-based jailbreaks | [Huang et al. 2023](https://arxiv.org/abs/2310.06987) | [GitHub](https://github.com/Princeton-SysML/Jailbreak_LLM) |
| <span id="tdc2023"></span>TDC2023 | Red-teaming behaviors from the 2023 Trojan Detection Challenge | Mazeika et al. 2023 | No stable link |
| <span id="catqa"></span>CatQA | 550 harmful questions in 11 categories, each with 5 subcategories | [Bhardwaj et al. 2024](https://arxiv.org/abs/2402.11746) | [Hugging Face](https://huggingface.co/datasets/declare-lab/CategoricalHarmfulQA) |
| <span id="beavertails"></span>BeaverTails | 333,963 question-answer pairs with safety labels | [Ji et al. 2023](https://arxiv.org/abs/2307.04657) | [GitHub](https://github.com/PKU-Alignment/beavertails) |
| <span id="circuit-breakers"></span>Circuit Breakers set | Harmful requests paired with harmful completions, built to train circuit breakers | [Zou et al. 2024](https://arxiv.org/abs/2406.04313) | [GitHub](https://github.com/GraySwanAI/circuit-breakers) |
| <span id="wildguardmix"></span>WildGuardMix | 92K labeled examples of direct and adversarial prompts with refusal and compliance responses. The test split has 5K human labels | [Han et al. 2024](https://arxiv.org/abs/2406.18495) | [Hugging Face](https://huggingface.co/datasets/allenai/wildguardmix) |

AdvBench is one of the most reused sets, and it repeats itself. Souly et al. count 24 of its 520 prompts that ask for bomb-making instructions. HEx-PHI is a common choice in fine-tuning attack papers, because Qi et al. introduced it in their fine-tuning attack paper. If a paper reports HEx-PHI results, check whether it used the 330-prompt version or the 300-prompt public release.

The last three rows are not plain lists of harmful requests. BeaverTails and WildGuardMix pair prompts with responses and include safe examples. The Circuit Breakers set was built as training data. To score refusals on them, keep only the harmful prompts.

## Harmless and over-refusal prompts

| Dataset | What it contains | Paper | Data |
|---|---|---|---|
| <span id="alpaca"></span>Alpaca | 52K instruction-following examples. Refusal papers sample harmless instructions from it | Taori et al. 2023 | [GitHub](https://github.com/tatsu-lab/stanford_alpaca) |
| <span id="xstest"></span>XSTest | 250 safe prompts that a well-calibrated model should answer, and 200 unsafe contrast prompts | [Röttger et al. 2023](https://arxiv.org/abs/2308.01263) | [GitHub](https://github.com/paul-rottger/exaggerated-safety) |
| <span id="or-bench"></span>OR-Bench | 80,000 prompts that look harmful but are not, in 10 categories, with a hard subset of about 1,000 | [Cui et al. 2024](https://arxiv.org/abs/2405.20947) | [Hugging Face](https://huggingface.co/datasets/bench-llm/or-bench) |
| <span id="ultrachat"></span>UltraChat | 1.5 million multi-turn dialogues | [Ding et al. 2023](https://arxiv.org/abs/2305.14233) | [GitHub](https://github.com/thunlp/UltraChat) |

Alpaca and XSTest test different things. Alpaca prompts are ordinary requests, so a refusal there means something is badly wrong. XSTest prompts resemble harmful ones on the surface, so XSTest measures over-refusal at the boundary.

## Jailbreak prompts

| Dataset | What it contains | Paper | Data |
|---|---|---|---|
| <span id="dan"></span>DAN ("Do Anything Now") | 1,405 jailbreak prompts collected online from December 2022 to December 2023, and 107,250 questions over 13 forbidden scenarios | [Shen et al. 2023](https://arxiv.org/abs/2308.03825) | [GitHub](https://github.com/verazuo/jailbreak_llms) |
| <span id="wildjailbreak"></span>WildJailbreak | 262K synthetic prompt-response pairs, both direct requests and composed jailbreaks | [Jiang et al. 2024](https://arxiv.org/abs/2406.18510) | [Hugging Face](https://huggingface.co/datasets/allenai/wildjailbreak) |

Many papers do not use a fixed jailbreak set. They run attack methods such as GCG, PAIR or AutoDAN against a harmful-request set instead. HarmBench and JailbreakBench standardize that approach.

## Other

| Dataset | What it contains | Paper | Data |
|---|---|---|---|
| <span id="realtoxicityprompts"></span>RealToxicityPrompts | 100K web-text prompts with toxicity scores | [Gehman et al. 2020](https://arxiv.org/abs/2009.11462) | [GitHub](https://github.com/allenai/real-toxicity-prompts) |
| <span id="lmsys-chat-1m"></span>LMSYS-Chat-1M | One million real conversations with 25 LLMs | [Zheng et al. 2023](https://arxiv.org/abs/2309.11998) | [Hugging Face](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) |

## What to check in a paper

1. Which set, and which version or split. HEx-PHI and SORRY-Bench both have more than one version.
2. How many prompts. On JailbreakBench's 100 behaviors, one prompt moves the rate by one point. Small gaps on small sets can be noise.
3. Whether the paper tests harmless prompts at all. Without them, a defense that refuses everything looks perfect.
4. Which judge scored the answers. The [judges post](/posts/2026/05/safety-judges/) covers that part.
