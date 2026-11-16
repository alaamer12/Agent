# High-yield source families (spawn many from a few)

- **Placeholder generators**: placehold.co, placehold.jp, dummyimage — accept
  `/WxH/fg/bg`, return png/svg. Reliable, controllable.
- **Random-photo CDNs**: picsum (`/seed/x`, `?grayscale`), gstatic webp gallery
  (`/1..4`), random.imagecdn.app.
- **Big content CDNs with predictable paths** (need a real id): images.pexels,
  cdn.pixabay, images.unsplash, upload.wikimedia (+ `Special:FilePath` by name).
- **Animals**: cataas, placebear, placedog.net, place.dog, cdn2.thecatapi.
- **Screenshots of arbitrary URLs**: thum.io, s0.wp.com/mshots.
- **GitHub image CDN trio** (all distinct hosts, stable): raw.githubusercontent,
  cdn.jsdelivr.net/gh/…, opengraph.githubassets.com/1/<owner>/<repo>.
- **Public-domain**: NASA `images-assets.nasa.gov` (`~small.jpg`), Internet
  Archive (`/download/<item>/<file>`), Wikimedia.
- **Media test files** (video/audio): test-videos.co.uk, w3schools,
  mdn.github.io/shared-assets, vjs.zencdn.net, download.blender.org,
  filesamples.com, actions.google.com/sounds (`media.w3.org` went 403 at the
  2026-10-26 re-check — it is a graveyard row now).
- **Avatars (distinct providers)**: api.dicebear, robohash, ui-avatars,
  i.pravatar.cc, gravatar, randomuser.me/api/portraits,
  avatars.githubusercontent.com, seccdn.libravatar.org, avataaars.io,
  cdn.discordapp.com/embed/avatars.
- **Brand logos (distinct providers)**: simple-icons, gilbarbara/logos,
  vectorlogo.zone, cdn.worldvectorlogo.com, yceballost/logotypes (repo only),
  @lobehub/icons-static-{svg,png}, Iconify sets (`thesvg-color`, `cib`, `bxl`,
  `logos`, `arcticons`, `streamline-logos`), icon-font npm paths
  (`remixicon/icons/Logos/`, `@tabler/icons/icons/outline/brand-*`,
  `@fortawesome/.../svgs/brands/`, `boxicons/svg/logos/bxl-*`), Commons, and the
  keyless domain APIs (google s2 `sz=256`, icon.horse, icons.duckduckgo.com/ip3,
  unavatar `?fallback=false`). See [brand-logos.md](brand-logos.md) for how to
  resolve their names; Clearbit/logo.dev/Brandfetch are all dead or token-gated.

## Practical gotchas learned

- Some sites block a browser-style User-Agent (GitHub gtv bucket 403s here but
  works in a real browser); others 403 with *no* UA. Try both before deciding.
- Wikimedia `/thumb/…/<W>px-…` only allows a fixed width set → 400 otherwise.
  Use the original full-size file or `Special:FilePath`.
- `filesamples.com` and `file-examples.com` are **different** sites; only the
  first serves direct files.
- Under heavy parallel load even good hosts (media.w3.org) rate-limit; confirm
  an individual failure with a single request before removing it.
- Keep TLS verification ON in anything shipped. A throwaway probe MAY relax it,
  but never ship a verifier that disables cert checks.
