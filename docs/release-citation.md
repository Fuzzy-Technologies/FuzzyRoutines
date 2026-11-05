<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Citing a FuzzyRoutines release

For reproducible research, cite the version you used. The repository's
[citation file](../CITATION.cff) describes the
[published 2.1.0 distribution](https://pypi.org/project/fuzzyroutines/2.1.0/)
and its [tagged source](https://github.com/Fuzzy-Technologies/FuzzyRoutines/releases/tag/v2.1.0).
Use the exact release URL and, when needed to reproduce a result, record the
source commit and distribution hash. The
[current documentation](https://fuzzy-technologies.com/FuzzyRoutines/api/latest/en/)
tracks the project over time.

## Maintainer checklist

1. Follow the [release policy](adr/0006-packaging-versioning-release-policy.md)
   for the approved version and tag. Check the citation's authors and SPDX
   license against `pyproject.toml` and the tagged source. For an approved
   release update the citation to the exact version and version-specific
   landing page. Confirm the release date from the publication record.
2. Validate `CITATION.cff` against the
   [CFF 1.2.0 schema](https://citation-file-format.github.io/1.2.0/schema.json).
   Inspect the built wheel's `METADATA` and the sdist's `PKG-INFO` for the
   version, author, license and project URLs, and verify that the sdist
   contains the citation file. Check that the homepage and documentation
   links resolve.
3. If the maintainers approve a DOI deposit, archive the exact released
   version and verify that the published record matches its tag and metadata.
   Cite that version's DOI for reproducibility. A concept DOI identifies all
   versions together. Add a `doi` field only after the version DOI resolves to
   the matching published record. Until then, cite the version-specific URL.

## Как ссылаться на релиз

Указывайте версию, которую использовали. Для 2.1.0 доступны
[дистрибутив на PyPI](https://pypi.org/project/fuzzyroutines/2.1.0/)
и [исходный код по тегу](https://github.com/Fuzzy-Technologies/FuzzyRoutines/releases/tag/v2.1.0).
Для воспроизведения результатов при необходимости запишите хеш коммита и
контрольную сумму дистрибутива. Если для версии опубликован DOI, проверьте,
что он ведёт к записи именно об этой версии. До этого используйте ссылку на
конкретный релиз.

## 如何引用发布版本

请注明实际使用的版本。对于 2.1.0，可引用
[PyPI 上的发行包](https://pypi.org/project/fuzzyroutines/2.1.0/)和
[对应标签的源代码](https://github.com/Fuzzy-Technologies/FuzzyRoutines/releases/tag/v2.1.0)。
如需复现实验结果，请同时记录提交哈希和发行包的校验值。若该版本已有 DOI，
请确认它指向同一版本的公开记录。在此之前，请使用该版本的发布链接。
