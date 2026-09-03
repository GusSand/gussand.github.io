#!/usr/bin/env python3
"""Sync research-radar reports into the _radar Jekyll collection.

Reports live at https://github.com/GusSand/research-radar under reports/.
Each report exists as Markdown, and (from 2026-07-22 on) also as HTML with its
own self-contained design. We publish the HTML version standalone when it
exists, and fall back to rendering the Markdown in the site's own style.

Usage: python3 scripts/sync_radar.py --source /path/to/research-radar
"""

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/GusSand/research-radar"
KINDS = ("daily", "weekly", "backfill")

WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
ARTIFACT_RE = re.compile(r"https://claude\.ai/code/artifact/[0-9a-f-]+")
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
STYLE_RE = re.compile(r"<style\b.*?</style>", re.S | re.I)
HEAD_RE = re.compile(r"<head\b[^>]*>(.*?)</head>", re.S | re.I)
BODY_RE = re.compile(r"<body\b[^>]*>(.*?)</body>", re.S | re.I)
BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def slug_date(slug, fallback):
    """Best-effort real date for a report slug, else its last-commit date."""
    m = DATE_RE.match(slug)
    if m:
        return dt.date(*(int(g) for g in m.groups()))
    m = WEEK_RE.match(slug)
    if m:
        year, week = int(m.group(1)), int(m.group(2))
        return dt.date.fromisocalendar(year, week, 1)
    return fallback


def git_date(source, path):
    try:
        out = subprocess.run(
            ["git", "-C", str(source), "log", "-1", "--format=%cs", "--", str(path)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return dt.date.fromisoformat(out)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        pass
    return dt.date.today()


def plain(line):
    """Strip the markdown a summary line picks up, leaving readable prose."""
    line = LINK_RE.sub(r"\1", line)
    line = BOLD_RE.sub(r"\1", line)
    return line.replace("*", "").replace("`", "").strip()


def md_title(text, slug):
    for line in text.splitlines():
        if line.startswith("# "):
            return plain(line[2:])
    return f"Research Radar — {slug}"


def md_summary(text):
    """The Window/Counts/Coverage header lines, as one sentence-ish blurb."""
    wanted = ("**Window:**", "**Counts:**", "**Coverage:**", "**Compiled:**")
    parts = []
    for line in text.splitlines()[:12]:
        line = line.strip()
        if line.startswith(wanted):
            parts.append(plain(line))
    return " · ".join(parts)


def md_window(text):
    """The report's coverage window, e.g. "July 6-12, 2026"."""
    for line in text.splitlines()[:12]:
        line = line.strip()
        if line.startswith("**Window:**"):
            return plain(line[len("**Window:**"):].split("·")[0])
    return ""


def iso_covered_week(slug):
    """The ISO week a weekly report covers, from its slug.

    Weeklies are named for the week they go out in, and summarise the week
    before: 2026-W29 ships Monday 13 July and covers 6-12 July.
    """
    m = WEEK_RE.match(slug)
    if not m:
        return None
    monday = dt.date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
    year, week, _ = (monday - dt.timedelta(days=7)).isocalendar()
    return year, week


def normalize_html(raw):
    """Return (title, fragment) for either a full document or a bare fragment.

    Most reports are fragments written for the Claude artifact wrapper: they
    open at <title>/<style> with no doctype, html, head or body. A few are
    complete documents. Both end up as a fragment we can drop into a layout.
    """
    title_m = TITLE_RE.search(raw)
    title = title_m.group(1).strip() if title_m else None

    body_m = BODY_RE.search(raw)
    if body_m:
        head_m = HEAD_RE.search(raw)
        styles = "\n".join(STYLE_RE.findall(head_m.group(1))) if head_m else ""
        fragment = f"{styles}\n{body_m.group(1)}"
    else:
        fragment = TITLE_RE.sub("", raw, count=1)

    return title, fragment.strip()


def front_matter(fields):
    lines = ["---"]
    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, (dt.date, int)):
            lines.append(f"{key}: {value}")
        else:
            lines.append(f'{key}: "{str(value).replace(chr(34), chr(39))}"')
    lines.append("---")
    return "\n".join(lines)


def collect(source):
    """Every report in the source repo, as dicts, before grouping."""
    reports = []
    for kind in KINDS:
        src_dir = source / "reports" / kind
        if not src_dir.is_dir():
            continue
        for md_path in sorted(src_dir.glob("*.md")):
            slug = md_path.stem
            md_text = md_path.read_text(encoding="utf-8")
            html_path = md_path.with_suffix(".html")
            reports.append({
                "kind": kind,
                "slug": slug,
                "md_path": md_path,
                "md_text": md_text,
                "html_path": html_path if html_path.is_file() else None,
                "date": slug_date(slug, git_date(source, md_path.relative_to(source))),
            })
    return reports


def assign_groups(reports):
    """Roll each daily up under the weekly that summarises its week.

    A daily whose week never got a weekly stays in the "latest" group and is
    listed in full on the index; the rest collapse under their weekly.
    """
    covered = {}
    for r in reports:
        if r["kind"] == "weekly":
            week = iso_covered_week(r["slug"])
            if week:
                covered[week] = r["slug"]

    for r in reports:
        if r["kind"] != "daily":
            r["group"] = r["kind"]
            continue
        year, week, _ = r["date"].isocalendar()
        r["group"] = covered.get((year, week), "latest")


def build(source, out_dir):
    reports = collect(source)
    assign_groups(reports)

    written = []
    for r in reports:
        md_text, slug, kind = r["md_text"], r["slug"], r["kind"]
        has_html = r["html_path"] is not None
        artifact_m = ARTIFACT_RE.search(md_text)
        common = {
            "kind": kind,
            "slug": slug,
            "date": r["date"],
            "group": r["group"],
            "window": md_window(md_text),
            "summary": md_summary(md_text),
            "artifact": artifact_m.group(0) if artifact_m else None,
            "source_url": f"{REPO_URL}/blob/main/reports/{kind}/{r['md_path'].name}",
            "styled": has_html,
            # reports wrap their body in {% raw %}, which Jekyll's excerpt
            # splitter would cut in half; we never use the excerpt anyway
            "excerpt_separator": "",
        }

        if has_html:
            title, fragment = normalize_html(r["html_path"].read_text(encoding="utf-8"))
            fields = {"layout": "radar", "title": title or md_title(md_text, slug), **common}
            body = fragment
            dest = out_dir / f"{slug}.html"
        else:
            fields = {"layout": "radar-page", "title": md_title(md_text, slug), **common}
            body = md_text
            dest = out_dir / f"{slug}.md"

        dest.write_text(
            f"{front_matter(fields)}\n\n{{% raw %}}\n{body}\n{{% endraw %}}\n",
            encoding="utf-8",
        )
        written.append(dest.name)
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path,
                        help="path to a checkout of GusSand/research-radar")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "_radar")
    args = parser.parse_args()

    if not (args.source / "reports").is_dir():
        sys.exit(f"no reports/ directory under {args.source}")

    args.out.mkdir(parents=True, exist_ok=True)
    for stale in list(args.out.glob("*.md")) + list(args.out.glob("*.html")):
        stale.unlink()

    written = build(args.source, args.out)
    print(f"wrote {len(written)} radar issues to {args.out}")


if __name__ == "__main__":
    main()
