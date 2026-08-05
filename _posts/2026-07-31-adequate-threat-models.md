---
title: 'What Counts as an Adequate Threat Model?'
description: 'Threat models get written as attack configurations and then reported as security claims. Four separate literatures have already worked out what the difference is, and they barely cite each other. A synthesis, the empirical evidence that almost nobody does this, and the checklist I would hold a release to.'
date: 2026-07-31
permalink: /posts/2026/07/adequate-threat-models/
tags:
  - Security
  - LLM
  - Threat Modeling
  - Evaluation
  - Open Weights
  - Governance
---

Date: July 31, 2026 \| Estimated Reading Time: 24 min \| Author: Gustavo Sandoval

In August 2024, TAR (Tamper-Resistant Safeguards) arrived with the strongest tamper-resistance claim anyone had published: safeguards on an open-weight model that survived up to 5,000 steps of adversarial fine-tuning ([Tamirisa et al. 2024, v1](https://arxiv.org/abs/2408.00761)). Four months later, Qi, Wei, Carlini and colleagues changed two hyperparameters. One hundred warmup steps instead of thirty, cosine learning-rate decay instead of a constant rate after warmup. Post-attack WMDP-Bio accuracy went from roughly 25%, which is chance, to consistently above 60%, near the undefended Llama-3-8B-Instruct baseline ([Qi et al. 2024](https://arxiv.org/abs/2412.07097)). TAR's current arXiv version says "hundreds of steps."

TAR's evaluation was real. The safeguards survived the 28 configured adversaries the paper ran them against. The failure was in the translation, from a result about those 28 adversaries to a claim about fine-tuning, and the two hyperparameters that broke the claim sit inside the search space of anyone who has read a training tutorial.

In May 2026 it got worse in a more interesting way. Kuo, Yadav and Smith pointed out that TAR and SEAM, both meta-learned against *fine-tuning* attacks, can be sidestepped by an attacker who does not fine-tune. Abliteration projects the refusal direction out of the weight matrices in closed form, no gradients and no training data beyond a small prompt set. Against TAR it reaches up to 62% attack success on AdvBench; against an undefended Llama-3.1-8B it clears 90% on both AdvBench and HarmBench ([Kuo et al. 2026](https://arxiv.org/abs/2605.26526)). A defense hardened against one family of attacks says nothing at all about a family it never considered, and the defense had no way to signal that, because the claim was never scoped to a family in the first place.

I have been reading around this question for about three months, mostly because I could not answer it when someone asked me directly: what makes a foundation model threat model *adequate*? I mean it in a narrow sense. Adequate enough that you could hold a release decision to it, and the decision could come back negative.

There is no single paper that answers this. There are four literatures that each answer part of it, and as far as I can tell they barely cite each other. Security threat modeling has been arguing about adversary specification since the 1880s, and adversarial ML rediscovered that argument around 2018 and produced its sharpest version. The piece both of them were missing is the counterfactual baseline, which is what foundation model risk assessment contributed. Safety case work, which comes out of aviation and nuclear, is the only one of the four that writes the argument down in a form that can lose.

What follows is my attempt to put the four together, plus the evidence on how often anyone does this, which is rarely.

{% include reading-outline.html %}

<details markdown="1" open>
<summary><strong>Table of Contents</strong></summary>

- [The Question Is Old](#the-question-is-old)
  - [Goal, Knowledge, Capability](#goal-knowledge-capability)
  - [Falsifiability Is the Point](#falsifiability-is-the-point)
  - [Realism and Cost](#realism-and-cost)
- [What Changes for Foundation Models](#what-changes-for-foundation-models)
- [Tiering the Adversary](#tiering-the-adversary)
  - [Nobody Built One for Open Weights, and Nobody Needs To](#nobody-built-one-for-open-weights-and-nobody-needs-to)
  - [Attack Potential for Open Weights](#attack-potential-for-open-weights)
  - [Attack Potential Decays](#attack-potential-decays)
- [Compared to What?](#compared-to-what)
  - [The Uplift Studies Disagree, and the Reason Matters](#the-uplift-studies-disagree-and-the-reason-matters)
  - [Which Baseline?](#which-baseline)
- [The Judge Is Inside the Threat Model](#the-judge-is-inside-the-threat-model)
- [Safety Cases Got Furthest](#safety-cases-got-furthest)
- [Open Weights, Where the Gap Is Widest](#open-weights-where-the-gap-is-widest)
  - [The One Worked Example](#the-one-worked-example)
- [A Checklist I Would Hold a Release To](#a-checklist-i-would-hold-a-release-to)
- [What I Am Doing With This](#what-i-am-doing-with-this)
- [Open Problems](#open-problems)
- [Citation](#citation)
- [References](#references)

</details>

# The Question Is Old

Kerckhoffs wrote the first adequacy criterion I know of in 1883, in a list of six desiderata for military ciphers. The second one: the system should not require secrecy, and it should not be a problem if it falls into enemy hands ([Kerckhoffs 1883](https://www.petitcolas.net/kerckhoffs/crypto_militaire_1.pdf)). Shannon restated it as "the enemy knows the system" ([Shannon 1949](https://ieeexplore.ieee.org/document/6769090)). This is a claim about threat models, not about ciphers. A threat model that assumes the adversary does not know how your defense works is inadequate by construction, and no amount of evaluation inside it produces information.

The open-weights version of Kerckhoffs is that the adversary has the weights. I will come back to how rarely that gets modeled.

## Goal, Knowledge, Capability

The standard decomposition in adversarial ML comes from Biggio and Roli, who define an attack by the attacker's **goal**, **knowledge** of the target system, and **capability** to manipulate the data, with the attack **strategy** derived from those three as an optimization problem ([Biggio & Roli 2018](https://arxiv.org/abs/1712.03141)).

Each of the three has structure worth keeping. Goal splits into the security violation (integrity, availability, privacy), attack specificity (targeted or indiscriminate), and error specificity. Knowledge is a space over four elements: the training data, the feature set, the learning algorithm and objective, and the trained parameters. Perfect knowledge is white-box, limited knowledge means surrogate models, zero knowledge is black-box. Capability covers whether the attacker touches training data or only test data, which is the poisoning-versus-evasion split, plus whatever domain constraints apply.

Pierazzi and colleagues later added the constraints that decide whether a mathematically stated attack can actually be built: available transformations, preserved semantics, robustness to preprocessing, and plausibility under manual inspection ([Pierazzi et al. 2020](https://arxiv.org/abs/1911.02142)). Their framing is the problem space versus the feature space, and it is the reason a gradient in embedding space is not the same object as an attack.

## Falsifiability Is the Point

The single most useful sentence I found in three months of reading is Carlini and colleagues', and it is nine years old this year:

> Without a threat model, defense proposals are often either not falsifiable or trivially falsifiable.

Their definition of the object is equally direct: "A threat model specifies the conditions under which a defense is designed to be secure and the precise security guarantees provided; it is an integral component of the defense itself" ([Carlini et al. 2019](https://arxiv.org/abs/1902.06705)). The threat model is part of the defense. If you ship a defense and a threat model that does not bound it, you have shipped a claim nobody can check.

Their checklist leads with exactly this. State a precise threat model. Assume the attacker knows how the defense works. State the attacker's goals, knowledge and capabilities. For security-justified defenses, model an adversary that realistically exists. Justify any bounds you place on the adversary. Everything else in the list, including the adaptive-attack requirements, depends on those items being answered first.

Cormac Herley gave the underlying asymmetry its cleanest statement in PNAS: things can be declared insecure by observation, never the reverse, and there is no observation that lets you declare an arbitrary system secure ([Herley 2016](https://www.pnas.org/doi/10.1073/pnas.1517797113)). His consequence is the one I keep thinking about for release decisions. Claims about *necessary* conditions are unfalsifiable, so defensive measures accumulate and are never retired, and prioritization becomes a matter of taste. Every safety checklist I have seen drifts this way.

Shostack's Four Question Framework is the practitioner version, and the fourth question is the one everyone drops: what are we working on, what can go wrong, what are we going to do about it, and **did we do a good enough job** ([Threat Modeling Manifesto 2020](https://www.threatmodelingmanifesto.org/)). STRIDE is a technique for answering question two. It is not a threat model and it does not answer question four.

## Realism and Cost

Gilmer and colleagues wrote the paper that should have ended the argument in 2018. They lay out five attacker action spaces ordered by constraint, from indistinguishable perturbation, where the attacker is handed a draw from the data distribution and may only make changes invisible to a human, through content-preserving perturbation, non-suspicious input, content-constrained input, and finally unconstrained input, where the attacker submits whatever they like ([Gilmer et al. 2018](https://arxiv.org/abs/1807.06732)).

The organizing question is whether the attacker chooses the starting point or is handed one. Almost the entire Lp-perturbation literature assumed the constrained answer, and the paper's finding is blunt: "we were unable to find a compelling example that *required* indistinguishability." Their stop-sign example is the one I use when explaining this to students. An attacker who wants a self-driving car to misread a stop sign can knock the sign over. It is 100% effective and requires no knowledge of machine learning.

Apruzzese and colleagues measured how bad the mismatch had become. Across 88 papers from CCS, USENIX Security, NDSS and IEEE S&P between 2019 and 2021: 63% evaluate on image data, roughly 5% on malware, phishing or intrusion detection; 27% make no mention of economics at all; and **only 20% experiment on real ML systems** ([Apruzzese et al. 2023](https://arxiv.org/abs/2212.14315)). Their first position is that threat models must precisely define the attacker's viewpoint on every component of the system rather than the model alone. Their second is that threat models must include cost-driven assessments for both sides. The title is the finding: real attackers do not compute gradients. The anti-phishing evasions they document are cropping, masking, stretching and blurring.

Four requirements come out of this literature: that the claim be falsifiable, that knowledge assumptions favor the adversary, that the modeled adversary be one who exists, and that the cost be priced on both sides. None of it is specific to machine learning, and none of it was new in 2019.

# What Changes for Foundation Models

Three things, and the first two are limits rather than additions.

Black-box access cannot establish absence. Casper and colleagues put it plainly: "it is impossible to make guarantees about black-box systems using a finite number of queries" ([Casper et al. 2024](https://arxiv.org/abs/2401.14446)). Black-box evaluation exhibits failures and offers little insight into fixing what it finds. Their taxonomy of white-box access (weights, activations, gradients, fine-tuning) and outside-the-box access (methodology, code, hyperparameters, training data, internal evaluation results) is the right vocabulary for saying what an auditor was actually allowed to do.

Safety is not a property of the model. Narayanan and Kapoor argued this in March 2024, in a blog post rather than a paper, and it has held up better than most papers ([Narayanan & Kapoor 2024](https://www.aisnakeoil.com/p/ai-safety-is-not-a-model-property)). Their phishing example is the sharp one: the model cannot see what makes an email a phish, because phishing emails are just regular emails. Most of the harm lives in the deployment context, which means a threat model scoped to the model alone is scoped to the wrong object. Weidinger and colleagues make the same argument structurally, with three layers of evaluation (capability, human interaction, systemic impact) and the observation that the second and third are rare ([Weidinger et al. 2023](https://arxiv.org/abs/2310.11986)).

The addition is the risk-assessment scaffolding. Shevlane and colleagues give the two-part decomposition that most frontier frameworks now inherit: dangerous capability evaluations ask whether a model has a capability, alignment evaluations ask whether it has the propensity to apply it harmfully, and a model is treated as highly dangerous if its capability profile would suffice for extreme harm *assuming* misuse or misalignment ([Shevlane et al. 2023](https://arxiv.org/abs/2305.15324)). Deployment sits in a separate table of adjustable variables: scale, use restrictions, autonomy, tool use, depth of model access, oversight. Worth being precise here, because people cite this paper for things it does not say. There is no actor-by-capability-by-deployment decomposition in it. Threat actors appear only in the security section, where the categories are insiders, outsiders, and the model itself as a vector.

# Tiering the Adversary

"An adversary" is the vaguest noun in most published threat models. The security field fixed this by attaching resource figures to it, and the reference implementation for AI is RAND's *Securing AI Model Weights* ([Nevo et al. 2024](https://www.rand.org/pubs/research_reports/RRA2849-1.html)). Five operational capacity levels, each defined by headcount, budget and time:

| | Name | Resources |
|---|---|---|
| **OC1** | Amateur attempts | one person with limited professional expertise, several days, up to $1,000 |
| **OC2** | Professional opportunistic efforts | one broadly capable person, several weeks, up to $10,000, personal infrastructure |
| **OC3** | Cybercrime syndicates and insider threats | ten experienced professionals, several months, up to $1M. Insiders fold in here |
| **OC4** | Standard operations by leading cyber-capable institutions | 100 people across relevant professions, a year, up to $10M, state resources |
| **OC5** | Top-priority operations by top cyber-capable institutions | 1,000 people with expertise years ahead of the public state of the art, years, up to $1B |

Security levels SL1 through SL5 are then defined as "a system that can likely thwart OC*n*." That is the move that makes the ladder useful: the defense is indexed to a named tier instead of described in the abstract, so the claim has a subject. SL5 gets a deliberately weaker verb, "a system that could **plausibly be claimed** to thwart" OC5, and the report elsewhere states that defending an internet-connected system against a determined and capable state actor is not currently feasible with off-the-shelf solutions. The labs RAND spoke to estimated roughly a year of work to reach SL3, two to three years for SL4, and at least five years plus national security support for SL5.

The widely repeated intuition that you cannot defend against a nation state comes from here, or from the Defense Science Board's earlier six-tier version, which concluded that properly executed defensive strategies can handle Tiers I and II and that confident defense against the most sophisticated attacks is not achievable ([DSB 2013](https://nsarchive2.gwu.edu/NSAEBB/NSAEBB424/docs/Cyber-081.pdf)). Both of those go back to the three-class taxonomy Anderson and Kuhn took from IBM in 1996: clever outsiders, knowledgeable insiders, funded organizations ([Anderson & Kuhn 1996](https://www.cl.cam.ac.uk/~mgk25/tamper.pdf)). The "script kiddie, insider, organized crime, nation state" version people quote in talks has no academic source I can find; it is certification-curriculum folklore.

Most of the AI field now defers to RAND rather than inventing its own. Anthropic's RSP cites SL4 explicitly, from v3.0 onward, for both the CBRN and automated-R&D thresholds. Google DeepMind's Frontier Safety Framework 3.1 adopts the security levels wholesale, on the stated grounds that RAND is "the most useful reference in this area." METR's survey quotes the SL definitions verbatim without proposing its own. OpenAI's Preparedness Framework v2 has no tiers at all; "novice" and "expert" appear as adjectives inside individual threshold definitions, which is a different and weaker thing.

AISI has one, for cyber. The Frontier AI Trends Report defines four Task Difficulty Levels by years of professional experience: technical non-expert, apprentice at one to three years, practitioner at three to ten, expert at ten or more ([AISI 2025](https://www.aisi.gov.uk/frontier-ai-trends-report)). No budgets, and the rungs are defined by who could do a task rather than by who is attacking, but it is a real ordered scale from a government body. Their safeguards work goes the other way and declines to impose a taxonomy at all, telling developers to specify their own threat actor, with one illustrative example: "a malicious technical non-expert with a total budget of up to $1,000 and several weeks on a specific operation" ([AISI 2025](https://www.aisi.gov.uk/blog/principles-for-safeguard-evaluation)). That is OC1 and OC2 with the labels filed off.

For misuse rather than theft, the ladder with real figures is the biosecurity one, from the Centre for Long-Term Resilience and SecureBio, tabulated with budgets by Righetti: non-expert individuals (one to five people, undergraduate degree at most, a basic at-home setup), highly skilled individuals (one to five, mostly PhDs, potential university facility access), somewhat capable group (tens of PhDs, $1M to $100M), moderately capable group (hundreds of PhD researchers, purpose-built facilities), highly capable group (world-class team, state-of-the-art facilities, above $100M) ([Rose et al. 2024](https://www.longtermresilience.org/wp-content/uploads/2024/07/CLTR-Report-The-near-term-impact-of-AI-on-biological-misuse-July-2024-1.pdf); [Righetti 2025](https://www.governance.ai/research-paper/dual-use-ai-capabilities-and-the-risk-of-bioterrorism)). This is the source people mean when they say the novice-to-expert ladder, and it is worth citing correctly, because I have seen it attributed to Gryphon Scientific and I cannot find an enumerated Gryphon ladder.

## Nobody Built One for Open Weights, and Nobody Needs To

Every framework above answers a question that an open-weight release has already foreclosed. RAND, the FSF and the RSP tier **weight theft**, and theft is moot once you publish. CLTR, AISI and the Preparedness Framework tier **misuse through an interface you control**, and every rung of those ladders assumes safeguards the adversary deletes in an afternoon. The Frontier Model Forum concedes the narrower cyber version on the record: frameworks "generally do not discuss thresholds around how highly skilled, well-resourced cyber actors, such as Advanced Persistent Threats (APTs) may leverage tools" ([FMF 2026](https://www.frontiermodelforum.org/technical-reports/managing-advanced-cyber-risks-in-frontier-ai-frameworks/)).

They also share a defect that has nothing to do with AI. Every one of them multiplies expertise and resources into a single ordinal. Read RAND's OC2 literally: "a single individual who is **broadly capable** in information security spending several weeks with a total budget of up to **$10,000**." Skill and money move together up the ladder, so there is no cell for a world-class researcher with no budget. MITRE's Cyber Prep scale, which NIST SP 800-30 Appendix D adapts, bundles "resources, expertise, and opportunities" into one Capability level ([Bodeau et al.](https://www.mitre.org/sites/default/files/pdf/10_2914.pdf)). IEC 62443 bundles "means, resources, skills, motivation" into each Security Level, and its SL3 to SL4 step holds skills constant and raises only resources, which means the designers knew the axes were separable and chose not to separate them. Anderson and Kuhn's Class I through III name intelligence, system knowledge and equipment separately inside every class definition, then order the classes anyway.

The adversarial ML literature does not fix this. Biggio and Roli's knowledge axis is knowledge *of the target system*, running Perfect-Knowledge to Limited-Knowledge to Zero-Knowledge, and their capability axis is a binary between causative and exploratory. Neither is about the attacker's skill. Papernot and colleagues' SoK has an ordered capability spectrum, read to injection to modification to logic corruption, but it is one axis and it is about access ([Papernot et al. 2018](https://arxiv.org/abs/1611.03814)). The FAIL model splits the adversary into four tunable dimensions, Features, Algorithm, Instances and Leverage, which is the right instinct, but its dimensions are knowledge and write-access rather than skill and money ([Suciu et al. 2018](https://arxiv.org/abs/1803.06975)). NIST AI 100-2 standardizes Biggio's knowledge axis plus Papernot's access list and adds nothing.

**Classical security engineering solved this in the 1990s, and the answer is sitting in a certification standard.** Common Criteria attack potential, ISO/IEC 18045 Annex B.4, scores an attack on five independently ordered factors and sums the points ([CEM v3.1 R5](https://www.commoncriteriaportal.org/files/ccfiles/CEMV3.1R5.pdf)):

| Factor | Levels (points) |
|---|---|
| Elapsed time | ≤1 day (0), ≤1 week (1), ≤2 weeks (2), ≤1 month (4), ≤2 months (7), ≤3 months (10), ≤4 months (13), ≤5 months (15), ≤6 months (17), >6 months (19) |
| Specialist expertise | Layman (0), Proficient (3), Expert (6), Multiple experts (8) |
| Knowledge of the target | Public (0), Restricted (3), Sensitive (7), Critical (11) |
| Window of opportunity | Unnecessary or unlimited access (0), Easy (1), Moderate (4), Difficult (10), None (not exploitable) |
| Equipment | Standard (0), Specialised (4), Bespoke (7), Multiple bespoke (9) |

Totals map to a rating: 0-9 Basic, 10-13 Enhanced-Basic, 14-19 Moderate, 20-24 High, 25 and above Beyond High. Expertise is graded independently of Equipment, so the researcher with no money is a well-formed adversary rather than an edge case.

## Attack Potential for Open Weights

Two of the five factors go to zero the moment you publish. **Knowledge of the target is pinned at Public**, because you released the weights, the architecture, and usually the training recipe. **Window of opportunity is unnecessary or unlimited**, because the adversary runs the model on their own hardware whenever they like. That is a formal statement of why resource-indexed ladders fail here: 11 and 10 points of discriminating power respectively are deleted by the release decision itself, and everything left has to be carried by expertise, equipment and time.

Scoring the attacks that actually appear in this post, with Knowledge and Window both at 0 throughout:

| Attack | Expertise | Equipment | Elapsed time | Total | Rating |
|---|---|---|---|---|---|
| Forum jailbreak prompt on the shipped model | Layman (0) | Standard (0) | ≤1 day (0) | **0** | Basic |
| Download and run a published abliteration | Layman (0) | Standard (0) | ≤1 day (0) | **0** | Basic |
| Tutorial LoRA on a public harmful dataset | Proficient (3) | Standard (0) | ≤1 week (1) | **4** | Basic |
| Curated fine-tune plus tool scaffolding and retrieval | Proficient (3) | Specialised (4) | ≤2 months (7) | **14** | Moderate |
| *Discovering* the refusal direction ([Arditi et al. 2024](https://arxiv.org/abs/2406.11717)) | Multiple experts (8) | Standard (0) | >6 months (19) | **27** | Beyond High |
| OpenAI's malicious fine-tuning recipe ([Wallace et al. 2025](https://arxiv.org/abs/2508.03153)) | Multiple experts (8) | Bespoke (7) | ≤3 months (10) | **25** | Beyond High |

These are my ratings, not certified evaluations, and someone doing this properly would argue about the equipment column. The shape is what matters. **Inventing the refusal-direction attack scores 27 points. Running it scores 0.** Same capability, same effect on the model, and the entire difference is expertise that was spent once by researchers and is now free for everyone.

So the answer to where a Nicholas Carlini sits is that he is Expert or Multiple experts on Standard equipment with Public knowledge and unlimited access, which is 25 to 27 points depending on the time he spends, and the standard has said since the 1990s that this beats a funded attacker with commodity skill. His empirical record is the demonstration: ten of ten detection defenses broken in 2017 ([Carlini & Wagner 2017](https://arxiv.org/abs/1705.07263)), thirteen of thirteen published at ICLR, ICML and NeurIPS broken in 2020, with the authors noting that "no single strategy would have been sufficient for all defenses" and that adaptive attacks "cannot be automated" ([Tramèr et al. 2020](https://arxiv.org/abs/2002.08347)). No budget, no bespoke equipment, and near-zero marginal cost per break.

## Attack Potential Decays

The 27-to-0 collapse is not a scoring quirk. It is the thing that makes open-weight threat models expire.

Once an attack is published, its expertise cost is paid forever and its elapsed-time cost drops to a download. Arditi and colleagues' paper is one NeurIPS publication and roughly 6,200 models on Hugging Face with "abliterated" in the name. The FIDO Alliance already hit this problem when it ported attack potential to software and added a sixth factor, **Replicability**, for how broadly an attack generalizes across instances ([FIDO 2021](https://fidoalliance.org/specs/fido-security-requirements/FIDO-L1+-Application-of-Attack-Potential-v1.0-fd-20211102.html)). For a model whose weights are identical on every machine that downloaded them, replicability is total.

This is old news in cryptography, where the rule of thumb is the NSA aphorism Schneier has been repeating since at least April 2000: attacks always get better, they never get worse ([Schneier 2000](https://www.schneier.com/crypto-gram/archives/2000/0415.html)). Lenstra and Verheul made it quantitative when they modeled key-size selection with two independent exponential rates, one for cryptanalytic improvement and one for hardware speedup, and found in retrospect that over twenty-five years the algorithmic term contributed about as much as the hardware term ([Lenstra & Verheul 2001](https://www.cs.ru.nl/E.Verheul/papers/Joc2001/joc2001.pdf)). Two axes, one of which is expertise accumulating in public.

The practical consequence is that **every attack potential rating in your threat model needs a date attached, and re-evaluation should be triggered by publication rather than by a calendar.** TAR is the case study three times over. Adequate against the attacks that existed in August 2024. Broken in December by a warmup schedule. Broken again eighteen months later by an attack class that does not fine-tune at all. Nothing about any adversary's budget changed across those events. What changed is that two papers came out.

That is an assumption you can write down, and writing it down is what makes it checkable: *this rating reflects published attacks as of date D; a new attack class against this defense family triggers re-evaluation.* I have not seen a model card that says anything like it.

# Compared to What?

This is the piece the security literature does not supply, and it is where most foundation model threat models fall over.

Kapoor, Bommasani and twenty-plus co-authors defined the framework in an ICML 2024 position paper, and it is the closest thing the field has to a stated adequacy standard ([Kapoor et al. 2024](https://arxiv.org/abs/2403.07918)). Six steps:

1. Threat identification
2. Existing risk, absent open foundation models
3. Existing defenses, absent open foundation models
4. Evidence of marginal risk of open foundation models
5. Ease of defending against new risks
6. Uncertainty and assumptions

Marginal risk is the extent to which these models increase societal risk by intentional misuse *beyond closed foundation models or pre-existing technologies*. Their empirical finding is the reason to take the framework seriously rather than treating it as a checklist someone invented: applying it to seven prior studies of open model risk, **the risk analysis is incomplete for six of the seven**. Incomplete rather than wrong, in the specific sense that the studies did not establish the marginal claim they were read as establishing. The hedge they attach to this is careful and worth repeating: an incomplete assessment does not indicate the prior analysis is flawed, only that those studies on their own do not show increased marginal risk. The illustration they use is that open language models generate accurate pathogen information, and that this information is on the internet.

Steps 2 and 3 are the ones that get skipped, and skipping them is what turns a capability demonstration into a threat model by assertion.

## The Uplift Studies Disagree, and the Reason Matters

The empirical record on biological uplift is split, and I think the split is more informative than either side of it.

RAND ran the most careful null. Fifteen cells across three conditions (internet only, internet plus LLM A, internet plus LLM B) and four vignettes, with operational plans scored 1 to 9 for viability by eight subject matter experts using a Delphi process. LLM access was associated with a **0.22 point decrease** in viability, p = 0.64. Per model: +0.12 (p = 0.87) and −0.56 (p = 0.25). Their statement is that plans generated with LLM assistance were statistically indistinguishable from plans generated without ([Mouton et al. 2024](https://www.rand.org/pubs/research_reports/RRA2977-2.html)).

OpenAI ran 100 participants, 50 biology PhDs and 50 students, randomized between internet-only and internet plus research-only GPT-4, scoring accuracy, completeness and innovation across five stages of the threat-creation pipeline. Mean accuracy uplift was 0.88 for experts and 0.25 for students on a ten-point scale. Their conclusion is worth quoting exactly, because it is a study interpreting its own null as weak positive evidence: "While none of the above results were statistically significant, we interpret our results to indicate that access to (research-only) GPT-4 *may* increase experts' ability to access information about biological threats" ([Patwardhan et al. 2024](https://openai.com/index/building-an-early-warning-system-for-llm-aided-biological-threat-creation/)).

Then in February 2026, Zhang and colleagues found a large positive effect. Fifty-seven participants, internet-only control with LLM access disabled, frontier models in the treatment arm. Novices with LLM access were **4.16 times more accurate**, 95% CI [2.63, 6.87], significant on seven of eight benchmarks, and LLM-assisted novices exceeded expert baselines on the Human Pathogen Capabilities Test and the Virology Capabilities Test ([Zhang et al. 2026](https://arxiv.org/abs/2602.23329)).

The results do not contradict each other, and the reason is the outcome variable. RAND and OpenAI scored *plans*: viability, operational feasibility, completeness across an acquisition pipeline. Zhang and colleagues scored *in silico question answering accuracy*. Those are different constructs, and a threat model that says "measure uplift" without saying which one has not said anything. This is Gilmer's point about action spaces, transposed. The choice of dependent variable is a threat modeling decision, and it is usually made silently by whoever picked the benchmark.

## Which Baseline?

Chen and Alaga at METR make the objection that I think is the strongest single criticism of the whole marginal-risk framing, and their title is my section heading: marginal risk relative to what ([Chen & Alaga 2025](https://openreview.net/forum?id=8pK2xrYwjD))?

They separate a **pre-GPAI baseline** (no modern general-purpose AI, roughly internet-only) from a **post-GPAI baseline** (including the most risk-enabling models already deployed), and find that developers frequently do not specify which one they are using. The failure mode they name is a boiling frog: if the most dangerous available model gets progressively more capable, aggregate risk can rise a great deal while every individual release passes its own test against the current post-GPAI baseline. Nothing in the framing catches the aggregate, because the aggregate is never what gets measured.

There is a live example. Anthropic's earlier bio trials used an internet-only control. The Claude Opus 4.5 and 4.6 system cards report uplift against *previous Claude models*, with Opus 4.5 described as meaningfully more helpful to participants than its predecessors. That is a post-GPAI baseline, and by Chen and Alaga's argument it is the one that cannot detect the aggregate. I do not read this as anyone acting in bad faith, and comparing against the previous model is the natural thing to do when you are shipping the next one. It is exactly the failure mode they predicted, arrived at honestly.

Chen and Alaga's recommendation is to report both. That seems right to me and I have not seen anyone do it.

On the measurement side, Vaccaro and colleagues at MIT wrote down what the design has to look like: three conditions (human alone with conventional tools, AI alone, human plus AI), an uplift ratio U = H_AI / H, and a statistical standard of powering the study to detect the smallest effect of safety concern, their example being U ≥ 5, at 95% power and α = 0.05 ([Vaccaro et al. 2026](https://arxiv.org/abs/2603.26676)). Surveying nine public evaluations from Anthropic, OpenAI, Meta and RAND, they find that red-team reports rarely include counterfactual baselines for what motivated humans could accomplish with conventional tools, and they are direct about the under-powered designs that dominate the literature. Given the effect sizes above, powering to detect a fivefold difference is not a high bar, and most published work does not clear it.

For the other pole, Peppin and colleagues argue in FAccT 2025 that biorisk threat models are nascent and often speculative, that the internet baseline was added to these studies belatedly, and that every study comparing uplift against internet access has found a non-significant increase ([Peppin et al. 2025](https://arxiv.org/abs/2412.01946)). Kapoor is a co-author. Zhang et al. postdates it. I mention it because the honest position here is that this is contested and the contest is about study design, not about anybody's politics.

# The Judge Is Inside the Threat Model

I wrote a long section on measurement in [the red teaming post](/posts/2026/07/red-teaming-language-models/#the-measurement-problem) and will not repeat it, but one 2026 result belongs in any discussion of adequacy.

Schwinn and colleagues audited four safety judges (AegisGuard, the Llama-2-13B HarmBench classifier, JailJudge, LlamaGuard-3) against 6,642 human-verified labels. Under the distribution shifts that red teaming produces, the judges perform on average only slightly better than a coin flip, and JailJudge bottoms out at **AUROC 0.48** on GCG-R, which is worse than random ([Schwinn et al. 2026](https://arxiv.org/abs/2603.06594)). Their conclusion is that many attacks inflate their success rates by exploiting judge insufficiencies rather than eliciting genuinely harmful content.

If who scores the outcome is unspecified, the threat model is unspecified, because the definition of a successful attack is downstream of the scorer. This applies to the numbers in this post too. TamperBench's harmfulness floor, which I use below, is a StrongREJECT number produced by an automated judge, and Schwinn's result is a reason to treat it as a lower-confidence quantity than the fine-tuning cost figures, which are dollars.

# Open Weights, Where the Gap Is Widest

Everything above is general. Open weights is where it gets measurable, because Paskov, Rodriguez, Dev and Casper went and counted.

They propose four proportional evaluation requirements ([Paskov et al. 2026](https://arxiv.org/abs/2606.19890)):

- **PE1**: evaluate without system-level safeguards
- **PE2**: assess robustness to modifications designed to undo model-level safeguards
- **PE3**: assess selective capability amplification via fine-tuning and tool use
- **PE4**: proxy worst-case feasible misuse, accounting for irreversibility

Then they reviewed 37 open-weight model families released between January 2025 and April 2026:

| Requirement | Families satisfying |
|---|---|
| PE1, no system-level safeguards | 14 of 37 (38%) |
| PE2, robustness to safeguard removal | 4 of 37 (11%) |
| PE3, selective capability amplification | 1 of 37 (3%) |
| PE4, worst-case feasible misuse | 1 of 37 (3%) |
| All four | 1 of 37 |

Four of thirty-seven assess whether their safeguards survive removal. This is Kerckhoffs, restated for 2026 and empirically checked: the adversary has the weights, and 89% of releases evaluate a configuration that adversary will not run. In the [attack potential terms above](#attack-potential-for-open-weights), 89% of open-weight releases evaluate only attacks scoring zero.

The costs that make PE2 non-optional are well established and I covered them [in the previous post](/posts/2026/07/red-teaming-language-models/#open-weights-changes-the-order). The short version: ten adversarial examples and under twenty cents of API spend took GPT-3.5 Turbo from 1.8% to 88.8% harmfulness ([Qi et al. 2023](https://arxiv.org/abs/2310.03693)), a QLoRA run under $200 on one GPU brought Llama 2-Chat 70B to roughly 1% refusal ([Lermen et al. 2023](https://arxiv.org/abs/2310.20624)), and abliteration needs no fine-tuning at all ([Arditi et al. 2024](https://arxiv.org/abs/2406.11717)). Searching Hugging Face for "abliterated" on 31 July 2026 returns roughly 6,200 models, though that is a name match rather than a formal tag. That is one NeurIPS paper's technique with roughly six thousand productionized instances on the main model hub, against the 11% of releases that test for safeguard removal at all.

TamperBench is the systematic version. Twenty-one open-weight models from 0.6B to 8B, including five defense-augmented variants of Llama-3-8B-Instruct, attacked under a constraint of no more than 10% MMLU-Pro degradation. Worst-case post-attack StrongREJECT harmfulness exceeds 0.68 for every model tested, and 0.77 for every model above 1B. Harmful LoRA equals or beats full fine-tuning in 14 of the 21 ([Hossain et al. 2026](https://arxiv.org/abs/2602.06911)). The utility constraint is the part I would copy: without it, attacks "succeed" by lobotomizing the model.

## The One Worked Example

The exception in Paskov's table is gpt-oss, and what OpenAI did is the clearest instance I know of a lab adopting an adversarial threat model as a release gate rather than as a paper ([Wallace et al. 2025](https://arxiv.org/abs/2508.03153)).

Their malicious fine-tuning recipe has two stages. First, incremental RL with a helpful-only reward to strip refusals while checking that general capability survives on GPQA. Second, domain capability maximization: for biology, RL with web browsing enabled over curated data including GPQA-bio, WMDP and LAB-Bench, plus a new TroubleshootingBench built with PhD experts; for cyber, an agentic dockerized terminal over 264 CTF challenges with internet access restricted so the model could not cheat. Then compare against both open and closed frontier models.

Results: on Gryphon free-response biology, the maliciously fine-tuned gpt-oss scores 74.4% against o3 at 76.9% and DeepSeek R1 at 66.6%. On SecureBio human pathogen questions, 54.2%, roughly matching o3. On professional CTFs, 27.7%, below o3. Their conclusion is that the model may marginally increase biological capabilities without substantially advancing the frontier, and that this contributed to the decision to release.

Two things worth noticing. The threat model has a stated adversary (someone who fine-tunes the released weights with a real compute budget), a stated baseline (existing open-weight models, which is Chen and Alaga's post-GPAI baseline), and a stated falsifier (OpenAI's Preparedness High threshold). It could have come back the other way, which is the property the other thirty-six releases do not have.

The regulatory clock is also running. The EU AI Act's Article 53(2) open-source exemption does not apply to general-purpose models with systemic risk, and Article 51(2) presumes systemic risk above 10^25 training FLOP, at which point Article 55(1)(a) requires model evaluation "in accordance with standardised protocols and tools reflecting the state of the art, including conducting and documenting adversarial testing." Commission fines under Article 101 attach from 2 August 2026. One caveat I want to be explicit about: the Digital Omnibus on AI adopted in mid-2026 moved several high-risk deadlines, and I could not find a source that positively confirms the Chapter V dates survived it untouched. Check the consolidated text before relying on that date. The substantive point does not depend on it: "state of the art adversarial testing" is going to be litigated, and at the moment the state of the art is four releases out of thirty-seven.

# Safety Cases Got Furthest

The safety case literature is the only one that treats the threat model as a load-bearing part of an argument that can fail, which is why it produced the sharpest requirements.

Buhl and colleagues give four required elements: objectives, arguments, evidence, and **scope**. The scope requirement is the sentence I would put on a poster. A safety case must specify the conditions under which the argument is valid, and the intended deployment context, "e.g. whether the model weights will be released or the model will be accessible only via API" ([Buhl et al. 2024](https://arxiv.org/abs/2410.21572)). That is a canonical safety case paper naming weight release as a scope variable in 2024, two years before anyone went and counted how many releases were scoped that way.

Clymer and colleagues structure the case around a macrosystem, meaning the models, the non-AI software and the humans together, and require deployment assumptions to be argued rather than presumed. Their examples of such assumptions include that model weights are secure from human actors, and that fine-tuning customers follow terms of service. Their six steps run from defining the deployment decision through decomposing "won't cause a catastrophe" into concrete threat models, to justifying assumptions, to assessing subsystem and then macrosystem risk against a stated threshold, their illustration being 0.1% ([Clymer et al. 2024](https://arxiv.org/abs/2403.10462)).

The worked example is the misuse safeguards case from Clymer, Weinbaum, Kirk, Mai, Zhang and Davies, hosted by the UK AI Security Institute with authors from Redwood, MATS and MIT ([Clymer et al. 2025](https://arxiv.org/abs/2505.18003)). Its adversary is defined quantitatively, and this is the level of specificity I have not seen anywhere else:

- A **novice actor** is an individual with little to no relevant experience and **less than $30,000** available. A lone wolf.
- A **misuse attempt** is that actor spending **more than two weeks** trying to cause large-scale harm.
- Adversary resources are enumerated: internet, other AI models, social media, black markets, crowd-worker platforms. The red team gets matched to them.
- The uplift model has named parameters: expected annual synthesis attempts, expected damage per success, the distribution of time actors invest, success probability with and without AI, hazardous requests per unit time, cumulative time to evade safeguards.
- The developer is assumed to correct deployment within **one month** of identifying a risk escalation.

Every one of those assumptions is closed-world and API-mediated. That is the honest thing about it. Read it next to an open-weight release and the one-month correction window, the account banning, the KYC and the input/output classifiers all evaporate at once. The case then fails at named nodes rather than degrading quietly, which is the whole reason to write it as a claim tree.

Goemans and colleagues have a template for cyber inability arguments using Claims-Arguments-Evidence, with an explicitly stated motivation that current practice uses implicit arguments for overall system safety ([Goemans et al. 2024](https://arxiv.org/abs/2411.08088)). Balesni and colleagues do the scheming version, with three core arguments and two supporting alignment arguments, and are candid that many of the assumptions required have not been confidently satisfied ([Balesni et al. 2024](https://arxiv.org/abs/2411.03336)).

For contrast, the enumerations. MITRE ATLAS catalogs adversary tactics and techniques observed against AI systems. The OWASP Top 10 for LLM Applications, still the 2025 edition, catalogs application-layer vulnerability classes. NIST AI 600-1 enumerates twelve generative AI risks with suggested actions and explicitly scopes itself to risks with an existing empirical evidence base. All three are useful for coverage checks and none of them defines a threat actor, a budget, a deployment setting, a baseline, or a threshold. None of them has a notion of the argument failing.

METR's December 2025 survey of twelve frontier developers' safety policies is the best picture of what industry commits to in practice, organized around nine common elements including capability thresholds, weight security, deployment mitigations and conditions for halting ([METR 2025](https://metr.org/blog/2025-12-09-common-elements-of-frontier-ai-safety-policies/)). Weight security in those frameworks means preventing theft. Open release appears as a discretionary risk-benefit carve-out in one framework, Google DeepMind's, rather than as a distinct risk regime with its own evaluation requirements.

# A Checklist I Would Hold a Release To

This ordering is mine. The individual items are other people's, and each one points at where it came from. I am not proposing a standard; I am proposing the eight questions I would want answered before I signed off on anything, and the honest state of affairs is that I have not yet run a release through all eight myself.

1. **Score the attack, do not tier the attacker.** "A sophisticated actor" is not a specification, and neither is a budget on its own, because expertise and money are separate axes and open weights zeroes out three of the five things a budget usually buys. Use Common Criteria attack potential ([ISO/IEC 18045 Annex B.4](https://www.commoncriteriaportal.org/files/ccfiles/CEMV3.1R5.pdf)) and put a date on the rating. If you want a resource ladder alongside it, RAND's OC1 through OC5 is what Anthropic and DeepMind index to ([Nevo et al. 2024](https://www.rand.org/pubs/research_reports/RRA2849-1.html)), and [Clymer et al. 2025](https://arxiv.org/abs/2505.18003) has a lone wolf under $30,000 over two weeks for the misuse case.
2. **Name the access level, and say whether the weights are in scope.** This is the single highest-value line in the document, and [Buhl et al. 2024](https://arxiv.org/abs/2410.21572) put it in the scope requirement. Assume the adversary knows how the defense works, per [Kerckhoffs](https://www.petitcolas.net/kerckhoffs/crypto_militaire_1.pdf) and [Carlini et al. 2019](https://arxiv.org/abs/1902.06705).
3. **Name the baseline, and say which baseline.** Pre-GPAI or post-GPAI, and ideally both ([Chen & Alaga 2025](https://openreview.net/forum?id=8pK2xrYwjD)). Steps 2 and 3 of the [Kapoor et al. 2024](https://arxiv.org/abs/2403.07918) framework are the ones that get skipped, and skipping them is what makes an assessment incomplete rather than wrong.
4. **Name the outcome variable and who scores it.** Plan viability and question-answering accuracy give opposite answers on the same threat ([Mouton et al. 2024](https://www.rand.org/pubs/research_reports/RRA2977-2.html) versus [Zhang et al. 2026](https://arxiv.org/abs/2602.23329)). If an automated judge does the scoring, validate it first ([Schwinn et al. 2026](https://arxiv.org/abs/2603.06594)).
5. **Name the falsifier.** What result would stop this release. Write it before you see the data. [Feffer et al. 2024](https://arxiv.org/abs/2401.15897) surveyed six industry red-teaming cases and found that in none of them did red teaming block a release, which tells you how often this question has a real answer.
6. **Evaluate with the safeguards off, then evaluate whether they can be removed.** [Paskov et al. 2026](https://arxiv.org/abs/2606.19890)'s PE1 and PE2. Thirty-eight percent and eleven percent of open-weight releases respectively.
7. **Price it, on both sides.** What does the attack cost the adversary, and what does the defense cost you. [Apruzzese et al. 2023](https://arxiv.org/abs/2212.14315) found 27% of security ML papers make no mention of economics. The reason the open-weights numbers land so hard is that they are denominated in dollars.
8. **Name what you could not test.** Step 6 of Kapoor's framework, and Clymer's deployment assumptions. Writing an assumption down converts it into a claim someone can come back and attack, which is the only way it ever gets checked.

If you only do three: name the baseline, name the falsifier, and evaluate with the safeguards off.

# What I Am Doing With This

Two things, and I want to be clear about which parts have run and which have not.

The first is a ranking-stability experiment. HELM Safety publishes a leaderboard of open-weight models, and my hypothesis is that the ordering does not survive a low-cost weight-space attack. Six instruction-tuned models in the 7-8B class spanning the published range from 0.729 to 0.905, directional ablation as the primary attack because it has few enough hyperparameters that identical treatment across models is achievable, LoRA as a robustness check, everything under a 10% utility constraint borrowed from TamperBench. If Spearman ρ between pre- and post-tamper rankings is well below 1, the leaderboard is measuring post-training effort rather than anything durable. If ρ stays above 0.8, that is a positive result for HELM Safety and I will report it as one. This is written up and not yet run.

The second is that marin-8b-instruct is one of those six rows. Marin is an open lab that publishes its training process, and its model card says plainly that the model has not undergone safety tuning or evaluation. I have a red-teaming harness validated against published Olmo-3 numbers, and the default-behavior results so far show Marin resisting persona-based jailbreaks better than Olmo-3 by 18.1 points on DoAnythingNow and doing materially worse on misinformation compliance by 14.8 points. Both of those measure a casual user. Neither says anything about an adversary holding the weights, which is the entire point of this post, and it is item six on the checklist that I have not done yet.

# Open Problems

**Nobody has validated an adequacy criterion.** Everything in this post is normative. As far as I know there is no study showing that threat models satisfying any of these criteria produce better release decisions than threat models that do not, and I am not sure how you would run it.

**Pre-registration has no home.** Vaccaro and colleagues recommend that funders require preregistration for uplift studies. There is no venue for that, no registry, and no norm. Preregistering a threat model before running the evaluation would fix a large fraction of the estimand problems in the field, and it costs nothing.

**The baseline is a moving target and nobody has proposed how to fix it.** Chen and Alaga's recommendation to report both baselines is right and incomplete. A pre-GPAI baseline gets harder to measure every year, because the population you would need to run internet-only has already been shaped by four years of using these models.

**Tamper-resistance claims are behavioral.** Every published protocol measures elicitation difficulty and reports it as capability removal. Nothing distinguishes verified deletion from a capability that is merely hard to reach, and until something does, "tamper-resistant" is a statement about the attacks that were run. Which is where this post started.

# Citation

Cited as:
> Sandoval, Gustavo. (Jul 2026). "What Counts as an Adequate Threat Model?". https://gussand.github.io/posts/2026/07/adequate-threat-models/.

Or

```
@article{sandoval2026threatmodels,
  title   = "What Counts as an Adequate Threat Model?",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jul",
  url     = "https://gussand.github.io/posts/2026/07/adequate-threat-models/"
}
```

# References

[1] Tamirisa, Bharathi, Phan, Zhou, Gatti, Suresh, et al. ["Tamper-Resistant Safeguards for Open-Weight LLMs"](https://arxiv.org/abs/2408.00761). ICLR 2025. The 5,000-step claim appears in v1; the current version says "hundreds of steps."

[2] Qi, Wei, Carlini, Huang, Xie, He, Jagielski, Nasr, Mittal, and Henderson. ["On Evaluating the Durability of Safeguards for Open-Weight LLMs"](https://arxiv.org/abs/2412.07097). ICLR 2025.

[3] Kuo, Yadav, and Smith. ["Open-Weight LLM Fine-Tuning Defenses are Susceptible to Simple Attacks"](https://arxiv.org/abs/2605.26526). arXiv preprint arXiv:2605.26526 (2026).

[4] Kerckhoffs. ["La cryptographie militaire"](https://www.petitcolas.net/kerckhoffs/crypto_militaire_1.pdf). Journal des sciences militaires, vol. IX (1883), pp. 5-83 and 161-191.

[5] Shannon. ["Communication Theory of Secrecy Systems"](https://ieeexplore.ieee.org/document/6769090). Bell System Technical Journal 28(4), 1949.

[6] Biggio and Roli. ["Wild Patterns: Ten Years After the Rise of Adversarial Machine Learning"](https://arxiv.org/abs/1712.03141). Pattern Recognition 84 (2018), pp. 317-331.

[7] Carlini, Athalye, Papernot, Brendel, Rauber, Tsipras, Goodfellow, Madry, and Kurakin. ["On Evaluating Adversarial Robustness"](https://arxiv.org/abs/1902.06705). arXiv preprint arXiv:1902.06705 (2019).

[8] Gilmer, Adams, Goodfellow, Andersen, and Dahl. ["Motivating the Rules of the Game for Adversarial Example Research"](https://arxiv.org/abs/1807.06732). arXiv preprint arXiv:1807.06732 (2018).

[9] Apruzzese, Anderson, Dambra, Freeman, Pierazzi, and Roundy. ["'Real Attackers Don't Compute Gradients': Bridging the Gap Between Adversarial ML Research and Practice"](https://arxiv.org/abs/2212.14315). IEEE SaTML 2023.

[10] Pierazzi, Pendlebury, Cortellazzi, and Cavallaro. ["Intriguing Properties of Adversarial ML Attacks in the Problem Space"](https://arxiv.org/abs/1911.02142). IEEE S&P 2020.

[11] Herley. ["Unfalsifiability of security claims"](https://www.pnas.org/doi/10.1073/pnas.1517797113). PNAS 113(23), 2016, pp. 6415-6420.

[12] Braiterman, Shostack, Marcil, et al. ["Threat Modeling Manifesto"](https://www.threatmodelingmanifesto.org/). November 2020.

[13] Casper, Ezell, Siegmann, Kolt, Curtis, Bucknall, et al. ["Black-Box Access is Insufficient for Rigorous AI Audits"](https://arxiv.org/abs/2401.14446). ACM FAccT 2024.

[14] Narayanan and Kapoor. ["AI safety is not a model property"](https://www.aisnakeoil.com/p/ai-safety-is-not-a-model-property). AI Snake Oil, March 2024.

[15] Weidinger, Rauh, Marchal, Manzini, Hendricks, Mateos-Garcia, et al. ["Sociotechnical Safety Evaluation of Generative AI Systems"](https://arxiv.org/abs/2310.11986). arXiv preprint arXiv:2310.11986 (2023).

[16] Shevlane, Farquhar, Garfinkel, Phuong, Whittlestone, Leung, et al. ["Model evaluation for extreme risks"](https://arxiv.org/abs/2305.15324). arXiv preprint arXiv:2305.15324 (2023).

[17] Kapoor, Bommasani, Klyman, Longpre, Ramaswami, Cihon, et al. ["Position: On the Societal Impact of Open Foundation Models"](https://arxiv.org/abs/2403.07918). ICML 2024.

[18] Mouton, Lucas, and Guest. ["The Operational Risks of AI in Large-Scale Biological Attacks: Results of a Red-Team Study"](https://www.rand.org/pubs/research_reports/RRA2977-2.html). RAND Corporation, RR-A2977-2, January 2024.

[19] Patwardhan, Liu, Markov, Chowdhury, Leet, Cone, et al. ["Building an early warning system for LLM-aided biological threat creation"](https://openai.com/index/building-an-early-warning-system-for-llm-aided-biological-threat-creation/). OpenAI, January 2024.

[20] Zhang, Knight, Kruus, Hausenloy, Medeiros, Li, et al. ["LLM Novice Uplift on Dual-Use, In Silico Biology Tasks"](https://arxiv.org/abs/2602.23329). arXiv preprint arXiv:2602.23329 (2026).

[21] Chen and Alaga. ["Marginal Risk Relative to What? Distinguishing Baselines in AI Risk Management"](https://openreview.net/forum?id=8pK2xrYwjD). Workshop on Technical AI Governance, ICML 2025.

[22] Vaccaro, Song, Almaatouq, and Bakker. ["Evaluating Human-AI Safety: A Framework for Measuring Harmful Capability Uplift"](https://arxiv.org/abs/2603.26676). arXiv preprint arXiv:2603.26676 (2026).

[23] Peppin, Reuel, Casper, Jones, Strait, Anwar, et al. ["The Reality of AI and Biorisk"](https://arxiv.org/abs/2412.01946). ACM FAccT 2025.

[24] Schwinn, Ladenburger, Beyer, Mofakhami, Gidel, and Günnemann. ["A Coin Flip for Safety: LLM Judges Fail to Reliably Measure Adversarial Robustness"](https://arxiv.org/abs/2603.06594). arXiv preprint arXiv:2603.06594 (2026).

[25] Paskov, Rodriguez, Dev, and Casper. ["Open Weight AI Models Require Proportional Evaluation Approaches"](https://arxiv.org/abs/2606.19890). arXiv preprint arXiv:2606.19890 (2026). Also RAND Perspective PE-A4886-1.

[26] Qi, Zeng, Xie, Chen, Jia, Mittal, and Henderson. ["Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!"](https://arxiv.org/abs/2310.03693). ICLR 2024.

[27] Lermen, Rogers-Smith, and Ladish. ["LoRA Fine-tuning Efficiently Undoes Safety Training in Llama 2-Chat 70B"](https://arxiv.org/abs/2310.20624). arXiv preprint arXiv:2310.20624 (2023).

[28] Arditi, Obeso, Syed, Paleka, Panickssery, Gurnee, and Nanda. ["Refusal in Language Models Is Mediated by a Single Direction"](https://arxiv.org/abs/2406.11717). NeurIPS 2024.

[29] Hossain, Tseng, Pandey, Vajpayee, Kowal, Nonta, et al. ["TamperBench: Systematically Stress-Testing LLM Safety Under Fine-Tuning and Tampering"](https://arxiv.org/abs/2602.06911). arXiv preprint arXiv:2602.06911 (2026).

[30] Wallace, Watkins, Wang, Chen, and Koch. ["Estimating Worst-Case Frontier Risks of Open-Weight LLMs"](https://arxiv.org/abs/2508.03153). arXiv preprint arXiv:2508.03153 (2025).

[31] Buhl, Sett, Koessler, Schuett, and Anderljung. ["Safety cases for frontier AI"](https://arxiv.org/abs/2410.21572). arXiv preprint arXiv:2410.21572 (2024).

[32] Clymer, Gabrieli, Krueger, and Larsen. ["Safety Cases: How to Justify the Safety of Advanced AI Systems"](https://arxiv.org/abs/2403.10462). arXiv preprint arXiv:2403.10462 (2024).

[33] Clymer, Weinbaum, Kirk, Mai, Zhang, and Davies. ["An Example Safety Case for Safeguards Against Misuse"](https://arxiv.org/abs/2505.18003). arXiv preprint arXiv:2505.18003 (2025).

[34] Goemans, Buhl, Schuett, Korbak, Wang, Hilton, and Irving. ["Safety case template for frontier AI: A cyber inability argument"](https://arxiv.org/abs/2411.08088). arXiv preprint arXiv:2411.08088 (2024).

[35] Balesni, Hobbhahn, Lindner, Meinke, Korbak, Clymer, et al. ["Towards evaluations-based safety cases for AI scheming"](https://arxiv.org/abs/2411.03336). arXiv preprint arXiv:2411.03336 (2024).

[36] Feffer, Sinha, Deng, Lipton, and Heidari. ["Red-Teaming for Generative AI: Silver Bullet or Security Theater?"](https://arxiv.org/abs/2401.15897). arXiv preprint arXiv:2401.15897 (2024).

[37] METR. ["Common Elements of Frontier AI Safety Policies (December 2025 Update)"](https://metr.org/blog/2025-12-09-common-elements-of-frontier-ai-safety-policies/). December 2025.

[38] NIST. ["Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile"](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf). NIST AI 600-1, July 2024.

[39] OWASP GenAI Security Project. ["OWASP Top 10 for LLM Applications 2025"](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/). November 2024.

[40] MITRE. ["Adversarial Threat Landscape for AI Systems (ATLAS)"](https://atlas.mitre.org/).

[41] O'Brien, Casper, Anthony, Korbak, Kirk, Davies, et al. ["Deep Ignorance: Filtering Pretraining Data Builds Tamper-Resistant Safeguards into Open-Weight LLMs"](https://arxiv.org/abs/2508.06601). arXiv preprint arXiv:2508.06601 (2025).

[42] Solaiman. ["The Gradient of Generative AI Release: Methods and Considerations"](https://arxiv.org/abs/2302.04844). ACM FAccT 2023.

[43] Kumar, Nyström, Lambert, Marshall, Goertzel, Comissoneru, Swann, and Xia. ["Adversarial Machine Learning: Industry Perspectives"](https://arxiv.org/abs/2002.05646). IEEE SPW 2020.

[44] Frontier Model Forum. ["Risk Taxonomy and Thresholds for Frontier AI Frameworks"](https://www.frontiermodelforum.org/technical-reports/risk-taxonomy-and-thresholds/). June 2025.

[45] Bengio et al. ["International AI Safety Report 2026"](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026). February 2026.

[46] Nevo, Lahav, Karpur, Bar-On, Bradley, and Alstott. ["Securing AI Model Weights: Preventing Theft and Misuse of Frontier Models"](https://www.rand.org/pubs/research_reports/RRA2849-1.html). RAND Corporation, RR-A2849-1, 2024.

[47] Defense Science Board. ["Task Force Report: Resilient Military Systems and the Advanced Cyber Threat"](https://nsarchive2.gwu.edu/NSAEBB/NSAEBB424/docs/Cyber-081.pdf). U.S. Department of Defense, January 2013.

[48] Anderson and Kuhn. ["Tamper Resistance: a Cautionary Note"](https://www.cl.cam.ac.uk/~mgk25/tamper.pdf). 2nd USENIX Workshop on Electronic Commerce, 1996. The three-class taxonomy originates in Abraham, Dolan, Double, and Stevens, "Transaction Security System," IBM Systems Journal 30(2), 1991.

[49] AI Security Institute. ["Frontier AI Trends Report"](https://www.aisi.gov.uk/frontier-ai-trends-report). December 2025.

[50] AI Security Institute. ["Principles for Evaluating Misuse Safeguards of Frontier AI Systems"](https://www.aisi.gov.uk/blog/principles-for-safeguard-evaluation). February 2025.

[51] Rose, Moulange, Smith, and Nelson. ["The near-term impact of AI on biological misuse"](https://www.longtermresilience.org/wp-content/uploads/2024/07/CLTR-Report-The-near-term-impact-of-AI-on-biological-misuse-July-2024-1.pdf). Centre for Long-Term Resilience, July 2024.

[52] Righetti. ["Dual-Use AI Capabilities and the Risk of Bioterrorism: Converting Capability Evaluations to Risk Assessments"](https://www.governance.ai/research-paper/dual-use-ai-capabilities-and-the-risk-of-bioterrorism). Centre for the Governance of AI, 2025.

[53] Frontier Model Forum. ["Managing Advanced Cyber Risks in Frontier AI Frameworks"](https://www.frontiermodelforum.org/technical-reports/managing-advanced-cyber-risks-in-frontier-ai-frameworks/). February 2026.

[54] Dombrowski, Bowen, Gleave, and Cundy. ["The Safety Gap Toolkit: Evaluating Hidden Dangers of Open-Source Models"](https://arxiv.org/abs/2507.11544). arXiv preprint arXiv:2507.11544 (2025).

[55] Anthropic. ["Responsible Scaling Policy"](https://www.anthropic.com/responsible-scaling-policy). RAND security levels are cited explicitly from v3.0 (February 2026) onward.

[56] Google DeepMind. ["Frontier Safety Framework, Version 3.1"](https://deepmind.google/discover/blog/strengthening-our-frontier-safety-framework/). 2025.

[57] OpenAI. ["Preparedness Framework, Version 2"](https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf). April 2025.

[58] Common Criteria. ["Common Methodology for Information Technology Security Evaluation (CEM), Version 3.1 Revision 5"](https://www.commoncriteriaportal.org/files/ccfiles/CEMV3.1R5.pdf). Annex B.4, "Calculating attack potential." Standardised as ISO/IEC 18045.

[59] FIDO Alliance. ["Application of Attack Potential to FIDO L1+ Authenticator, v1.0"](https://fidoalliance.org/specs/fido-security-requirements/FIDO-L1+-Application-of-Attack-Potential-v1.0-fd-20211102.html). November 2021. Adds Replicability as a sixth factor for software targets.

[60] Bodeau, Fabius-Greene, and Graubart. ["How Do You Assess Your Organization's Cyber Threat Level?"](https://www.mitre.org/sites/default/files/pdf/10_2914.pdf). The MITRE Corporation. The Capability/Intent/Targeting scale that NIST SP 800-30 Rev. 1 Appendix D adapts.

[61] Papernot, McDaniel, Sinha, and Wellman. ["SoK: Security and Privacy in Machine Learning"](https://arxiv.org/abs/1611.03814). IEEE EuroS&P 2018.

[62] Suciu, Mărginean, Kaya, Daumé III, and Dumitraş. ["When Does Machine Learning FAIL? Generalized Transferability for Evasion and Poisoning Attacks"](https://arxiv.org/abs/1803.06975). USENIX Security 2018.

[63] Carlini and Wagner. ["Adversarial Examples Are Not Easily Detected: Bypassing Ten Detection Methods"](https://arxiv.org/abs/1705.07263). ACM AISec 2017.

[64] Tramèr, Carlini, Brendel, and Madry. ["On Adaptive Attacks to Adversarial Example Defenses"](https://arxiv.org/abs/2002.08347). NeurIPS 2020.

[65] Lenstra and Verheul. ["Selecting Cryptographic Key Sizes"](https://www.cs.ru.nl/E.Verheul/papers/Joc2001/joc2001.pdf). Journal of Cryptology 14(4), 2001, pp. 255-293.

[66] Schneier. ["Crypto-Gram, April 15, 2000"](https://www.schneier.com/crypto-gram/archives/2000/0415.html). Earliest published instance I can find of the NSA aphorism "attacks always get better; they never get worse." Schneier attributes it to the NSA rather than claiming it.

[67] Casey. ["Threat Agent Library Helps Identify Information Security Risks"](https://static1.squarespace.com/static/5a111571d0e628a8679b6b6c/t/5c379b84b8a045a55b983f3a/1547148165167/Intel+-+Threat+Agent+Library+Helps+Identify+Information+Security+Risks.pdf). Intel white paper, September 2007. Separates Skills from Resources as ordered attributes.

[68] Vassilev, Oprea, Fordyce, and Anderson. ["Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations"](https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.100-2e2023.pdf). NIST AI 100-2e2023, January 2024.
