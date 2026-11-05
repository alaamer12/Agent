# How to run things

- **Shell / build:** use the `dotnet` CLI. On this Windows dev box prefer `cmd` chaining - the
  PowerShell profile hangs the MAUI workload restore.
- **Chaining:** one command at a time while investigating; avoid `&&`/pipes unless a build step truly
  needs it.
- **Complex commands:** write a throwaway script under `scratch/`, run it, delete when finished
  (`scratch/` is gitignored - section 7).
- **Package manager / toolchain:** `dotnet` for build/run/test and NuGet via `dotnet add package` -
  the single toolchain; no other package manager touches this repo.
- **Verification commands:** `dotnet build` (warnings gate, section 17); `dotnet test` for unit and
  integration; `dotnet workload ...` only when a target is genuinely missing.
