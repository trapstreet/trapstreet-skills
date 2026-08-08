<p align="center">
  <a href="https://trapstreet.run"><img src="https://raw.githubusercontent.com/trapstreet/trapstreet-skills/main/docs/logo.png" width="92" alt="Trapstreet"/></a>
</p>

<h1 align="center">Trapstreet</h1>

<p align="center">
  <a href="https://pypi.org/project/trap-cli/"><img src="https://img.shields.io/pypi/v/trap-cli?label=trap-cli" alt="PyPI"/></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"/></a>
  <a href="https://discord.gg/Ymm57FzYmF"><img src="https://img.shields.io/badge/Discord-Join-5865F2?style=flat&logo=discord&logoColor=white" alt="Discord"/></a>
  <a href="https://trapstreet.run"><img src="https://img.shields.io/badge/trapstreet.run-live-60a5fa" alt="trapstreet.run"/></a>
</p>

<p align="center">
  <b>Find the best AI solution for your task.</b><br/>
  <a href="https://trapstreet.run">trapstreet.run</a>
</p>

There are four ways to parse that PDF, five models that might handle it, and a skill someone
swears by. Which one actually works on *your* documents — and what does each run cost?

Trapstreet answers that with numbers instead of opinions. Every candidate runs against the
same cases, is scored by the same judge, and lands on a public board that anyone can
reproduce.

---

<p align="center">
  <img src="https://raw.githubusercontent.com/trapstreet/trapstreet-skills/main/docs/leaderboard.png" alt="A trapstreet.run leaderboard comparing four PDF parsing solutions on the same document, showing score, latency and cost per run for each" width="900">
</p>
<p align="center">
  <em>Four ways to read the same half-scanned PDF, all on <code>claude-sonnet-5</code>. The top
  score costs <b>$0.76</b> a run; the one 0.05 behind costs <b>$0.026</b> — 29× less, and
  5× faster than the winner. The row you want is rarely row 1.</em>
</p>

- **Non-invasive.** Your solution is a black box. `tp` runs it as a subprocess, captures what it writes, and scores that through the task's judge. Nothing to import, no SDK, no callbacks — so a skill, a Python pipeline and a Rust binary compete on one board.
- **Reproducible by construction.** Every ranked entry is pinned to a public `repo@commit`, task and solution both. Re-run any row yourself.
- **Ranked on merit.** Scores are the median across independent users. Anything fewer than three people have reproduced carries a *provisional* badge.

This repo holds three skills that let your coding assistant do all of it — pick a task, build
a solution, submit the run — from plain language.

---

## Quick start

### 1. Install the skills

```bash
npx skills add trapstreet/trapstreet-skills
```

Installs into every coding agent it detects — Claude Code, Cursor, Codex, Cline, Amp,
Antigravity and 70+ more — and keeps them updatable with `npx skills update`. Start a new
session afterwards; skills load at session start.

Or paste this to your coding agent and it does the whole thing:

```
Install trapstreet: run `npx -y skills add trapstreet/trapstreet-skills --global --yes`, then read ~/.agents/skills/trapstreet-setup/SKILL.md and follow it.
```

<details>
<summary><b>No Node?</b> Install with curl instead</summary>

```bash
D=~/.claude/skills; T=$(mktemp -d); mkdir -p "$D" \
  && curl -fsSL https://github.com/trapstreet/trapstreet-skills/archive/refs/heads/main.tar.gz \
   | tar -xz -C "$T" --strip-components=1 \
  && cp -R "$T"/trapstreet-* "$D"/ && rm -rf "$T"
```

This writes to Claude Code's directory only — change `D` for another agent — and skills
installed this way don't participate in `npx skills update`. Prefer the npx route when you
have it. Not on Claude Code at all? [Other platforms](#other-platforms).

</details>

### 2. Set up the CLI — say this

```
set up trapstreet
```

`trapstreet-setup` installs `uv` and the `tp` CLI, runs `tp auth login`, and verifies the
pairing. You don't type a command. (Authorization is only needed to *submit* — scoring
locally needs no account.)

### 3. Build a solution — say this

```
build a solution for pdf-mixed-scan using claude-sonnet-5
```

Pick any task from [the boards](https://trapstreet.run). `trapstreet-solution-scaffold`
writes `trap.yaml` and the solver, then runs it locally and prints the score per case:

```
╭────────────────── Summary ───────────────────╮
│  cases  2 cases                              │
│ grader  {"score": 1.0, "n_passed": 2, "n": 2}│
╰──────────────────────────────────────────────╯
╭─────────┬──────┬────────┬─────────┬──────┬──────────╮
│ case    │ exit │   time │ # score │ #got │#expected │
├─────────┼──────┼────────┼─────────┼──────┼──────────┤
│ case_01 │    0 │ 0.056s │    100% │    5 │        5 │
│ case_02 │    0 │ 0.029s │    100% │   42 │       42 │
╰─────────┴──────┴────────┴─────────┴──────┴──────────╯
run 2026-08-08T21:33:41 → .trap/runs/…/report.json
```

Nothing has been published yet. Iterate until the score looks right.

### 4. Submit — say this

```
submit it
```

Your row appears on that task's board with everyone else's. The CLI prints a link to it.

> **Runs are always accepted; ranking has a bar.** A run with no public solution repo is
> stored and viewable but never ranked — boards only rank entries anyone can re-run.

<details>
<summary><b>Prefer to drive the CLI yourself?</b> Three commands, no skills needed.</summary>

```bash
uv tool install trap-cli   # 1. install
tp auth login              # 2. authorize this machine (once)
tp run && tp submit        # 3. from any directory with a trap.yaml
```

Full walkthrough: [Quick start](https://trapstreet.run/docs/quick-start) ·
[Build a solution](https://trapstreet.run/docs/build-a-solution) ·
[Build a task](https://trapstreet.run/docs/build-a-task)

</details>

---

## Measure your own thing

The board above is one we made. The interesting one is the one you haven't — you have a
skill, an agent, a parser or a prompt, and no evidence it beats the alternative.

A task is three things:

| | |
|---|---|
| `inputs/<case>/` | what the solution sees |
| `expected/<case>/` | the answer it never sees |
| `judge.py` | scores one against the other, returns `0.0`–`1.0` |

That is the whole contract. Your solution runs as a subprocess, so anything that reads files
and writes an answer can be measured — a Claude Code skill, a Python pipeline, a shell script,
a Rust binary. No SDK, no instrumentation.

Say this:

```
make a task that evaluates <the thing you want measured>
```

`trapstreet-task-scaffold` interviews you on what counts as correct, where ground truth comes
from, and how to keep the scoring ungameable — then writes `traptask.yaml`, `judge.py` and
`grader.py`. Publish it from your own public repo and register it at
[trapstreet.run](https://trapstreet.run) → **+ New Task**. Tasks live in their author's
repository, not ours.

[`mineral-species-id`](https://trapstreet.run/tasks/mineral-species-id) and
[`karpathys-jagged-questions`](https://trapstreet.run/tasks/karpathys-jagged-questions) are
community tasks built exactly that way, by people who are not us.

Want to read finished ones first?
[**trapstreet-tasks**](https://github.com/trapstreet/trapstreet-tasks) has 36 worked examples
with judges and gold cases.

---

## Beyond the skills

| | |
|---|---|
| [**trapstreet.run**](https://trapstreet.run) | The boards. Browse tasks, read results, register your own task. |
| [**Documentation**](https://trapstreet.run/docs/quick-start) | [Quick start](https://trapstreet.run/docs/quick-start) · [Build a solution](https://trapstreet.run/docs/build-a-solution) · [Build a task](https://trapstreet.run/docs/build-a-task) · [Reference](https://trapstreet.run/docs/reference) |
| [**trapstreet/trap**](https://github.com/trapstreet/trap) | The `tp` CLI, for driving it directly instead of through an agent. MIT. |
| [**trapstreet/trapstreet-tasks**](https://github.com/trapstreet/trapstreet-tasks) | 36 reference tasks with judges and gold cases. MIT. |

---

## Other platforms

`npx skills add` writes one copy to `~/.agents/skills/`, which Codex, Cursor, Cline, Amp,
Antigravity and a dozen more read directly, and symlinks it into Claude Code. Nothing to
translate.

For a tool that reads neither — paste the `SKILL.md` body into its system prompt or
custom-instructions field, or point it at the file at session start. Each skill is one
`SKILL.md` (YAML frontmatter with `name` and `description`, then the body) plus optional
`references/` and `scripts/`; it is plain markdown and shell commands, with no Claude
Code-specific dependencies.

---

## License

MIT — see [LICENSE](./LICENSE).
