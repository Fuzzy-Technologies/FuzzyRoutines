<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Linguistic terms and scales

## Worked examples

[Severity and abstention](../../guides/risk.md) explains selection; [scale auditing](../../guides/scale-audit.md) diagnoses ties and gaps.

[Result records](../../guides/results.md) demonstrate every diagnostic property,
lookup and explicit record constructor.

::: fuzzyroutines.linguistic
    options:
      members:
        - LinguisticTerm
        - TermMembership
        - FuzzificationPolicy
        - FuzzificationResult
        - ScaleDiagnosticsPolicy
        - ScaleDiagnosticPoint
        - ScaleDiagnosticsResult
        - LinguisticScale

::: fuzzyroutines.presets
    options:
      members:
        - CreateUniversalFuzzyScale
        - UniversalFuzzyScalePolicy
        - UniversalFuzzyScaleDomains

[Linguistic encoding](../../guides/linguistic-encoding.md) converts labels, full memberships and numeric predictions with explicit domains.

::: fuzzyroutines.encoding
    options:
      members:
        - LinguisticCodec
