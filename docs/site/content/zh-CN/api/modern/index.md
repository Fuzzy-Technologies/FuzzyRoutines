<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 现代 API {#modern-api}

根包 [`fuzzyroutines`][fuzzyroutines] 重新导出推荐的公共符号。模块页面保留其架构归属，并提供稳定的完全限定名称锚点：

| 模块                                      | 职责               |
| --------------------------------------- | ---------------- |
| [`alphacuts`](alphacuts.md)             | 精确离散与采样连续 α-截集   |
| [`defuzzification`](defuzzification.md) | 连续质心的解析与自适应计算    |
| [`domain`](domain.md)                   | 声明的论域与有限积分域      |
| [`exceptions`](exceptions.md)           | 现代参数、域及数值错误类别    |
| [`fuzzysets`](fuzzysets.md)             | 标量模糊集、运算、策略与归一化  |
| [`linguistic`](linguistic.md)           | 不可变语言词项与有序尺度     |
| [`membership`](membership.md)           | 具有几何参数的不可变解析隶属函数 |
| [`operators`](operators.md)             | 标量否定与范数策略        |
| [`properties`](properties.md)           | 精确或采样的支集、核、边界与高度 |
| [`relations`](relations.md)             | 显式指定域的相等与包含比较    |

权威的根导入接口见[包导出](package.md)。
