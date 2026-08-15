# trapstreet-task-scaffold

A Claude Code skill that helps design and scaffold a **new** task for
[trapstreet.run](https://trapstreet.run) -- the reverse of
[`trapstreet-solution-scaffold`](../trapstreet-solution-scaffold), which
builds a solution against an *existing* task.

Task design isn't fully mechanizable the way solution scaffolding is: the
file layout and manifest contracts are the same every time (and this skill
generates them), but whether a task is actually *good* -- discriminating,
hard to game, legally sound -- depends on real judgment specific to the
agent/skill/domain being tested. This skill covers both halves: a
structured interview for the judgment-heavy decisions, and working
scaffolding scripts for the mechanical parts.

See [`SKILL.md`](./SKILL.md) for the full skill content: the interview
questions, the generated file layout, and pointers into the reference docs
covering real exploits and pitfalls already found the hard way (keyword-
matching false positives, anti-shotgun scoring, ground-truth leakage risk,
licensing, and legal/IP considerations).

It also carries the harder half of the problem: whether the task is
actually *hard*, and how you'd know. Difficulty turns out to live in
horizon and depth rather than per-step difficulty, capability gates get
synthesised by anything with a shell, and a single run is noise -- eight
rounds of design changes on one task produced conclusions that a repeat
run showed were all reading the same ±1 spread.

## Installing

```bash
git clone https://github.com/trapstreet/trapstreet-skills.git
cp -r trapstreet-skills/trapstreet-task-scaffold ~/.claude/skills/trapstreet-task-scaffold
```

## Contents

```
SKILL.md                              # the skill itself
references/difficulty-design.md       # what actually makes a task hard, and the fairness invariants
references/calibration.md             # probing, repeated trials, ablation, cost and latency
references/traptask-contract.md       # authoritative task file layout + manifest contracts
references/scoring-design.md          # real scoring exploits and how they were fixed
references/ground-truth-sourcing.md   # computed vs. real vs. authored, leakage mitigation
references/legal-ip-checklist.md      # when a task needs to stay local-only
scripts/scaffold_task.py              # generates gold.cases.json/build_cases.py/judge.py/grader.py/traptask.yaml/tests/README skeleton
scripts/validate_task.py              # structural self-consistency checks after build_cases.py runs
```

## License

MIT -- see [../LICENSE](../LICENSE)
