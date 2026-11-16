# Documents (PDF books) — the rights gate comes first

For documents, "can I fetch the bytes" is the *easy* half. A PDF is only a
passing source if the **rights holder released it**. So run the gate before the
verifier, not after:

- Accept: CC / GFDL / public-domain / BSD-licensed full texts, and official
  author-or-publisher-hosted free downloads (MIT Press, Stanford, UPenn,
  `greenteapress.com`, `opendatastructures.org`, releases in the author's own
  repo).
- Refuse: lending-library or `/Encrypt`-ed items, DRM-stripped files, and any
  copy of a commercially-sold title. There is no legal free full-text PDF of
  Clean Code, Code Complete, Refactoring, The Pragmatic Programmer, CLRS, or K&R
  — so "found it on a GitHub repo / Archive item" is a red flag, not a win.
- A CC `LICENSE` file in a repo does **not** prove the repo holds the rights to
  what it contains (translations and link-dumps of paid books look CC-licensed).
  Check the copyright page inside the PDF itself.
- A refusal is catalog material too: write it as `status=refuse` so the next hunt
  does not rediscover the same tempting-looking upload.

Three harvest routes, in yield order — all license-gated:

```bash
# 1. GitHub: verify license, then list every PDF in the tree + release assets
echo "progit/progit2" | python scripts/gh_tree_pdfs.py | \
  python scripts/verify_sources.py pdf

# 2. Internet Archive: metadata-gated (skips access-restricted / no-license items)
python scripts/ia_open_pdfs.py 'mediatype:texts AND description:"creative commons"' 20 | \
  python scripts/verify_sources.py pdf

# 3. Landing pages: never guess a filename — harvest the page's own hrefs
python scripts/harvest_pdfs.py < pages.txt | python scripts/verify_sources.py pdf
```

`verify_sources.py pdf` checks `%PDF-` magic **and** a real `%%EOF` trailer,
because release assets serve `application/octet-stream` (Content-Type lies) and
"free book" hosts happily return `200` + HTML. Then run
`scripts/pdf_identity.py <dir>` to prove what is on disk: it inflates the object
streams and prints page `/Count`, `/Title`, and a first-page text fingerprint —
which is how you catch the 1.1 MB "book" that is really a sample chapter.

Write each proven book as `catalog.py add --category document --kind pdf
--rights <cc-by|gfdl|…> --coverage '<MB>, <N> pp' --notes '<the licence and where
it is hosted>'`; `coverage` holds the size and the poppler page count, because
"it fetched" is not what makes it a book.
