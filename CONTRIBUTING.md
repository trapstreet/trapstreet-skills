# Contributing

## First — you probably don't need a PR here

**Publishing a task?** Don't add it to this repo, or to
[`trapstreet-tasks`](https://github.com/trapstreet/trapstreet-tasks). Tasks live in **your own
public repository**; you register them at [trapstreet.run](https://trapstreet.run) → **+ New
Task**, and the platform pins them to your `repo@commit`. Say *"make a task that evaluates
&lt;X&gt;"* to your agent and `trapstreet-task-scaffold` writes it.

**Publishing a solution?** Same — your repo, your account. `tp submit` links the board row back
to it.

That's the whole design: nothing you build has to go through us.

## What is welcome here

These three skills are instructions handed to a coding agent, so the bugs are things like a
flag that changed, a command that no longer exists, or a step that fails on Windows.

- **Fixes** — a wrong or stale command, a broken `references/` path, a step that doesn't work
  on your OS or shell.
- **Trigger problems** — the skill didn't activate when it should have, or activated when it
  shouldn't. Say what you typed and which skill you expected; the fix is usually a `description`
  keyword.
- **Platform coverage** — install notes for an agent not covered in the README.
- **A fourth skill** — only for a trapstreet workflow that the existing three don't cover.
  Open an issue first so we can agree it belongs here rather than in your own skills repo.

## Before you open a PR

`main` is protected: push a branch and open a PR, and both checks must pass.

```bash
# 1. spec compliance — the official Agent Skills validator
uvx --from "git+https://github.com/agentskills/agentskills#subdirectory=skills-ref" \
  skills-ref validate ./trapstreet-setup

# 2. installable — install your checkout for real, confirm all three arrive
npx -y skills add . --global --yes
npx -y skills list --global
```

The second check exists because the first is not enough. A malformed `SKILL.md` is **skipped
silently** by the installer rather than failing it, so a skill can pass validation and still
never reach anyone. That is not hypothetical — it is how `trapstreet-solution-scaffold` was
missing from every agent except Claude Code until [#3427158](
https://github.com/trapstreet/trapstreet-skills/commit/3427158).

### Two frontmatter traps

Both cost us a release. Both are invisible in Claude Code and fatal everywhere else.

- **A colon-space in an unquoted value breaks YAML.** `description: Covers three points: like
  this` will not parse. Use a folded block scalar:

  ```yaml
  description: >-
    Text with: colons, "quotes" and anything else, wrapped across
    as many lines as you like.
  ```

- **`description` has a 1024-character limit**, `name` has 64, and `name` must match the
  directory. The validator above enforces all three.

## Style

Skills are read by agents, not people. Prefer exact commands over prose, say what to verify
after each step, and state what to do when a step fails. Keep `SKILL.md` under ~500 lines and
move detail into `references/`, which agents load only when needed.

## Reporting something without fixing it

An issue is fine. For a skill that misbehaved, the useful details are: which agent, what you
typed, what the skill did, and what you expected.
