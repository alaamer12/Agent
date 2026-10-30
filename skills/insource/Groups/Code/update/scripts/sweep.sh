#!/usr/bin/env bash
# sweep.sh - find every form of a term across a codebase.
#
# Plain grep for "catalog" misses catalog__item, catalogService, CATALOG_URL,
# and file names. This script generates the naming-convention variants and
# reports hits grouped by variant, plus matching file/directory names.
#
# Usage:
#   sweep.sh <term> [path] [--count]
#
# Examples:
#   sweep.sh catalog
#   sweep.sh "user profile" ./src
#   sweep.sh catalog . --count
#
# Read-only. Never modifies files.
#
# Requirements: bash 3.2+ (macOS default is fine), grep or ripgrep, find.
# Not POSIX sh: it uses bash arrays, so run it with `bash`, not `sh`.
#
# Language-agnostic by design: it generates the naming variants used across
# ecosystems (snake_case in Python/Rust/Ruby/SQL, camelCase in Java/Go/JS,
# PascalCase in C#/Go/Java types, SCREAMING_CASE for constants, kebab-case in
# URLs/CSS/CLI flags) plus a separator-tolerant catch-all. The variant list is
# a starting point, not an exhaustive set: if your stack spells things another
# way (e.g. dotted i18n keys, Train-Case headers), search for that spelling too.

set -u

if [ $# -lt 1 ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
fi

TERM_IN="$1"
ROOT="${2:-.}"
COUNT_ONLY=0
for arg in "$@"; do [ "$arg" = "--count" ] && COUNT_ONLY=1; done
[ "$ROOT" = "--count" ] && ROOT="."

if [ ! -d "$ROOT" ]; then
  echo "error: path not found: $ROOT" >&2
  exit 2
fi

# Split the term into lowercase words. "User Profile", "user-profile",
# "user_profile", and "userProfile" all become: user profile
words=$(printf '%s' "$TERM_IN" \
  | sed -E 's/([a-z0-9])([A-Z])/\1 \2/g' \
  | tr '[:upper:]' '[:lower:]' \
  | tr -c 'a-z0-9\n' ' ' \
  | tr -s ' ' \
  | sed -E 's/^ +| +$//g')

if [ -z "$words" ]; then
  echo "error: term contains no searchable characters" >&2
  exit 2
fi

# Build each variant from the word list.
lower_join() {
  # join words with a separator (which may be empty) without relying on tr,
  # since `tr ' ' ''` is invalid.
  local sep="$1" out="" w
  for w in $words; do
    if [ -z "$out" ]; then out="$w"; else out="${out}${sep}${w}"; fi
  done
  printf '%s' "$out"
}
camel() {
  echo "$words" | awk '{
    out=$1
    for(i=2;i<=NF;i++) out=out toupper(substr($i,1,1)) substr($i,2)
    print out }'
}
pascal() {
  echo "$words" | awk '{
    for(i=1;i<=NF;i++) out=out toupper(substr($i,1,1)) substr($i,2)
    print out }'
}

KEBAB=$(lower_join '-')
SNAKE=$(lower_join '_')
FLAT=$(lower_join '')
CAMEL=$(camel)
PASCAL=$(pascal)
SCREAM=$(echo "$SNAKE" | tr '[:lower:]' '[:upper:]')
SPACED="$words"

# Plurals are a common miss (catalog -> catalogs, category -> categories).
# Only pluralise the last word.
last=$(echo "$words" | awk '{print $NF}')
head_words=$(echo "$words" | awk '{$NF=""; sub(/ +$/,""); print}')
# If the last word already looks plural ("projects", "categories"), the user
# typed the plural form, so do not pluralise it again ("projectses").
ALREADY_PLURAL=0
case "$last" in
  *ies) ALREADY_PLURAL=1; plural_last="$last" ;;
  *ss|*us|*is) plural_last="${last}es" ;;      # class, status, analysis: singular
  *s) ALREADY_PLURAL=1; plural_last="$last" ;;
  *[^aeiou]y) plural_last="${last%y}ies" ;;
  *x|*z|*ch|*sh) plural_last="${last}es" ;;
  *) plural_last="${last}s" ;;
esac
# Build the plural in each naming convention. Ecosystems disagree on which one
# they use for collections (Go: orderStatuses, Rust: order_statuses, C#: OrderStatuses).
PLURAL_WORDS="$plural_last"
[ -n "$head_words" ] && PLURAL_WORDS="$head_words $plural_last"
_saved_words="$words"
words="$PLURAL_WORDS"
PLURAL_SNAKE=$(lower_join '_')
PLURAL_KEBAB=$(lower_join '-')
PLURAL_CAMEL=$(camel)
PLURAL_PASCAL=$(pascal)
words="$_saved_words"

# Directories that are noise. Extend via SWEEP_EXCLUDE (comma separated).
# Build output, dependency caches, and VCS metadata across common ecosystems.
# Illustrative, not exhaustive: extend with SWEEP_EXCLUDE="dir1,dir2" for your stack.
#   JS/TS      node_modules dist build .next .nuxt .turbo .svelte-kit coverage
#   Python     __pycache__ .venv venv .tox .mypy_cache .pytest_cache
#   JVM        target .gradle .mvn out
#   .NET       bin obj
#   Rust/Go    target vendor
#   Elixir     _build deps
#   Swift/iOS  Pods DerivedData .build
#   Dart       .dart_tool
#   Haskell    .stack-work dist-newstyle
#   IaC        .terraform
#   generic    .git .cache
EXCLUDES="node_modules,dist,build,.next,.nuxt,.turbo,.svelte-kit,coverage,__pycache__,.venv,venv,.tox,.mypy_cache,.pytest_cache,target,.gradle,.mvn,out,bin,obj,vendor,_build,deps,Pods,DerivedData,.build,.dart_tool,.stack-work,dist-newstyle,.terraform,.git,.cache"
[ -n "${SWEEP_EXCLUDE:-}" ] && EXCLUDES="$EXCLUDES,$SWEEP_EXCLUDE"

GREP_EXCLUDES=()
FIND_PRUNE=()
IFS=',' read -ra EX <<< "$EXCLUDES"
for d in "${EX[@]}"; do
  GREP_EXCLUDES+=(--exclude-dir="$d")
  FIND_PRUNE+=(-name "$d" -o)
done

# Prefer ripgrep when available, else fall back to grep.
search() {
  local pattern="$1" mode="$2"
  if command -v rg >/dev/null 2>&1; then
    local rg_ex=()
    for d in "${EX[@]}"; do rg_ex+=(-g "!$d"); done
    if [ "$mode" = "ci" ]; then
      rg -n --no-heading -I -i "${rg_ex[@]}" -e "$pattern" "$ROOT" 2>/dev/null
    else
      rg -n --no-heading -I "${rg_ex[@]}" -e "$pattern" "$ROOT" 2>/dev/null
    fi
  else
    if [ "$mode" = "ci" ]; then
      grep -rnI -i "${GREP_EXCLUDES[@]}" -e "$pattern" "$ROOT" 2>/dev/null
    else
      grep -rnI "${GREP_EXCLUDES[@]}" -e "$pattern" "$ROOT" 2>/dev/null
    fi
  fi
}

report() {
  local label="$1" pattern="$2" mode="$3"
  local out n
  out=$(search "$pattern" "$mode")
  if [ -z "$out" ]; then n=0; else n=$(printf '%s\n' "$out" | wc -l | tr -d ' '); fi
  printf '%-34s %6s hits\n' "$label" "$n"
  if [ "$COUNT_ONLY" -eq 0 ] && [ "$n" -gt 0 ]; then
    printf '%s\n' "$out" | head -n 8 | sed 's/^/      /'
    [ "$n" -gt 8 ] && printf '      ... %s more\n' $((n - 8))
  fi
}

echo "== sweep: \"$TERM_IN\"  in  $ROOT"
echo "   words: [$words]"
echo "   (counts are matching LINES, not individual occurrences; one line can hold several)"
echo

# For a single-word term, kebab/snake/camel/flat are all the same string.
# Collapse identical patterns so the report is not padded with duplicate rows.
# (Uses a newline-delimited string, not `declare -A`, so it runs on bash 3.2,
# which is what macOS ships.)
SEEN_KEYS=""
emit() {
  local label="$1" pattern="$2" mode="$3"
  local key="${mode}:${pattern}"
  case "
$SEEN_KEYS
" in
    *"
$key
"*) return ;;
  esac
  SEEN_KEYS="${SEEN_KEYS}
${key}"
  report "$label" "$pattern" "$mode"
}

echo "-- Contents, by variant (case-sensitive so conventions stay distinguishable)"
emit "lower/kebab ($KEBAB)"     "$KEBAB"  cs
emit "snake       ($SNAKE)"     "$SNAKE"  cs
emit "camel       ($CAMEL)"     "$CAMEL"  cs
emit "Pascal      ($PASCAL)"    "$PASCAL" cs
emit "SCREAMING   ($SCREAM)"    "$SCREAM" cs
if [ "$ALREADY_PLURAL" -eq 0 ]; then
  emit "plural snake ($PLURAL_SNAKE)"   "$PLURAL_SNAKE"  cs
  emit "plural kebab ($PLURAL_KEBAB)"   "$PLURAL_KEBAB"  cs
  emit "plural camel ($PLURAL_CAMEL)"   "$PLURAL_CAMEL"  cs
  emit "plural Pascal($PLURAL_PASCAL)"  "$PLURAL_PASCAL" cs
fi
if [ "$SPACED" != "$KEBAB" ]; then
  emit "spaced      ($SPACED)"  "$SPACED" ci
fi

echo
echo "-- Delimiter-joined fragments (e.g. CSS BEM block__element / block--modifier; also Rails-style namespaces)"
report "element     (${KEBAB}__*)"  "${KEBAB}__"  cs
report "modifier    (${KEBAB}--*)"  "${KEBAB}--"  cs
report "prefixed    (*__${KEBAB})"  "__${KEBAB}"  cs

echo
# Separator-tolerant, case-insensitive catch-all. For "user id" this matches
# userid, user_id, user-id, user.id, user id, UserID, USER__ID ... so it also
# finds spellings the named variants above did not anticipate.
LOOSE=$(echo "$words" | sed 's/ /[-_. ]*/g')
echo "-- Catch-all: separator-tolerant, case-insensitive  (/$LOOSE/i)"
report "any spelling" "$LOOSE" ci

# Excluded directories are noise MOST of the time, but vendored code is exactly
# where unrelated look-alikes live (a third-party library that uses the same word). Never hide that
# silently: count hits inside excluded dirs and tell the reader.
echo
echo "-- Hits inside EXCLUDED directories (not counted above)"
excluded_total=0
for d in "${EX[@]}"; do
  while IFS= read -r found_dir; do
    [ -z "$found_dir" ] && continue
    if command -v rg >/dev/null 2>&1; then
      c=$(rg -c -I -i --no-ignore --hidden -e "$LOOSE" "$found_dir" 2>/dev/null \
            | awk -F: '{s+=$NF} END{print s+0}')
    else
      c=$(grep -rIi -e "$LOOSE" "$found_dir" 2>/dev/null | wc -l | tr -d ' ')
    fi
    if [ "${c:-0}" -gt 0 ]; then
      printf '   %-40s %6s hits  <- review: possible look-alike or generated output\n' "$found_dir" "$c"
      excluded_total=$((excluded_total + c))
    fi
  done < <(find "$ROOT" -type d -name "$d" -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | head -n 20)
done
[ "$excluded_total" -eq 0 ] && echo "   none"

echo
echo "-- File names containing the term (files only, not parent directories)"
names=$(find "$ROOT" \( "${FIND_PRUNE[@]}" -false \) -prune -o -type f \
  \( -iname "*${FLAT}*" -o -iname "*${KEBAB}*" -o -iname "*${SNAKE}*" \) \
  -print 2>/dev/null | head -n 30)
if [ -z "$names" ]; then
  echo "   none"
else
  printf '%s\n' "$names" | sed 's/^/   /'
fi

echo
echo "-- Directory names containing the term"
# -mindepth 1 excludes the search root itself. Without it, `find` reports the
# starting directory whenever ITS OWN name contains the term, so the result
# would depend on how the path was typed (site-catalog vs . from inside it).
dnames=$(find "$ROOT" -mindepth 1 \( "${FIND_PRUNE[@]}" -false \) -prune -o -type d \
  \( -iname "*${FLAT}*" -o -iname "*${KEBAB}*" -o -iname "*${SNAKE}*" \) \
  -print 2>/dev/null | head -n 30)
if [ -z "$dnames" ]; then
  echo "   none"
else
  printf '%s\n' "$dnames" | sed 's/^/   /'
fi

# A total of zero is ambiguous: the concept may be absent, or the phrase may
# simply not match how the code spells it (e.g. "max projects" will NOT match
# MAX_FREE_PROJECTS because of the word in the middle). Never let a silent zero
# read as "nothing else to change".
TOTAL=$(search "$LOOSE" ci | wc -l | tr -d ' ')
if [ "${TOTAL:-0}" -eq 0 ]; then
  echo
  echo "!! ZERO MATCHES for \"$TERM_IN\". This does NOT prove nothing else needs"
  echo "!! changing. The phrase may not match how the code spells it. Try a single"
  echo "!! distinctive word, a literal value, or the identifier itself, and search"
  echo "!! for related words that could sit between or around your terms."
fi

echo
echo "Tip: also check by hand for things a text search cannot see: URLs that"
echo "are built from parts, DB column names in migrations, i18n keys, and"
echo "generated or minified files. See references/variant-patterns.md."
