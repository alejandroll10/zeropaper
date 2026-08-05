#!/usr/bin/env bash
# setup_push_token.sh — sandbox-safe git push credentials for this project.
#
# WHY: sandboxed runtimes cannot reach the macOS keychain. grok's Seatbelt
# profile denies mach-lookup com.apple.SecurityServer (the endpoint the
# osxkeychain credential helper needs), and grok's sandbox schema is
# filesystem+network only, so the grant cannot be added (issue #190). With an
# HTTPS remote + osxkeychain, every pipeline `git push` fails on auth while
# local commits succeed. This script switches the repo to a repo-scoped
# credential store: a fine-grained PAT limited to this one backup repo, held
# in an untracked file inside .git/ — the narrowest blast radius (a
# compromised agent can reach only this repo's token, not the keychain).
#
# Usage (run from anywhere inside the project):
#   bash code/utils/setup_push_token.sh              # prompts for the token (input hidden)
#   GIT_PUSH_TOKEN=... bash code/utils/setup_push_token.sh
#
# Create the token first: GitHub → Settings → Developer settings →
# Fine-grained personal access tokens → repository access: ONLY this project's
# backup repo → permissions: Contents: Read and write.
#
# NOTE: the credential-store path is baked in absolute; if you move the
# project directory, re-run this script.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

remote_url="$(git remote get-url origin 2>/dev/null || true)"
case "$remote_url" in
    "")
        echo "ERROR: no 'origin' remote configured — add the backup remote first." >&2
        exit 1
        ;;
    https://*) ;;
    *)
        echo "Remote is not HTTPS ($remote_url) — the keychain limitation does not apply; nothing to do." >&2
        exit 0
        ;;
esac
host="${remote_url#https://}"
host="${host%%/*}"
host="${host##*@}"

token="${GIT_PUSH_TOKEN:-}"
if [ -z "$token" ]; then
    if [ ! -t 0 ]; then
        echo "ERROR: no TTY and GIT_PUSH_TOKEN is not set — export GIT_PUSH_TOKEN and re-run." >&2
        exit 1
    fi
    read -r -s -p "Fine-grained PAT for $remote_url (input hidden): " token
    echo
fi
if [ -z "$token" ]; then
    echo "ERROR: no token provided." >&2
    exit 1
fi

cred_file="$(pwd)/.git/push-credentials"
umask 177
printf 'https://x-access-token:%s@%s\n' "$token" "$host" > "$cred_file"

# The leading empty helper resets the cumulative helper list (clearing the
# system-level osxkeychain, which fails inside the sandbox); the store helper
# then serves the token. --local: this repo only. Git hands the helper value
# to `sh -c`, so the path must be shell-quoted or a space/apostrophe in the
# project path shears or breaks the command — printf %q emits the correct
# sh-safe form for any realistic path. (Known exotic edge: a raw control char
# — e.g. an embedded tab — in the path makes bash's %q emit $'...' ANSI-C
# quoting, which dash — Linux's default /bin/sh — does not interpret, so such
# a path would break credential lookup on a dash-based Linux deploy.
# Space/apostrophe/plain paths, the realistic case, are unaffected.)
cred_file_quoted="$(printf '%q' "$cred_file")"
git config --local --replace-all credential.helper ""
git config --local --add credential.helper "store --file=$cred_file_quoted"

if git ls-remote origin >/dev/null 2>&1; then
    echo "OK: authenticated to $host via $cred_file — sandboxed 'git push' will work."
else
    # On auth rejection git calls `credential reject`, and the store helper
    # erases the bad token from the file — so it is gone, not just wrong.
    echo "ERROR: the auth test (git ls-remote origin) was rejected, and git erased the token from $cred_file." >&2
    echo "       Fix the token (repo access, Contents: Read and write, expiry) and re-run this script." >&2
    exit 1
fi
