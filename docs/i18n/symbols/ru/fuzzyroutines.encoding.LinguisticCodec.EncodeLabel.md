<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает центроид указанного терма на его явном интервале интегрирования.

Args:
    label: Полное имя с учётом регистра; поиск по префиксу, приближённому совпадению или без учёта регистра не применяется.

Returns:
    Одного численного представителя в координатных единицах шкалы.

Raises:
    TypeError: `label` не является строкой.
    InvalidParameterError: Точное имя неизвестно.
    UndefinedResultError: У выбранного терма нулевая площадь либо неразрешённые неконечные моменты на интервале.
    CentroidConvergenceError: Адаптивное интегрирование превысило ограничение.
