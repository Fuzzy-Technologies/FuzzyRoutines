<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 标量运算 {#scalar-operators}

运算模块负责不可变的否定、T-范数和 S-范数策略及其标量公式。从 `fuzzyroutines.fuzzysets` 进行的现有导入仍保留相同的策略类对象。集合代数使用这些策略，不依赖全局配置。

## 应用示例 {#worked-examples}

[传感器判据](../../guides/sensors.md)比较组合方式；[运算示例](../../guides/api-recipes.md#choose-scalar-operator-families-deliberately)执行每个函数族。[运算曲线](../../guides/operators.md)展示所选策略如何改变合取与析取。

::: fuzzyroutines.operators
    options:
      members:
        - NegationPolicy
        - TNormPolicy
        - SNormPolicy
