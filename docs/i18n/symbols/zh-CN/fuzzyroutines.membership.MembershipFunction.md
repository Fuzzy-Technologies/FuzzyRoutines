<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

实数轴上经过验证的不可变解析隶属函数。

`family` 指定以下函数族之一：`hyperbolic`、`bell`、`s_shoulder`、`triangle`、
`trapezoid`、`gaussian`、`logistic` 或 `harrington_desirability`。
具名构造函数公开完整的几何参数约束。求值接受有限实数坐标，不接受布尔值。
构造时会复制参数；读取 `parameters` 无法修改原对象。

Args:
    family: 类契约中列出的现代规范函数族标识符。
    **parameters: 参数名称必须与具名函数族构造函数的规定完全一致，参数值必须为有限实数；不接受布尔值。

Raises:
    ValueError: 函数族、参数名称、有限性或几何顺序无效。

Attributes:
    family: 现代 API 的规范函数族标识符。
    parameters: 以现代几何参数名称为键的只读映射。

Notes:
    正的解析尾部在求值时可能因下溢变为零。
    Triangle 允许 `peak == right`；此端点处隶属度为一，其右侧为零。
    Bell 的右侧底点为 `plateauEnd + plateauStart - left`。
    早期开发版本中的关键字 `plateau_start` 和 `plateau_end` 仍可作为输入别名；
    参数映射使用 camelCase 键。同时提供别名和对应的规范名称属于无效输入。
