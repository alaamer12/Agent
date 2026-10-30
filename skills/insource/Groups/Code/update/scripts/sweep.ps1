<#
.SYNOPSIS
    sweep.ps1 - find every form of a term across a codebase.

.DESCRIPTION
    Plain search for "catalog" misses catalog__item, catalogService, CATALOG_URL,
    and file names. This script generates the naming-convention variants and
    reports hits grouped by variant, plus matching file and directory names.

    PowerShell port of sweep.sh. Same variants, same output shape, same exit codes.

    Read-only. Never modifies files.

    Requirements: PowerShell 5.1 or later (Windows PowerShell or PowerShell 7+,
    on Windows, macOS, or Linux). No external tools needed: it does not use grep,
    ripgrep, or find.

    Language-agnostic by design: it generates the naming variants used across
    ecosystems (snake_case in Python/Rust/Ruby/SQL, camelCase in Java/Go/JS,
    PascalCase in C#/Go/Java types, SCREAMING_CASE for constants, kebab-case in
    URLs/CSS/CLI flags) plus a separator-tolerant catch-all. The variant list is a
    starting point, not an exhaustive set: if your stack spells things another way
    (for example dotted i18n keys, Train-Case headers), search for that spelling too.

.PARAMETER Term
    The word or phrase being changed, in any casing ("user profile", "userProfile").

.PARAMETER Path
    Directory to search. Defaults to the current directory.

.PARAMETER Count
    Print only per-variant counts, without sample lines.

.EXAMPLE
    ./sweep.ps1 catalog
.EXAMPLE
    ./sweep.ps1 "user profile" ./src
.EXAMPLE
    ./sweep.ps1 catalog . -Count

.NOTES
    Exit codes: 0 = ran, 2 = bad input (missing path or unsearchable term).
    Extend the excluded directories with the SWEEP_EXCLUDE environment variable
    (comma separated), for example:  $env:SWEEP_EXCLUDE = "generated,third_party"

    Known limitation shared with sweep.sh: files containing NUL bytes are treated
    as binary and skipped, which includes UTF-16 encoded text files.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Term,

    [Parameter(Position = 1)]
    [string]$Path = '.',

    [switch]$Count,

    [Alias('h')]
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help -or [string]::IsNullOrWhiteSpace($Term)) {
    Get-Help $MyInvocation.MyCommand.Path -Full | Out-String | Write-Output
    exit 0
}

if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
    [Console]::Error.WriteLine("error: path not found: $Path")
    exit 2
}

# ---------------------------------------------------------------------------
# Split the term into lowercase words. "User Profile", "user-profile",
# "user_profile", and "userProfile" all become: user profile
# ---------------------------------------------------------------------------
$spaced = [regex]::Replace($Term, '([a-z0-9])([A-Z])', '$1 $2')
$spaced = $spaced.ToLowerInvariant()
$spaced = [regex]::Replace($spaced, '[^a-z0-9]+', ' ').Trim()

if ([string]::IsNullOrEmpty($spaced)) {
    [Console]::Error.WriteLine('error: term contains no searchable characters')
    exit 2
}
[string[]]$wordList = $spaced -split ' '

# ---------------------------------------------------------------------------
# Naming-convention builders. Each takes a word array so the plural forms can
# reuse them.
# ---------------------------------------------------------------------------
function ConvertTo-Cap([string]$w) {
    if ($w.Length -eq 0) { return $w }
    return $w.Substring(0, 1).ToUpperInvariant() + $w.Substring(1)
}
function Join-Words([string[]]$ws, [string]$sep) { return ($ws -join $sep) }
function ConvertTo-CamelCase([string[]]$ws) {
    $out = $ws[0]
    for ($i = 1; $i -lt $ws.Count; $i++) { $out += (ConvertTo-Cap $ws[$i]) }
    return $out
}
function ConvertTo-PascalCase([string[]]$ws) {
    $out = ''
    foreach ($w in $ws) { $out += (ConvertTo-Cap $w) }
    return $out
}

$KEBAB  = Join-Words $wordList '-'
$SNAKE  = Join-Words $wordList '_'
$FLAT   = Join-Words $wordList ''
$CAMEL  = ConvertTo-CamelCase $wordList
$PASCAL = ConvertTo-PascalCase $wordList
$SCREAM = $SNAKE.ToUpperInvariant()
$SPACED = $spaced

# ---------------------------------------------------------------------------
# Plurals are a common miss (catalog -> catalogs, category -> categories).
# Only pluralise the last word. If it already looks plural, the user typed the
# plural form, so do not pluralise it again ("projectses").
# ---------------------------------------------------------------------------
$last = $wordList[$wordList.Count - 1]
$headWords = @()
if ($wordList.Count -gt 1) { $headWords = $wordList[0..($wordList.Count - 2)] }

$alreadyPlural = $false
if ($last -match 'ies$') {
    $alreadyPlural = $true;  $pluralLast = $last
}
elseif ($last -match '(ss|us|is)$') {
    # class, status, analysis: these end in "s" but are singular
    $pluralLast = $last + 'es'
}
elseif ($last -match 's$') {
    $alreadyPlural = $true;  $pluralLast = $last
}
elseif ($last -match '[^aeiou]y$') {
    $pluralLast = $last.Substring(0, $last.Length - 1) + 'ies'
}
elseif ($last -match '(x|z|ch|sh)$') {
    $pluralLast = $last + 'es'
}
else {
    $pluralLast = $last + 's'
}

# Ecosystems disagree on which convention they use for collections
# (Go: orderStatuses, Rust: order_statuses, C#: OrderStatuses).
[string[]]$pluralWords = @($headWords) + @($pluralLast)
$PLURAL_SNAKE  = Join-Words $pluralWords '_'
$PLURAL_KEBAB  = Join-Words $pluralWords '-'
$PLURAL_CAMEL  = ConvertTo-CamelCase $pluralWords
$PLURAL_PASCAL = ConvertTo-PascalCase $pluralWords

# ---------------------------------------------------------------------------
# Directories that are noise. Extend via SWEEP_EXCLUDE (comma separated).
# Build output, dependency caches, and VCS metadata across common ecosystems.
# Illustrative, not exhaustive: extend with SWEEP_EXCLUDE for your stack.
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
# ---------------------------------------------------------------------------
$excludeList = @(
    'node_modules', 'dist', 'build', '.next', '.nuxt', '.turbo', '.svelte-kit', 'coverage',
    '__pycache__', '.venv', 'venv', '.tox', '.mypy_cache', '.pytest_cache',
    'target', '.gradle', '.mvn', 'out', 'bin', 'obj', 'vendor',
    '_build', 'deps', 'Pods', 'DerivedData', '.build', '.dart_tool',
    '.stack-work', 'dist-newstyle', '.terraform', '.git', '.cache'
)
if (-not [string]::IsNullOrEmpty($env:SWEEP_EXCLUDE)) {
    $excludeList += ($env:SWEEP_EXCLUDE -split ',' | Where-Object { $_ -ne '' })
}
# Directory names compare case-insensitively on Windows and macOS default volumes.
$excludeSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
foreach ($e in $excludeList) { [void]$excludeSet.Add($e) }

# ---------------------------------------------------------------------------
# File enumeration.
#
# Get-ChildItem -Exclude filters leaf names only and still descends into an
# excluded directory, so the tree is walked manually and excluded directories
# are pruned without being entered.
# ---------------------------------------------------------------------------
$rootFull = (Resolve-Path -LiteralPath $Path).ProviderPath

# grep and find print paths prefixed with the path exactly as the user typed it
# ("site-catalog/src/a.js", "./src/a.js"). Do the same, so output matches
# sweep.sh instead of showing long absolute paths.
$rootPrefix = $Path.TrimEnd('/', '\')
function Format-DisplayPath([string]$full) {
    if ($full.Length -le $rootFull.Length) { return $rootPrefix }
    $rel = $full.Substring($rootFull.Length).TrimStart('/', '\')
    return ($rootPrefix + '/' + ($rel -replace '\\', '/'))
}

function Get-PrunedEntries {
    # Emits every file and directory under $Root, never entering an excluded
    # directory. Does not follow directory symlinks/junctions (avoids cycles).
    # Output objects: @{ Path; Name; IsDir }
    param([string]$Root, [System.Collections.Generic.HashSet[string]]$Skip)

    $stack = New-Object 'System.Collections.Generic.Stack[string]'
    $stack.Push($Root)
    while ($stack.Count -gt 0) {
        $dir = $stack.Pop()
        try { $entries = [System.IO.Directory]::EnumerateFileSystemEntries($dir) }
        catch { continue }   # unreadable directory: skip it, do not abort the sweep
        foreach ($entry in $entries) {
            $name = [System.IO.Path]::GetFileName($entry)
            $isDir = [System.IO.Directory]::Exists($entry)
            if ($isDir) {
                $isReparse = $false
                try {
                    $attrs = [System.IO.File]::GetAttributes($entry)
                    $isReparse = (($attrs -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
                } catch { }
                [pscustomobject]@{ Path = $entry; Name = $name; IsDir = $true }
                if (-not $isReparse -and -not $Skip.Contains($name)) { $stack.Push($entry) }
            }
            else {
                [pscustomobject]@{ Path = $entry; Name = $name; IsDir = $false }
            }
        }
    }
}

# grep -I treats a file as binary when it contains a NUL byte in its first
# block. Do the same, so binary blobs never inflate the counts.
function Test-BinaryFile([string]$p) {
    try {
        $fs = [System.IO.File]::OpenRead($p)
        try {
            $buf = New-Object byte[] 8192
            $n = $fs.Read($buf, 0, $buf.Length)
        }
        finally { $fs.Dispose() }
        for ($i = 0; $i -lt $n; $i++) { if ($buf[$i] -eq 0) { return $true } }
        return $false
    }
    catch { return $true }   # unreadable: treat as not searchable
}

# Materialise the searchable text files once, so each variant row does not
# re-walk the disk. Sorted (ordinal) so sample lines are reproducible from run
# to run rather than depending on the filesystem's enumeration order.
$allEntries = @(Get-PrunedEntries -Root $rootFull -Skip $excludeSet)
$textFiles  = New-Object 'System.Collections.Generic.List[string]'
foreach ($e in ($allEntries | Where-Object { -not $_.IsDir } | Sort-Object -Property Path)) {
    if (-not (Test-BinaryFile $e.Path)) { [void]$textFiles.Add($e.Path) }
}

# ---------------------------------------------------------------------------
# Search. Returns "path:line:text" strings, matching grep -rn output, so counts
# are matching LINES (one line can hold several occurrences).
#
# PowerShell regexes are case-INsensitive by default, the opposite of grep. The
# variant rows must be case-SENSITIVE or "catalog" and "Catalog" would collapse
# into one row, so options are always set explicitly.
# ---------------------------------------------------------------------------
function Search-Files {
    param(
        [string]$Pattern,
        [ValidateSet('cs', 'ci')][string]$Mode,
        [System.Collections.Generic.List[string]]$Files
    )
    $opts = [System.Text.RegularExpressions.RegexOptions]::None
    if ($Mode -eq 'ci') { $opts = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase }
    $rx = New-Object System.Text.RegularExpressions.Regex($Pattern, $opts)

    foreach ($f in $Files) {
        $lineNo = 0
        try {
            foreach ($line in [System.IO.File]::ReadLines($f)) {
                $lineNo++
                if ($rx.IsMatch($line)) { '{0}:{1}:{2}' -f (Format-DisplayPath $f), $lineNo, $line }
            }
        }
        catch { continue }   # unreadable or locked file: skip, keep sweeping
    }
}

function Write-Report {
    param([string]$Label, [string]$Pattern, [string]$Mode)
    $out = @(Search-Files -Pattern $Pattern -Mode $Mode -Files $textFiles)
    $n = $out.Count
    Write-Output ('{0,-34} {1,6} hits' -f $Label, $n)
    if (-not $Count -and $n -gt 0) {
        $out | Select-Object -First 8 | ForEach-Object { Write-Output ('      ' + $_) }
        if ($n -gt 8) { Write-Output ('      ... {0} more' -f ($n - 8)) }
    }
}

# Collapse identical patterns so a single-word term is not padded with
# duplicate rows (kebab, snake, camel, and flat are the same string).
$script:seen = New-Object 'System.Collections.Generic.HashSet[string]'
function Write-UniqueReport {
    param([string]$Label, [string]$Pattern, [string]$Mode)
    $key = $Mode + ':' + $Pattern
    if (-not $script:seen.Add($key)) { return }
    Write-Report -Label $Label -Pattern $Pattern -Mode $Mode
}

Write-Output ('== sweep: "{0}"  in  {1}' -f $Term, $Path)
Write-Output ('   words: [{0}]' -f $spaced)
Write-Output '   (counts are matching LINES, not individual occurrences; one line can hold several)'
Write-Output ''

Write-Output '-- Contents, by variant (case-sensitive so conventions stay distinguishable)'
Write-UniqueReport ('lower/kebab ({0})' -f $KEBAB)  ([regex]::Escape($KEBAB))  'cs'
Write-UniqueReport ('snake       ({0})' -f $SNAKE)  ([regex]::Escape($SNAKE))  'cs'
Write-UniqueReport ('camel       ({0})' -f $CAMEL)  ([regex]::Escape($CAMEL))  'cs'
Write-UniqueReport ('Pascal      ({0})' -f $PASCAL) ([regex]::Escape($PASCAL)) 'cs'
Write-UniqueReport ('SCREAMING   ({0})' -f $SCREAM) ([regex]::Escape($SCREAM)) 'cs'
if (-not $alreadyPlural) {
    Write-UniqueReport ('plural snake ({0})'  -f $PLURAL_SNAKE)  ([regex]::Escape($PLURAL_SNAKE))  'cs'
    Write-UniqueReport ('plural kebab ({0})'  -f $PLURAL_KEBAB)  ([regex]::Escape($PLURAL_KEBAB))  'cs'
    Write-UniqueReport ('plural camel ({0})'  -f $PLURAL_CAMEL)  ([regex]::Escape($PLURAL_CAMEL))  'cs'
    Write-UniqueReport ('plural Pascal({0})'  -f $PLURAL_PASCAL) ([regex]::Escape($PLURAL_PASCAL)) 'cs'
}
if ($SPACED -ne $KEBAB) {
    Write-UniqueReport ('spaced      ({0})' -f $SPACED) ([regex]::Escape($SPACED)) 'ci'
}

Write-Output ''
Write-Output '-- Delimiter-joined fragments (e.g. CSS BEM block__element / block--modifier; also Rails-style namespaces)'
Write-Report ('element     ({0}__*)' -f $KEBAB) ([regex]::Escape($KEBAB + '__')) 'cs'
Write-Report ('modifier    ({0}--*)' -f $KEBAB) ([regex]::Escape($KEBAB + '--')) 'cs'
Write-Report ('prefixed    (*__{0})' -f $KEBAB) ([regex]::Escape('__' + $KEBAB)) 'cs'

Write-Output ''
# Separator-tolerant, case-insensitive catch-all. For "user id" this matches
# userid, user_id, user-id, user.id, user id, UserID, USER__ID ... so it also
# finds spellings the named variants above did not anticipate.
$LOOSE = ($wordList | ForEach-Object { [regex]::Escape($_) }) -join '[-_. ]*'
Write-Output ('-- Catch-all: separator-tolerant, case-insensitive  (/{0}/i)' -f $LOOSE)
Write-Report 'any spelling' $LOOSE 'ci'

# Excluded directories are noise MOST of the time, but vendored code is exactly
# where unrelated look-alikes live (a third-party library that uses the same
# word). Never hide that silently: count hits inside excluded dirs and say so.
Write-Output ''
Write-Output '-- Hits inside EXCLUDED directories (not counted above)'
$looseRx = New-Object System.Text.RegularExpressions.Regex($LOOSE, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
$excludedTotal = 0
$excludedDirs = @($allEntries | Where-Object { $_.IsDir -and $excludeSet.Contains($_.Name) -and
                                                 $_.Path -notmatch '[\\/]node_modules[\\/]' -and
                                                 $_.Path -notmatch '[\\/]\.git[\\/]' } |
                                 Select-Object -First 20)
foreach ($d in $excludedDirs) {
    $c = 0
    # Walk this excluded directory fully (no pruning) so its contents are counted.
    $none = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($inner in (Get-PrunedEntries -Root $d.Path -Skip $none)) {
        if ($inner.IsDir) { continue }
        if (Test-BinaryFile $inner.Path) { continue }
        try {
            foreach ($line in [System.IO.File]::ReadLines($inner.Path)) {
                if ($looseRx.IsMatch($line)) { $c++ }
            }
        } catch { }
    }
    if ($c -gt 0) {
        Write-Output ('   {0,-40} {1,6} hits  <- review: possible look-alike or generated output' -f (Format-DisplayPath $d.Path), $c)
        $excludedTotal += $c
    }
}
if ($excludedTotal -eq 0) { Write-Output '   none' }

# ---------------------------------------------------------------------------
# File and directory names containing the term.
# -mindepth-1 equivalent: the search root itself is never reported, even when
# its own name contains the term, so the result does not depend on how the
# path was typed ("site-catalog" vs "." from inside it).
# ---------------------------------------------------------------------------
function Test-NameMatch([string]$name) {
    $lower = $name.ToLowerInvariant()
    return ($lower.Contains($FLAT) -or $lower.Contains($KEBAB) -or $lower.Contains($SNAKE))
}

Write-Output ''
Write-Output '-- File names containing the term (files only, not parent directories)'
$fnames = @($allEntries | Where-Object { -not $_.IsDir -and (Test-NameMatch $_.Name) } |
                          Sort-Object Path | Select-Object -First 30)
if ($fnames.Count -eq 0) { Write-Output '   none' }
else { $fnames | ForEach-Object { Write-Output ('   ' + (Format-DisplayPath $_.Path)) } }

Write-Output ''
Write-Output '-- Directory names containing the term'
# Excluded directories are pruned in the sh version too, so skip them here.
# The root itself is excluded from $allEntries by construction (EnumerateFileSystemEntries
# starts one level below $rootFull), so no extra check is needed for that case.
$dnames = @($allEntries | Where-Object { $_.IsDir -and -not $excludeSet.Contains($_.Name) -and (Test-NameMatch $_.Name) } |
                          Sort-Object Path | Select-Object -First 30)
if ($dnames.Count -eq 0) { Write-Output '   none' }
else { $dnames | ForEach-Object { Write-Output ('   ' + (Format-DisplayPath $_.Path)) } }

# ---------------------------------------------------------------------------
# A total of zero is ambiguous: the concept may be absent, or the phrase may
# simply not match how the code spells it (for example "max projects" will NOT
# match MAX_FREE_PROJECTS because of the word in the middle). Never let a silent
# zero read as "nothing else to change".
# ---------------------------------------------------------------------------
$total = @(Search-Files -Pattern $LOOSE -Mode 'ci' -Files $textFiles).Count
if ($total -eq 0) {
    Write-Output ''
    Write-Output ('!! ZERO MATCHES for "{0}". This does NOT prove nothing else needs' -f $Term)
    Write-Output '!! changing. The phrase may not match how the code spells it. Try a single'
    Write-Output '!! distinctive word, a literal value, or the identifier itself, and search'
    Write-Output '!! for related words that could sit between or around your terms.'
}

Write-Output ''
Write-Output 'Tip: also check by hand for things a text search cannot see: URLs that'
Write-Output 'are built from parts, DB column names in migrations, i18n keys, and'
Write-Output 'generated or minified files. See references/variant-patterns.md.'
