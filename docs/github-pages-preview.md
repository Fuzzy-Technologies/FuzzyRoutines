<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# GitHub Pages preview

The FuzzyRoutines product page is a static site in `docs/`. It does not require Jekyll, Node.js, a CDN, or external runtime assets.

## Local preview

From the repository root:

```console
python -m http.server 8000 --directory docs
```

Open <http://localhost:8000/> and check the desktop and narrow/mobile layouts.

Run the deterministic site checks with:

```console
python -m pytest tests/test_pages_site.py
```

The checks verify required metadata, local files, same-page fragments, HTTPS-only external links, and the absence of runtime script dependencies.

## Publication boundary

This task prepares and validates the site on `develop`. It does not enable GitHub Pages or change repository settings. Publication remains a separate reviewed operation after the site reaches `master`.
