# trap.yaml — authoritative schema and gotchas

Verified against the installed `trap-cli`'s own source
(`trap/models/trap_yaml.py`). Some older solutions in shared monorepos use a
stale schema (`tasks: {<alias>: {solution:, cmd:, traptask:, ...}}`, reads
`INPUTS`/`OUTPUTS`) — that schema does **not** match the current runner and
will break. Always use the shape below.

```yaml
name: <optional, server auto-assigns a serial name if omitted>
profile:
  model: [<model-id>, ...]       # self-reported, shown in leaderboard ENGINE column
  framework: [<framework-id>, ...]
cmd: <shell command, shlex.split, cwd = the trap.yaml's own directory>
manifest_envvar: TRAP_MANIFEST   # default; solution reads this env var
timeout: 600                     # default seconds, per-case wall-clock ceiling
tasks:
  <alias>:                       # alias = local run-dir name AND the trapstreet task_id on submit
    source: <local-dir-path-relative-to-trap.yaml, OR git+URL>
```

A scalar also works for `profile.model`/`profile.framework` (normalized to a
single-element list) — write `model: claude-opus-4-8` if there's only one.

## `profile.model` is a LABEL, not a switch

This is the single most important thing to get right. `profile.model` is
**purely self-reported** — it's what shows up in the leaderboard's ENGINE
column, and it does **not** drive execution. The model that actually runs is
whatever `cmd:` invokes. If you set the model via an environment variable
(`MODEL=claude-opus-4-8` read inside `solution.py`) and separately write
`profile.model: claude-opus-4-8` in the yaml, **nothing keeps these in
sync** — edit the env var without touching the yaml (or vice versa) and the
leaderboard will show the wrong model while a different one actually ran.
This happened repeatedly in real use before the fix below.

**The fix: never use an env var as the source of truth for the model. Bake
the model into `cmd:` as a literal CLI argument.**

```yaml
# GOOD — model is a literal part of the command; cannot drift from profile.model
cmd: uv run ../solution.py --provider anthropic --model claude-opus-4-8
profile:
  model: claude-opus-4-8
```

```yaml
# BAD — MODEL env var and profile.model can silently disagree
cmd: uv run python solution.py
profile:
  model: claude-opus-4-8   # nothing enforces this matches $MODEL at runtime
```

This also cleanly solves the "I want to compare N models" case: don't build
one solution with a model-switching env var — build **one shared
`solution.py` + one subdirectory per model variant**, each holding only a
`trap.yaml` whose `cmd:` bakes in that variant's provider/model. See
`scripts/scaffold_solution.py`.

## The manifest contract

Solution reads:

```python
manifest = json.loads(os.environ["TRAP_MANIFEST"])
inputs_dir = Path(manifest["inputs_dir"])    # a directory, not a per-file path
outputs_dir = Path(manifest["outputs_dir"])
question = (inputs_dir / "question.txt").read_text()
```

Write the answer to **stdout**. `ANTHROPIC_API_KEY` (or other provider keys)
just need to be present in the ambient shell env — trap's cost-tracking
proxy reroutes via `ANTHROPIC_BASE_URL` but the solution's own SDK client
still needs the real key; there's no special trap-side key injection.

## Provenance — what makes a run rankable

`GET /api/submit` (or `tp submit`) requires the **task**'s git provenance to
resolve to a repo+commit that's actually **published** on trapstreet.run —
see `scripts/check_provenance.py` to verify this before running anything.

For the **solution** to show up on the public leaderboard (not just submit
successfully), it additionally needs:
- Its own git repo (not a shared monorepo with unrelated dirty files —
  "local never ranks": a dirty tree anywhere in the repo nulls out
  `provenance.solution`)
- That repo pushed to a public remote (e.g. GitHub)
- Clean working tree at the moment `tp run` executes

Since a shared monorepo can basically never guarantee this (someone's
always mid-edit on something else in it), give every solution its **own
dedicated repo**.

## `tp submit` CLI bug (historical, may be fixed by your CLI version)

`tp submit` has previously returned `status ✗ failed, score None` even for
a completely valid report.json. If you hit this, the workaround is to POST
the report directly:

```bash
API_KEY=$(python3 -c "import json; print(json.load(open(__import__('os').path.expanduser('~/.config/trapstreet/auth.json')))['api_key'])")
curl -s -X POST https://trapstreet.run/api/submit \
  -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  --data-binary @.trap/<task>/<run-timestamp>/report.json
```

Try the real `tp submit` first — `uv tool upgrade trap-cli` before assuming
this bug is still present; it may have been fixed upstream.

## Credentials via direnv

```
# .envrc (committed)
dotenv_if_exists

# .env (gitignored — copy from .env.example and fill in real values)
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=
```

A root-level `.envrc`/`.env` covers subdirectories too (direnv walks up the
tree), so a multi-variant layout only needs one copy at the repo root — not
one per variant subdirectory.

## Multi-provider note

Only Anthropic model IDs can be verified against an authoritative catalog
from within this skill (defer to the `claude-api` skill's model table —
never guess a Claude model ID). Other providers (OpenRouter, OpenAI direct,
etc.) need their own verification — e.g. for OpenRouter, hit
`GET https://openrouter.ai/api/v1/models` and confirm the exact model slug
exists before writing it into a trap.yaml. Guessed non-Anthropic model IDs
have been wrong before (e.g. a bare `gpt-5.6` doesn't exist on OpenRouter —
only suffixed variants like `openai/gpt-5.6-luna-pro` do).
