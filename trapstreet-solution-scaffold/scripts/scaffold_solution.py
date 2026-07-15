#!/usr/bin/env python3
"""Scaffold a trap-cli solution directory: shared solution.py + one trap.yaml
per model/provider variant, following the pattern that avoids the
profile.model / actual-model drift bug (see ../references/trap-yaml-schema.md).

Single variant -> flat layout (trap.yaml at repo root, next to solution.py).
Multiple variants -> one subdirectory per variant, each holding only a
trap.yaml; cmd: points at ../solution.py.

Usage:
    python3 scaffold_solution.py \\
        --output-dir <path where the new solution repo folder goes> \\
        --repo-name <folder / repo name> \\
        --task-source <local-path-or-git+URL, relative to where trap.yaml ends up> \\
        --task-alias <alias used as both local run-dir name and trapstreet task_id> \\
        --variant anthropic:claude-opus-4-8 \\
        --variant anthropic:claude-sonnet-4-6 \\
        --variant openrouter:openai/gpt-5.6-luna-pro

Each --variant is "<provider>:<model-id>". provider must be "anthropic" or
"openrouter" (the two providers the generated solution.py knows how to call
-- extend call_<provider>() in the generated file for others).

--task-source is written VERBATIM into each trap.yaml's tasks.<alias>.source.
For a local path, get the relative depth right for wherever the file ends
up: one level deeper than the flat case if you're generating a multi-variant
layout (since variant trap.yaml files sit one directory below the repo
root). This script does NOT compute that for you -- pass the exact string
you've already worked out, or use a git+URL to sidestep the issue entirely.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SOLUTION_PY_TEMPLATE = '''# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "anthropic",
#     "openai",
# ]
# ///
"""{repo_name} -- solution for trap-cli.

Shared across every model/provider variant in this repo: each variant's
trap.yaml picks the provider and model via CLI arguments baked directly
into its cmd: line (never an env var -- see
../references/trap-yaml-schema.md in the trapstreet-solution-scaffold
skill for why that matters), e.g.
``uv run ../solution.py --provider anthropic --model claude-opus-4-8``.

Customize build_prompt() below for your solution's actual logic (e.g.
loading a SKILL.md + reference files as the system prompt). The default
is a bare relay: no system prompt, question.txt sent verbatim.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def build_prompt(question: str) -> tuple[str | None, str]:
    """Return (system_prompt_or_None, user_message).

    Customize this for your solution's real logic -- e.g. read a SKILL.md
    and reference files next to this script and return them as the system
    prompt. Left as a bare relay by default: no system prompt at all.
    """
    return None, question


def call_anthropic(model: str, system: str | None, user_message: str) -> str:
    from anthropic import Anthropic

    client = Anthropic(max_retries=10)
    kwargs = {{}}
    if system is not None:
        kwargs["system"] = system
    msg = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{{"role": "user", "content": user_message}}],
        **kwargs,
    )
    return next((b.text for b in msg.content if b.type == "text"), "").strip()


def call_openrouter(model: str, system: str | None, user_message: str) -> str:
    from openai import OpenAI

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    messages = []
    if system is not None:
        messages.append({{"role": "system", "content": system}})
    messages.append({{"role": "user", "content": user_message}})
    resp = client.chat.completions.create(model=model, max_tokens=1024, messages=messages)
    return (resp.choices[0].message.content or "").strip()


PROVIDERS = {{
    "anthropic": call_anthropic,
    "openrouter": call_openrouter,
}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=sorted(PROVIDERS))
    parser.add_argument("--model", required=True)
    args = parser.parse_args()

    manifest = json.loads(os.environ["TRAP_MANIFEST"])
    inputs_dir = Path(manifest["inputs_dir"])
    question = (inputs_dir / "question.txt").read_text()

    system, user_message = build_prompt(question)
    answer = PROVIDERS[args.provider](args.model, system, user_message)

    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

FLAT_TRAP_YAML_TEMPLATE = """name: {repo_name}
cmd: uv run solution.py --provider {provider} --model {model}
profile:
  model: {model}
  framework: {provider}-api
timeout: 300
tasks:
  {task_alias}:
    source: {task_source}
"""

VARIANT_TRAP_YAML_TEMPLATE = """name: {repo_name}-{variant_dir}
cmd: uv run ../solution.py --provider {provider} --model {model}
profile:
  model: {model}
  framework: {provider}-api
timeout: 300
tasks:
  {task_alias}:
    source: {task_source}
"""

ENVRC = "dotenv_if_exists\n"

ENV_EXAMPLE = "ANTHROPIC_API_KEY=\nOPENROUTER_API_KEY=\n"

GITIGNORE = ".venv/\n.trap/\n__pycache__/\n*.pyc\n.DS_Store\n.env\n"


def variant_dirname(model: str) -> str:
    # e.g. "claude-opus-4-8" stays as-is; "openai/gpt-5.6-luna-pro" -> "gpt-5.6-luna-pro"
    return model.split("/")[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--repo-name", required=True)
    parser.add_argument("--task-source", required=True)
    parser.add_argument("--task-alias", required=True)
    parser.add_argument("--variant", action="append", required=True, dest="variants",
                         help='"<provider>:<model-id>", repeatable')
    parser.add_argument("--skip-solution-py", action="store_true",
                         help="Don't write a template solution.py -- use this when you already "
                              "have one (hand-written, or adapted from an existing project) and "
                              "only want the trap.yaml / credentials / directory scaffolding.")
    args = parser.parse_args()

    variants = []
    for v in args.variants:
        if ":" not in v:
            print(f"error: --variant must be provider:model, got {v!r}", file=sys.stderr)
            return 1
        provider, model = v.split(":", 1)
        if provider not in ("anthropic", "openrouter"):
            print(f"error: unknown provider {provider!r} (known: anthropic, openrouter)", file=sys.stderr)
            return 1
        variants.append((provider, model))

    repo_root = Path(args.output_dir).expanduser() / args.repo_name
    repo_root.mkdir(parents=True, exist_ok=False)

    if args.skip_solution_py:
        print("Skipping solution.py -- place your own next to the generated trap.yaml(s).")
        print("It must: read TRAP_MANIFEST -> {inputs_dir, outputs_dir}, read inputs_dir/question.txt")
        print("(or whatever the task's real input filename is), and print the final answer to stdout.")
    else:
        (repo_root / "solution.py").write_text(SOLUTION_PY_TEMPLATE.format(repo_name=args.repo_name))
    (repo_root / ".envrc").write_text(ENVRC)
    (repo_root / ".env.example").write_text(ENV_EXAMPLE)
    (repo_root / ".gitignore").write_text(GITIGNORE)

    if len(variants) == 1:
        provider, model = variants[0]
        (repo_root / "trap.yaml").write_text(FLAT_TRAP_YAML_TEMPLATE.format(
            repo_name=args.repo_name, provider=provider, model=model,
            task_alias=args.task_alias, task_source=args.task_source,
        ))
        print(f"Flat layout written to {repo_root}")
    else:
        for provider, model in variants:
            vdir = repo_root / variant_dirname(model)
            vdir.mkdir(parents=True)
            (vdir / "trap.yaml").write_text(VARIANT_TRAP_YAML_TEMPLATE.format(
                repo_name=args.repo_name, variant_dir=variant_dirname(model),
                provider=provider, model=model,
                task_alias=args.task_alias, task_source=args.task_source,
            ))
        print(f"Multi-variant layout written to {repo_root}")
        print("Variant directories:", ", ".join(variant_dirname(m) for _, m in variants))

    print()
    print("Next steps:")
    step = 1
    if args.skip_solution_py:
        print(f"  {step}. Add your own solution.py to {repo_root} (see the contract printed above)")
    else:
        print(f"  {step}. Review {repo_root}/solution.py -- customize build_prompt() if this isn't a bare relay")
    step += 1
    print(f"  {step}. Double-check every trap.yaml's tasks.{args.task_alias}.source path is correct")
    print(f"     (relative paths are relative to EACH trap.yaml's own directory)")
    step += 1
    print(f"  {step}. cp {repo_root}/.env.example {repo_root}/.env and fill in real API keys")
    step += 1
    print(f"  {step}. cd {repo_root} && direnv allow .")
    step += 1
    print(f"  {step}. git init, create a dedicated GitHub repo, commit, push (needed for leaderboard provenance)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
