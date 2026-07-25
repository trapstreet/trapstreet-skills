---
name: trapstreet-setup
description: Install and authorize the trapstreet CLI (tp) -- install uv, install trap-cli, run tp auth login, verify the pairing. Use when the user says "set up trapstreet", "install tp", "install the CLI", "auth failed", "tp isn't working", or trapstreet-solution-scaffold/trapstreet-task-scaffold discover tp is missing or unauthenticated.
---

# trapstreet-setup -- install and authorize

Target state: `tp` runs, and (only if the user wants to submit) `tp auth status --verify` shows
the correct identity. Verify each step before moving to the next.

**Say this first, to lower the stakes**: local scoring (`tp run`) needs no authorization and no
GitHub account -- once `tp` is installed, `trapstreet-solution-scaffold` (or
`trapstreet-task-scaffold`) can already build and run against a task. Authorization (Step 4) is
only needed to submit to the leaderboard.

## Step 1 -- check current state (installation may not be needed at all)

```bash
which uv && uv --version
which tp && tp --help | head -5   # do NOT verify with `tp --version` -- old versions lack that
                                    # flag and throw a scary Error while the tool is actually fine
uv tool list | grep -i trap        # real installed package name: current is trap-cli;
                                    # an older machine may instead have trapstreet-cli
tp auth status --no-verify 2>&1 | head -5
```

All good already? Don't reinstall -- report the current state (tool works, login status) and
move straight to whatever the user actually wants to do. If the installed package is
`trapstreet-cli` (not `trap-cli`), recommend upgrading: `uv tool uninstall trapstreet-cli && uv
tool install trap-cli` -- the old package predates the trap.yaml schema that
`trapstreet-solution-scaffold`'s templates target, and has no confirmation gates for remote code
/ unanchored runs. If the user declines, say so plainly rather than pretending it's current.

## Step 2 -- install uv (if missing)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS/Linux, official script
# or: brew install uv
uv --version   # verify; if not found, reopen the shell or source the profile
```

## Step 3 -- install tp

```bash
uv tool install trap-cli
tp --help | head -5
```

The command is `tp`; the package is `trap-cli`. If Step 1 detected the old `trapstreet-cli`
package instead, `uv tool upgrade trap-cli` against it returns "not installed" (wrong package
name) -- uninstall the old one and install the new one, don't try to upgrade in place.

## Step 4 -- authorize (only needed to submit; skip if the user just wants to run locally)

```bash
tp auth login
```

Opens a browser to trapstreet.run/cli/authorize -- **the user clicks Approve themselves**
(requires a logged-in GitHub session; sign in there first if needed). Never click Approve or
enter any credential on the user's behalf. Warn the user: approving revokes the account's
previous CLI token, so any other machine paired earlier stops working.

No browser available (headless/CI): `tp auth login --with-token` reads an api_key from stdin
instead -- the user still has to obtain that token themselves by visiting `/cli/authorize` in a
browser they control; never ask them to paste a token into chat for you to store or forward.

## Step 5 -- verify and hand off

```bash
tp auth status --verify
```

Report the identity name and that setup is done. Next step is whatever the user came here for --
building/wiring a solution (`trapstreet-solution-scaffold`) or scaffolding a new task
(`trapstreet-task-scaffold`).

## Common failures

| Symptom | Handling |
|---|---|
| `tp --version` throws an Error | Old versions have no `--version` flag -- does not mean the install is broken. Verify with `tp --help` instead |
| `uv tool upgrade trap-cli` says not installed | The installed package is the old name `trapstreet-cli` -- uninstall old, install new (Step 1/3) |
| `tp: command not found` right after installing | uv's tool bin directory isn't on PATH -- run `uv tool update-shell`, then reopen the shell |
| `tp auth login` hangs without opening a browser | Visit the printed URL manually; in headless environments use `--with-token` instead |
| `tp auth status` shows UNAUTHORIZED | The token was revoked by a newer Approve on another machine -- run `tp auth login` again |
