<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

仅在已声明坐标处定义的不可变隶属度表。

可以直接调用该表，也可以将其 `universe` 和表本身传给 `ScalarFuzzySet`。
在已声明坐标之间或范围之外的坐标均无隶属度。

Attributes:
    points: 非空元组，其中每项是 `(坐标, 隶属度)` 二元组。坐标有限且严格递增；
        隶属度有限且位于 $[0, 1]$。不接受布尔值。
    universe: 与保存的点对应的离散论域。
