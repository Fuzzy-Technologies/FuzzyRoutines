<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

显式离散论域上的精确派生属性。

Attributes:
    universe: 已穷举求值的离散论域。
    positiveSupport: 已声明坐标中隶属度为正的点。
    supportClosure: 在离散拓扑下等于 `positiveSupport`。
    core: 已声明坐标中隶属度等于一的点。
    boundary: 已声明坐标中隶属度严格介于零和一之间的点。
    height: 所有已声明坐标上的最大隶属度。
