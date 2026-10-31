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
  {% for week in site.data.radar_weeks %}
    {% assign covered = site.radar | where: "group", week.slug | sort: "date" | reverse %}
    <div class="post-entry">
      {% if week.type == "weekly" %}
        {% assign issue = weeklies | where: "slug", week.slug | first %}
        <span class="post-date">{{ issue.date | date: "%Y-%m-%d" }}</span>
        <a href="{{ issue.url | relative_url }}" class="post-link">{{ issue.title }}</a>
        {% if issue.summary != "" %}<p class="post-summary">{{ issue.summary }}</p>{% endif %}
        <div class="post-tags">
          <span class="post-tag">{{ issue.kind }}</span>
          {% if issue.styled %}<span class="post-tag">illustrated</span>{% endif %}
          <a class="post-tag post-tag-link" href="{{ issue.source_url }}">source</a>
        </div>
      {% else %}
        <span class="post-date">{{ week.date }}</span>
        <span class="post-link radar-unsummarised">{{ week.label }}</span>
      {% endif %}
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
    border-bottom: 1px solid var(--rule);
  }
  .radar-list .post-entry:last-child { border-bottom: 0; }

  .radar-list .post-date {
    display: block;
    width: auto;
    color: var(--teal);
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
    color: var(--muted);
    font-size: 15px;
    line-height: 1.55;
  }

  .radar-list .post-tags { margin-top: 9px; }

  .radar-list .post-tag {
    display: inline-block;
    margin: 0 6px 0 0;
    padding: 2px 8px;
    border: 1px solid var(--rule);
    border-radius: 3px;
    color: var(--muted);
    font-size: 11.5px;
  }


  .radar-label {
    margin: 34px 0 18px;
    color: var(--muted);
    font-size: 12px;
    letter-spacing: 0.09em;
    text-transform: uppercase;
  }
  .radar-list .radar-label:first-child { margin-top: 0; }

  .radar-children {
    margin: 11px 0 0;
    font-size: 13px;
    line-height: 1.8;
    color: var(--muted);
  }
  .radar-children-label { margin-right: 4px; }
  .radar-list .radar-unsummarised { color: var(--muted); font-weight: 500; }
  .radar-children a { color: var(--muted); }
  .radar-children a:hover { color: var(--red); }
  .radar-sep { padding: 0 6px; color: var(--rule); }

  .radar-list .post-tag-link { text-decoration: none; }
  .radar-list .post-tag-link:hover { color: var(--muted); border-color: var(--red); }
</style>
