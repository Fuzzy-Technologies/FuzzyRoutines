<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Явная политика сетки и допусков выборочной диагностики шкалы.

Attributes:
    sampleCount: Число равноотстоящих точек, включая обе границы области анализа.
    membershipThreshold: Терм активен только при степени строго выше порога. Нет активных термов — пробел; два или больше — перекрытие.
    partitionTolerance: Максимальная допустимая абсолютная разность суммы принадлежностей термов и единицы.
