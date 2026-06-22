---
layout: default
---

## Recent Work

<div class="post-list">
  <div class="post-entry">
    <span class="post-date">2026-04</span>
    <a href="https://arxiv.org/abs/2604.16697" class="post-link" target="_blank">Surgical Repair of Insecure Code Generation in LLMs: From Mechanistic Diagnosis to Deployment-Ready Intervention</a>
    <p class="post-summary">
      LLMs that write insecure code can often correctly explain the very vulnerability they just introduced — a gap we call the "Format-Reliability Gap." Mechanistic analysis traces this to a single layer where format-compliance demands crowd out otherwise-present security representations. Because the failure is localized, per-vulnerability steering vectors reduce insecure generation by up to 74% with negligible overhead.
    </p>
    <div class="post-links">
      <a href="https://arxiv.org/abs/2604.16697" target="_blank" class="link-button">arXiv</a>
      <a href="https://arxiv.org/html/2604.16697v1" target="_blank" class="link-button">HTML</a>
    </div>
  </div>

  <div class="post-entry">
    <span class="post-date">2025-09</span>
    <a href="https://arxiv.org/abs/2509.14271" class="post-link" target="_blank">Early Approaches to Adversarial Fine-Tuning for Prompt Injection Defense</a>
    <p class="post-summary">
      A study of prompt injection and goal hijacking against GPT-3-era models, introducing Adversarial Fine-Tuning as a defense. Without it, attacks succeeded 31% of the time; with it, attack success dropped to near zero for smaller GPT-3 variants. We also find more flexible models are more vulnerable — large models like GPT-3 Davinci more so than GPT-2.
    </p>
    <div class="post-links">
      <a href="https://arxiv.org/abs/2509.14271" target="_blank" class="link-button">arXiv</a>
    </div>
  </div>

  <div class="post-entry">
    <span class="post-date">2023-08</span>
    <a href="https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval" class="post-link" target="_blank">Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants</a>
    <p class="post-summary">
      Large Language Models (LLMs) such as OpenAI Codex are increasingly being used as AI-based coding assistants. We conducted a security-driven user study (N=58) to assess code written by student programmers when assisted by LLMs. Our results indicate that in low-level C programming with pointer and array manipulations, the security impact is small: AI-assisted users produce critical security bugs at a rate no greater than 10% more than the control, indicating the use of LLMs does not introduce new security risks.
    </p>
    <div class="post-links">
      <a href="https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval" target="_blank" class="link-button">Paper</a>
      <a href="https://www.usenix.org/system/files/sec23summer_sandoval.pdf" target="_blank" class="link-button">PDF</a>
    </div>
  </div>
</div>

## Recent News

- **April 2026**: New preprint on surgically repairing insecure code generation in LLMs is out
- **September 2025**: Released our study on early adversarial fine-tuning for prompt injection defense
- **August 2023**: Presented "Lost at C" at USENIX Security '23

## Recent Blog Posts

<div class="post-list">
  {% for post in site.posts limit:3 %}
  <div class="post-entry">
    <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
    <a href="{{ post.url | relative_url }}" class="post-link">{{ post.title }}</a>
    <p class="post-summary">
      {{ post.content | strip_html | truncatewords: 50 }}
    </p>
    <div class="post-links">
      <a href="{{ post.url | relative_url }}" class="link-button">Read More</a>
    </div>
  </div>
  {% endfor %}
</div>

<p class="see-all">
  <a href="/archives/">See all blog posts →</a>
</p> 