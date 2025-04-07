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
    </div>
  {% endfor %}

  {% if site.posts.size == 0 %}
    <p>No posts yet. Check back soon!</p>
  {% endif %}
</section>

<style>
  .post-entry {
    margin-bottom: 10px;
  }
  .post-date {
    color: #aaa;
    display: inline-block;
    width: 120px;
  }
  .post-link {
    display: inline-block;
  }
</style> 