<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# GitHub Pages preview

The FuzzyRoutines product page is a static site in `docs/`. It does not require Jekyll, Node.js, a CDN, or external runtime assets. The generated API reference uses the version-pinned MathJax browser asset selected by ADR-0010; API generation itself remains reproducible after dependencies are provisioned.

## Local preview

The product page shares fonts, illustration assets and the image viewer with
the generated API reference. Build and serve the complete deployment tree
below so the local preview matches production.

Run the deterministic site checks with:

```console
python -m pytest tests/test_pages_site.py tests/test_pages_publication.py
```

The checks verify required metadata, local files, same-page fragments, HTTPS-only external links, locale publication and fallback boundaries, version navigation, and the publication boundary.

To preview the complete deployment artifact, first build the strict installed-package API reference and then compose the Pages tree:

```console
python tools/build_api_reference.py
python tools/compose_pages_site.py --locale-root _build/api-reference/locales
python -m http.server 8000 --directory _build/pages/site
```

The complete routes are:

- `/` for the product overview;
- `/api/latest/en/` for the canonical English reference;
- `/api/latest/ru/` and `/api/latest/zh-CN/` for reviewed Russian and Simplified Chinese references;
- `/api/versions/` for the current package version and tagged documentation sources.

## Publication boundary

Pull requests and pushes to `develop` build both a downloadable preview and the official Pages artifact without deploying it. The deployment job has `pages: write` and OpenID Connect permissions, but its fail-closed condition permits production publication only for a push to `master`. Package publication is a separate workflow and is neither required nor triggered by documentation deployment.

The repository owner must select **GitHub Actions** as the Pages source once. Thereafter the workflow publishes to <https://fuzzy-technologies.github.io/FuzzyRoutines/> when an approved documentation change reaches `master`.
