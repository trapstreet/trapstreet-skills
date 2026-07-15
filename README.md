# trapstreet-skills

Claude Code skills for building on [trapstreet.run](https://trapstreet.run).
Each subdirectory is a self-contained, independently installable skill.

| Skill | Use it to |
|---|---|
| [`trapstreet-solution-scaffold`](./trapstreet-solution-scaffold) | Scaffold a submission-ready solution against an *existing* trapstreet.run task -- from scratch, wrapping existing code, or adapting an external project. |
| [`trapstreet-task-scaffold`](./trapstreet-task-scaffold) | Design and scaffold a *new* trapstreet.run task to evaluate a given agent/skill/tool. |

They're complementary and cover opposite directions: one takes a task and
builds a solution against it, the other takes an agent/skill and builds a
task to evaluate it.

## Installing a skill

Skills are discovered by Claude Code from `~/.claude/skills/<name>/`. Clone
this repo once, then copy (or symlink) whichever skill(s) you want:

```bash
git clone https://github.com/trapstreet/trapstreet-skills.git
cp -r trapstreet-skills/trapstreet-solution-scaffold ~/.claude/skills/trapstreet-solution-scaffold
cp -r trapstreet-skills/trapstreet-task-scaffold ~/.claude/skills/trapstreet-task-scaffold
```

Each skill's own README has more detail on what it does and how it's
structured.

## License

MIT -- see [LICENSE](./LICENSE)
