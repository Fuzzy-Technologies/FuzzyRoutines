<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Historical compatibility facade

The `fuzzyroutines.FuzzyRoutines` module preserves the observed public API of
version 1.0.3. Its names and mutable object model remain available for existing
software, but new code should prefer the [modern API](../modern/index.md).

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
