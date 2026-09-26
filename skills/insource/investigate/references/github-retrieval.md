# GitHub Retrieval

Use this reference whenever the target Skill is hosted in a public GitHub repository.

## Preferred retrieval model

Use web search/browsing to discover the repository and exact Skill path.

Once the path is known, retrieve file contents directly from GitHub's raw endpoint.

Typical raw URL:

    https://raw.githubusercontent.com/OWNER/REPOSITORY/BRANCH/PATH

Preferred Python:

    import requests

    r = requests.get(raw_url, timeout=30)
    r.raise_for_status()
    text = r.text

For binary files, use `r.content` instead of `r.text`.

## Why direct retrieval

Search results can truncate or summarize file contents. A complete HTTP response provides the actual file content available at that raw URL.

Do not use a GitHub HTML `blob` page as a substitute for the raw file when complete contents are needed.

## File tree

First determine the exact Skill directory.

Then enumerate files under that directory. Preserve paths, for example:

    target-skill/
    ├── SKILL.md
    ├── references/api.md
    ├── scripts/check.py
    └── assets/template.md

Read `SKILL.md` first. Then read files it references or files required to understand its implementation.

## Version integrity

When possible, record:
- repository
- branch
- commit SHA
- source URL

A branch such as `main` can change after investigation. A commit SHA provides a stable snapshot.

If SkillsMP and GitHub appear different, report the difference rather than silently mixing versions.

## Retrieval failures

If a raw file returns an error:
- verify owner/repository/branch/path
- check whether the file moved
- check repository visibility
- try the GitHub source page for discovery
- do not fabricate missing content

For private repositories, do not attempt to bypass access controls.
