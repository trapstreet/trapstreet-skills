# trapstreet-solution-scaffold

A Claude Code skill that scaffolds a submission-ready [`trap-cli`](https://github.com/trapstreet/trap)
solution for a task on [trapstreet.run](https://trapstreet.run).

It handles the parts of building a trap-cli solution that are repetitive and
easy to get subtly wrong -- the current `trap.yaml` schema, credential setup
via direnv, avoiding a real class of bug where the reported model drifts
from the model actually run, and the leaderboard-provenance requirements
that determine whether a submission actually shows up as ranked -- while
leaving the part that has to be bespoke (a solution's actual logic) to you.

See [`SKILL.md`](./SKILL.md) for the full skill content: the three starting
points it supports (from scratch, wrapping an existing `solution.py`, or
adapting an existing external project into a trapstreet-testable solution),
the layout decisions it makes, and the provenance/submission gotchas it
guards against.

## Installing

Copy (or symlink) this directory into your Claude Code skills folder:

```bash
git clone https://github.com/trapstreet/trapstreet-solution-scaffold.git \
  ~/.claude/skills/trapstreet-solution-scaffold
```

## Contents

```
SKILL.md                          # the skill itself
references/trap-yaml-schema.md    # authoritative trap.yaml schema + full gotcha writeups
scripts/scaffold_solution.py      # generates solution.py (optional) + trap.yaml + credentials scaffolding
scripts/check_provenance.py       # verifies a task's local git HEAD matches what's published before you spend an API call on it
```

## License

MIT -- see [../LICENSE](../LICENSE)
