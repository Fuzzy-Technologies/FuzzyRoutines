# API Documentation Comparison Evidence

## Evaluation identity

```text
Date:            2026-09-16
Source revision: bb83748afb31176ac338eb4fe638a5470feb5122
Python:          CPython 3.14.7
Primary module:  fuzzyroutines.fuzzysets
Type dependency: fuzzyroutines.domain
```

Every candidate ran in a separate virtual environment. The build process set
`PYTHONPROFILEIMPORTTIME=1`; the evaluator then inspected the build log for a
runtime import of `fuzzyroutines.fuzzysets`. All generated-output checks were
performed against actual HTML and search/inventory artifacts.

## Evaluated versions

- pdoc 16.0.0;
- MkDocs 1.6.1;
- Material for MkDocs 9.7.7;
- mkdocstrings 1.0.6;
- mkdocstrings-python 2.0.8;
- griffelib 2.3.0;
- PyMdown Extensions 12.0.1;
- Sphinx 9.1.0.

The dependency manifests pin the complete observed environments rather than
adding any package to FuzzyRoutines runtime dependencies.

## Generated evidence

| Candidate           | Build time | Files | Bytes     | Runtime project import |
|---------------------|------------|-------|-----------|------------------------|
| pdoc                | 0.361238   | 4     | 488,641   | Yes                    |
| mkdocstrings-python | 0.670812   | 55    | 2,761,004 | No                     |
| Sphinx autodoc      | 0.637847   | 28    | 356,017   | Yes                    |

Times are single-run observations for reproducibility, not performance claims.
All three builds were repeated successfully with HTTP, HTTPS, and all-protocol
proxies pointed to an unusable local endpoint. Offline-repeat times were
0.361760 seconds, 0.665601 seconds, and 0.642539 seconds respectively. A second
run also created all three environments from the pinned manifests using `uv pip
sync --offline` and completed every build and output check from the local uv
cache.

## Visual identity follow-up

The Task #233 candidate was rebuilt on 2026-09-18 from parent revision
`d52d620956d1a13b4846579d10a939923dbe0c41`, including the new product
identity assets in the working tree. Fresh, isolated CPython 3.14.7
environments used the same pinned package versions listed above.

| Candidate           | Build time | Files | Bytes     | Runtime project import |
|---------------------|------------|-------|-----------|------------------------|
| pdoc                | 0.709574   | 4     | 554,443   | Yes                    |
| mkdocstrings-python | 1.281988   | 57    | 2,790,025 | No                     |
| Sphinx autodoc      | 1.738075   | 28    | 393,652   | Yes                    |

The 57-file mkdocstrings result includes the reusable sign and horizontal
wordmark copied from tracked source; no generated HTML or raster preview is
tracked. An offline repeat reused only those provisioned environments while
all proxy protocols pointed to an unusable local endpoint. It completed in
0.382186, 0.710229, and 0.665479 seconds respectively, with identical checks
and file counts. The pdoc and mkdocstrings byte counts were identical. The
Sphinx total was 393,653 bytes because its disposable
`.doctrees/environment.pickle` differed by one byte; its rendered site files
were identical.

## Criteria matrix

| Criterion                   | pdoc                          | mkdocstrings-python                     | Sphinx autodoc               |
|-----------------------------|-------------------------------|-----------------------------------------|------------------------------|
| Type/object cross-reference | Pass within generated modules | Pass across Markdown/API pages          | Pass through Python domain   |
| Search                      | Pass; generated `search.js`   | Pass; generated local JSON index        | Pass; generated JS index     |
| Rendered mathematics        | Pass; `--math` and MathJax    | Pass; Arithmatex and pinned MathJax     | Pass; math extension         |
| Stable anchors              | Partial; short object IDs     | Pass; fully qualified object IDs        | Pass; fully qualified IDs    |
| Source access               | Pass; inline source views     | Pass; expandable source views           | Pass; generated source pages |
| Offline HTML generation     | Pass after provisioning       | Pass after provisioning                 | Pass after provisioning      |
| F-Tech theming              | Custom templates required     | Pass; Material palette and project CSS  | Theme customization required |
| Safe project discovery      | Fail; imported package        | Pass; no project-module import observed | Fail; imported module        |
| Docs-only dependencies      | Pass                          | Pass                                    | Pass                         |
| Existing Pages composition  | Static subtree possible       | Native narrative/API composition        | Static subtree possible      |

The current math spikes reference browser-time CDN assets. The offline result
above applies to HTML generation. ADR-0010 requires Task #206 to decide whether
the production output vendors MathJax for offline viewing.

## Observable output checks

Each candidate output contained:

- the real `ScalarFuzzySet` API;
- a resolvable type/object cross-reference;
- a stable target anchor for `ScalarFuzzySet`;
- a search artifact;
- a source-code link or view;
- a configured mathematics renderer.

mkdocstrings additionally produced an `objects.inv` inventory and a fully
qualified `fuzzyroutines.fuzzysets.ScalarFuzzySet` anchor without executing the
project module. That safe-discovery result is the main discriminator.

## Decision

Select MkDocs + Material + mkdocstrings-python/Griffe. Select English
Google-style docstrings with Markdown cross-references and LaTeX mathematics.
The decision is recorded in ADR-0010.

## Scope exclusions

This spike does not:

- rewrite package docstrings (Tasks #199 and #200);
- generate or commit a repository-wide API reference;
- replace or modify the current `docs/index.html` landing page;
- publish or deploy GitHub Pages output (Task #206).
