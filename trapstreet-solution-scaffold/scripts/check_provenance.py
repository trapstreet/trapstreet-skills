#!/usr/bin/env python3
"""Verify a task's local git HEAD matches what's actually published on
trapstreet.run before running/submitting a solution against it.

`tp submit` derives task provenance from the LOCAL git state of the task's
checkout at the moment `tp run` executes -- not from what you intend to
submit against. If the task repo has moved past whatever commit is
registered on the platform (e.g. after a revert, or before a "publish"
step), every submission fails with:

    error: http 404: {"error":"this task version isn't registered on the
    platform -- provenance.task (repo, commit, subdirectory) didn't match
    any published version. Publish the task first.","code":"NOT_FOUND"}

Run this BEFORE `tp run` to catch that ahead of time rather than after
wasting a real API call. No `tp auth login` required -- task info is public.

Usage:
    python3 check_provenance.py <task-slug> <path-to-task-repo-checkout>

Example:
    python3 check_provenance.py python-bugfix-diff ~/Documents/Projects/trapstreet-tasks
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def local_head(repo_path: Path) -> tuple[str, bool]:
    """Return (commit_sha, is_clean)."""
    sha = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(repo_path), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    ).stdout
    return sha, status.strip() == ""


def published_commit(task_slug: str) -> str | None:
    """GET /api/tasks/<slug> is a public, unauthenticated endpoint -- no api_key needed
    (and no api_key would grant access to a private task either; that's session-gated).
    This intentionally never requires `tp auth login` to have happened, since checking
    provenance is exactly the kind of thing you want to do before deciding whether to
    authenticate or spend anything at all."""
    import urllib.request

    req = urllib.request.Request(f"https://trapstreet.run/api/tasks/{task_slug}")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
    except Exception as e:
        print(f"error: could not fetch task info: {e}", file=sys.stderr)
        sys.exit(1)
    return data.get("task", {}).get("latest", {}).get("commit_sha")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    task_slug, repo_path_str = sys.argv[1], sys.argv[2]
    repo_path = Path(repo_path_str).expanduser().resolve()

    if not (repo_path / ".git").exists():
        print(f"error: {repo_path} is not a git repo root", file=sys.stderr)
        return 1

    local_sha, is_clean = local_head(repo_path)
    remote_sha = published_commit(task_slug)

    print(f"task:            {task_slug}")
    print(f"local repo:      {repo_path}")
    print(f"local HEAD:      {local_sha}  {'(clean)' if is_clean else '(DIRTY -- uncommitted changes)'}")
    print(f"published on trapstreet.run: {remote_sha or '(not found -- task may not be published at all)'}")
    print()

    if not is_clean:
        print("BLOCKED: local checkout has uncommitted changes. Commit and push before running.")
        return 1

    if remote_sha is None:
        print("BLOCKED: task doesn't appear to be published on trapstreet.run at all.")
        return 1

    if local_sha == remote_sha:
        print("OK: local HEAD matches the published version. Safe to `tp run` + submit.")
        return 0

    print("MISMATCH: local HEAD has moved past the published commit.")
    print()
    print("Options:")
    print("  1. Ask whoever publishes this task to re-publish at the current commit")
    print("     (this registers the new commit as the task's latest version).")
    print("  2. If you've confirmed the two commits are content-identical (e.g. a revert")
    print("     back to a previously-published state), you can temporarily check out the")
    print("     published commit, run, submit, then check back out to your branch:")
    print(f"       cd {repo_path}")
    print(f"       git checkout {remote_sha}")
    print("       # ... tp run / tp submit from the solution directory ...")
    print("       git checkout <your-branch>")
    print("     Confirm with whoever owns this repo before doing this -- it's a real,")
    print("     if temporary, detached-HEAD state change on a shared checkout.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
