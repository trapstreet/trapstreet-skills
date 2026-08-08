---
name: trapstreet-solution-scaffold
description: >-
  Scaffold a submission-ready trap-cli solution for a trapstreet.run task -- generates trap.yaml
  (and, optionally, solution.py) with the correct current schema, sets up credentials, and gets
  the repo into leaderboard-eligible shape. Covers writing one from scratch, wrapping an existing
  solution.py, and adapting someone else's existing repo. Use whenever the user wants to build a
  new solution for a trapstreet task, wrap an existing script so it can be evaluated, port a
  project they found elsewhere into this task-eval format, add another model/provider to compare
  against an existing task, or is troubleshooting why a solution won't submit or isn't showing up
  on the leaderboard -- even if they don't say "trap.yaml" or "trap-cli" by name, e.g. "I want to
  test claude opus against this task", "make a solution for X", "I found this agent repo, can we
  test it against our task", "why isn't my run showing up", "add gpt-5 as another comparison
  point".
---

# trapstreet-solution-scaffold

Scaffolds a `trap-cli` solution directory for a task on trapstreet.run, and
helps diagnose the real submission failures this ecosystem produces. Built
from repeated real incidents, not theory -- every gotcha below actually
happened.

`tp` missing, or `tp auth status` shows no valid pairing? Hand off to `trapstreet-setup` first --
everything below assumes `tp` already runs.

## Ground rules

- Never read the task's `expected/`, `judge.py`, or `grader.py` to construct or embellish an
  answer -- only the IO-contract part of `traptask.yaml` (inputs/outputs shape) is fair game,
  and only as much of it as writing the adapter/solution.py actually requires.
- `tp run`/`tp submit` pause on two confirmation gates -- remote-source (about to execute code
  pulled from a repo) and unanchored (no git provenance, won't rank). Both are the user's call,
  never yours: explain the consequence in plain words, recommend an answer, let them decide (see
  "Gates and consent" below). Never pass `--trust-remote`/`--allow-unanchored` on your own
  initiative.
- Never submit to the public leaderboard without the user's explicit go-ahead on that specific
  submission -- a prior yes does not carry forward to the next run.

## Before writing anything: interview

1. **Which task, and where does it live?** A local path (most common when
   the task repo is checked out nearby), a `git+URL`, or a trapstreet.run task page
   (`https://trapstreet.run/tasks/<slug>`). For the trapstreet.run case, resolve it via the
   public API rather than fetching the page itself -- faster, more reliable, and doesn't depend
   on page layout or content-blob parsing:
   ```bash
   curl -s https://trapstreet.run/api/tasks/<slug> | python3 -m json.tool
   # -> task.latest.{repo_url, commit_sha, repo_path}
   ```
   Assemble `git+<repo_url>@<commit_sha>#subdirectory=<repo_path>` yourself from those three
   fields -- don't scrape the task's web page for this, and don't ask the user to copy a git URL
   off it by hand. If local, you'll need the exact relative path from wherever each `trap.yaml`
   ends up -- get this right per-file (see Layout below), since a wrong relative depth is a
   common mistake.
2. **Which of the three starting points is this?** (see below) -- from
   scratch, wrapping an existing `solution.py`, or adapting an existing
   external project. This determines whether the scaffold script writes a
   template `solution.py` for you or leaves that part to you.
3. **One model, or several to compare?** This determines the layout (see
   below). If several: which providers/models exactly?
4. **API keys, then model IDs.** Before verifying anything, confirm the user actually has an API
   key for each provider in play -- ask directly if unsure; don't assume `.env` has real values
   just because `.env.example` exists. A missing key isn't obvious until `solution.py` crashes on
   a bare `KeyError` at runtime, so catch it here instead of there. If it's missing, point to
   where to get one and pause until the user has it:
   - Anthropic: https://console.anthropic.com/settings/keys
   - OpenRouter: https://openrouter.ai/keys
   - Any other provider: its own dashboard/account settings page

   Once a key is confirmed present, never guess the model ID -- verify the exact ID against that
   provider's own API before writing it anywhere. Every provider gets checked the same way,
   including Anthropic:
   ```bash
   # Anthropic
   curl -s https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01"
   # OpenRouter
   curl -s https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     | python3 -c "import json,sys; print([m['id'] for m in json.load(sys.stdin)['data'] if '<keyword>' in m['id']])"
   ```
   (In a Claude Code session that has it installed, the `claude-api` skill is a faster shortcut
   covering the same Anthropic catalog -- use it if available, but the curl above works with no
   dependency on any particular tool.) A plausible-looking bare model name (e.g. `gpt-5.6`) may
   not exist -- only specific suffixed variants might (e.g. `openai/gpt-5.6-luna-pro`), and Claude
   names get hallucinated the same way (appended dates, made-up versions like "claude-sonnet-5").
   Ask the user to pick if there's ambiguity; don't guess.
5. **Repo name / destination.** Where should the solution folder live, and
   what should the eventual GitHub repo be called?

## Three starting points

The scaffold script always handles the surrounding scaffolding (`trap.yaml`,
directory layout, `.envrc`/`.env.example`, `.gitignore`) the same way. What
differs is `solution.py` -- how much of it, if any, the script should write.

**1. From scratch, no existing code.** Let the script generate a template
`solution.py` with a `build_prompt()` hook (default: bare relay, no system
prompt -- a useful floor/baseline to compare other solutions against).
Customize `build_prompt()` for anything more elaborate.

**2. You already have a working `solution.py`.** Pass `--skip-solution-py`
to the scaffold script so it only writes the surrounding files, then place
your existing script in the repo. The only two things it needs to satisfy
the task contract: read `TRAP_MANIFEST` (a JSON env var,
`{inputs_dir, outputs_dir}`) to find the task's input files, and print the
final answer to stdout. If it already does something equivalent (e.g. reads
argv paths instead), adapt just that part -- the rest of your logic is
yours to keep as-is. Reference `references/trap-yaml-schema.md` for the
exact manifest contract.

**3. Adapting an existing external project you found elsewhere** (a GitHub
repo, a research reproduction, someone else's agent). This is the most
involved path and the scaffold script alone will not do it -- go read the
target project first:

- What does it actually take as input, and how do you invoke it -- a CLI
  command, a Python import, an HTTP call to a server you'd need to run?
- Does it already produce a single final answer, or does it need glue code
  to extract one (e.g. it prints a lot of intermediate reasoning and you
  need the last line, or it writes a result file you need to read back)?
- Does it have its own dependencies, and can those coexist with `uv run` /
  PEP 723 inline deps, or does it need its own virtualenv / `pyproject.toml`
  that the generated `trap.yaml`'s `cmd:` should invoke instead?

Then write a bespoke `solution.py` (or `cmd:` that invokes something else
entirely -- `cmd:` just needs to be a shell command, it doesn't have to be
`uv run solution.py`) that acts as a thin **adapter**: reads
`TRAP_MANIFEST`, drives the external project however it's actually meant to
be driven, and prints its final answer to stdout. Run the scaffold script
with `--skip-solution-py` for the rest of the scaffolding, same as path 2.
This is exactly the shape used for wrapping real community Claude Skills in
past sessions -- fetch the target's own files (its equivalent of `SKILL.md`
+ reference docs), load them faithfully as the system prompt or feed them
into the adapter's logic, rather than reimplementing an approximation of
what the project does.

## Layout: single model vs. multiple

**Single model** -- flat layout, `trap.yaml` at the repo root next to
`solution.py`.

**Multiple models/providers being compared** -- one shared `solution.py` at
the repo root (using PEP 723 inline script metadata for its dependencies,
so no separate `pyproject.toml`/`uv.lock` is needed), plus one subdirectory
per variant holding only a `trap.yaml`. Each variant's `cmd:` bakes the
provider and model in as literal CLI arguments. **This is the load-bearing
design decision** -- see "Why not a MODEL env var" below for the real
incident that motivates it. As of trap-cli v0.0.8, `SOLUTION` is a positional
argument and the task alias is a `--task` flag (older CLIs had it the other
way around -- check `tp run --help` if unsure which you have): `tp run
./<variant-dir> --task <alias>` (or `cd <variant-dir> && tp run --task
<alias>`) runs one variant; there's no built-in "run every variant at once"
-- each is independent from trap-cli's point of view.

Read `references/trap-yaml-schema.md` for the exact schema, the
model-drift rationale in full, and the manifest contract.

## Generating the files

The generated `trap.yaml` only targets the current (new-generation) `trap-cli` schema --
`tp run --help 2>&1 | grep -c -- "--trust-remote"` (>=1 = new generation). If the installed CLI
is old-generation (`trapstreet-cli`, no match), these templates will not work as-is; have the
user upgrade first (`uv tool uninstall trapstreet-cli && uv tool install trap-cli`) rather than
hand-adapting the schema.

Use the bundled script rather than hand-writing every file -- it's
deterministic and gets the escaping/relative-path plumbing right:

```bash
python3 scripts/scaffold_solution.py \
  --output-dir <parent dir for the new solution folder> \
  --repo-name <folder-and-repo-name> \
  --task-source <path-or-git+URL, exactly as it should appear in trap.yaml> \
  --task-alias <alias> \
  --variant anthropic:claude-opus-4-8 \
  --variant openrouter:openai/gpt-5.6-luna-pro \  # repeat --variant per model; single entry = flat layout
  --skip-solution-py   # omit this flag for starting point 1; include it for 2 and 3
```

This writes `.envrc`, `.env.example`, `.gitignore`, and either one
`trap.yaml` (single variant) or one subdirectory per variant (multiple);
`solution.py` too, unless `--skip-solution-py` was passed. It does **not**
run `git init` or create a GitHub repo -- do those explicitly, and confirm
with the user before pushing anywhere public.

After generating: **actually read the generated `solution.py`** and
customize `build_prompt()` if the solution needs real logic beyond a bare
relay (e.g. reading a `SKILL.md` next to the script and returning it as the
system prompt). The template's `call_anthropic()`/`call_openrouter()`
dispatch functions handle the API mechanics; `build_prompt()` is the one
hook meant to be edited.

## Before the first run

Before any of this: confirm `.env` actually has real values, not just `.env.example`'s blanks
copied over. If a key turns out to be missing only now, stop and get it (the interview's API keys
step above has where to look) rather than let the first real run crash on it.

Three things to get right before `tp run` touches anything -- in this order, because scaffolding
starts from nothing: no cost spent yet, no git history yet, no task-version check done yet.

### 1. Cost -- ask before any paid call happens

`tp run` never talks to the platform, but the solution's own API calls bill normally, and this
skill often multiplies the bill: several variants (one per provider/model from the interview)
times however many cases the task has. Classify before running anything; can't tell = treat as
paid and ask:

- **No paid calls, confirmed** (deterministic code -- no LLM SDK, no API key in env/.env, no HTTP
  to a paid endpoint): free to iterate, skip the rest of this section.
- **Paid calls**: spending the user's money is a gate with the same weight as the CLI's own
  safety gates -- no paid call happens before the user's OK, the first smoke test included.
  Estimate one full pass per variant (case count from the task's `traptask.yaml` x calls per case
  x that provider's price; order of magnitude is enough), total the whole plan across every
  variant, and get consent through a structured question (see "Gates and consent" below). Can't
  estimate confidently? Get consent for a **1-case smoke** first: trim a local copy of the task's
  cases to one, point a scratch `trap.yaml` at it, run it, read the real per-case cost off
  `report.json`, then delete the scratch copy (a forgotten copy is the same stale-version trap as
  running against an unpinned task checkout). Smoke numbers are wiring evidence, never a result --
  they are not the submission candidate.

### 2. Task provenance

A run only submits successfully if the **task's** local git commit is
actually registered on trapstreet.run. This is a real, repeatedly-hit
failure mode -- the task repo can move past whatever was last published
(e.g. after a revert) and every submission then fails with a 404 saying the
task version "isn't registered on the platform." Check this **before**
spending a real API call on `tp run`:

```bash
python3 scripts/check_provenance.py <task-slug> <path-to-task-repo-checkout>
```

If it reports a mismatch, don't try to work around it silently -- it prints
the options (re-publish, or a temporary checkout of the published commit if
content is confirmed identical) and explicitly flags that the checkout
option needs the repo owner's confirmation before doing it, since it's a
detached-HEAD state change on a possibly-shared checkout.

### 3. Solution provenance -- git init early, anchor before you spend for real

The scaffold script does not run `git init` or create a GitHub repo (previous section) -- so the
very first `tp run` in a freshly scaffolded directory has no git history at all, which trips the
CLI's unanchored gate immediately. `git init` locally is free and safe to do without asking (it
touches nothing public); the public push is the part that needs the user's go-ahead.

Sequencing matters more than the init itself, because `tp run` bakes git provenance into
`report.json` **at the moment it runs** -- a run born from a dirty or unpushed tree is unanchored
forever, and committing afterwards cannot retrofit it; the only fix is running again, at full
price if the pass was paid:
- **Free passes**: iterate unanchored freely; before the run meant to be the submission
  candidate, commit + push (with the user's OK), then run.
- **Paid passes**: get the wiring right on the 1-case smoke first (smoke runs are unanchored too,
  and that is expected -- they are not a submission candidate anyway), then commit + push, and
  make the **first full-price pass per variant** the submittable one. Never let a full-price pass
  run unanchored "just to test" -- that silently doubles the bill, and the user may not have
  budget for the second half.

Also applies mid-iteration: if you edit `trap.yaml` after the repo is anchored (e.g. switching a
model), commit + push again *before* re-running, or the new run's provenance will not reflect the
edit (bitten twice in real usage: an unstaged yaml edit, and `tp submit` silently re-uploading a
stale pre-existing report instead of the fresh run).

One more thing while here: give each solution **its own dedicated git repo**, not a shared
monorepo -- a monorepo where anything else is dirty nulls out the whole repo's provenance ("local
never ranks"), so a perfectly clean solution folder still gets shut out by an unrelated dirty
sibling.

## Gates and consent

The CLI's two confirmation gates (remote-source, unanchored) and the cost gate above are all the
user's decisions, not yours -- explain, don't relay: the gate vocabulary and flag names in this
document are for you, not for them. Ask through the harness's structured question tool when one
exists (one question per gate, plain words in the question and option descriptions, a marked
recommendation); fall back to plain text only when no such tool exists. For the remote-source
gate, say whose code is about to run -- "this task's judging code, from the task repo you pointed
at" reads very differently depending on whether that repo is the user's own, and the
recommendation should reflect that.

## Submitting

Try `tp submit <path> --task <task-alias>` first (positional `SOLUTION` + `--task` flag,
as of trap-cli v0.0.8 -- older CLIs used `--solution <path> <task-alias>` instead). If it reports `status
✗ failed, score None` on what looks like a genuinely valid report, that's a
known historical CLI bug -- `uv tool upgrade trap-cli` first in case it's
been fixed, and if not, fall back to POSTing the report directly (exact
command in `references/trap-yaml-schema.md`). The go-ahead requirement is in Ground rules above --
it applies here without exception.

## Why not a MODEL env var (the short version)

Earlier real solutions read `MODEL` from the environment and separately
declared `profile.model` in `trap.yaml` for the leaderboard display. These
drifted apart in practice more than once -- someone would switch the env
var without touching the yaml (or vice versa), and the leaderboard would
show a different model than what actually ran. Baking the model into
`cmd:` as a literal CLI argument makes this class of bug structurally
impossible: there's only one place the model string lives, and it's the
same place that determines both what runs and what gets reported. Full
detail and the before/after yaml in `references/trap-yaml-schema.md`.
