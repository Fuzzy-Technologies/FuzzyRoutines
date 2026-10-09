<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Полные неизменяемые сведения об одной классификации по шкале.

Attributes:
    memberships: Одна оценка на каждый объявленный терм шкалы, в заданном порядке.
    confidence: Наибольшая записанная степень принадлежности.
    policy: Политика получения отказа и выбора среди равных максимумов.
    tiedTerms: Максимальные термы после применения `tieTolerance` либо пустой кортеж, если уверенность не превышает минимум.
    selectedTerms: Термы, выбранные из `tiedTerms` по `tiePolicy`, либо пустой кортеж при отсутствии совпадения.
