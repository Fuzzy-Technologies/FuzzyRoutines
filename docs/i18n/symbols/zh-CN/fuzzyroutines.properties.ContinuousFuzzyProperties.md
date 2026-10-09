<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

连续论域上由解析表达式推导的精确属性。

Attributes:
    universe: 所有区域均限制于该连续论域内。
    positiveSupport: 隶属度严格大于零的坐标集合。
    supportClosure: `positiveSupport` 在论域内的闭包。
    core: 隶属度等于一的坐标集合。
    boundary: 根据解析函数族的约定，隶属度严格介于零和一之间的坐标集合。
    height: 论域内隶属度的精确上确界。
