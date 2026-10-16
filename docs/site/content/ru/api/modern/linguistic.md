<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Лингвистические термы и шкалы {#linguistic-terms-and-scales}

## Практические примеры {#worked-examples}

[Серьёзность и отказ от классификации](../../guides/risk.md) объясняют выбор; [аудит шкалы](../../guides/scale-audit.md) выявляет равные максимумы и пробелы.

[Записи результатов](../../guides/results.md) показывают все диагностические свойства, поиск терма и явные конструкторы записей.

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

[Лингвистическое кодирование](../../guides/linguistic-encoding.md) преобразует названия уровней в числовых представителей, вычисляет векторы степеней принадлежности и интерпретирует численные прогнозы. Интервалы интегрирования задаются явно.

::: fuzzyroutines.encoding
    options:
      members:
        - LinguisticCodec
