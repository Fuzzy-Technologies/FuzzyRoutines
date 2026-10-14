<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

按声明顺序返回一个坐标的全部隶属度。

Args:
    coordinate: 位于每个项论域内且已采用尺度单位的有限标量；不进行归一化或截断。

Returns:
    长度为 N 的不可变元组，各隶属度均在 `[0, 1]` 内。隶属度不是概率，其和不必为一；即使策略未选择标签，仍保留弱覆盖或零覆盖信息。

Raises:
    TypeError: 坐标不是实数标量。
    ValueError: 坐标非有限或位于任一论域之外。
