<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Аффинное преобразование входов {#affine-input-mapping}

`AffineInputMapping` переводит физическое измерение в координату
существующего конечного замкнутого непрерывного универсума. При создании
укажите обе единицы и границы физического диапазона. Для безразмерной
координаты используйте `1`. Обозначения единиц должны совпадать точно.
Значения за границами диапазона отклоняются, а отсутствующее измерение
вызывает `MissingObservationError`.

В примере 30 °C из рабочего диапазона 10–50 °C соответствует 0.5 на
единичном интервале. Обратное преобразование возвращает 30 °C. Границы
отображаются точно. Внутренние координаты округляются до binary64, что
может ограничить точность обратного преобразования. Сценарий проекта v1
принимает координаты шкалы. Примените преобразование до создания сценария.

```python
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.input_mapping import AffineInputMapping, MissingObservationError

universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
mapping = AffineInputMapping(10, 50, universe, "°C", "1")
coordinate = mapping.Forward(30, unit="°C")
assert coordinate == 0.5
assert universe.Contains(coordinate)
assert mapping.Inverse(coordinate, unit="1") == 30

try:
    mapping.Forward(None, unit="°C")
except MissingObservationError as error:
    missing = error
else:
    raise AssertionError("Expected a missing-observation error.")
```

::: fuzzyroutines.input_mapping
