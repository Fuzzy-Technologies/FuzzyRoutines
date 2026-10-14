<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Нормированный скалярный вклад одного правила.

Attributes:
    name: Точное имя правила в порядке объявления.
    antecedentGrade: Результат вычисления типизированного условия.
    weight: Объявленный мультипликативный вес правила.
    firingStrength: Произведение веса и степени истинности условия.
    consequentValue: Постоянное или аффинное заключение при заданных входах.
    normalizedStrength: Степень срабатывания, делённая на сумму степеней срабатывания.
    contribution: Произведение нормированной степени срабатывания и значения заключения.
