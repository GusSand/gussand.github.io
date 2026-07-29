---
layout: page
title: "Blog"
permalink: /archives/
---

---

<section class="posts">
  {% for post in site.posts %}
    <div class="post-entry">
      <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
      <a href="{{ post.url | relative_url }}" class="post-link">{{ post.title }}</a>
      <p class="post-summary">
        {% if post.description %}{{ post.description }}{% else %}{{ post.excerpt | strip_html | truncatewords: 45 }}{% endif %}
      </p>
      {% if post.tags.size > 0 %}
      <div class="post-tags">
        {% for tag in post.tags limit:5 %}<span class="post-tag">{{ tag }}</span>{% endfor %}
      </div>
      {% endif %}
    </div>
  {% endfor %}

  {% if site.posts.size == 0 %}
    <p>No posts yet. Check back soon!</p>
  {% endif %}
</section>

<style>
  .posts .post-entry {
    margin: 0 0 26px;
    padding-bottom: 22px;
    border-bottom: 1px solid #1e1e1c;
  }
  .posts .post-entry:last-child { border-bottom: 0; }

  .posts .post-date {
    display: block;
    width: auto;
    color: #6f6e69;
    font-size: 12.5px;
    letter-spacing: 0.04em;
    margin-bottom: 3px;
  }

  .posts .post-link {
    display: inline-block;
    font-size: 19px;
    font-weight: 600;
    line-height: 1.3;
  }

  .posts .post-summary {
    margin: 7px 0 0;
    color: #a3a29b;
    font-size: 15px;
    line-height: 1.55;
  }

  .posts .post-tags { margin-top: 9px; }

  .posts .post-tag {
    display: inline-block;
    margin: 0 6px 0 0;
    padding: 2px 8px;
    border: 1px solid #2c2c2a;
    border-radius: 3px;
    color: #6f6e69;
    font-size: 11.5px;
  }
</style>
