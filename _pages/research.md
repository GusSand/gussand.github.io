---
layout: page
title: "Research"
permalink: /research/
---

---

## Research interests

My research asks why language models fail to act on what they know about safety, and what to do about it. I work on three steps: find where safe behavior breaks down inside the model, repair it without retraining, and prevent unsafe behavior from being learned in the first place.

- **Diagnosis: how safety breaks during training.** How refusal and other safe behavior erode across pretraining and post-training (SFT, DPO and RL), measured inside the model with tools such as the [refusal direction](/posts/2026/10/refusal-direction-two-years-later/).
- **Intervention: repair without retraining.** Probes and steering vectors that locate where a model's safe knowledge gets lost and push the decision back. [Insecure code generation](/posts/2026/10/models-know-the-fix/) is my first worked case.
- **Prevention: open-weight risk.** Which training data teaches an unsafe behavior, whether [data attribution](/posts/2026/10/safety-data-attribution/) or filtering can stop it, and how to test safeguards against attackers who hold the weights.
- **Measurement: safety numbers you can trust.** Red-teaming methods, judges and benchmarks, and why one model gets different safety numbers from different evaluations.

Earlier work, which I still build on, studied how AI coding assistants affect the security of the code people write ([Lost at C](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval)) and how to defend against prompt injection.

I received my PhD from NYU and was advised by [Siddharth Garg](https://engineering.nyu.edu/faculty/siddharth-garg) and [Brendan Dolan-Gavitt](https://engineering.nyu.edu/faculty/brendan-dolan-gavitt), and a member of the [EnSuRe Research Lab](https://wp.nyu.edu/ensure_group/).

## Publications

### 2026
- **Sandoval, G.**, Dolan-Gavitt, B., & Garg, S. "Surgical Repair of Insecure Code Generation in LLMs: From Mechanistic Diagnosis to Deployment-Ready Intervention." *arXiv preprint arXiv:2604.16697.* [[paper]](https://arxiv.org/abs/2604.16697)

### 2025
- **Sandoval, G.**, Fenchenko, D., & Chen, J. "Early Approaches to Adversarial Fine-Tuning for Prompt Injection Defense: A 2022 Study of GPT-3 and Contemporary Models." *arXiv preprint arXiv:2509.14271.* [[paper]](https://arxiv.org/abs/2509.14271)

### 2023
- **Sandoval, G.**, Pearce, H., Nys, T., Karri, R., Garg, S., & Dolan-Gavitt, B. "Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants." *32nd USENIX Security Symposium (USENIX Security '23).* [[paper]](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval) [[PDF]](https://www.usenix.org/system/files/sec23summer_sandoval.pdf) *(G. Sandoval and H. Pearce contributed equally.)*

## Collaborations

I'm always interested in collaborating with other researchers in AI safety and interpretability. Feel free to reach out if you're working on related problems.
