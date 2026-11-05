# How to develop in this project

- Branch model: `main` = released code - every push to main runs the release pipeline and publishes
  to PyPI + the web host. `beta` = integration - all feature work merges here first; nightly
  builds deploy to staging `beta.tidepool.dev`. Feature branches `feat/<slug>` branch off `beta`.
- Where work lands: implement on `feat/<slug>`, merge to `beta`; `beta` -> `main` is a release
  decision the user drives - every outward step is section 14's ask tier, never this section's data.
- Versioning means only this here: a branch has version consequences - scheme, bump rule, sites,
  attachments belong to section 17, never restated in this section.

### 3.1 What `main` means operationally

- Recognized in tree: the only branch whose pushes publish (PyPI + web host); release tags point at
  it (section 17.4). The agent never commits on it; merges and pushes need an explicit order.

### 3.2 What `beta` means operationally

- Recognized at runtime: a deploy labeled `beta` on `beta.tidepool.dev`. The agent may commit
  locally here per section 14; every merge into beta moves a version number - what moves and where:
  section 17.

### 3.3 What `feat/<slug>` means operationally

- Recognized by name: slug-named, branched from `beta`. The same slug is reused in stash names and
  decision records so work-in-progress is attributable (sections 14, 17).
