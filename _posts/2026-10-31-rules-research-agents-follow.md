---
title: 'The rules my research agents actually follow'
short_title: 'The rules my research agents follow'
description: 'A year of running ML research with Claude Code, from an agent that asked which of three roles to play to one that works overnight behind commit gates. Which rules held, which ones the agent ignored, and what I took from a friend who went the other way.'
date: 2026-10-31
permalink: /posts/2026/10/research-agent-rules/
tags:
  - AI Agents
  - Claude Code
  - Research Process
kind: "Essay"
hook: |
  An AI agent ran an evaluation overnight. A second agent checked the numbers from the raw outputs, and they matched.

  The model behind those numbers had finished only half of its training.
thumb_text: "Three roles, then none, then gates"
reading_time: 11
---

The bug was one line of shell. The eval script found the last checkpoint with `sort -t- -k2 -n`, which splits a path on hyphens. The project lives in a folder called `safety-decay`, so the sort keyed on a field that never changed. It fell back to alphabetical order, where `checkpoint-9372` comes after `checkpoint-16875`. The agent evaluated a checkpoint that was 55% of the way through training.

My verification step did not catch it. A fresh subagent recomputed every headline number from the per-item output files and read raw responses. Everything agreed, because the files were internally consistent. They just came from the wrong model. The agent found the bug four days later. It retracted the result in the journal and re-ran the eval.

That was August 26. The rule it produced now sits in every research repo I start. Trace each number back to a finished run, using the checkpoint's own metadata instead of its path. This post is about how I got to rules like that one. It is also about why most of them now block a commit instead of sitting in a file.

My friend Sam George wrote [a post about his own path](https://secondhalfsoftware.com/blog/2026-10-09) with Claude on a mobile app. He ended up with a team of fourteen agent roles. I went the other way. I started with three roles and ended with none, plus a set of gates. Both of us are describing one person's setup, with nothing measured.

## How did I start?

In October 2025, Denis Paperno and I were studying latent chain-of-thought in [CODI](https://arxiv.org/abs/2502.21074). The repo was `CoT_Exploration`, and its `CLAUDE.md` began with a stop sign. Before any task, Claude had to ask which role to play: Product Manager, Architect or Developer. It had to ask permission before writing code or touching documentation.

Each role had a process. The Product Manager gathered requirements, wrote user stories and estimated their cost. The Developer reported progress as stories done out of stories planned. The Architect checked the data: is there enough, are there duplicates, are the labels right, is there a held-out test split?

This was software process applied to research, and much of it did not fit. Experiments are not features. A user story for "find out whether the latent tokens encode intermediate results" has no meaningful cost estimate. And because every change waited on my permission, I was the bottleneck. Nothing ran while I slept.

Some of it survived. The experiment write-ups used a fixed name, `MM-DD_<model>_<dataset>_<experiment>.md`, and I still use it. The data inventory survived. The Architect's four data questions survived word for word. They are the "standing data gates" in my current workflow, a year later.

One rule failed in a way I only understood later. `CLAUDE.md` required a saved summary of every conversation, in a fixed format. Over 217 commits, Claude saved 3. Over the same commits it wrote 97 experiment files. The rule was clear and sat in the file every session read. It still did not happen.

## What changed when the agent ran overnight?

In April 2026, Dhruv Patil, a grad student, set up a research project manager for our unlearning paper, [Suppression is not Deletion](https://openreview.net/forum?id=6WYjBeIioq). Claude held the plan, the backlog, the experiment log, the decision records and the draft, all cross-referenced by stable IDs. It followed seven rules. Two of them I still like: "No experiment without a hypothesis" and "Claims before prose." The setup also gave blocked work to the human through an inbox file.

That inbox idea became the core of my next setup. In July 2026 I started `marin_red_teaming`, a red-team study of Marin 8B and OLMo 3. Its first commit had the autonomy model I still use. Claude works freely on anything unblocked: code, configs, jobs, analysis, commits. Anything it cannot or should not do goes in `INBOX.md` as one line, and it moves to the next task. It never waits on me.

Now the agent ran overnight on an NYU cluster, and the failures changed. They were no longer misunderstandings about roles. They were things that broke at 3 a.m. Each one became a dated section in `CLAUDE.md`, which was revised 14 times in six weeks.

A determinism check "failed" because it ran as a Slurm array across three different GPUs. The rule now says any comparison between runs pins the hardware, and provenance records the GPU it ran on. Another night, an `rsync --delete` to the cluster wiped every directory the repo did not track. That included about 100 GB of model weights and a gated judge model that only a human can re-download. `--delete` is now on the list of things never to do on the cluster.

The ceremony also came back. By the end of August the repo had a `STATUS.md`, stable task IDs and a limit of one task in progress. A script checked the project state before any job. These helped a long study stay on track. They also made a 270-line `CLAUDE.md` that every session had to read.

## Who checks the agent's work?

The rule that mattered most was the shortest: the doer never signs off on its own work. Before a result goes in the journal as a finding, a fresh subagent gets only the raw data and the pre-registered success criteria. It does not get my reasoning or the agent's scripts. It recomputes the metric on its own path and compares.

Design review came from a near miss. On August 13, a reviewing agent read an experiment design for my safety-decay paper and found the training cost understated by a factor of 4.5. The number had been carried over from context without a check. Now any design that needs more than about 20 GPU-hours gets an adversarial review before it runs. The reviewer has a short checklist: fact-check every number, redo the arithmetic, and check that words like "matched" have an operational definition.

The half-trained checkpoint showed where this kind of review stops. Recomputing from item files and reading raw outputs both passed, because both read the wrong model's outputs. A checker that only checks consistency will agree with a consistent mistake. So the provenance rule asks a different question: which run produced this number, and did that run finish?

## Why did the ceremony go away?

In September I asked whether my rules were any good. I compared them against the 2026 papers on research-agent harnesses. The answer was mostly reassuring. Three systems, SIBYL, Xcientist and File-as-Bus, had converged on the same design: state kept in files, append-only evidence, and gates between stages. The gaps were in enforcement. My "never bypass the pre-commit hook" rule was a sentence, and only goodwill kept the agent from passing `--no-verify`.

The audit's advice was one line I took seriously: do not keep evolving rule prose, evolve the checks. That matches the three saved conversation logs. A rule in `CLAUDE.md` is a request. A check that fails a commit is a fact.

So when I made a template on October 16, `research_template`, I cut. No roles, no ID scheme. The backlog is a checklist, top item next. The inbox is one line per decision I need to make. A shared methodology file, symlinked into every project, holds the autonomy model, the integrity rules, verification and design review. Each project's `CLAUDE.md` holds only that project's compute setup and lessons.

This week the safety-decay journal fell a day behind its experiment files. The fix was not another sentence. A pre-commit hook now blocks any commit where an experiment file names a job that the journal does not. Its first run flagged 43 older entries, which went on an allowlist, each with a reason.

## What did I take from Sam?

Sam's post has a sign-in bug that no test caught. One agent diagnosed it, another wrote the fix, and others reviewed it over four rounds. One review found that the fix caused a loop of requests. Another found that it reopened a path he had rejected that morning.

My design review only ran on big experiments. Small runs went straight to the cluster. Reading Sam's post, I could not defend that line. A wrong number in a small run is still a wrong number, and small runs feed the big ones.

So, as of today, every experiment gets a design review by a fresh subagent before it runs. In the template, small runs will get a short checklist: the numbers, the controls and the decision rule. Runs over 20 GPU-hours keep the full one. And the review is a gate, in the same hook as the journal:

- An experiment file cannot get a job ID until it has a design-review line, with reviewer, date and verdict, and the reviewer's report is saved in `docs/reviews/`.
- A result cannot be marked VERIFIED without a verification line that points to the verifier's saved report.

It landed in safety-decay and in the template this morning. Its first run put 114 older jobs and 36 experiment files on the allowlist. None of them had a review on file.

The cost is about one extra subagent call per small experiment, a few minutes.

The first version had a hole. The hook could check that a review line and a report existed. It could not check that a separate agent wrote them. Nine minutes later, the hook started checking who wrote them.

Each report now names the reviewing subagent's ID, and nobody types it by hand. A script copies the brief and the report straight from that subagent's Claude Code transcript. The hook reads the transcript and fails the commit in four cases:

- The saved brief or report differs from the transcript, even by one number.
- The verdict in the header is not the reviewer's own word. The doer cannot upgrade "VERIFIED-WITH-FLAGS" to "VERIFIED".
- The reviewer edited the work it reviewed, or committed anything. An agent that did the work cannot sign it off.
- The transcript's hash does not match the copy saved when the report was written.

I tested it on real transcripts. A real verifier's report from that morning passed. An edited number, an upgraded verdict, an unknown agent ID and a wrong hash were each blocked. So was a subagent that had prepared an experiment and then was offered as its reviewer. It had edited seven of the files it was meant to review.

Some limits remain. The transcripts live on my laptop, outside git, and on a machine without them the hook skips these checks with a warning. An agent with shell access could, in principle, edit both the transcript and the saved copy. The checks make faking harder and visible, and I am still the final check.

## Does any of this work?

I do not know, in the sense that a reviewer would accept. I have no counterfactual: no copy of a project run without the gates. The September audit named this as the missing piece. What I have is a list of failures, each caught once and then turned into a rule or a check. I have not counted whether any of them came back.

What I would tell another researcher:

- Start with autonomy and an inbox, not with roles. The agent should never wait on you, and you should never have to read its execution log.
- Keep the old checklists that worked. My data gates are a year-old Architect role with the role removed.
- When a rule fails, turn it into a check. Rules the agent reads are the ones that get skipped.
- Verify the artifact, not only the arithmetic. Consistent numbers from the wrong checkpoint pass every consistency check.

Sam closes by saying he does not know yet whether his team beats a looser setup. I don't know whether my gates beat his team. It would be a good experiment.

## Timeline

| Date | Repo | Change | What prompted it |
|---|---|---|---|
| Oct 2025 | `CoT_Exploration` | Three roles (PM, Architect, Developer); ask permission for every change; save every conversation | Software process carried over to research |
| Oct 2025 | `CoT_Exploration` | Experiment file naming, data inventory, Architect's data checks | Still in use |
| Oct–Nov 2025 | `CoT_Exploration` | 3 conversation logs saved, 97 experiment files written, over 217 commits | The prose-only rule was not followed |
| Apr 2026 | `Deep_learning_final_project` (Dhruv Patil) | Research PM: charter, stable IDs, inbox for the human, seven rules | A paper with a deadline |
| Jul 27, 2026 | `marin_red_teaming` | Autonomy model: work on anything unblocked, queue the rest in INBOX, never wait | Overnight runs on the cluster |
| Aug 13, 2026 | safety-decay | Design review before compute | A reviewing agent found a training cost understated 4.5 times |
| Aug 26, 2026 | safety-decay | Artifact provenance gate | An eval scored a half-trained checkpoint and passed verification |
| Aug 27, 2026 | `marin_red_teaming` | Pin the hardware for any run comparison | A determinism check "failed" across three GPUs |
| Aug 31, 2026 | `marin_red_teaming` | `STATUS.md`, stable task IDs, one task in progress, state checker | Keep a long study on one task at a time |
| Sep 8, 2026 | `marin_red_teaming` | No `rsync --delete` to the cluster | About 100 GB of weights deleted, including a gated judge |
| Sep 9, 2026 | Audit | "Evolve checks, not rule prose" | Comparison with 2026 harness papers |
| Oct 16, 2026 | `research_template` | Shared methodology plus per-project contract; no roles, no IDs | Starting new projects the same way |
| Oct 31, 2026 | `research_template`, safety-decay | Journal gate in the pre-commit hook | Journal fell a day behind; 43 entries grandfathered |
| Oct 31, 2026 | `research_template` | Inbox rewritten for the researcher: decisions only, answered items archived | Inbox had become an execution log |
| Oct 31, 2026 | safety-decay, `research_template` | Design review for every experiment; saved verifier report before VERIFIED | Sam's post; 114 jobs and 36 files grandfathered |
| Oct 31, 2026 | safety-decay, `research_template` | Hook checks each report against the reviewer's transcript: verbatim text, own verdict, no edits by the reviewer, matching hash | The first gate could not tell who wrote a report |
