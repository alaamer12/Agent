<#
.SYNOPSIS
  Turn on (or inspect / remove) Windows Error Reporting LocalDumps for ONE executable, so the next fatal crash leaves a
  dump that can answer the questions the `fatal` skill asks.
.DESCRIPTION
  Writes HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\<ExeName>. Needs an elevated PowerShell.
  Supports -WhatIf. Touches only the per-exe subkey.
  Why DumpType 2 (full) by default for investigations: a MINI dump holds stacks + modules but usually NOT the heap. In the
  DemoApp case the stowed-exception pointer (inner HRESULT of a 0xC000027B fail-fast) was 'not in any captured memory range',
  so the fact that would have named the inner error was unrecoverable. Full dumps are big (hundreds of MB for .NET/WinUI) -
  keep DumpCount low and return to -DumpType 1 or -Remove when finished.
.EXAMPLE
  .\enable_crash_dumps.ps1 -ExeName MyApp.exe
  .\enable_crash_dumps.ps1 -ExeName MyApp.exe -DumpFolder D:\dumps -DumpCount 3 -WhatIf
  .\enable_crash_dumps.ps1 -ExeName MyApp.exe -Show
  .\enable_crash_dumps.ps1 -ExeName MyApp.exe -Remove
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [Parameter(Mandatory = $true)][string]$ExeName,
  [string]$DumpFolder = '%LOCALAPPDATA%\CrashDumps',
  [ValidateSet(1, 2)][int]$DumpType = 2,
  [ValidateRange(1, 100)][int]$DumpCount = 5,
  [switch]$Show,
  [switch]$Remove
)
$root = 'HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps'
$key  = Join-Path $root $ExeName
function Test-Admin {
  $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
  return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
if ($Show) {
  foreach ($k in @($root, $key)) {
    if (Test-Path $k) { Write-Host "== $k"; Get-ItemProperty $k | Format-List DumpFolder, DumpCount, DumpType } else { Write-Host "(absent) $k" }
  }
  Get-ChildItem ([Environment]::ExpandEnvironmentVariables($DumpFolder)) -Filter *.dmp -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 10 Name, Length, LastWriteTime | Format-Table -AutoSize
  return
}
if (-not (Test-Admin)) { throw 'Run from an elevated (Administrator) PowerShell: HKLM is being modified.' }
if ($Remove) {
  if (Test-Path $key) { if ($PSCmdlet.ShouldProcess($key, 'Remove per-exe LocalDumps key')) { Remove-Item $key -Recurse -Force; Write-Host "Removed $key" } }
  else { Write-Host "Nothing to remove: $key" }
  return
}
if ($PSCmdlet.ShouldProcess($key, "Enable LocalDumps (type=$DumpType, count=$DumpCount, folder=$DumpFolder)")) {
  New-Item -Path $key -Force | Out-Null
  New-ItemProperty -Path $key -Name DumpFolder -PropertyType ExpandString -Value $DumpFolder -Force | Out-Null
  New-ItemProperty -Path $key -Name DumpCount  -PropertyType DWord        -Value $DumpCount  -Force | Out-Null
  New-ItemProperty -Path $key -Name DumpType   -PropertyType DWord        -Value $DumpType   -Force | Out-Null
  $f = [Environment]::ExpandEnvironmentVariables($DumpFolder)
  if (-not (Test-Path $f)) { New-Item -ItemType Directory -Path $f -Force | Out-Null }
  Write-Host "LocalDumps enabled for $ExeName -> $f (type $DumpType, keep $DumpCount). Applies to the NEXT crash of a freshly started process. Verify: -Show"
  if ($DumpType -eq 2) { Write-Host 'Full dumps are large; use -DumpType 1 or -Remove when finished.' }
}
