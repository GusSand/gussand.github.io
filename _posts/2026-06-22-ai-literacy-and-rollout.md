---
title: 'AI Literacy Audit and Rollout Plan'
date: 2026-06-22
permalink: /posts/2026/06/ai-literacy-and-rollout/
tags:
  - Vibe Coding
  - Security
  - LLM
---

I have to confess something: I have been vibe coding and beyond for over a couple of years now. I started with CoPilot, for which I even created a plugin for a research paper (https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval), then moved on to Cursor and eventually landed in Claude Code. I have created my initial [Claude.md](https://gist.github.com/GusSand/549883ca0a1f326a31239cc3fcfa7f69) for research that has different personas, etc. However, given that I have spent the past (few) years in Academia, this has mainly been either a solo journey or with a few graduate students. 

Over the weekend, I read a nice post that Steve Yegge wrote up in [The Flat Curve Society](https://steve-yegge.medium.com/the-flat-curve-society-36c8b01eb33b) ([Yegge 2026](https://steve-yegge.medium.com/the-flat-curve-society-36c8b01eb33b)) that made me think back to my Engineering Management days. How would you introduce AI Engineering, as it wants to be called now, to a medium-size team?

Most organizations treat AI adoption as a tooling problem. Buy the licenses, turn on the agent, wait for productivity. Obviously, this doesn't work, and the reason is boring: agentic coding is a skill, today's models are hard to work with, and nobody is born knowing how to drive them. The good news is that the skill is cheap to teach and the gap is cheap to measure.

What follows is a practical plan lifted almost entirely from a Netflix training study that Ezra Savard ran from December 2025 through March 2026. Steve Yegge wrote this up in the article and I'm just adding a security reviewer's caveats, because the productivity story has a denominator problem you should not ignore.

**Table of Contents**

- [The Problem Is Anxiety, Not Tools](#the-problem-is-anxiety-not-tools)
- [Step 1: A Coarse Literacy Audit](#step-1-a-coarse-literacy-audit)
- [Step 2: The Training Recipe](#step-2-the-training-recipe)
- [Step 3: From Spending to Saving](#step-3-from-spending-to-saving)
- [Measure Outcomes, Not Output](#measure-outcomes-not-output)
- [The One-Page Version](#the-one-page-version)
- [Caveats](#caveats)
- [Citation](#citation)
- [References](#references)


# The Problem Is Anxiety, Not Tools

Two things are true at every company right now. The org has to pivot to AI, and the employees are anxious about AI. Those two facts feed each other, because the pivot changes everyone's job, and the change feeds the anxiety. If you push tooling into that loop without addressing literacy first, you get resistance, and the resistance is often passive, which makes it hard to see and harder to fix.

The claim worth internalizing is that the resistance is downstream of skill. People who cannot make an agent useful will not advocate for agents. Once someone crosses into actually getting value, they tend to start reshaping their own workflow without being told to. So the lever is literacy, and literacy turns out to be measurable and trainable.

# Step 1: A Coarse Literacy Audit

Before you train anyone, find out where you stand. The Netflix work gives a usable proxy: average token spend on a heavy-use day, counting only people who use the tools at least three days a week. That sorts people into three beginner cohorts.

The zero cohort is roughly zero tokens a day, people not using coding agents for real work. The single-agent cohort lands around four million tokens a day, one agent driven synchronously through the workday. The multi-agent cohort sits at twelve to fifteen million tokens a day, two to four agents running without constant supervision.

Use this for what it is, which is a thermometer, not a thesis. Token spend is an input metric, and it tells you nothing about whether the output was any good. It is the reading-literacy equivalent of counting pages turned. It works here only because below fifteen million a day, spend correlates with skill in a way that is cheap to read off existing telemetry. Above that line it stops meaning anything, since people get clever about inventing reasons to burn tokens. So audit at a coarse level, learn how much of your org is stuck at zero, and move on.

# Step 2: The Training Recipe

This is the part that earns the post. The Netflix team found that the curriculum barely matters, but the delivery format matters enormously, and the effect collapses if you cut corners. The format that stuck:

Five hours, one team at a time, five to ten people including their manager. The manager has to opt the team in, and it has to run during regular hours as blessed company time. Trainees bring their real work, not toy exercises, and the instructor helps them do that actual work with agents.

The reported result is that people jump a cohort in those five hours and stay there, with 96% of trainees still in the higher cohort six weeks later. When they tried to make it cheaper, with shorter sessions, larger audiences, or individual opt-in instead of whole teams, it did not stick.

None of those constraints are arbitrary, and they line up with what we already know about skill transfer in adults. Manager opt-in supplies sponsorship and air cover. Whole-team cohorts create peer norms instead of lonely early adopters. Real work during blessed hours removes the "I'll learn it later" escape hatch. The curriculum is interchangeable precisely because the social scaffolding is doing the work.

# Step 3: From Spending to Saving

Getting everyone to single-agent literacy solves the first culture problem, which is fear. It immediately creates the second one, which is waste. Beginners are token pigs, and that is fine, since you cannot learn to economize before you learn to spend. But once a team can spend, the skill flips, and the thing worth measuring becomes token waste rather than token spend.

The advanced curriculum is about hygiene and decomposition. The canonical beginner sin is being two hundred thousand tokens deep in a context and then asking the agent what time it is, or whether a file exists. The mature version of the skill is routing the easy thing to the cheap path, doing trivial work by hand, and structuring tasks so the model stays inside its competence. The bell-curve meme applies cleanly here, where the master and the novice do the same thing, which is keep spend low, for opposite reasons.

# Measure Outcomes, Not Output

Here is where I put my security hat on, because the productivity finding in the study deserves more scrutiny than it usually gets. The headline was a large jump in code produced by trained agentic coders. When they dug in, the entire difference was additional test code.

Read that twice before you celebrate it. More test code can mean better coverage, or it can mean lines-of-code inflation that looks like productivity because we are bad at measuring productivity. Lines of code is exactly the proxy that the DORA tradition has warned against for a decade, and "the agent wrote more code" is the single least trustworthy success signal in software. It also sits uncomfortably next to controlled studies, including [METR's 2025 work](https://metr.org), where experienced developers were measurably slower with AI assistance even while believing they were faster.

The reviewer's concern compounds this. Agents generate code faster than humans can review it, and AI-generated code shifts the bottleneck from authoring to verification. If your literacy program raises output volume without raising review capacity and provenance tracking, you have not made the org faster, you have moved the risk downstream to whoever owns security. So train for literacy, but gate the celebration on outcome metrics you actually trust: defect rates, review throughput, time to a working change, not raw volume.

There is a deeper version of this problem that I think about constantly in my own work. Past a certain capability level you cannot grade the answer at all, because checking it is beyond you. Yegge calls this the discernment horizon, and it is the same wall that scalable-oversight research keeps running into. An org's binding limit is eventually not how hard a problem it can pose to a model, but how hard an answer it can verify. Build your measurement around that fact early, because it does not get easier.

# The One-Page Version

Run a coarse audit from existing token telemetry, and find out what fraction of the org is at zero. Train everyone up to single-agent literacy first, five hours, whole teams, managers in the room, real work, blessed time. Let them practice and be wasteful for a few weeks. Then run the second five-hour course for multi-agent work, team by team, once a manager has a fully single-agent team. Add a third course on efficiency and token hygiene once spending is a solved problem. Give people token budgets, and make them earn increases with real outcomes rather than volume. Throughout, measure outcomes you trust and treat token spend only as an early thermometer that you discard the moment it stops meaning anything.

# Caveats

This is one study, with self-selected participants who opted into agentic training and brought their own work, which is not a random sample, and the people who say yes are exactly the people most likely to succeed. Yegge is candid that he skipped the rigor in the writeup, which is the part I would most want to see. Treat the five-hour figure and the 96% retention as encouraging and directionally plausible, not as established constants for your org. The recipe is cheap enough to pilot that you can generate your own numbers, and you should, because your numbers are the only ones that will survive contact with your codebase.

# Citation

Cited as:
> Sandoval, Gustavo. (Jun 2026). "AI Literacy Audit and Rollout Plan". https://gussand.github.io/posts/2026/06/ai-literacy-and-rollout/.

Or

```
@article{sandoval2026ailiteracy,
  title   = "AI Literacy Audit and Rollout Plan",
  author  = "Sandoval, Gustavo",
  journal = "gussand.github.io",
  year    = "2026",
  month   = "Jun",
  url     = "https://gussand.github.io/posts/2026/06/ai-literacy-and-rollout/"
}

```

# References

[1] Yegge, Steve. ["The Flat Curve Society"](https://steve-yegge.medium.com/the-flat-curve-society-36c8b01eb33b). Medium (2026).

[2] Kim, Gene and Yegge, Steve. *Vibe Coding: Building Production-Grade Software With GenAI, Chat, Agents, and Beyond*. IT Revolution (2025).

[3] METR. ["Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity"](https://metr.org). (2025).

---


© 2026 Gustavo Sandoval
