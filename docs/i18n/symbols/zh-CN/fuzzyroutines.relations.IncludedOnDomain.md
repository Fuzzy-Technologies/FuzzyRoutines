<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在穷尽域或显式有限域上求模糊包含关系。

包含意味着每个求值点都满足 $\mu_{subset}(x) \leq \mu_{superset}(x)$。容差模式允许不等式有轻微违反，但仅限于两个隶属度按显式比较策略判定为数值接近的情形。

Args:
    subset: 候选子模糊集。
    superset: 具有完全相同论域的候选超集。
    comparisonPolicy: 精确或容差隶属度比较策略。
    comparisonDomain: 连续论域必需的有限观测点；离散论域应省略。

Returns:
    每个求值坐标都满足包含关系时返回 `True`。

Raises:
    TypeError: 参数类型不符合约定。
    ValueError: 论域不同或比较域选择无效。
