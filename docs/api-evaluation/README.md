# API Documentation Architecture Evaluation

This directory is the reproducible Task #198 spike. It compares pdoc,
mkdocstrings-python, and Sphinx autodoc against the real
`fuzzyroutines.fuzzysets` module and its `fuzzyroutines.domain` type dependency.
It is not a production Pages integration.

## Source-of-truth boundary

Tracked inputs are configurations, Markdown/RST spike pages, theme assets,
pinned dependency manifests, the evaluator, and written evidence. Generated
HTML, build logs, virtual environments, and `evaluation.json` are disposable
and belong under ignored `_build/` paths or a temporary directory.

Never edit generated HTML. Production composition and deployment remain Task
#206.

## One-command comparison

Run all three candidates in new isolated CPython 3.14 environments:

```bash
python tools/evaluate_api_documentation.py \
  --environment-root /tmp/fuzzyroutines-api-docs-envs \
  --output-root /tmp/fuzzyroutines-api-docs-build
```

The command emits the same JSON written to
`/tmp/fuzzyroutines-api-docs-build/evaluation.json`. It fails rather than
replacing an existing environment or output directory.

To repeat only the builds with the previously provisioned environments and no
usable HTTP connection:

```bash
HTTP_PROXY=http://127.0.0.1:9 \
HTTPS_PROXY=http://127.0.0.1:9 \
ALL_PROXY=http://127.0.0.1:9 \
NO_PROXY='' \
python tools/evaluate_api_documentation.py \
  --environment-root /tmp/fuzzyroutines-api-docs-envs \
  --output-root /tmp/fuzzyroutines-api-docs-offline-build \
  --skip-install
```

For cached, fail-closed environment provisioning, add `--offline` and select a
new environment root. The command then passes `--offline` to `uv pip sync`.

## Individual builds

The evaluator records exact expanded commands in `evaluation.json`. The
equivalent candidate entry points are:

```bash
python tools/evaluate_api_documentation.py pdoc \
  --environment-root /tmp/fuzzyroutines-pdoc-env \
  --output-root /tmp/fuzzyroutines-pdoc-build

python tools/evaluate_api_documentation.py mkdocstrings \
  --environment-root /tmp/fuzzyroutines-mkdocs-env \
  --output-root /tmp/fuzzyroutines-mkdocs-build

python tools/evaluate_api_documentation.py sphinx \
  --environment-root /tmp/fuzzyroutines-sphinx-env \
  --output-root /tmp/fuzzyroutines-sphinx-build
```

## Current primary references

The architecture conclusions use official project documentation:

- [pdoc documentation](https://pdoc.dev/docs/pdoc.html)
- [mkdocstrings overview](https://mkdocstrings.github.io/)
- [mkdocstrings-python docstring configuration](https://mkdocstrings.github.io/python/usage/configuration/docstrings/)
- [Material for MkDocs search](https://squidfunk.github.io/mkdocs-material/plugins/search/)
- [Material for MkDocs math](https://squidfunk.github.io/mkdocs-material/reference/math/)
- [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)
- [Sphinx viewcode](https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html)

The references and package versions were checked on 2026-09-16.
