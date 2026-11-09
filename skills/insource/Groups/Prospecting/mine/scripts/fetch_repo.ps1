<#
.SYNOPSIS
    fetch_repo.ps1 — clone or verify a GitHub repository for /mine.
    Windows/PowerShell counterpart to scripts/fetch_repo.sh — same flags,
    same exit codes, same JSON output shape. Use whichever matches the
    shell actually available in this environment.

.DESCRIPTION
    Two modes:
      Verify only  (-Verify):  confirm a repo exists and is reachable,
                                without cloning it. Used while building the
                                source plan (Phase 1), so a candidate can
                                be marked verified/not-found in the plan
                                table before the user approves it and
                                before any real clone cost is paid.
      Clone        (default):  actually clone the repo to a destination
                                directory. Used during mining (Phase 2),
                                once a candidate is on the approved plan.

    Output is a single line of JSON on stdout in all cases, so the calling
    agent can parse the result programmatically instead of screen-scraping
    git's own text output. Human-readable progress/errors go to stderr.

.PARAMETER Verify
    Only check the repo exists/is reachable. No clone.

.PARAMETER Dest
    Destination directory to clone into. Required unless -Verify is
    passed. Created if it doesn't exist. If it already exists and is
    non-empty, fails rather than overwriting — pass a fresh path or
    remove it first.

.PARAMETER Depth
    Shallow-clone depth (default: 1 — this skill mines structure and
    history-as-evidence via targeted lookups, not a full clone; pass a
    larger -Depth, or -Depth 0 for a full clone, only when full commit
    history is specifically needed).

.PARAMETER Branch
    Clone a specific branch instead of the repo's default.

.PARAMETER RepoUrl
    The repository URL. Positional — pass it last, unquoted flags aside.

.EXAMPLE
    ./fetch_repo.ps1 -Verify https://github.com/zed-industries/zed

.EXAMPLE
    ./fetch_repo.ps1 -Dest C:\mine-work\zed https://github.com/zed-industries/zed

.EXAMPLE
    ./fetch_repo.ps1 -Dest C:\mine-work\zed -Depth 50 https://github.com/zed-industries/zed

.NOTES
    Exit codes (identical to fetch_repo.sh):
      0  success (repo verified reachable, or clone succeeded)
      1  repo not reachable / doesn't exist (404, DNS failure, etc.)
      2  usage error (bad flags, missing required argument)
      3  destination conflict (-Dest path exists and is non-empty)
      4  clone command failed for a reason other than repo-not-found
         (network failure, auth wall on a private repo, disk full, etc.)
#>

[CmdletBinding()]
param(
    [switch]$Verify,
    [string]$Dest,
    [int]$Depth = 1,
    [string]$Branch,
    [Parameter(Position = 0)]
    [string]$RepoUrl
)

$ErrorActionPreference = "Stop"

function Write-ResultJson {
    param(
        [string]$Status,
        [string]$RepoUrlValue,
        [string]$DestValue,
        [string]$Message
    )
    $obj = [ordered]@{
        status   = $Status
        repo_url = $RepoUrlValue
        dest     = if ($DestValue) { $DestValue } else { $null }
        message  = $Message
    }
    # ConvertTo-Json handles all escaping correctly (unlike hand-rolled
    # string escaping) and -Compress keeps it to the single line the
    # calling agent expects to parse.
    $obj | ConvertTo-Json -Compress
}

function Exit-WithError {
    param(
        [int]$Code,
        [string]$Status,
        [string]$Message
    )
    Write-ResultJson -Status $Status -RepoUrlValue $RepoUrl -DestValue $Dest -Message $Message
    exit $Code
}

# --- Usage validation -------------------------------------------------------

if (-not $RepoUrl) {
    Exit-WithError -Code 2 -Status "usage_error" -Message "Missing required repo URL argument"
}

if (-not $Verify -and -not $Dest) {
    Exit-WithError -Code 2 -Status "usage_error" -Message "-Dest is required unless -Verify is passed"
}

# --- Verify mode -------------------------------------------------------------

if ($Verify) {
    # git ls-remote hits the remote without cloning anything locally — the
    # correct way to answer "does this repo exist and is it reachable" for
    # the plan-building phase, where N candidates need checking cheaply
    # before any of them are actually cloned.
    & git ls-remote --exit-code $RepoUrl *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-ResultJson -Status "verified" -RepoUrlValue $RepoUrl -DestValue "" -Message "Repository exists and is reachable."
        exit 0
    } else {
        Exit-WithError -Code 1 -Status "not_found" -Message "Repository is not reachable — it may not exist, may be private, or the URL may be wrong. Try fetching the URL directly to distinguish a 404 from a network issue before excluding this candidate."
    }
}

# --- Clone mode ----------------------------------------------------------

if (Test-Path -LiteralPath $Dest) {
    $existingItems = Get-ChildItem -LiteralPath $Dest -Force -ErrorAction SilentlyContinue
    if ($existingItems) {
        Exit-WithError -Code 3 -Status "dest_conflict" -Message "Destination '$Dest' already exists and is not empty. Choose a fresh path or remove it first — this script never overwrites an existing non-empty destination."
    }
    # empty existing directory is fine, clone will use it
}

$parentDir = Split-Path -Parent $Dest
if ($parentDir -and -not (Test-Path -LiteralPath $parentDir)) {
    New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
}

$cloneArgs = @("clone")
if ($Depth -gt 0) {
    $cloneArgs += @("--depth", "$Depth")
}
if ($Branch) {
    $cloneArgs += @("--branch", $Branch, "--single-branch")
}
$cloneArgs += @($RepoUrl, $Dest)

Write-Host "Cloning $RepoUrl -> $Dest ..." -ForegroundColor Gray | Out-Host
[Console]::Error.WriteLine("Cloning $RepoUrl -> $Dest ...")

$stderrFile = [System.IO.Path]::GetTempFileName()
try {
    & git @cloneArgs 2> $stderrFile
    $cloneExitCode = $LASTEXITCODE
    $cloneStderr = Get-Content -LiteralPath $stderrFile -Raw -ErrorAction SilentlyContinue

    if ($cloneExitCode -eq 0) {
        Write-ResultJson -Status "cloned" -RepoUrlValue $RepoUrl -DestValue $Dest -Message "Repository cloned successfully."
        exit 0
    } else {
        # Distinguish "repo doesn't exist" from other failures where
        # possible, since the caller (the mining agent) should handle
        # these differently — a not-found repo means swap the candidate;
        # a network/auth failure on a real private repo means retry or
        # ask the user, not assume the candidate is bad. Note: in some
        # sandboxed/credential-less environments, a genuinely nonexistent
        # repo can surface as a credential prompt failure rather than a
        # clean 404 — treat that pattern as not-found too, since a real
        # private repo would need credentials supplied up front anyway
        # and this script doesn't support that.
        $notFoundPattern = "not found|does not exist|repository not found|could not read username|could not read password|terminal prompts disabled|authentication failed"
        if ($cloneStderr -match $notFoundPattern) {
            Exit-WithError -Code 1 -Status "not_found" -Message "Repository does not exist or is not accessible without credentials this script doesn't supply: $cloneStderr"
        } else {
            Exit-WithError -Code 4 -Status "clone_failed" -Message "Clone failed for a reason other than repo-not-found: $cloneStderr"
        }
    }
} finally {
    Remove-Item -LiteralPath $stderrFile -ErrorAction SilentlyContinue
}
