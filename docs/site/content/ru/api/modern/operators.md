<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Скалярные операторы {#scalar-operators}

Модуль операторов владеет неизменяемыми политиками отрицания, T-норм и S-норм и их скалярными формулами. Существующие импорты из `fuzzyroutines.fuzzysets` сохраняют те же объекты классов политик. Алгебра множеств использует эти политики без глобальной конфигурации.

## Практические примеры {#worked-examples}

[Критерии датчиков](../../guides/sensors.md) сравнивают комбинации; [рецепты операторов](../../guides/api-recipes.md#choose-scalar-operator-families-deliberately) выполняют каждое семейство. [Кривые операторов](../../guides/operators.md) показывают влияние политики на конъюнкцию и дизъюнкцию.

::: fuzzyroutines.operators
    options:
      members:
        - NegationPolicy
        - TNormPolicy
        - SNormPolicy
