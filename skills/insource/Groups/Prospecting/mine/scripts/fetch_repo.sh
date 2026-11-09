#!/usr/bin/env bash
#
# fetch_repo.sh — clone or verify a GitHub repository for /mine.
#
# Two modes:
#   Verify only  (--verify): confirm a repo exists and is reachable,
#                             without cloning it. Used while building the
#                             source plan (Phase 1), so a candidate can be
#                             marked ✅/❌ in the plan table before the
#                             user approves it and before any real clone
#                             cost is paid.
#   Clone        (default):  actually clone the repo to a destination
#                             directory. Used during mining (Phase 2), once
#                             a candidate is on the approved plan.
#
# Output is a single line of JSON on stdout in all cases, so the calling
# agent can parse the result programmatically instead of screen-scraping
# git's own text output. Human-readable progress/errors go to stderr.
#
# Usage:
#   fetch_repo.sh --verify <repo-url>
#   fetch_repo.sh --dest <path> [--depth N] [--branch NAME] <repo-url>
#
# Flags:
#   --verify         Only check the repo exists/is reachable. No clone.
#   --dest PATH       Destination directory to clone into. Required unless
#                     --verify is passed. Created if it doesn't exist. If
#                     it already exists and is non-empty, fails rather than
#                     overwriting — pass a fresh path or remove it first.
#   --depth N         Shallow-clone depth (default: 1 — this skill mines
#                     structure and history-as-evidence via targeted
#                     lookups, not a full clone; use a larger depth or omit
#                     --depth entirely, which does a full clone, only when
#                     full commit history is specifically needed).
#   --branch NAME     Clone a specific branch instead of the repo's
#                     default.
#   -h, --help        Show usage and exit.
#
# Examples:
#   ./fetch_repo.sh --verify https://github.com/zed-industries/zed
#   ./fetch_repo.sh --dest /home/claude/mine-work/zed https://github.com/zed-industries/zed
#   ./fetch_repo.sh --dest /home/claude/mine-work/zed --depth 50 https://github.com/zed-industries/zed
#
# Exit codes:
#   0  success (repo verified reachable, or clone succeeded)
#   1  repo not reachable / doesn't exist (404, DNS failure, etc.)
#   2  usage error (bad flags, missing required argument)
#   3  destination conflict (--dest path exists and is non-empty)
#   4  clone command failed for a reason other than repo-not-found
#      (network failure, auth wall on a private repo, disk full, etc.)

set -euo pipefail

VERIFY_ONLY=0
DEST=""
DEPTH=""
BRANCH=""
REPO_URL=""

print_usage() {
  sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
}

json_escape() {
  # Minimal JSON string escaping for the fields we emit ourselves
  # (paths and URLs) — avoids a jq/python dependency for a one-line
  # output. Not a general-purpose JSON escaper.
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '%s' "$s"
}

emit_json() {
  # emit_json <status> <repo_url> <dest_or_null> <message>
  local status="$1" repo="$2" dest="$3" message="$4"
  local dest_json="null"
  if [ -n "$dest" ]; then
    dest_json="\"$(json_escape "$dest")\""
  fi
  printf '{"status":"%s","repo_url":"%s","dest":%s,"message":"%s"}\n' \
    "$(json_escape "$status")" \
    "$(json_escape "$repo")" \
    "$dest_json" \
    "$(json_escape "$message")"
}

fail() {
  # fail <exit_code> <status_word> <message>
  local code="$1" status="$2" message="$3"
  emit_json "$status" "${REPO_URL:-}" "${DEST:-}" "$message"
  exit "$code"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --verify)
      VERIFY_ONLY=1
      shift
      ;;
    --dest)
      [ $# -ge 2 ] || fail 2 "usage_error" "--dest requires a path argument"
      DEST="$2"
      shift 2
      ;;
    --depth)
      [ $# -ge 2 ] || fail 2 "usage_error" "--depth requires a numeric argument"
      DEPTH="$2"
      shift 2
      ;;
    --branch)
      [ $# -ge 2 ] || fail 2 "usage_error" "--branch requires a branch name"
      BRANCH="$2"
      shift 2
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    -*)
      fail 2 "usage_error" "Unknown flag: $1"
      ;;
    *)
      if [ -n "$REPO_URL" ]; then
        fail 2 "usage_error" "Unexpected extra argument: $1 (repo URL already given as $REPO_URL)"
      fi
      REPO_URL="$1"
      shift
      ;;
  esac
done

if [ -z "$REPO_URL" ]; then
  fail 2 "usage_error" "Missing required repo URL argument"
fi

if [ "$VERIFY_ONLY" -eq 0 ] && [ -z "$DEST" ]; then
  fail 2 "usage_error" "--dest is required unless --verify is passed"
fi

# --- Verify mode ---------------------------------------------------------
if [ "$VERIFY_ONLY" -eq 1 ]; then
  # git ls-remote hits the remote without cloning anything locally — the
  # correct way to answer "does this repo exist and is it reachable" for
  # the plan-building phase, where N candidates need checking cheaply
  # before any of them are actually cloned.
  if git ls-remote --exit-code "$REPO_URL" >/dev/null 2>&1; then
    emit_json "verified" "$REPO_URL" "" "Repository exists and is reachable."
    exit 0
  else
    fail 1 "not_found" "Repository is not reachable — it may not exist, may be private, or the URL may be wrong. Try fetching the URL directly to distinguish a 404 from a network issue before excluding this candidate."
  fi
fi

# --- Clone mode ------------------------------------------------------------
if [ -e "$DEST" ]; then
  if [ -d "$DEST" ] && [ -z "$(ls -A "$DEST" 2>/dev/null)" ]; then
    : # empty existing directory is fine, clone will use it
  else
    fail 3 "dest_conflict" "Destination '$DEST' already exists and is not empty. Choose a fresh path or remove it first — this script never overwrites an existing non-empty destination."
  fi
fi

mkdir -p "$(dirname "$DEST")" 2>/dev/null || true

CLONE_ARGS=(git clone)
if [ -n "$DEPTH" ]; then
  CLONE_ARGS+=(--depth "$DEPTH")
fi
if [ -n "$BRANCH" ]; then
  CLONE_ARGS+=(--branch "$BRANCH" --single-branch)
fi
CLONE_ARGS+=("$REPO_URL" "$DEST")

echo "Cloning $REPO_URL -> $DEST ..." >&2

if "${CLONE_ARGS[@]}" 2>/tmp/fetch_repo_stderr.$$; then
  rm -f /tmp/fetch_repo_stderr.$$
  emit_json "cloned" "$REPO_URL" "$DEST" "Repository cloned successfully."
  exit 0
else
  clone_stderr="$(cat /tmp/fetch_repo_stderr.$$ 2>/dev/null || true)"
  rm -f /tmp/fetch_repo_stderr.$$
  # Distinguish "repo doesn't exist" from other failures where possible,
  # since the caller (the mining agent) should handle these differently —
  # a not-found repo means swap the candidate; a network/auth failure on
  # a real private repo means retry or ask the user, not assume the
  # candidate is bad. Note: in some sandboxed environments, git has no
  # credential helper configured, so a genuinely nonexistent repo can
  # surface as a credential prompt failure ("could not read Username")
  # rather than a clean 404 — treat that pattern as not-found too, since
  # a real private repo would need credentials supplied up front anyway
  # and this script doesn't support that.
  if printf '%s' "$clone_stderr" | grep -qiE "not found|does not exist|repository not found|could not read username|could not read password|terminal prompts disabled"; then
    fail 1 "not_found" "Repository does not exist or is not accessible without credentials this script doesn't supply: $clone_stderr"
  else
    fail 4 "clone_failed" "Clone failed for a reason other than repo-not-found: $clone_stderr"
  fi
fi
