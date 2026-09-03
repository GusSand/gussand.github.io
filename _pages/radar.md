---
layout: page
title: "Research Radar"
permalink: /radar/
description: "A daily and weekly automated radar of new AI/LLM safety, alignment, and pragmatic mechanistic-interpretability research."
---

---

[Research Radar](https://github.com/GusSand/research-radar) is an automated sweep of new
work in AI/LLM safety, alignment, and pragmatic mechanistic interpretability. Claude Code
cloud routines search OpenReview, the ACL Anthology, TMLR, arXiv (cs.CL / cs.LG / cs.CR /
cs.AI), and the alignment forums, then write up what they find: a daily top ten Tuesday
through Sunday, and a wider aggregate on Monday mornings.

Entries are ranked by importance to that agenda rather than by recency, and peer-reviewed
work outranks incremental preprints. Each one carries a technical summary of method and
result rather than a reprinted abstract, plus the venue and its peer-review status. If a
day turns up fewer than ten genuinely relevant papers, the report says so instead of
padding.

<section class="radar-list">
  {% assign latest = site.radar | where: "group", "latest" | sort: "date" | reverse %}
  {% assign weeklies = site.radar | where: "kind", "weekly" | sort: "date" | reverse %}
  {% assign backfills = site.radar | where: "kind", "backfill" | sort: "date" | reverse %}

  {% if latest.size > 0 %}
    {% if weeklies.size > 0 %}<p class="radar-label">Since the last weekly</p>{% endif %}
    {% for issue in latest %}
      <div class="post-entry">
        <span class="post-date">{{ issue.date | date: "%Y-%m-%d" }}</span>
        <a href="{{ issue.url | relative_url }}" class="post-link">{{ issue.title }}</a>
        {% if issue.summary != "" %}<p class="post-summary">{{ issue.summary }}</p>{% endif %}
        <div class="post-tags">
          <span class="post-tag">{{ issue.kind }}</span>
          {% if issue.styled %}<span class="post-tag">illustrated</span>{% endif %}
          <a class="post-tag post-tag-link" href="{{ issue.source_url }}">source</a>
        </div>
      </div>
    {% endfor %}
  {% endif %}

  {% if weeklies.size > 0 %}<p class="radar-label">Weekly editions</p>{% endif %}
  {% for issue in weeklies %}
    {% assign covered = site.radar | where: "group", issue.slug | sort: "date" | reverse %}
    <div class="post-entry">
      <span class="post-date">{{ issue.date | date: "%Y-%m-%d" }}</span>
      <a href="{{ issue.url | relative_url }}" class="post-link">{{ issue.title }}</a>
      {% if issue.summary != "" %}<p class="post-summary">{{ issue.summary }}</p>{% endif %}
      <div class="post-tags">
        <span class="post-tag">{{ issue.kind }}</span>
        {% if issue.styled %}<span class="post-tag">illustrated</span>{% endif %}
        <a class="post-tag post-tag-link" href="{{ issue.source_url }}">source</a>
      </div>
      {% if covered.size > 0 %}
        <p class="radar-children">
          <span class="radar-children-label">Dailies:</span>
          {% for day in covered %}<a href="{{ day.url | relative_url }}">{{ day.date | date: "%b %-d" }}</a>{% unless forloop.last %}<span class="radar-sep">·</span>{% endunless %}{% endfor %}
        </p>
      {% endif %}
    </div>
  {% endfor %}

  {% if backfills.size > 0 %}<p class="radar-label">Backfill</p>{% endif %}
  {% for issue in backfills %}
    <div class="post-entry">
      <span class="post-date">{{ issue.date | date: "%Y-%m-%d" }}</span>
      <a href="{{ issue.url | relative_url }}" class="post-link">{{ issue.title }}</a>
      {% if issue.summary != "" %}<p class="post-summary">{{ issue.summary }}</p>{% endif %}
      <div class="post-tags">
        <span class="post-tag">{{ issue.kind }}</span>
        {% if issue.styled %}<span class="post-tag">illustrated</span>{% endif %}
        <a class="post-tag post-tag-link" href="{{ issue.source_url }}">source</a>
      </div>
    </div>
  {% endfor %}

  {% if site.radar.size == 0 %}
    <p>No issues synced yet. Run <code>scripts/sync_radar.py</code> or the
    <code>sync-radar</code> workflow to pull them in.</p>
  {% endif %}
</section>

<style>
  .radar-list { margin-top: 34px; }

  .radar-list .post-entry {
    margin: 0 0 26px;
    padding-bottom: 22px;
    border-bottom: 1px solid #1e1e1c;
  }
  .radar-list .post-entry:last-child { border-bottom: 0; }

  .radar-list .post-date {
    display: block;
    width: auto;
    color: #6f6e69;
    font-size: 12.5px;
    letter-spacing: 0.04em;
    margin-bottom: 3px;
  }

  .radar-list .post-link {
    display: inline-block;
    font-size: 19px;
    font-weight: 600;
    line-height: 1.3;
  }

  .radar-list .post-summary {
    margin: 7px 0 0;
    color: #a3a29b;
    font-size: 15px;
    line-height: 1.55;
  }

  .radar-list .post-tags { margin-top: 9px; }

  .radar-list .post-tag {
    display: inline-block;
    margin: 0 6px 0 0;
    padding: 2px 8px;
    border: 1px solid #2c2c2a;
    border-radius: 3px;
    color: #6f6e69;
    font-size: 11.5px;
  }


  .radar-label {
    margin: 34px 0 18px;
    color: #6f6e69;
    font-size: 12px;
    letter-spacing: 0.09em;
    text-transform: uppercase;
  }
  .radar-list .radar-label:first-child { margin-top: 0; }

  .radar-children {
    margin: 11px 0 0;
    font-size: 13px;
    line-height: 1.8;
    color: #6f6e69;
  }
  .radar-children-label { margin-right: 4px; }
  .radar-children a { color: #8a8981; }
  .radar-children a:hover { color: #c9c8c1; }
  .radar-sep { padding: 0 6px; color: #3a3a37; }

  .radar-list .post-tag-link { text-decoration: none; }
  .radar-list .post-tag-link:hover { color: #a3a29b; border-color: #4a4a46; }
</style>
