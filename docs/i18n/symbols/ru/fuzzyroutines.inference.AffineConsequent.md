<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Заключение Сугено первого порядка: линейная функция входов с постоянным членом $b+\sum_j a_j x_j$.

Постоянный член $b$ не обязан равняться нулю; в терминологии линейной алгебры такая функция называется аффинной.

Attributes:
    intercept: Конечный свободный член $b$ в единицах выхода.
    coefficients: Неизменяемый упорядоченный кортеж пар `(inputName, coefficient)`; имена уникальны, коэффициенты отсутствующих входов равны нулю.
