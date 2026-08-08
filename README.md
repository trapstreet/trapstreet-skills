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
[trapstreet.run](https://trapstreet.run) answers that with numbers: every candidate runs
against the same cases, scored by the same judge, on a public board anyone can reproduce.

<p align="center">
  <img src="https://raw.githubusercontent.com/trapstreet/trapstreet-skills/main/docs/leaderboard.png" alt="A trapstreet.run leaderboard comparing four PDF parsers on the same document and model, with score, latency and cost for each run" width="900">
</p>
<p align="center">
  <em>Four parsers, same PDF, same model. The pick is row 3 — 0.05 behind, 29× cheaper.</em>
</p>

**This repo holds three skills that do it for you.** Install them and your coding assistant
sets up the CLI, builds solutions, and authors tasks — from plain language.

---

## Install

```bash
npx skills add trapstreet/trapstreet-skills
```

Installs into every coding agent it detects — Claude Code, Cursor, Codex, Cline, Amp,
Antigravity and 70+ more. Start a new session afterwards; skills load at session start.

Or paste this to your agent and it does everything:

```
Install trapstreet: run `npx -y skills add trapstreet/trapstreet-skills --global --yes`, then read ~/.agents/skills/trapstreet-setup/SKILL.md and follow it.
```

<details>
<summary><b>No Node?</b> Install with curl</summary>

```bash
D=~/.claude/skills; T=$(mktemp -d); mkdir -p "$D" \
  && curl -fsSL https://github.com/trapstreet/trapstreet-skills/archive/refs/heads/main.tar.gz \
   | tar -xz -C "$T" --strip-components=1 \
  && cp -R "$T"/trapstreet-* "$D"/ && rm -rf "$T"
```

Writes to Claude Code's directory only — change `D` for another agent — and skills installed
this way don't participate in `npx skills update`.

</details>

## Then say

| Say this | Skill | What it does |
|---|---|---|
| *"set up trapstreet"* | [`trapstreet-setup`](./trapstreet-setup) | Installs and authorizes the `tp` CLI. One time — local scoring needs no account. |
| *"build a solution for &lt;task&gt;"* | [`trapstreet-solution-scaffold`](./trapstreet-solution-scaffold) | Writes `trap.yaml` and the solver, runs it locally, submits when you're happy. From scratch, around code you have, or by adapting someone else's repo. |
| *"make a task that evaluates &lt;X&gt;"* | [`trapstreet-task-scaffold`](./trapstreet-task-scaffold) | Interviews you on what counts as correct and where ground truth comes from, then writes `traptask.yaml`, `judge.py` and `grader.py`. |

Tasks live in their author's own repository, not ours — publish from anywhere public and
register it on the site.

<details>
<summary><b>Prefer the CLI directly?</b></summary>

```bash
uv tool install trap-cli   # install
tp auth login              # authorize this machine, once
tp run && tp submit        # from any directory with a trap.yaml
```

</details>

## Links

| | |
|---|---|
| [**trapstreet.run**](https://trapstreet.run) | The boards. Browse tasks, read results, register your own. |
| [**Docs**](https://trapstreet.run/docs/quick-start) | [Quick start](https://trapstreet.run/docs/quick-start) · [Build a solution](https://trapstreet.run/docs/build-a-solution) · [Build a task](https://trapstreet.run/docs/build-a-task) · [Reference](https://trapstreet.run/docs/reference) |
| [**trapstreet/trap**](https://github.com/trapstreet/trap) | The `tp` CLI. MIT. |
| [**trapstreet/trapstreet-tasks**](https://github.com/trapstreet/trapstreet-tasks) | 36 reference tasks with judges and gold cases. MIT. |

## Other platforms

`npx skills add` writes one copy to `~/.agents/skills/`, which Codex, Cursor, Cline, Amp,
Antigravity and a dozen more read directly, and symlinks it into Claude Code. Nothing to
translate.

For anything that reads neither: each skill is one `SKILL.md` (YAML frontmatter with `name`
and `description`, then the body) plus optional `references/` and `scripts/` — plain markdown
and shell commands. Paste the body into your tool's custom-instructions field, or point it at
the file at session start.

## License

MIT — see [LICENSE](./LICENSE).
