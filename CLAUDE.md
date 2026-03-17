# CLAUDE.md — AI-Assisted Research Project

## Prerequisites

The following must be installed on the host system before using this project:

- **Python 3.12+** (`sudo apt-get install python3`)
- **uv** (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **pip** (`sudo apt-get install python3-pip`)
- **bubblewrap** (`sudo apt-get install bubblewrap`) — for sandbox mode
- **Git** (`sudo apt-get install git`)

Claude Code operates in a sandboxed environment that restricts Bash writes to the project folder. All Python packages should be installed into a local `.venv/` via `uv`.

---

## Purpose

This project produces **two deliverables**:

1. **A research paper** (topic TBD).
2. **A practical guide on AI-assisted research** (`process_log/guide.md`) — a standalone, tutorial-style document that teaches PhD students how to use AI to produce academic research, built from the real record of how *this* project was done.

Everything we log — discussions, decisions, prompting patterns, dead ends — is raw material for that guide. The guide is the primary pedagogical output; the raw logs in `process_log/` are the supporting evidence.

---

## Documentation Protocol

**Every interaction matters.** But documentation should not interrupt the research workflow. We use a **background scribe agent** to handle all logging.

### How it works

1. **We just work.** The main conversation focuses entirely on research — discussing ideas, writing code, making decisions. No pausing to write log entries.
2. **The scribe runs in the background.** A custom subagent defined in `.claude/agents/scribe.md` handles all documentation. Claude delegates to it at natural breakpoints. It reads the conversation, updates all log files and the narrative guide, and commits to git. Its commits are prefixed with `scribe:` so they're identifiable in `git log`.
3. **Trigger points:** Claude should invoke the scribe:
   - After a cluster of decisions or a major discussion
   - When switching topics or tasks
   - When the user asks to "log this" or "update the guide"
   - At the end of a session
   - Roughly every 15-20 minutes of active work, if nothing else triggers it

### What the scribe documents

| What | Where |
|------|-------|
| Conversations & decisions | `process_log/discussions/YYYY-MM-DD.md` |
| Prompting patterns | `process_log/patterns/YYYY-MM-DD.md` |
| Research decisions | `process_log/decisions/YYYY-MM-DD.md` |
| Session summaries | `process_log/sessions/YYYY-MM-DD.md` |
| Literature & references | `references/references.md` |
| General guide | `process_log/guide.md` |
| Project history | `process_log/history.md` |

### Scribe capabilities

The scribe has access to: file read/write, git, and the full conversation context. It runs lean — no web search, no code execution. Just reads context and writes documentation.

It also has **project-level persistent memory** (`.claude/agent-memory/scribe/`) so it remembers conventions and context across sessions.

### Code & Drafts

- All code goes in `code/`. Each script should have a clear header comment.
- Paper drafts go in `paper/`. The paper uses a master file (`paper/main.tex`) that `\input`s one file per section from `paper/sections/`. Never write the paper as one giant file. Version notes in `paper/revision_notes.md`.
- **No inline code in bash commands.** Always write Python/R code to a script file first, then run it. This keeps everything reproducible and version-controlled.
- **Exploratory scripts go in `code/tmp/`.** Use this for one-off checks, data inspection, etc. Promote to `code/` once the logic stabilizes. The `code/tmp/` directory is gitignored.
- **Never edit `paper/library.bib`** — it is managed externally by Zotero. If a citation is missing, tell the user to add it in Zotero. You may read the file to check for existing entries.

---

## Project Structure

```
project_name/
├── CLAUDE.md                 # This file — project instructions for Claude
├── .gitignore
├── .claude/agents/scribe.md  # Background scribe subagent definition
│
├── process_log/              # All documentation
│   ├── guide.md              # General AI-assisted research manual
│   ├── history.md            # This project's specific story
│   ├── discussions/          # What we discussed (YYYY-MM-DD.md per day)
│   ├── decisions/            # Research choices made (YYYY-MM-DD.md per day)
│   ├── patterns/             # Prompting techniques (YYYY-MM-DD.md per day)
│   └── sessions/             # Session summaries (YYYY-MM-DD.md per day)
│
├── references/
│   └── references.md         # Papers, data sources, links
├── code/                     # All analysis code
│   ├── download/             # Data download scripts (reproducible)
│   ├── analysis/             # Empirical analysis scripts
│   └── tmp/                  # Exploratory throwaway scripts (gitignored)
├── data/                     # Raw and processed data
├── paper/                    # Research paper drafts and notes
│   └── revision_notes.md     # Change log across drafts
└── output/                   # Figures, tables, results
```

---

## Workflow Rules

1. **Think out loud.** Claude should explain its reasoning before acting — not just produce output. PhD students need to see the thought process.
2. **Ask before assuming.** When a decision has multiple reasonable paths, present the options with trade-offs rather than silently picking one.
3. **Flag uncertainty.** If Claude is unsure about a fact, method, or claim, say so explicitly. Model good epistemic practice.
4. **Iterate in the open.** Show drafts, get feedback, revise. Don't aim for a perfect first pass — the iteration *is* the lesson.
5. **Cite sources.** Any empirical claim, stylized fact, or methodological choice should reference specific papers or data.
6. **No hallucinated references.** Never invent citations. If unsure of a reference, say so and offer to search.
7. **Keep it reproducible.** Code should be runnable. Data sources should be clearly identified. Steps should be repeatable.
8. **Never fabricate numbers or results.** If a number, statistic, or empirical result is not computed from actual data or derived from a verified source, mark it explicitly as `[CONJECTURED]` or `[TODO: compute]`. Start drafts with minimal claims and add results incrementally as they are produced. A placeholder is always better than a fabrication.
9. **Commit compulsively.** After every meaningful change — a new log entry, a code addition, a decision documented — commit to git immediately. Small, frequent commits with clear messages. The git history itself becomes part of the pedagogical record. Don't wait for "a good stopping point"; every atomic piece of progress gets its own commit.

---

## Communication Style

- Write clearly and directly — as you would in an academic setting.
- Use precise terminology but explain jargon when first introduced (PhD students at various stages will read this).
- When presenting research options, use structured comparisons (tables, pros/cons).
- Keep code comments informative but concise.

## Paper Writing Style Guide

These rules apply when writing paper drafts, not to logs or conversation.

- Active voice always. The real enemy is passive voice: not "it is assumed that," "data were constructed," "it can be seen." Search for "is" and "are" to root out passives.
- "I" is fine on a solo paper. But "I show that X" is just the "that" rule: strike "I show that" and say X. Same for "I derive," "I extend," "I find," "I confirm," "I illustrate." These announce the result instead of stating it. Keep "I" only for genuine real-world restrictions the reader might question: "I assume there are no demand shifts," "I require 120 months of data," "I recommend." Do not "assume" model structure — just state it: "Consumers have power utility," not "I assume consumers have power utility." Save "assume" for things that modify the real world, not for describing a model.
- When possible, make the object the subject: "Table 5 presents estimates" rather than "I present estimates in Table 5." This is preferred over "I" when natural.
- Never use the royal "we" (meaning the author alone). "We" is allowed only to mean "you the reader and I": "We can see the pattern in Table 5."
- Concrete, not abstract. Use normal sentence structure: subject, verb, object.
- Avoid bold and italics unless absolutely necessary.
- No bold paragraph starters (e.g., "First,", "Second,").
- Italics only for: variable names in prose, foreign phrases, or true emphasis.
- No em-dashes; use commas, colons, periods, or parentheses.
- Avoid filler adverbs: crucially, critically, importantly, essentially, notably, strikingly.
- Each sentence should mean what it says. Cut preambles before "that": "It should be noted that X" → "X". "It is easy to show that" → just show it. "Note that" is usually filler. If the point of the sentence is X, say X.
- Do not use adjectives to describe your own work. Not "striking results," not "very significant," not "very novel." If results merit adjectives, the reader will supply them. Never use double adjectives.
- Use simple short words. "Use" not "utilize." "Several" not "diverse."
- Clothe the naked "this." Never write "This shows..." — write "This regression shows..." or "This result shows..." The word "this" must always have a noun after it.
- Do not write "I leave X for future research." The reader cares about results, not plans.
- Let the content speak for itself.

---

## Referee Simulations

Use the **referee agent** (`.claude/agents/referee.md`) when the user asks for a referee report. It runs as an Opus agent with no prior knowledge, reads the paper fresh, and writes a top-3-finance / top-5-econ style R1 report. Reports are saved to `paper/referee_reports/YYYY-MM-DD_vN.md`.

**Before launching a referee agent, delete all previous reports in `paper/referee_reports/` and `paper/referee_report_simulated.md` (if it exists).** Each run should start clean. We focus on the latest report only, not on averages or repeated runs.

**Known issue:** The referee agent sometimes ignores save-path instructions from its definition file (see [#7515](https://github.com/anthropics/claude-code/issues/7515)). Always include the save path explicitly in the launch prompt, e.g.: `CRITICAL SAVE INSTRUCTION: Save the report to ONLY ONE file: paper/referee_reports/YYYY-MM-DD_v1.md`.

---

## How to Start a New Session

At the start of each working session, Claude should:
1. Read the latest file in `process_log/sessions/` to recall where we left off.
2. Briefly state what was last accomplished and propose next steps.
3. Confirm direction with the user before proceeding.

## Keeping This File Current

This CLAUDE.md starts as a generic template. As the project takes shape, Claude should update it to reflect the specifics — paper title, target journal, key references, section structure, etc. If the project has evolved enough that a section is still generic (e.g., "topic TBD"), propose an update. The goal is that this file always accurately describes the *current* project, not the template it started from.

Similarly, update the **referee agent** (`.claude/agents/referee.md`) to list the actual section files once the paper structure stabilizes. The referee agent should stay generic in tone and evaluation criteria, but its "How to read the paper" section should list the specific `paper/sections/*.tex` files so it reads them in the right order.

---

## Pedagogical Deliverables — Two Documents

### 1. The Guide (`process_log/guide.md`)

A **general, transferable manual** on how to do AI-assisted academic research. A PhD student working on *any* topic should be able to read this and apply the lessons. It covers principles, workflow design, prompting techniques, pitfalls, and best practices — drawn from our experience but not dependent on knowing our specific research topic.

- Written as a standalone document that could be shared independently.
- Structured by phase: setup, scoping, literature review, data, modelling, writing, revision.
- Each section distils general lessons and links to the history for concrete examples.
- Should be useful even to someone who never reads the history.

### 2. The Project History (`process_log/history.md`)

The **specific, detailed record** of how this project unfolded. This is the "DVD commentary" — what we actually discussed, decided, tried, failed at, and revised, in chronological order.

- Written as a narrative, not raw logs (the raw logs in `discussions/`, `decisions/`, etc. are supporting material).
- A student who wants to see how AI-assisted research *actually plays out* in practice reads this.
- References the actual prompts, AI responses, code files, and data.
- Highlights dead ends and course corrections — the messy, real story.

### How they relate

The **guide** says "here's what you should do." The **history** says "here's what we actually did." The guide references the history for worked examples; the history links back to the guide for the general principles behind each decision.
