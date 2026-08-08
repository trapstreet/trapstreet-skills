# trapstreet-skills

### You installed a skill. Does it actually make your agent better?

Nobody knows, because nobody measures it. Skills, agents, parsers, models — the whole
ecosystem runs on screenshots and vibes.

[**trapstreet.run**](https://trapstreet.run) measures it. Pick a task, run any solution
against it locally, submit the score. Every entry on a board is a real run, pinned to a
public `repo@commit`, reproducible by anyone.

Here is a real board. Four community code-review skills and a no-skill baseline, same
11 cases, judged the same way:

| | Solution | Model | Score |
|---|---|---|---|
| 1 | `nexscope` skill | sonnet-4-6 | **0.891** |
| 2 | `coreyhaines` skill | sonnet-4-6 | **0.891** |
| 3 | `cgallic` skill | sonnet-4-6 | 0.836 |
| 4 | `mohitagw` skill | sonnet-4-6 | 0.836 |
| 5 | **no skill** | opus-4-8 | 0.836 |
| 6 | **no skill** | sonnet-4-6 | 0.782 |

Every skill beat the bare model it ran on, and the best two beat a *larger* bare model.
That's the case for skills — with a number attached.

The same experiment on a
[harder task](https://trapstreet.run/tasks/python-bugfix-diff) is less flattering: the
no-skill `opus-5` baseline scored **0.7** on one run and **0.5** on another. The spread
between two runs of the same thing was larger than the gap between the best skill and the
best baseline. Which is the point — one run proves nothing, and a leaderboard of other
people's runs is the only way to tell a real effect from noise.

[Browse the boards →](https://trapstreet.run)

---

## Install

Three skills. They teach your coding agent to set up trapstreet, build solutions, and
author tasks.

```bash
git clone --depth 1 -q https://github.com/trapstreet/trapstreet-skills.git /tmp/ts-skills \
  && mkdir -p ~/.claude/skills \
  && cp -r /tmp/ts-skills/trapstreet-* ~/.claude/skills/ \
  && rm -rf /tmp/ts-skills
```

Start a new session afterward — skills load at session start. Then just say:

```
set up trapstreet
```

`trapstreet-setup` takes it from there: installs `uv` and the `tp` CLI, runs `tp auth login`,
verifies the pairing. You don't have to touch a command.

> Not on Claude Code? These are plain markdown — see [other platforms](#other-platforms) for
> Cursor, Codex, and anything with a custom-instructions field.

## The three skills

| Skill | Say this | What it does |
|---|---|---|
| [`trapstreet-setup`](./trapstreet-setup) | *"set up trapstreet"* | Installs and authorizes the `tp` CLI. One time. Local scoring needs no account — authorization is only for submitting. |
| [`trapstreet-solution-scaffold`](./trapstreet-solution-scaffold) | *"build a solution for &lt;task&gt;"* | Writes `trap.yaml` (+ `solution.py`) against an existing task. Works from scratch, around code you already have, or by adapting someone else's repo. |
| [`trapstreet-task-scaffold`](./trapstreet-task-scaffold) | *"make a task that evaluates &lt;X&gt;"* | The other direction: designs a new task to evaluate an agent, skill, or tool. Interviews you on what counts as correct and where ground truth comes from, then generates `traptask.yaml`, `judge.py`, `grader.py`. |

The two scaffolds are opposites: one takes a task and builds a solution against it, the other
takes a thing you want measured and builds a task around it.

## Your first run

```
you  → set up trapstreet
you  → build a solution for pdf-mixed-scan using claude-sonnet-5
```

The scaffold skill writes the solution, runs it locally, and shows you the score per case.
Nothing has been published yet. When you like the result:

```
you  → submit it
```

It lands on [that task's board](https://trapstreet.run) next to everyone else's.

**Runs are always welcome; ranking has a bar.** A run with no public solution repo is stored
and viewable but never ranked — the leaderboard only ranks entries anyone can re-run.

## How the measurement works

A task declares only **inputs** and **expected outputs**. Your solution is a black box: `tp`
invokes it as a subprocess, captures what it writes, and scores that through the task's judge.

No hooks. No instrumentation. Nothing to import. Which is why the same task can compare a
Claude Code skill, a smolagents pipeline, a raw model call, and a Rust binary — they only
have to agree on files in and files out.

Trust comes from provenance, not from us re-running your code: ranked entries require a
public solution repo, scores are the median across independent users, and anything fewer
than three users have reproduced carries a *provisional* badge.

## Where to go next

| | |
|---|---|
| [**trapstreet.run**](https://trapstreet.run) | The boards. Browse tasks, read results, register your own task. |
| [**Docs**](https://trapstreet.run/docs/quick-start) | Quick start · [Build a solution](https://trapstreet.run/docs/build-a-solution) · [Build a task](https://trapstreet.run/docs/build-a-task) · [Reference](https://trapstreet.run/docs/reference) |
| [**trapstreet/trap**](https://github.com/trapstreet/trap) | The `tp` CLI itself — if you'd rather drive it directly than through an agent. MIT. |
| [**trapstreet/trapstreet-tasks**](https://github.com/trapstreet/trapstreet-tasks) | 36 reference tasks with judges and gold cases. Read one before writing your own. MIT. |

Tasks live in **their author's own repo**, not ours — you publish from anywhere public and
register it on the site. [`mineral-species-id`](https://trapstreet.run/tasks/mineral-species-id)
and [`karpathys-jagged-questions`](https://trapstreet.run/tasks/karpathys-jagged-questions) are
community tasks that work exactly that way.

## Other platforms

Each skill is one `SKILL.md` (YAML frontmatter with `name`/`description`, then the body) plus
supporting `references/` and `scripts/`. The content has no Claude Code-specific dependencies —
it's plain markdown and shell commands.

<details>
<summary><b>Cursor</b></summary>

Cursor Rules have a similar shape but different frontmatter. Copy the `SKILL.md` body into
`.cursor/rules/<name>.mdc` and translate the frontmatter:

```yaml
---
description: <the SKILL.md description, verbatim>
alwaysApply: false
---
```

`alwaysApply: false` plus a description is what makes Cursor pull the rule in contextually —
the closest match to how Claude Code triggers a skill. Copy any `references/` files it points
at alongside it and fix the relative paths.

</details>

<details>
<summary><b>Codex, or anything <code>AGENTS.md</code>-based</b></summary>

These have no multi-file auto-triggered skill system. Fold the content into your project's
`AGENTS.md` — the whole `SKILL.md` body, or just the sections relevant to what you're doing.
If your tool supports per-session file references instead, pointing it at the `SKILL.md` path
at session start works too.

</details>

<details>
<summary><b>Anything else</b></summary>

No skill or rule system at all: paste the `SKILL.md` body into your tool's system prompt or
custom-instructions field, or tell the agent to read the file before starting.

</details>

Each skill's own README has more on what it does and how it's put together.

## License

MIT — see [LICENSE](./LICENSE)
