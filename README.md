# trapstreet-skills

Claude Code skills for building on [trapstreet.run](https://trapstreet.run).
Each subdirectory is a self-contained, independently installable skill.

| Skill | Use it to |
|---|---|
| [`trapstreet-setup`](./trapstreet-setup) | Install and authorize the `tp` CLI -- the one-time step before either skill below can run anything. |
| [`trapstreet-solution-scaffold`](./trapstreet-solution-scaffold) | Scaffold a submission-ready solution against an *existing* trapstreet.run task -- from scratch, wrapping existing code, or adapting an external project. |
| [`trapstreet-task-scaffold`](./trapstreet-task-scaffold) | Design and scaffold a *new* trapstreet.run task to evaluate a given agent/skill/tool. |

The two scaffold skills are complementary and cover opposite directions: one takes a task and
builds a solution against it, the other takes an agent/skill and builds a task to evaluate it.
`trapstreet-setup` is a prerequisite for `trapstreet-solution-scaffold` (which needs `tp` to run
and submit) -- install it alongside that one. `trapstreet-task-scaffold` doesn't invoke `tp` at
all, so it has no dependency on `trapstreet-setup`.

## Installing a skill

Each skill is one `SKILL.md` (Claude Code Skill format -- YAML frontmatter with `name`/
`description`, then the skill body) plus supporting `references/`/`scripts/`. The content itself
has no Claude Code-specific dependencies -- it's plain markdown and shell commands, portable by
default. How you install it depends on what you're using:

**Claude Code** -- skills are discovered from `~/.claude/skills/<name>/`. Clone this repo once,
then copy (or symlink) whichever skill(s) you want:

```bash
git clone https://github.com/trapstreet/trapstreet-skills.git
cp -r trapstreet-skills/trapstreet-setup ~/.claude/skills/trapstreet-setup
cp -r trapstreet-skills/trapstreet-solution-scaffold ~/.claude/skills/trapstreet-solution-scaffold
cp -r trapstreet-skills/trapstreet-task-scaffold ~/.claude/skills/trapstreet-task-scaffold
```

Open a new session afterward -- skills load at session start.

**Cursor** -- Cursor Rules use a similar shape (a description-triggered rule the agent pulls in
when relevant) but different frontmatter. Copy the skill's `SKILL.md` body into
`.cursor/rules/<name>.mdc` in your project, and translate the frontmatter:

```yaml
---
description: <the SKILL.md description, verbatim>
alwaysApply: false
---
```

(`alwaysApply: false` plus a description is what makes Cursor request the rule contextually --
the closest match to how Claude Code triggers a skill.) Copy any `references/` files it points to
alongside it and update the relative paths.

**Codex, or any `AGENTS.md`-based tool** -- these don't have a multi-file, auto-triggered skill
system. The practical route is folding the content into your project's `AGENTS.md` (or equivalent
single instructions file) -- either the whole `SKILL.md` body or just the sections relevant to
what you're doing. If your tool supports per-session file references instead, telling it to read
the `SKILL.md` path at the start of a session works too.

**Anything else** -- no skill/rule system at all: paste the `SKILL.md` body into your tool's
system prompt or custom-instructions field, or tell the agent to read the file before starting.

Each skill's own README has more detail on what it does and how it's
structured.

## License

MIT -- see [LICENSE](./LICENSE)
