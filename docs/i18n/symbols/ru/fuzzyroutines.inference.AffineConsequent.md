<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Заключение Сугено первого порядка: аффинная функция входов $b+\sum_j a_j x_j$.

Свободный член $b$ может быть ненулевым.

Attributes:
    intercept: Конечный свободный член $b$ в единицах выхода.
    coefficients: Неизменяемый упорядоченный кортеж пар `(inputName, coefficient)`; имена уникальны, коэффициенты отсутствующих входов равны нулю.
