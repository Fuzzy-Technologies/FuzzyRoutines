<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Экспорт научных графиков {#scientific-plot-export}

Используйте дополнение `plot` с проверенным wheel FuzzyRoutines 2.2,
в котором есть модуль `fuzzyroutines.plotting`. Задайте абсолютный путь к
wheel в `FUZZYROUTINES_WHEEL`. Для обычных скалярных вычислений достаточно
базовой установки.

```bash
: "${FUZZYROUTINES_WHEEL:?Set the absolute path to the reviewed wheel}"
python -m pip install "${FUZZYROUTINES_WHEEL}[plot]"
```

Сохраните шкалу в SVG и явно обозначьте безразмерную ось. Временный каталог
позволяет запускать пример повторно. Второй вызов показывает, как узнать
причину ошибки вычисления в отдельной точке.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from fuzzyroutines import CreateUniversalFuzzyScale, DiscreteUniverse, ScalarFuzzySet
from fuzzyroutines.plotting import ExportMembershipPlot, PlotSamplingError

def UnavailableGrade(coordinate):
    """Report an unavailable observation at the requested coordinate."""

    raise ValueError(f"No observation at {coordinate}")

scale = CreateUniversalFuzzyScale()
with TemporaryDirectory() as temporaryDirectory:
    folder = Path(temporaryDirectory)
    figure = ExportMembershipPlot(
        scale, folder / "membership.svg", coordinateLabel="Normalized coordinate x",
    )
    assert figure.read_bytes().startswith(b"<?xml")

    incomplete = ScalarFuzzySet(DiscreteUniverse((0, 1)), UnavailableGrade)
    failedFigure = folder / "missing.svg"
    try:
        ExportMembershipPlot(incomplete, failedFigure)
    except PlotSamplingError as error:
        sampleFailure = error
    else:
        raise AssertionError("An unavailable scalar sample must fail the export.")

    assert isinstance(sampleFailure.__cause__, ValueError) and not failedFigure.exists()
```

- Для неограниченного универсума задайте конечный диапазон
  `displayWindow=(left, right)`. Он определяет видимую часть графика.
  Носитель и границы интегрирования сохраняют свой математический смысл.
- `sampleCount` задаёт базовую сетку на каждом видимом непрерывном участке.
  Экспорт учитывает известные узлы. На дискретном универсуме и для функций
  с неизвестной непрерывностью точки остаются отдельными маркерами.
  Конечная сетка определяет разрешение графика.
- Для прозрачного фона выберите `.png` или `.svg` и `transparent=True`.
  Для JPEG задайте непрозрачный `background`, например `"#121829"`.
  Текст SVG по умолчанию редактируется. Параметр `svgTextAsPaths=True`
  сохраняет контуры символов.
- Родительский каталог должен существовать. Чтобы заменить файл после
  успешного рендеринга, задайте `overwrite=True`. Расширение имени файла
  и явно заданный `formatName` должны совпадать.

Контракт ошибок скалярного вычисления описан в [справочнике API](../api/modern/plotting.md).
