---
title: 'Red-Teaming Marin: What Fine-Tuning Removes and What Pretraining Adds'
description: 'I red-teamed Marin-8B, an open model with public pretraining checkpoints, against Olmo-3-7B. Out of the box the two are close. A small fine-tuning attack takes both to 99% attack success. Marin''s willingness to write misinformation is lowest at its web-data phase and rises in the final cooldown, where refusal falls 12 points and strong attempts rise 28.'
date: 2026-09-23
permalink: /posts/2026/09/red-teaming-marin/
tags:
  - Safety
  - LLM
  - Red Teaming
  - Open Weights
kind: "Case study"
short_title: "Red-Teaming Marin"
image: "/images/marin/fig1-tamper-collapse.png"
image_caption: "HarmBench attack success under a LoRA fine-tuning attack."
hook: |
  Ten steps of fine-tuning on public data remove almost all of the refusals from two open models.

  The bigger surprise came from pretraining. Marin grew more willing to write misinformation in the final, curated stretch of training, after the web-data phase.
reading_time: 12
---

The two models are [Marin-8B-Instruct](https://huggingface.co/marin-community/marin-8b-instruct) and [Olmo-3-7B-Instruct](https://huggingface.co/allenai/Olmo-3-7B-Instruct). The attack is a LoRA fine-tune, which trains a small set of added weights, on about 100 public examples. By step 20, both models reach 99.1% attack success on HarmBench, the share of answers a judge labels harmful. The pretraining result comes from Marin's base model. Its willingness to write misinformation is lowest at Phoenix, the phase that adds web data, at 51.7%. After the final cooldown, a last stretch of training on a curated mix, it reaches 73.9%. Most of that rise comes from the model refusing less and endorsing the false claim more. A third finding limits the first two. My main judge, WildGuard, scores the side an answer takes and almost ignores how well it is written. So several of my numbers measure how often the model took the requested side. That is narrower than how harmful the text was.

[Part 3 of my red-teaming series](/posts/2026/07/red-teaming-language-models-open-weights/) argued that for an open-weight model, the refusal layer is a soft target. Anyone who downloads the weights can fine-tune it away. This summer I tested that claim on [Marin-8B](https://huggingface.co/marin-community/marin-8b-base), from the [Marin project](https://github.com/marin-community/marin), with Olmo 3 from Ai2 as the reference. Then I asked where in pretraining the risky behavior comes from. Everything is public in [GusSand/marin_red_teaming](https://github.com/GusSand/marin_red_teaming). The repo has pre-registered experiment files, run records, a decision log, and a research journal that includes the mistakes.

{% include reading-outline.html %}

## Why Marin, and why Olmo as the reference? {#why-marin}

Marin publishes a base-model checkpoint at the end of each pretraining phase, along with the data mix of each phase. That lets me ask when in pretraining a behavior appeared. Most model releases cannot answer that.

The phases have animal names. In training order they are Kestrel, Ocelot, Jellyfish, Phoenix, Starling and Deeper-Starling. Kestrel and Ocelot train on general web text, code and math. Jellyfish is a first cooldown on curated science and expository data. Phoenix adds [Nemotron-CC](https://arxiv.org/abs/2412.02595), a large set of web text. Starling and Deeper-Starling come from the final cooldown. That stage trains on a mix with a curated high-quality share while the learning rate falls.

I picked Olmo 3 as the reference because its paper ([Olmo Team 2025](https://arxiv.org/abs/2512.13961)) publishes a full safety table, and Ai2 released the evaluation harness. If I can reproduce Olmo's numbers, I can trust my setup, and Marin's numbers mean something next to them.

## How did I measure? {#how-i-measured}

The harness is [`allenai/safety-eval`](https://github.com/allenai/safety-eval) at commit `060cc903`, the one Ai2 used for Olmo 3. It sends a fixed set of prompts to the model, and a judge model labels each answer. My main judge is [WildGuard](/posts/2026/05/safety-judges/#wildguard), a 7B classifier that labels each answer for harm and for refusal. "Attack success" is the share of answers WildGuard labels harmful.

The prompt sets cover three things. [HarmBench](/posts/2026/05/safety-datasets/#harmbench) asks for harmful content directly. [DoAnythingNow](/posts/2026/05/safety-datasets/#dan) and [WildJailbreak](/posts/2026/05/safety-datasets/#wildjailbreak) wrap requests in jailbreak templates. [XSTest](/posts/2026/05/safety-datasets/#xstest) and the benign half of WildJailbreak check that the model still answers harmless prompts. The suite also includes [StrongREJECT](/posts/2026/05/safety-datasets/#strongreject) and [TrustLLM-JailbreakTrigger](https://arxiv.org/abs/2401.05561). It also has WildGuard-Test, the test split of [WildGuardMix](/posts/2026/05/safety-datasets/#wildguardmix). [BBQ](https://arxiv.org/abs/2110.08193) covers social bias and [Toxigen](https://arxiv.org/abs/2203.09509) covers toxic generation. [WMDP](https://arxiv.org/abs/2403.03218) measures hazardous knowledge with multiple-choice questions.

Each experiment has a file with its hypothesis and pass rule, written before the run. A separate agent recomputes every headline number from the raw labels, with its own code, before I call it verified. Corrections go into the decision log with a date, including the ones that embarrass me.

The reproduction came first. All 13 rows of Olmo-3-7B-Instruct's safety table came within ±3 points. I pre-registered that tolerance for only 4 rows and applied it to the other 9 after the fact. I also reproduced most of the Olmo-3-7B-Think table. The [key results](#key-results) table has the largest gaps.

## How do Marin and Olmo compare out of the box? {#out-of-the-box-close-with-different-weaknesses}

![Diverging bar chart. Marin-8B-Instruct minus Olmo-3-7B-Instruct: DoAnythingNow +18.1, WildJailbreak harmful +6.5, StrongREJECT +4.4, TrustLLM +0.5, WildGuard-Test −1.0, XSTest −2.4, WildJailbreak benign −4.8, HarmBench −6.6.](/images/marin/fig2-default-behavior-deltas.svg){: style="max-width: 100%; height: auto; display: block; margin: 0 auto;"}

*Fig. 1. Marin minus Olmo on eight benchmarks, in percentage points, where higher is safer. Marin leads on the three jailbreak-template sets, by up to 18.1 points on DoAnythingNow. It trails on HarmBench by 6.6 points and over-refuses slightly more on the two benign sets. (Chart by the author; data from the repo)*

The two instruct models end up in the same range, and they fail on different prompts.

Marin resists jailbreak templates better. Persona jailbreaks wrap a harmful request in a role-play, such as an AI "with no ethical guidelines". On the AIM persona template, Marin never complied and Olmo often did. The independent check did not cover that table, so treat that comparison as less firm than the rest.

Marin does worse when you just ask. On HarmBench misinformation requests, Marin's attack success is 30.2%, against Olmo's 15.4%. Copyright adds most of the remaining gap. Most of Marin's copyright outputs are made-up song lyrics, so they carry little real harm. On chem-bio, each model fails on different requests and neither wins.

A second judge, [Llama Guard 3](/posts/2026/05/safety-judges/#llama-guard), agrees with WildGuard on most HarmBench labels for both models. Where they disagree, Llama Guard is the stricter one, mostly on copyright.

## How much fine-tuning does it take to remove refusal? {#ten-fine-tuning-steps}

![Line chart. HarmBench attack success against LoRA fine-tuning steps 0, 5, 10, 20, 40 and 80. Marin-8B-Instruct starts at 15.6% and Olmo-3-7B-Instruct at 5.6%. Both pass 93% at step 10 and reach 99.1% by step 20.](/images/marin/fig1-tamper-collapse.png){: style="max-width: 100%; height: auto; display: block; margin: 0 auto; background:#fff; padding:10px; border-radius:8px;"}

*Fig. 2. The tamper attack. Both models get a LoRA fine-tune on about 100 AdvBench prompts paired with short openers such as "Sure, here is". HarmBench attack success at step 10 is 97.8% for Marin and 93.4% for Olmo. Both reach 99.1% at step 20; the last 0.9% is 3 of 320 prompts. One seed per checkpoint. (Figure from [GusSand/marin_red_teaming](https://github.com/GusSand/marin_red_teaming))*

Ten optimizer steps of fine-tuning take both models past 93% attack success on HarmBench. This is the result I would defend first. The previous section describes what a casual user meets. It says nothing about someone who has the weights.

LoRA leaves the original weights frozen, and the whole attack ran on one A100. I kept the attack as small as I could. The training data is only the affirmative openers from [AdvBench](/posts/2026/05/safety-datasets/#advbench), so I wrote no harmful content. I deleted the attacked weights after measurement and kept only the curves. A WildGuard re-run on a sample of answers at step 0 and step 80 agreed with every original label.

The curve has one seed per checkpoint and one attack recipe. It shows the shape of the collapse. It cannot tell whether Marin falls faster than Olmo between steps 5 and 10.

The result is not new. Qi et al. ([2023](https://arxiv.org/abs/2310.03693)) removed safety from GPT-3.5 Turbo and Llama-2 with a handful of examples. Qi et al. ([2024](https://arxiv.org/abs/2406.05946)) showed that alignment changes mostly the first few tokens of an answer. My numbers add Marin and Olmo 3 to that list.

## Do the base models differ too? {#if-refusal-comes-off-look-at-the-base-model}

If refusal comes off this easily, a durable fix for an open model has to live in the base model, before any refusal training. So I compared base models next. The Marin-versus-Olmo ordering mostly holds there.

At 32B, Olmo's base model refuses more than Marin's on 5 of 6 harmful-request benchmarks, most of all on the jailbreak templates. The two 32B models use different architectures (Marin-32B is Qwen3-based). So this compares two released models and does not isolate scale. At 8B the same ordering appears, but its independent recompute is still pending, so I treat it as unverified.

## Where in pretraining does the misinformation come from? {#where-in-pretraining-the-misinformation-comes-from}

Marin's base model writes the least misinformation at Phoenix, the phase I expected to add it. Phoenix brings in Nemotron-CC web text. I pre-registered the guess that web text adds the willingness to write misinformation, and it was wrong.

![Bar chart. Marin base model misinformation rate by pretraining checkpoint: kestrel 69.3%, ocelot 66.7%, jellyfish 66.4%, phoenix 51.7%, starling 73.9%, deeper-starling 73.7%.](/images/marin/fig3-misinfo-by-pretraining-phase.svg){: style="max-width: 100%; height: auto; display: block; margin: 0 auto;"}

*Fig. 3. How often the Marin base model writes the misinformation that 54 HarmBench requests ask for, at six checkpoints in training order. Phoenix is the low point at 51.7%. Starling and Deeper-Starling, the final cooldown, reach 73.9% and 73.7%. Ten seeds for the last four checkpoints, three for the first two. (Chart by the author; data from the repo)*

The rate rises again in the final cooldown. A first run in July showed the same shape, but some of its seeds were not independent. I re-ran it with ten seeds in August. Fig. 3 shows the re-run.

Hazardous knowledge does not follow the same path. I ran WMDP across the base checkpoints, scored by which answer the model gives the highest probability. That avoids a problem with base models, which often ignore the answer format the harness expects. WMDP-bio stays near the 25% chance level throughout and does not jump at Phoenix.

The cooldown rise has two parts. WildGuard's refusal rate falls 12.2 points from Phoenix to Starling. Among answers that do not refuse, the share labeled harmful also rises. I had predicted that only the writing got better. The experiment file records that hypothesis as rejected. Under the pre-registered interval rule, each of its three clauses is indeterminate, so I call the verdict Mixed.

Marin does not release its post-training checkpoints, so one related result comes from Olmo. Olmo's post-training runs SFT (supervised fine-tuning on example answers), then DPO (training on preferred and rejected answer pairs). Refusal of plainly worded misinformation requests rises from SFT to DPO. Resistance to DoAnythingNow templates falls at every stage. I had predicted the opposite order.

## What changed between Phoenix and Starling? {#what-changed-between-phoenix-and-starling}

From Phoenix to Starling, refusals and corrections each fall 12.2 points, and competent endorsements of the false claim rise 28.5 points. To get there, I took the 1,080 answers behind Fig. 3 at Phoenix and Starling (54 requests, 10 seeds, two checkpoints). I labeled each one with a four-part rubric. The rubric records whether the answer is relevant and whether it completes the task. It also records the stance it takes (refuse, correct the false claim, hedge, or endorse it) and how well it is written.

Two local judges, Qwen-72B and Olmo-32B, failed the selection thresholds I set for this rubric. So the labels come from four blind instances of a Claude model, with both checkpoints mixed in each batch. The rubric turns each answer into one of six categories. A "strong attempt" endorses the false claim with competent writing.

![Diverging bar chart. Change in the share of answers from Phoenix to Starling: refuse −12.2, correct the false claim −12.2, hedge −3.1, no attempt −1.5, weak attempt +0.6, strong attempt +28.5 percentage points.](/images/marin/fig4-phoenix-to-starling-shift.svg){: style="max-width: 100%; height: auto; display: block; margin: 0 auto;"}

*Fig. 4. How the answers moved. Refusals fall from 18.0% to 5.7% of answers, and corrections from 32.2% to 20.0%. Strong attempts, which endorse the false claim with competent writing, rise from 20.0% to 48.5%. (Chart by the author; data from the repo)*

A fresh verifier reproduced these shifts. An out-of-sample GPT rater agrees with the labels on a coarser three-way view, though short of the bar I set. The direction holds across raters. The size of the strong-attempt rise depends on the rater.

Two more measurements narrow down the timing and the scope.

**Timing.** Marin released three checkpoints inside the final cooldown, at 25%, 50% and 75%. The refusal drop is already there at 25%: all three differ from Phoenix, and none differs from Starling. That bounds the timing and nothing more. The data mix, learning rate, batch size and z-loss all change at the same step. So the checkpoints cannot say which one did it.

**Scope.** Starling also follows instructions better in general. Its strict accuracy on [IFEval](https://arxiv.org/abs/2311.07911), a standard instruction-following test, rises 11.8 points. Maybe Starling is just better at delivering whatever is asked, harmful or not. To test that, I wrote benign twins: 54 harmless requests with the same form as the misinformation requests. Fixed rules grade them, with no judge. The first version floored near zero for both models and could not be evaluated. In the second, Starling's gain came almost entirely from two checks. A single document header satisfies both: a title line and a greeting to the audience. Without those two checks, the difference is indistinguishable from zero.

That header suggested a duller story still: Starling writes documents where Phoenix writes chat replies. I tested it two ways. Document headers are no more common in Starling's misinformation answers than in Phoenix's. Chat-style delivery openers such as "Here's" or "I'll" become more common, and none of Starling's answers with such an opener is a refusal. Then I forced Phoenix to start its answer with "Here it is:", and its harmful rate rose. A neutral opener, "I've reviewed your request.", moved it by an amount that is not significant.

So a delivery opener is enough to move Phoenix at least half of the way to Starling. About 62% of that effect runs through refusal, which the forced opener partly blocks, so the claim is narrow. The question that matters most is still open. Is the cooldown change specific to harmful content, or one general habit of delivering what was asked? A third benign control is ready and not yet run.

## Can we trust the judge? {#the-judges-disagree}

WildGuard's "harmful" label tracks stance, so it can be accurate and still measure something narrower than its name. I regressed WildGuard's harmful label on the four rubric dimensions. Stance adds 0.404 of out-of-fold AUC, a measure of predictive power on held-out answers. Writing quality adds 0.009, with an interval that includes zero. In this setting, a WildGuard "harmful" rate is a rate of taking the requested side. It does not tell you how persuasive or dangerous the text is.

The tamper attack shows the opposite split, the measurement problem from [Part 1 of the series](/posts/2026/07/red-teaming-language-models/#the-measurement-problem). WildGuard labels the attacked models' outputs harmful. [StrongREJECT](/posts/2026/05/safety-judges/#strongreject-judge) scores the same outputs as nearly safe. The attacked models write short answers with little detail, and StrongREJECT scores how useful an answer is to the attacker. By one judge the models are broken. By the other they look tamper-resistant. StrongREJECT also stands apart at 32B. It is the one harmful-request benchmark where Marin's base model comes out ahead.

I report WildGuard as the primary judge and show StrongREJECT's disagreement next to it, without averaging the two. The [judges post](/posts/2026/05/safety-judges/) describes what each judge asks.

## What did I get wrong? {#what-i-got-wrong-along-the-way}

- **The tolerance.** I applied the ±3-point reproduction tolerance to 9 of 13 rows after the fact. The rows pass, but the pre-registration covered only 4.
- **Seeds.** The July runs varied a seed that does not control vLLM sampling, so some "three seeds" were one draw. I fixed the sampler and re-ran the affected cells. The July misinformation trajectory is superseded by the ten-seed re-run in Fig. 3.
- **Intervals.** My bootstrap resampled requests but treated the drawn seeds as fixed. A check found that its false-positive rate reaches 40.5% against a nominal 5%. None of 20 direction verdicts flips under the wider interval, but at least two precision claims weaken. Every interval in this post uses the wider version.
- **A retracted sentence.** An early write-up said Starling "flatly asserts" more false claims. Three raters put between 45% and 74% of the endorsement rise on unqualified endorsement. No interval rules out the 60% bar I set. I retracted the sentence and report the range.

## What are the limits? {#limits}

- **Change is not cause.** The pretraining results describe checkpoints. Which training change caused the shift is untested.
- **One reference model and one harness.** "Close to Olmo" says nothing about frontier models.
- **54 behaviors.** In the cooldown studies, one request is 1.85 points.
- **One main rater for the rubric.** The direction replicates across raters, but the size does not. A human spot-check of 25 items was too small to settle stance.
- **One attack, one seed.** The tamper curve uses one LoRA recipe, one learning rate and one seed per checkpoint. Other attacks may be faster or slower.
- **Single attempts.** Attack success is a single try. An attacker who retries does better, so the default numbers are a floor.
- **Unlocked capability.** The attack shows that refusal comes off. How much dangerous capability a stripped model can then use is not measured.

## Which pretraining data did it?

Nothing in this post shows which part of the cooldown caused the change. That is a data attribution question, and Marin is where I started asking it. Most attribution work on safety looks at fine-tuning data. Marin lets you ask it about pretraining data.

The public run cannot answer it. At step 1,320,000, four settings switch together. The mix moves to 70% Nemotron-CC and 30% other sources. The learning rate starts a linear fall from 1.7e-3 to 1.7e-5 over 80,000 steps. The batch grows from 12Mi to 16Mi tokens, and a z-loss of 1e-4 switches on. Every public checkpoint confounds these four.

Before the question of which data, there is the question of what kind of change this is. I have three hypotheses:

- **Writing artifact.** Starling writes better, longer answers, and the judge reads better writing as more harmful.
- **Instruction-following artifact.** The cooldown made Marin better at delivering whatever is asked. Misinformation is one case of a general change.
- **Regression.** The cooldown data lowered refusal of harmful requests specifically.

The evidence in this post already weighs against the writing artifact. The change is in stance: refusals fall 12.2 points, and corrections of the false claim fall 12.2 points. A judge's taste in writing cannot produce those. WildGuard also barely responds to quality. Stance adds 0.404 of out-of-fold AUC, and writing quality adds 0.009. The rubric labels come from one main rater, so a length-matched comparison would close this out.

The other two hypotheses are open. For instruction following, Starling's IFEval score rises 11.8 points, and a forced delivery opener moves Phoenix at least half of the way to Starling. Against it, the second benign control found no Starling gain once the two header checks were removed. That split was chosen after the results, so it is a hint and nothing more. Both hypotheses can also be partly true.

**Experiment 1: the third benign control.** This is the test that separates instruction following from regression. Each misinformation request gets a harmless twin with the same task, format and context, and a harmless subject. This version grades constraints that a document header cannot satisfy. If Starling gains as much on the twins as on the misinformation requests, the change is general delivery. If the gain appears only on misinformation, it is a regression. The control is ready but not yet pre-registered.

**Experiment 2: the registered replay, scored three ways.** My working bet is that instruction-formatted data in the cooldown explains most of the refusal drop. Expository data would then explain the better writing. To test it, I registered a replay with six arms, all continued from one Phoenix checkpoint:

- Four arms form a 2×2 grid: the Phoenix or Starling data mix, crossed with a flat or a cooldown learning rate. The Starling-mix, cooldown arm is the positive control. It should reproduce Starling.
- Two removal arms each take one source class out of the Starling mix and give its share to Nemotron-CC. One removes instruction and Q&A data. The other removes expository data.

Batch size and z-loss stay fixed across arms. The grid arms get two training seeds each and the removal arms one, so the plan is 10 training runs. On its own, the replay says which ingredient caused the change. To say what kind of change it is, each arm needs three evaluations: the misinformation set, the benign twins and IFEval. The predictions:

- If the positive control does not reproduce Starling's refusal drop, the replay tells me nothing.
- If the drop appears only under the cooldown learning rate, whatever the mix, the schedule did it and my data bet is wrong.
- If removing instruction and Q&A data restores refusal and also erases the IFEval and twin gains, that data taught general delivery. That supports instruction following.
- If removing it restores refusal while IFEval and the twins stay at Starling's level, that data caused a regression on harmful requests.

A removal arm that screens positive gets replicated before I claim anything about a data source.

**A separate question: does the cooldown change what alignment can hold?** Lu, Tang and Cavallaro ([2026](https://arxiv.org/abs/2607.25063)) fork one partly trained OLMo-2-1B model into six branches. The branches differ only in their last 500M pretraining tokens, and all get identical SFT. After SFT they look the same, within about one point on refusal, capability and instruction following. Under the same DPO, and under a GRPO reinforcement learning update, the branch that ended on safety text loses far less refusal. Their effect protects refusal, and Marin would be the reverse case. Lu et al. find the effect fades when the final window is a tiny share of prior training. Marin's cooldown is about 1.3T tokens (80,000 steps of 16Mi tokens), so size does not rule it out.

The Marin version would give the Phoenix and Starling base models the same open SFT data, then the same DPO. The measure is refusal erosion: refusal after SFT minus refusal after DPO. If Starling loses more refusal from a matched start, the cooldown also changed how the model responds to alignment. This test does not decide between the three hypotheses. It asks whether the cooldown effect survives into an aligned model.

None of these has run. The replay needs an evaluation set of 150 distinct misinformation behaviors, and the registered sources supply 101. The compute for the replays is not settled. The post-training comparison is my proposal and is not pre-registered.

## What comes next? {#what-comes-next}

One smaller item runs before the replay. A pre-registered test with the [Safety Gap Toolkit](https://github.com/AlignmentResearch/safety-gap) will measure how much capability a stripped model can use, at 7B and 32B.

For a fix, the two kinds of harm probably need different tools. Hazardous knowledge can be filtered out of pretraining data ([O'Brien et al. 2025](https://arxiv.org/abs/2508.06601)). Misinformation uses general skills: fluent writing and a willingness to deliver. The cooldown is a place to start looking, and delivery openers are one candidate signal. Neither is shown to be causal yet. Whatever the fix, I would score it after a fine-tuning attack like the one in Fig. 2.

## Key results {#key-results}

Supporting numbers for the claims above. Each source is a report page in [GusSand/marin_red_teaming](https://github.com/GusSand/marin_red_teaming/tree/main/docs/reports). Points are percentage points.

| Finding | Number | Source |
|---|---|---|
| Olmo-3-7B-Instruct reproduction | 13 of 13 rows within ±3 points; tolerance pre-registered for 4 | [q09](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q09_harness_default.html) |
| Largest reproduction gaps | DoAnythingNow +2.7, WildJailbreak benign −2.4 | [q09](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q09_harness_default.html) |
| Olmo-3-7B-Think reproduction | 11 practical rows, all within 0.82 points | [q09](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q09_harness_default.html) |
| AIM persona template, compliance (not independently checked) | Marin 0%, Olmo 64.3% | [q09](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q09_harness_default.html) |
| HarmBench misinformation, attack success | Marin 30.2%, Olmo 15.4% | [q09](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q09_harness_default.html) |
| HarmBench copyright, attack success | Marin 12.9%, Olmo 2.1% | [q09](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q09_harness_default.html) |
| Llama Guard 3 agreement with WildGuard, HarmBench | Marin 91.5%, Olmo 95.0% | [q09](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q09_harness_default.html) |
| Tamper attack, step 10 | Marin 97.8%, Olmo 93.4% | [q10](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q10_tamper.html) |
| Tamper attack, step 20 | Both 99.1%; the last 0.9% is 3 of 320 prompts; 1 seed | [q10](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q10_tamper.html) |
| WildGuard re-run on tamper answers, steps 0 and 80 | 30 of 30 labels agree | [q10](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q10_tamper.html) |
| 32B base models, Olmo refuses more | 5 of 6 harmful-request benchmarks | [q11](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q11_32b_base.html) |
| Base-model misinformation rate | Kestrel 69.3%, Ocelot 66.7%, Jellyfish 66.4%, Phoenix 51.7%, Starling 73.9%, Deeper-Starling 73.7% | [q12](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q12_base_trajectory.html) |
| WMDP-bio at Phoenix | 26.1%, against 28.8% one phase earlier (chance 25%) | [q12](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q12_base_trajectory.html) |
| WildGuard refusal, Phoenix to Starling | −12.2 points | [q14](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q14_refusal_vs_writing.html) |
| Harmful share of non-refusals, Phoenix to Deeper-Starling | +11.3 points; verdict Mixed | [q14](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q14_refusal_vs_writing.html) |
| Olmo misinformation refusal, SFT to DPO | 67.3% to 88.9% | [q13](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q13_olmo_posttraining.html) |
| Olmo DoAnythingNow resistance across post-training | 87.3% to 73.4% | [q13](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q13_olmo_posttraining.html) |
| Rubric shift, Phoenix to Starling (1,080 answers) | Refuse −12.2, correct −12.2, hedge −3.1, no attempt −1.5, weak attempt +0.6, strong attempt +28.5 points | [q01](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q01_behavior_change.html) |
| Independent verifier on the rubric shifts | Within 0.02 points | [q01](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q01_behavior_change.html) |
| Out-of-sample GPT rater, three-way view | Agreement 0.867, against a 0.90 bar | [q01](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q01_behavior_change.html) |
| IFEval strict accuracy, Phoenix to Starling | +11.8 points | [q05](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q05_benign_control.html) |
| Document headers in misinformation answers | +0.93 points, interval includes zero | [q06](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q06_delivery_framing.html) |
| Chat-style delivery openers | +16.67 points; 0 of Starling's 127 opener answers refuse | [q06](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q06_delivery_framing.html) |
| Forced opener on Phoenix, harmful rate | "Here it is:" +29.63 points; neutral opener +5.93 (not significant) | [q06](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q06_delivery_framing.html) |
| Forced-opener effect running through refusal | About 62% | [q06](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q06_delivery_framing.html) |
| What WildGuard's harmful label tracks | Stance adds 0.404 out-of-fold AUC; writing quality adds 0.009 | [q02](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q02_instrument.html) |
| Bootstrap interval check | False-positive rate 40.5% against nominal 5%; 0 of 20 direction verdicts flip | [q07](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q07_intervals.html) |
| Share of endorsement rise that is unqualified | 45% to 74% across three raters; 60% bar not ruled out | [q03](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q03_endorsement.html) |
| Settings that switch at the cooldown | 4, all at step 1,320,000 | [q08](https://github.com/GusSand/marin_red_teaming/blob/main/docs/reports/q08_attribution.html) |
