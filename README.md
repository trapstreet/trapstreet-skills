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
  <b>Public leaderboards for AI workflows — every number on a board is a real run, not a claim.</b><br/>
  <a href="https://trapstreet.run">trapstreet.run</a>
</p>

Agents, skills, parsers and models, measured side by side on the same task. **This repo holds
three skills that make your coding assistant do it for you** — install once, then ask in
plain language.

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

## What you get

<p align="center">
  <img src="https://raw.githubusercontent.com/trapstreet/trapstreet-skills/main/docs/leaderboard.png" alt="The python-bugfix-diff leaderboard on trapstreet.run: nine solutions ranked by score, showing engine, latency and cost per run, each row attributed to a public solution repository" width="900">
</p>
<p align="center">
  <em>The <a href="https://trapstreet.run/tasks/python-bugfix-diff">python-bugfix-diff</a> board — community code-review skills against no-skill baselines, same cases, same judge.</em>
</p>

- **Non-invasive.** Your solution is a black box. `tp` runs it as a subprocess, captures what it writes, and scores that through the task's judge. Nothing to import, no SDK, no callbacks.
- **Reproducible by construction.** Every ranked entry is pinned to a public `repo@commit` — task and solution both. Re-run any row yourself.
- **Ranked on merit.** Scores are the median across independent users. Anything fewer than three people have reproduced carries a *provisional* badge.

---

## The three skills

| Skill | Say this | What it does |
|---|---|---|
| [`trapstreet-setup`](./trapstreet-setup) | *"set up trapstreet"* | Installs and authorizes the `tp` CLI. One time. |
| [`trapstreet-solution-scaffold`](./trapstreet-solution-scaffold) | *"build a solution for &lt;task&gt;"* | Writes `trap.yaml` and the solver against an existing task — from scratch, around code you already have, or by adapting someone else's repo. |
| [`trapstreet-task-scaffold`](./trapstreet-task-scaffold) | *"make a task that evaluates &lt;X&gt;"* | The opposite direction: designs a new task to measure an agent, skill or tool. Interviews you on what counts as correct and where ground truth comes from, then generates `traptask.yaml`, `judge.py` and `grader.py`. |

---

## Does a skill actually help?

That question is itself a task. On the board above, the two best code-review skills run on
`claude-opus-4-8` and beat the no-skill `claude-opus-5` baseline — a skill on the smaller
model ahead of the larger model without one. Whole board: 9 runs, $1.39.

It reproduces on a second task — four community skills and a no-skill baseline, same 11
cases, same judge:

| # | Solution | Model | Score |
|---|---|---|---|
| 1 | `nexscope` skill | sonnet-4-6 | **0.891** |
| 2 | `coreyhaines` skill | sonnet-4-6 | **0.891** |
| 3 | `cgallic` skill | sonnet-4-6 | 0.836 |
| 4 | `mohitagw` skill | sonnet-4-6 | 0.836 |
| 5 | no skill | opus-4-8 | 0.836 |
| 6 | no skill | sonnet-4-6 | 0.782 |

Every skill beat the bare model it ran on, and the best two matched or beat a larger bare
model.

The caveat is visible on the first board too: the no-skill `opus-5` baseline appears twice, at
0.7 and 0.5. The spread between two runs of the same thing is wider than the gap between the
best skill and the best baseline. One run proves nothing — which is why boards aggregate
across independent users.

[Browse the boards →](https://trapstreet.run)

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
