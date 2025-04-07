---
layout: default
---

## Recent Work

<div class="post-list">
  <div class="post-entry">
    <span class="post-date">2023-08</span>
    <a href="https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval" class="post-link" target="_blank">Lost at C: A User Study on the Security Implications of Large Language Model Code Assistants</a>
    <p class="post-summary">
      Large Language Models (LLMs) such as OpenAI Codex are increasingly being used as AI-based coding assistants. We conducted a security-driven user study (N=58) to assess code written by student programmers when assisted by LLMs. Our results indicate that in low-level C programming with pointer and array manipulations, the security impact is small: AI-assisted users produce critical security bugs at a rate no greater than 10% more than the control, indicating the use of LLMs does not introduce new security risks.
    </p>
    <div class="post-links">
      <a href="https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval" target="_blank" class="link-button">Paper</a>
      <a href="https://www.usenix.org/system/files/sec23summer_sandoval.pdf" target="_blank" class="link-button">PDF</a>
      <a href="https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval" target="_blank" class="link-button">Slides</a>
    </div>
  </div>

  <div class="post-entry">
    <span class="post-date">2023-05</span>
    <a href="/teaching/" class="post-link">Teaching ML Security at Scale: Challenges and Opportunities</a>
    <p class="post-summary">
      An exploration of pedagogical approaches to teaching machine learning security concepts to large undergraduate and graduate classes. This work presents curriculum design strategies, hands-on exercises, and assessment techniques that effectively prepare students for security challenges in deployed ML systems.
    </p>
    <div class="post-links">
      <a href="/teaching/" class="link-button">Course Materials</a>
    </div>
  </div>

  <div class="post-entry">
    <span class="post-date">2022-12</span>
    <a href="/research/" class="post-link">Robust Defenses Against Adversarial Attacks in Vision Transformers</a>
    <p class="post-summary">
      This research investigates novel defense mechanisms against adversarial examples targeting vision transformer architectures. We demonstrate that certain architectural modifications can significantly improve robustness while maintaining performance on clean inputs.
    </p>
    <div class="post-links">
      <a href="/research/" class="link-button">Research</a>
    </div>
  </div>
</div>

## Recent News

- **August 2023**: Presented our paper on LLM code assistants at USENIX Security '23
- **May 2023**: Received teaching award for CS-GY 6033 Design and Analysis of Algorithms
- **January 2023**: New course on Machine Learning Security launched 

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