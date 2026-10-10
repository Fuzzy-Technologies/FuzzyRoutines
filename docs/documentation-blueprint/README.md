<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Fuzzy Technologies documentation blueprint

This blueprint transfers the documentation contracts proven by FuzzyRoutines
to another Python repository. It reuses upstream MkDocs, Material,
mkdocstrings-python, and Griffe rather than forking any generator. It includes
tracked configuration templates and a project-neutral locale validator; it
does not include generated HTML or FuzzyRoutines product prose.

The architectural invariants remain those accepted in
[ADR-0010](../adr/0010-api-documentation-architecture.md) and
[ADR-0011](../adr/0011-multilingual-documentation-pipeline.md). Adopting a
different generator, canonical language, stable-ID scheme, source-hash
payload, approval model, or fallback semantics requires an explicit project
ADR. Choosing project values, navigation, or branding does not.

## Explicit project inputs

Copy `templates/project.toml` to `docs/i18n/project.toml` and replace every
sample value. None of these values may be inferred from FuzzyRoutines.

| Input              | Manifest location              | Contract                                                         |
|--------------------|--------------------------------|------------------------------------------------------------------|
| Project identity   | `projectId`, `projectName`     | Stable machine ID and user-facing product name                   |
| Python packages    | `packageNames`                 | One or more statically documented top-level package names        |
| Languages          | `sourceLocale`, `locales`      | English first, followed by explicit target locale keys           |
| Branding           | `[branding]`                   | Organization name and tracked asset root                         |
| Publication path   | `publicationPath`              | Absolute URL path such as `/SampleProject` without trailing `/`  |
| Authored content   | `contentRoot`                  | Locale directories containing canonical and translated Markdown  |
| API inventory      | `apiCoverageManifest`          | Static authored/export surfaces and reviewed exclusions          |
| Translation state  | `unitManifest`, `[glossaries]` | Stable units, review evidence, and terminology                   |
| Disposable output  | `buildRoot`                    | Ignored build directory, conventionally below `_build/`          |

`tools/locale_documentation.py` consumes only those tracked paths and Python
syntax. It neither imports FuzzyRoutines nor imports the adopting package. The
validator supports a project-selected target-locale list; every target locale
must have one glossary and one state in every active unit record.

## Adoption sequence

1. Copy the files in `templates/` into the equivalent repository locations.
   Use `requirements-api.txt` as the direct-input seed for a fully pinned
   transitive documentation lock. Copy `tools/locale_documentation.py` as
   project-owned source and update only its ownership header; do not change the
   hash scheme or review rules.
2. Put canonical English Markdown below `<contentRoot>/en/`. Keep English
   Google-style Markdown docstrings in Python source. Generated HTML stays
   below `_build/` and remains untracked.
3. Declare every API surface in `docs/site/api-coverage.toml`. Use `authored`
   for definitions in a module and `exports` for a package `__all__` facade.
   Discovery is AST-based and therefore does not execute package code.
4. Run the inventory command, review every stable ID, and populate
   `docs/i18n/units.toml` with the emitted hashes:

   ```bash
   python -m tools.locale_documentation inventory --project-root .
   ```

5. Create one glossary for each target locale. Missing translations use an
   explicit `missing` state without a path or reviews. Automation must never
   create an `approved` state or human review record.
6. Adapt `templates/mkdocs.yml`, keeping strict mode and static Griffe
   discovery. Set `PACKAGE_INSTALLED_PACKAGES` to the isolated environment
   containing the installed wheel. Replace the sample navigation and assets;
   do not copy FuzzyRoutines prose.
7. Adapt `templates/documentation-gates.yml`. Pull requests build and validate
   disposable artifacts. Only a protected default-branch push may deploy
   Pages. Keep package publication separate from documentation deployment.
8. Run the deterministic gate before enabling Pages:

   ```bash
   python -m tools.locale_documentation validate \
     --project-root . \
     --output _build/documentation-gates/locales.json
   mkdocs build --strict --config-file docs/site/mkdocs.yml
   ```

The tracked second-project fixture at
`tests/fixtures/documentation-blueprint/sampleproject/` exercises this flow
with a package and locale set unrelated to FuzzyRoutines.

## Tool upgrades

Keep documentation dependencies outside runtime package metadata and pinned in
`docs/requirements-api.txt`. Upgrade upstream packages there, rebuild from a
clean installed wheel, and run strict build, source-link, anchor, formula,
search, locale, and generated-output gates. A normal dependency upgrade needs
no ADR when these contracts remain true. A generator or discovery-model change
must repeat the ADR-0010 comparison and record a superseding decision.

Do not vendor generated theme output or edit generated HTML. Brand through
tracked assets and supported MkDocs configuration so future upstream upgrades
remain possible.

## TKSBrokerAPI migration

TKSBrokerAPI currently uses a pdoc-oriented builder. Migrate it as an explicit
replacement, not as a second permanent documentation stack:

1. inventory pdoc pages, public objects, custom templates, source links, and
   existing public URLs before changing the build;
2. declare the actual package roots (for example `tksbrokerapi`) and map each
   public surface into `api-coverage.toml`;
3. convert narrative content to canonical English Markdown and source
   contracts to English Google-style docstrings without changing public APIs;
4. configure Griffe against a clean installed wheel and add an import guard for
   every declared package root;
5. preserve intentional public URLs with redirects or a documented migration
   map, and set `publicationPath` to TKSBrokerAPI's Pages root;
6. introduce locale unit manifests, glossaries, `missing` states, and review
   ownership before advertising translated routes;
7. run pdoc and MkDocs in CI only during a bounded comparison period, compare
   object coverage and links, then remove the pdoc builder after the MkDocs
   gates pass;
8. deploy only from the protected release/default branch and retain the prior
   site artifact for rollback.

Product-specific pdoc templates and prose are migration inputs, not reusable
blueprint components. The reusable boundary is configuration, deterministic
validation, build gates, and safe publication behavior.
