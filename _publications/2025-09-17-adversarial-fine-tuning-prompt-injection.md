---
title: "Early Approaches to Adversarial Fine-Tuning for Prompt Injection Defense: A 2022 Study of GPT-3 and Contemporary Models"
collection: publications
permalink: /publication/2025-adversarial-fine-tuning-prompt-injection
excerpt: 'A 2022 study of prompt injection and goal hijacking attacks against GPT-3-era models, introducing Adversarial Fine-Tuning as a defense that drove attack success from 31% to near zero on smaller GPT-3 variants.'
date: 2025-09-17
venue: 'arXiv preprint (arXiv:2509.14271)'
paperurl: 'https://arxiv.org/abs/2509.14271'
citation: 'Gustavo Sandoval, Denys Fenchenko, and Junyao Chen. (2025). &quot;Early Approaches to Adversarial Fine-Tuning for Prompt Injection Defense: A 2022 Study of GPT-3 and Contemporary Models.&quot; <i>arXiv preprint arXiv:2509.14271</i>.'
---
This paper documents early research conducted in 2022 on defending against prompt injection attacks in large language models, providing historical context for the evolution of the field. We study two adversarial attacks against LLMs — prompt injection and goal hijacking — examining how to construct them, testing them across models, and comparing their effectiveness.

We propose and evaluate **Adversarial Fine-Tuning** as a defense. Without it, attacks succeeded 31% of the time on GPT-3 series models; with it, attack success dropped to near zero for smaller GPT-3 variants (Ada, Babbage, Curie). We also find that more flexible models are more vulnerable — large models such as GPT-3 Davinci are more susceptible than smaller models like GPT-2. While the specific models tested are now superseded, the core methodology and empirical findings helped lay groundwork for modern prompt injection defenses, including instruction-hierarchy systems and constitutional AI approaches.

[arXiv:2509.14271](https://arxiv.org/abs/2509.14271)
