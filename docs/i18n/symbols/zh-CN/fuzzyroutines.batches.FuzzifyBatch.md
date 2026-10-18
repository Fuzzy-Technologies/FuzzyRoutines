<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

使用内置函数组成的标度及显式标量策略对数组进行分类。

Args:
    scale: 由合格内置函数组成的现代标度。连续论域端点及离散论域坐标须可由 float64 精确表示。
    values: 满足批量接口约定且属于每个语言项论域的坐标。任一违规值导致整个批次失败。
    policy: first/last/all 选择策略。默认选择首个精确最大项，零覆盖表示未匹配。阈值须为 int/float；任意有理数策略仍使用标量接口。
    backend: 显式后端选择；支持 `"numpy"`。

Returns:
    有序隶属度、最大隶属度、并列项及选中项掩码。各数组拥有独立存储且默认只读。空批次保留原形状并增加语言项轴。

Raises:
    ImportError: 未安装 NumPy。
    TypeError: 不支持的标度、策略、函数、数组类型或数值表示。自定义、归一化和复合函数仍使用标量接口。
    ValueError: 后端、坐标、论域或隶属度无效。
    ArithmeticError: 实际执行的隶属函数分支无法计算。

Notes:
    不进行坐标或隶属度归一化、概率转换、模糊推理或解模糊化。浮点容差保留标量策略对近似并列边界的处理规则。
