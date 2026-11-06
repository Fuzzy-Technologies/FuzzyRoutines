<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Экспорт графиков {#plot-export-api}

Импортируйте функцию из `fuzzyroutines.plotting`. Опциональный бэкенд
загружается при построении графика. [Руководство по экспорту](../../guides/plot-export.md)
описывает установку, диапазон отображения и параметры форматов.

::: fuzzyroutines.plotting
    options:
      members:
        - ExportMembershipPlot

## `PlotSamplingError` {#plot-sampling-error}

Обрабатывайте `fuzzyroutines.plotting.PlotSamplingError`, если вычисление
в видимой точке завершилось ошибкой. В сообщении указаны ряд и координата,
а `__cause__` хранит исходное исключение. Файл появляется после успешного
вычисления отсчётов и построения графика.
