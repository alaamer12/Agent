# Version Bump Procedure

Policy lives in AGENTS.md section 20; this file is the file-by-file checklist only.

External bump (release cut, explicit user request only):
1. Decide the kind from the written table (MAJOR = billing-model breaking, MINOR = additive
   feature, PATCH = fix); if no row fits, stop and ask.
2. Update `pyproject.toml` and `package.json` to the new version.
3. Confirm the About page still reads the runtime value (never hardcode).
4. Add the `CHANGELOG.md` entry (Keep a Changelog format, user-facing voice).
5. Ask the user before creating the `v<version>` tag or pushing anything.

Internal bump (every merge into `beta`, mechanical):
1. Increment the integer in `services/api/build.py` by exactly one; never repeat or decrement.
