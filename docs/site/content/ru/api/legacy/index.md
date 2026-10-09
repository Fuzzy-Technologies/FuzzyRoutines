<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Исторический фасад совместимости {#historical-compatibility-facade}

Модуль `fuzzyroutines.FuzzyRoutines` сохраняет наблюдаемый публичный API версии 1.0.3. Его имена и изменяемая объектная модель доступны существующим программам, но новому коду рекомендуется [современный API](../modern/index.md).

[Исторические рецепты](../../guides/historical-recipes.md) показывают каждое поддерживаемое семейство, скалярные операторы, изменяемые множества и шкалы, включая порядок параметров, окна интегрирования и выбор позднего терма при равенстве.

::: fuzzyroutines.FuzzyRoutines
    options:
      members:
        - DiapasonParser
        - IsNumber
        - IsCorrectFuzzyNumberValue
        - FuzzyNOT
        - FuzzyNOTParabolic
        - FuzzyAND
        - FuzzyOR
        - TNorm
        - TNormCompose
        - SCoNorm
        - SCoNormCompose
        - MFunction
        - FuzzySet
        - FuzzyScale
        - UniversalFuzzyScale
