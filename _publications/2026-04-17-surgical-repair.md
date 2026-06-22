---
title: "Surgical Repair of Insecure Code Generation in LLMs: From Mechanistic Diagnosis to Deployment-Ready Intervention"
collection: publications
permalink: /publication/2026-surgical-repair
excerpt: 'LLMs that write insecure code can often correctly explain the very vulnerability they just introduced — a "Format-Reliability Gap." We trace this to a single layer and use per-vulnerability steering vectors to cut insecure generation by up to 74%.'
date: 2026-04-17
venue: 'arXiv preprint (arXiv:2604.16697)'
paperurl: 'https://arxiv.org/abs/2604.16697'
citation: 'Gustavo Sandoval, Brendan Dolan-Gavitt, and Siddharth Garg. (2026). &quot;Surgical Repair of Insecure Code Generation in LLMs: From Mechanistic Diagnosis to Deployment-Ready Intervention.&quot; <i>arXiv preprint arXiv:2604.16697</i>.'
---
Large language models write production code, yet they routinely introduce well-known vulnerabilities. We show this is not a knowledge deficit: the same models that generate insecure code correctly identify and explain the vulnerability when asked directly. We call this the **Format-Reliability Gap**.

Mechanistic analysis reveals the cause: security-relevant representations are encoded from the earliest layers but remain computationally inert until the final layer, where format-compliance demands compete with them. Because the failure is localized to a single layer, per-vulnerability steering vectors reduce insecure generation by up to 74% with negligible overhead — a targeted intervention rather than broad retraining.

[arXiv:2604.16697](https://arxiv.org/abs/2604.16697) &middot; [HTML](https://arxiv.org/html/2604.16697v1)
