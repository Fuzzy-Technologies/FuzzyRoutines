<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Вычисляет все заключения и нормированные вклады правил.

Args:
    inputs: Ровно объявленные имена входов и конечные координаты.

Returns:
    Неизменяемый скалярный результат со всеми упорядоченными вкладами правил.

Raises:
    InvalidParameterError: Ключи или значения входов нарушают контракт.
    InvalidParameterTypeError: Неверный тип входа или степени принадлежности.
    InvalidDomainError: Координата или заключение вне своего универсального множества.
    UndefinedResultError: Все взвешенные степени срабатывания равны нулю.
    NumericalError: Неконечная промежуточная аффинная арифметика или сумма.
