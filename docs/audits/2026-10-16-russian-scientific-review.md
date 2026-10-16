<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Russian scientific and editorial review — 2026-10-16

Reviewed the new 2.1 Russian inference, linguistic encoding, historical-scale,
NumPy batch, agent quickstart, neural integration and differentiable Sugeno
guides, their API landing pages and corresponding inference/encoding/batches/
presets symbol fragments. Also checked navigation and the scale-audit context.
The review used the development evidence protocol, multilingual architecture
and Russian project glossary. It is an editorial review, not independent
verification of the concurrently implemented numerical fixes.

Base revision: `640199f4b615d64ce64c2c1f0e9d72afaadd83bc`.
Changes are confined to Russian prose and this audit. Public identifiers,
existing formulas, executable examples, output values and the distinction
between published 2.0.0, candidate 2.1 and repository-only research are retained.

## Verified academic sources

Sources were opened and inspected on 2026-10-16; these are university-hosted
teaching materials or an original scholarly article, not translation glossaries.

1. М. В. Носков, К. В. Симонов, С. В. Кириллова.
   **Оценка риска и ущерба от наводнений на основе нечетких множеств**.
   *Журнал Сибирского федерального университета. Техника и технологии*,
   4(2), 2011, pp. 200–212.
   [University PDF](https://elib.sfu-kras.ru/bitstream/2311/2330/1/09_Noskov.pdf),
   pp. 203 and 209: rule conditions, aggregation of subconditions, activation,
   accumulation of conclusions and defuzzification. The article also
   distinguishes center-of-gravity and area-bisector methods on p. 209.
2. Ю. Н. Хижняков.
   **Алгоритмы нечеткого, нейронного и нейро-нечеткого управления в системах
   реального времени**. Пермь: ПНИПУ, 2013, 160 pp.
   [University-hosted PDF](https://pzs.dstu.dp.ua/logic/bibl/higa.pdf),
   § 2.7.1, pp. 127–130, especially p. 130: degrees of rule fulfillment,
   normalization and a consequent formula with an explicit constant term.
   This source also uses aggregation for combining outputs: Russian usage
   is not uniform, so API operations must be identified explicitly.
3. Э. М. Галеев. **Условия экстремума 2 порядка в теории экстремальных задач**.
   МГУ, механико-математический факультет, 2023.
   [Department PDF](https://kafedra-opu.ru/sites/default/files/extra_courses/uslovija_2_porjadka.pdf),
   chapter 1, § 4.1.2, p. 48, example 3: an affine function is given by
   a linear form plus a constant. This verifies that «аффинная» is
   mathematically correct; its replacement in introductory prose is an
   explanatory choice, not a correction of the mathematical concept.

## Terminology decisions

| Concept / former wording                               | Reviewed Russian wording                                                                  | Rationale                                                                                                                                         |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Inference / «численный отклик» heading                 | «Нечёткий вывод: модели Мамдани и Сугено»                                                 | Name the operation and models directly.                                                                                                           |
| Antecedent / consequent                                | «условие правила» / «заключение правила»                                                  | Explain the if/then parts before introducing API fields; source 1.                                                                                |
| `antecedentGrade` / `firingStrength`                   | «степень выполнения (истинности) условия» / «степень активации»                           | Explicit local convention: the latter includes the rule weight. Sources 1–2 support the terminology, not the library-specific weighting contract. |
| Activation / aggregation                               | «активизация заключения» / «аккумуляция заключений»                                       | Distinguish output operations from «агрегирование подусловий»; identify API `aggregation` explicitly. Sources 1–2.                                |
| First-order Sugeno / affine                            | «линейная функция входов с постоянным членом»                                             | Keep the intercept and formula; explain the precise affine term once and retain `AffineConsequent`. Sources 2–3.                                  |
| Centroid / «центр площади»                             | «центр тяжести площади под функцией принадлежности»                                       | Avoid confusion with area-bisector defuzzification; source 1.                                                                                     |
| Confidence / «уверенность»                             | «максимальная степень принадлежности (`confidence`)»                                      | Describe the actual field without suggesting statistical calibration.                                                                             |
| Seed, input width, held-out predictions                | «начальное значение генератора», «число входных признаков», «прогнозы на тестовых данных» | Replace compressed English constructions with concrete explanations.                                                                              |
| Nonfinite, non-real / «нефинитный», «недействительный» | «неконечный», «не являющийся действительным числом»                                       | Separate a numerical range failure from a type failure.                                                                                           |
| Universe / support                                     | «универсальное множество» / «множество поддержки»                                         | Preserve the established project glossary despite variants in external literature.                                                                |

Other corrections clarify pre-processing fitted on training data, batch axes,
copying and write protection, and the distinction between training targets
and learned weights. Removed wording that could imply statistical independence
of membership grades. The historical shoulder is described as piecewise
quadratic. Existing historical coefficients and weak-coverage behavior remain.

## Numerical and figure handoff

Russian inference text now distinguishes retained built-in shape boundaries
from the sampling limitation of arbitrary callbacks. At the implementer's
request it describes explicit `NumericalError` when a positive weighted firing
product underflows, and exact `Fraction` preservation when a positive normalized
Sugeno strength cannot be represented in binary64. Ordinary strengths remain
floats; the text makes no promise of unrestricted real-number arithmetic.
The research guide retains its representable-product parity qualification.

Canonical English figure assets were left to the integrating agent, as required
by the shared figure policy. Russian explanations and captions describe the
stages and values. A follow-through added the caption and analytical area/centroid
explanation for the integrating agent's new `inference-support.svg` figure and
adapted the three updated centroid/inference symbol contracts. Source hashes
and locale review state must be refreshed by the integrating agent after the
numerical changes settle.

## Focused validation

- CPython 3.14.8 from `/workspace/scratch/0a9762bec34b/fix-env/bin/python`;
  existing test environment, no dependency changes made by this review.
- `python -m pytest -q tests/test_markdown_source_style.py`: 9 passed.
- `ValidateSourceLinks` restricted to changed Russian Markdown: passed.
- Compared fenced examples and display formulas against the base revision:
  unchanged in all edited Russian files.
- `git diff --check`: passed.
- No full suite, documentation build or browser check was run. Numerical
  validation and cross-locale source-manifest checks belong to integration.

Integration follow-through: source/translation review bindings were refreshed
with AI reviewer attribution. Multilingual validation passed, as did 33 focused
layout, markup, API-documentation and documentation-gate tests. The new support
figure was generated and its Russian reference is now present. Additional
canonical EN/zh-CN explanations preserve the same inline mathematical symbols
as the Russian exposition; existing executable fences/display formulas remain.

Final independent AI scientific follow-through checked the numerical limits and
support-figure area balance against implementation. It identified and corrected
two overstatements: rational normalization also covers representable subnormal
weights, and a max-aggregated active consequent may be dominated by another.
The disjoint-support figure now explicitly limits its title to that example.
No human line-by-line review or full independent test run is claimed.
