---
layout: "radar-page"
title: "Backfill Radar — Text Diffusion Language Models (July 2024 → June 30 2026)"
kind: "backfill"
slug: "text-diffusion-2024-2026"
date: 2026-06-30
group: "backfill"
window: ""
summary: "Compiled: 2026-06-30 · Window: posted/accepted Jul 2024 – Jun 2026 (seminal older anchors flagged) · Counts: ~27 items · peer-reviewed: SEDD (ICML'24 best paper), MDLM (NeurIPS'24), DiffuLLaMA (ICLR'25), Block Diffusion (ICLR'25 oral), Fast-dLLM (ICLR'26), DIJA/A2D/DiffuGuard (ICLR'26); rest preprints/industry reports."
source_url: "https://github.com/GusSand/research-radar/blob/main/reports/backfill/text-diffusion-2024-2026.md"
styled: false
excerpt_separator: ""
---

{% raw %}
# Backfill Radar — Text Diffusion Language Models (July 2024 → June 30 2026)

**Compiled:** 2026-06-30 · **Window:** posted/accepted Jul 2024 – Jun 2026 (seminal older anchors flagged)
**Focus:** text diffusion / masked-discrete-diffusion LMs (dLLMs) — capabilities for grounding, with **security and mechanistic interpretability weighted highest** (Gus's priority).
**Method:** 3 parallel sweeps (security, mech-interp, foundations) via web + arXiv/OpenReview/ACL, each entry verified by fetching its page.
**Counts:** ~27 items · peer-reviewed: SEDD (ICML'24 best paper), MDLM (NeurIPS'24), DiffuLLaMA (ICLR'25), Block Diffusion (ICLR'25 oral), Fast-dLLM (ICLR'26), DIJA/A2D/DiffuGuard (ICLR'26); rest preprints/industry reports.

> **State of the field (mid-2026).** Masked/absorbing discrete diffusion is the dominant paradigm; open 7–8B models (LLaDA, Dream) rival same-size AR models on general/math/code, and commercial systems (Inception **Mercury**, Google **Gemini Diffusion**) deliver the real selling point — parallel decoding at >1,000 tok/s. The recipe has consolidated: AR-initialization/adaptation + block/semi-autoregressive decomposition (to recover KV cache + arbitrary length) + training-free parallel-decoding accelerators. Diffusion's structural edges — bidirectional infilling, arbitrary-order generation, planning/constraint-satisfaction, built-in error correction — are now empirically real. **Security and interpretability of these models are nascent (born mid/late-2025) but accelerating**, and they do **not** behave like AR models: the decoding mechanism itself is an attack surface, AR safety alignment doesn't transfer, and standard interp tools port but behave qualitatively differently.

---

## ★ Most important (priority order — security & interp first)
1. ◆ [**DIJA — The Devil behind the mask**](https://arxiv.org/abs/2507.11097) — ICLR 2026 — first dLLM-native jailbreak; the decoding mechanism *is* the attack surface.
2. ◆ [**A2D: Any-Order, Any-Step Safety Alignment**](https://arxiv.org/abs/2509.23286) — ICLR 2026 — AR alignment doesn't transfer; diffusion-native refusal cuts DIJA ASR >80%→~1%.
3. ◆ [**DLM-Scope: SAEs for Diffusion LMs**](https://arxiv.org/abs/2602.05859) — first SAE framework for dLLMs; SAE insertion in early layers *reduces* loss (opposite of AR).
4. ◆ [**DiffuGuard**](https://arxiv.org/abs/2509.24296) — ICLR 2026 — training-free defense from a "denoising-path dependence" diagnosis.
5. ◆ [**How Transparent is DiffusionGemma?**](https://arxiv.org/abs/2606.20560) — Nanda/GDM — first interp study of a diffusion LLM; monitorability ≈ AR once mapped.
6. ◆ [**Thinking Out of Order**](https://arxiv.org/abs/2601.22035) — output order ≠ reasoning order in dLLMs → CoT-monitoring is more fraught than for AR.
7. [**LLaDA: Large Language Diffusion Models**](https://arxiv.org/abs/2502.09992) — the proof-at-scale open 8B dLLM.
8. [**Block Diffusion (BD3-LMs)**](https://arxiv.org/abs/2503.09573) — ICLR'25 oral — the semi-AR blueprint behind the efficient/commercial dLLMs.
9. ◆ [**Extracting Training Data from dLLMs via Infilling**](https://arxiv.org/abs/2605.24173) — bidirectional infilling is a new extraction channel AR audits miss.
10. ◆ [**Mechanism Shift AR→Masked Diffusion**](https://arxiv.org/abs/2601.14758) — circuit-level: planning tasks discard inherited AR circuits, computation moves earlier.

---

## §A — Security & safety of dLLMs (HIGH priority; field ~1 yr old)
**Attacks (decoding mechanism = attack surface):**
- ◆ [**The Devil behind the mask: An emergent safety vulnerability of Diffusion LLMs (DIJA)**](https://arxiv.org/abs/2507.11097) — Wen, Qu, Chen et al., ICLR 2026 — 2025-07 — interleaved mask-text prompts force the model to fill masked spans; bidirectional modeling keeps them coherent even when harmful and parallel decoding removes mid-generation refusal. Up to 100% keyword-ASR on Dream-Instruct; +78.5 pts evaluator-ASR over the best AR baseline, no content rewriting. *The canonical dLLM jailbreak.*
- [**Jailbreaking Large Language Diffusion Models (PAD)**](https://arxiv.org/abs/2507.19227) — Zhang, Xie, Zhou et al., preprint — 2025-07 — "Multi-Point Attention Attack" seeds affirmative patterns across positions to steer the parallel denoising trajectory; ~97% ASR across four LLDMs, harmful output ~2× faster than size-matched AR. *Concurrent confirmation parallel decoding is exploitable.*
- [**Safer by Diffusion, Broken by Context**](https://arxiv.org/abs/2602.00388) — He, …, Torr, Bibi, Yu, preprint — 2026-01 — dLLMs have an *intrinsic* safety "blessing" (denoising progressively suppresses unsafe content) but a black-box context-nesting attack defeats it — including a claimed first jailbreak of **Gemini Diffusion** (deployed). *Reframes "are dLLMs safer?" → yes by default, no under context manipulation.*

**Defenses & alignment:**
- ◆ [**A2D: Any-Order, Any-Step Safety Alignment for Diffusion LMs**](https://arxiv.org/abs/2509.23286) — Jeung, Yoon, Cho et al., ICLR 2026 — 2025-09 — trains the model to emit an `[EOS]` refusal under randomized masking so safety holds across arbitrary order/steps; cuts DIJA ASR >80%→~1.3% (LLaDA-8B)/0.0% (Dream-7B), up to 19.3× faster safe termination. *Strongest evidence AR alignment doesn't transfer + the leading diffusion-native fix.*
- ◆ [**DiffuGuard: How Intrinsic Safety is Lost and Found**](https://arxiv.org/abs/2509.24296) — Li, Nie, Zhou et al., ICLR 2026 — 2025-09 — training-free defense: Stochastic Annealing Remasking (vs pre-optimized prompts) + Block-level Audit & Repair (vs dLLM-native attacks); ASR 47.9%→14.7% across six jailbreaks, utility preserved. *Leading inference-time defense.*
- [**Step-Wise Refusal Dynamics in AR and Diffusion LMs**](https://arxiv.org/abs/2602.02600) — Rahimi et al., preprint — 2026-02 — switching AR→diffusion *sampling* improves jailbreak robustness even at fixed weights (remasking recovers from harmful intermediates); proposes the SRI signal + an attack-agnostic detector trained on benign traces. *Cleanest "weights vs decoding" disentangling.*

**Privacy / memorization & watermarking:**
- ◆ [**Extracting Training Data from Diffusion LMs via Infilling**](https://arxiv.org/abs/2605.24173) — Yihan Wang, N. Asokan, preprint — 2026-05 — "infilling extraction" with arbitrary binary masks; edge-conditioned masks extract up to 3× more verbatim than prefix-only, and higher recall on redacted emails from dLLMs than size-matched AR. *Bidirectional access = new extraction channel AR audits miss.*
- [**Characterizing Memorization in Diffusion LMs**](https://arxiv.org/abs/2603.02333) — Luo, Yu, Li, Bjerva, preprint — 2026-03 — generalized extraction framework; proves a monotone sampling-resolution↔extraction relationship (AR = max-resolution limit); dLLMs show lower PII leakage under aligned prefix-only eval. *Theoretical complement to the infilling attack.*
- [**DMark: Order-Agnostic Watermarking for Diffusion LLMs**](https://arxiv.org/abs/2510.02902) — Wu, Zhong, Qu et al., preprint — 2025-10 — KGW-style watermarks break on dLLMs (they hash preceding tokens, but diffusion finalizes in arbitrary order); predictive + bidirectional watermarking reaches 92–99.5% detection @1% FPR. *Representative of the order-agnostic dLLM-watermark cluster.*

*Maturity:* no dedicated S&P/CCS/USENIX track yet; lives on arXiv + a few ICLR'26 acceptances. Most results on two open models (LLaDA-8B, Dream-7B). **Gap:** indirect prompt-injection *specific* to dLLMs is barely studied.

## §B — Mechanistic interpretability of dLLMs (HIGH priority; field <1 yr old)
- ◆ [**DLM-Scope: Mechanistic Interpretability of Diffusion LMs via SAEs**](https://arxiv.org/abs/2602.05859) — Wang, Jiang, …, Kong, Zou (HKU+Alibaba), preprint — 2026-02 — first SAE framework for dLLMs (Top-K SAEs on Dream-7B, LLaDA-8B); SAE insertion in **early layers *reduces* cross-entropy** (opposite of AR), and diffusion-time interventions beat standard steering. *The closest thing to a foundational MI paper for the architecture.*
- ◆ [**Mechanism Shift During Post-training from AR to Masked Diffusion**](https://arxiv.org/abs/2601.14758) — Kong, Lee, Jo (SNU), preprint — 2026-01 — circuit analysis from the same backbone: locally-causal tasks preserve inherited AR circuits, global/planning tasks discard them and move computation earlier; concentrated specialist circuits become distributed. *Answers "does denoising rewire computation?" — yes, task-dependently.*
- [**Steering Without Breaking: Mechanistically Informed Interventions for Discrete Diffusion LMs**](https://arxiv.org/abs/2605.10971) — Zhou, Roy, Gangadharaiah (AWS), preprint — 2026-05 — SAEs show attributes "commit" on distinct denoising schedules (topic early, sentiment gradual); a schedule-adaptive scheduler injects steering only when each attribute forms, up to 93% control strength, +15 pts over baseline. *Steering counterpart to DLM-Scope.*
- [**Attention Sinks in Diffusion Language Models**](https://arxiv.org/abs/2510.15731) — Rulli et al. (Sapienza), preprint — 2025-10 — dLLM sinks have **dynamic positions shifting across the denoising trajectory** (vs fixed in AR), and masking sinks barely hurts (vs AR's high sensitivity). *Basic building block for dLLM circuit analysis.*
- ◆ [**Thinking Out of Order: When Output Order Stops Reflecting Reasoning Order**](https://arxiv.org/abs/2601.22035) — Yu, Fu, …, Dong (UCR), preprint — 2026-01 — answer-before-explanation tests: AR drops ≤67% accuracy, MDLMs ≤14% because reasoning tokens stabilize earlier than answer tokens. *Key monitorability warning: a dLLM's visible output order ≠ its internal reasoning order.*
- [**Discrete Diffusion Models Exploit Asymmetry to Solve Lookahead Planning**](https://arxiv.org/abs/2602.19980) — Trainin, Ravfogel, Abend, Feder (HUJI/Google), preprint — 2026-02 — planning is asymmetric (hard forward, easy reverse); diffusion exploits it by decoding backward from future tokens; NAR needs exponentially fewer examples. *Mechanistic account of dLLM planning advantage.*
- [**Reasoning with Latent Tokens in Diffusion LMs**](https://arxiv.org/abs/2602.03769) — He, Welleck, Fried (CMU), preprint — 2026-02 — dLLMs jointly predict distributions over all undecoded ("latent") positions each step; ablating that joint prediction speeds inference but hurts reasoning — the latent computation is load-bearing. *Identifies the internal computation behind global coherence.*
- [**Beyond Surface Reasoning: True Long-CoT Capacity of Diffusion LLMs**](https://arxiv.org/abs/2510.09544) — Chen, Li, Qin et al., preprint — 2025-10 — skeptical audit of dLLM "reasoning," surfacing parallel-vs-sequential contradictions and long-chain limits. *Faithfulness/monitorability-relevant.*
- *Cross-ref:* [**How Transparent is DiffusionGemma?**](https://arxiv.org/abs/2606.20560) (Engels/…/Nanda, GDM, 2026-06) — first interp study of a diffusion LLM; the 28.6× "opaque serial depth" disadvantage collapses to 1.1×, monitorability ≈ autoregressive. *(Also in the main backfill §16.)*

*Maturity:* nascent — ~2 SAE/feature papers, 1 circuit study, 1 attention study, several reasoning/order analyses + the GDM anchor; no canonical circuits or agreed tooling yet. **Gap:** no dedicated dLLM-CoT faithfulness/monitorability-for-safety paper beyond the order analyses.

## §C — Foundations, models & capabilities (grounding)
- [**SEDD — Discrete Diffusion by Estimating Data-Distribution Ratios**](https://arxiv.org/abs/2310.16834) — Lou, Meng, Ermon, **ICML 2024 (Best Paper)** — 2023-10 *(pre-window foundation)* — "score entropy" extends score matching to discrete spaces; −25–75% perplexity vs prior, first discrete diffusion LM to beat GPT-2. *The breakthrough that made discrete diffusion serious.*
- [**MDLM — Simple and Effective Masked Diffusion LMs**](https://arxiv.org/abs/2406.07524) — Sahoo, Arriola, …, Kuleshov (Cornell), **NeurIPS 2024** — 2024-06 — Rao-Blackwellized ("SUBS") objective = weighted MLM loss; beats AR perplexity on some datasets; semi-AR arbitrary-length sampling. *Turned masked diffusion into the default paradigm.*
- [**DiffuGPT / DiffuLLaMA — Scaling dLLMs via Adaptation from AR Models**](https://arxiv.org/abs/2410.17891) — Gong et al. (HKU), **ICLR 2025** — 2024-10 — convert GPT2/LLaMA→diffusion with <200B tokens via attention-mask annealing + shift op. *The cheap "adapt, don't train from scratch" on-ramp.*
- [**Block Diffusion (BD3-LMs)**](https://arxiv.org/abs/2503.09573) — Arriola, …, Sahoo, Kuleshov, **ICLR 2025 (Oral)** — 2025-03 — AR over blocks, diffusion within; recovers KV cache + parallel sampling + arbitrary length; SOTA discrete-diffusion perplexity. *The semi-AR blueprint behind Mercury/Gemini Diffusion/Fast-dLLM v2.*
- [**LLaDA: Large Language Diffusion Models**](https://arxiv.org/abs/2502.09992) — Nie, Zhu, …, Li (RUC/Ant), preprint — 2025-02 — 8B from-scratch masked-diffusion LM competitive with LLaMA3-8B; beats GPT-4o on reversal-poem (reversal curse). *Proof-at-scale that capabilities don't need autoregression; spawned LLaDA-V/-MoE/2.0.*
- [**Dream 7B: Diffusion Large Language Models**](https://arxiv.org/abs/2508.15487) — Ye, Xie, …, Kong (HKU/Huawei), preprint — 2025-08 — AR-initialized 7B with context-adaptive token-level noise rescheduling; matches/exceeds same-size AR on general/math/code; strong planning/constraint-satisfaction. *Co-defines the open-weights frontier.*
- [**Mercury: Ultra-Fast LMs Based on Diffusion**](https://arxiv.org/abs/2506.17298) — Inception Labs, industry report — 2025-06 — block-parallel denoising; 1,109/737 tok/s on one H100 (~10× speed-optimized AR), #2 quality / #1 speed in Copilot Arena. *First commercial-scale dLLM.*
- [**Gemini Diffusion**](https://deepmind.google/models/gemini-diffusion/) — Google DeepMind, model/blog — 2025-05 — block-parallel decoder (≥128 tok/step), ~1,479 tok/s with iterative error correction, rivaling comparable AR on quality. *A frontier lab validating text diffusion.*
- [**DiffuCoder: Masked Diffusion for Code Generation**](https://arxiv.org/abs/2506.20639) — Gong, Zhang, …, Gu, Kong, Zhang (Apple/HKU), preprint — 2025-06 — 7B code dLLM + **Coupled-GRPO** (complementary mask-noise RL, lower log-likelihood variance), +4.4% EvalPlus to match Qwen2.5-Coder. *Shows RL must be redesigned for diffusion; code = natural killer app.*
- [**Fast-dLLM: Training-free KV Cache + Parallel Decoding**](https://arxiv.org/abs/2505.22618) — NVIDIA et al., **ICLR 2026** — 2025-05 — block-wise approximate KV cache + confidence-aware parallel decode; drops into LLaDA/Dream, LLaDA-V latency 60s→6s. *Solved the two bottlenecks that kept open dLLMs slower than AR.*
- *Honorable mentions:* LLaDA-MoE (2509.24389), LLaDA 2.0 (100B MoE), Dream-Coder 7B (2509.01142); scaling-law analyses [2602.15014](https://arxiv.org/abs/2602.15014), [2512.10858](https://arxiv.org/abs/2512.10858).

## Caveats
- **Security "safer/less-safe" is conditional** — dLLMs resist *ported AR* jailbreaks and prefix-only privacy probes, but diffusion-native attacks (DIJA/PAD) and infilling extraction reverse it. Don't average ASR numbers across papers (keyword vs evaluator vs StrongREJECT, different model sets).
- **Heavy preprint share** — security/interp are <1 yr old; only DIJA/A2D/DiffuGuard/Fast-dLLM are peer-reviewed (ICLR'26). Many 2026 IDs are very fresh.
- **Vendor-reported** — Gemini Diffusion / Mercury throughput & quality come from blogs/abstracts, not independently verified.
- **Genuine gaps:** dLLM-specific indirect prompt injection; a dedicated dLLM-CoT-monitorability-for-safety paper. Both are open opportunities.

{% endraw %}
