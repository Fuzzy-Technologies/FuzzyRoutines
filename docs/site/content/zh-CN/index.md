<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FuzzyRoutines 文档 {#fuzzyroutines-documentation}

![Fuzzy Technologies 研究实验室中的 Alice 与 FuzzyRoutines](../en/assets/brand/fuzzyroutines-alice.png){ .fr-project-art }

从[快速入门](quick-start.md)开始，安装现代 API，并对一个物理测量值进行分类。[九个完整场景](guides/index.md)说明输入、计算策略、计算过程、预期结果和图形。需要选择曲线时，可查看[隶属函数图集](guides/membership-families.md)；需要完成单项操作时，可查阅[实用 API 示例](guides/api-recipes.md)。

新代码应使用[现代 API](api/modern/index.md)。[历史兼容接口](api/legacy/index.md)用于维护基于 FuzzyRoutines 1.0.3 编写的软件。

现代 API 将模糊集、显式声明的论域、α-截集、派生性质、语言结构和比较策略分别放在独立模块中。例如，标量模糊集可以定义在 [`ContinuousUniverse`][fuzzyroutines.domain.ContinuousUniverse] 或 [`DiscreteUniverse`][fuzzyroutines.domain.DiscreteUniverse] 上。

有向差运算采用

$$
\mu_{A \setminus B}(x)
= T\left(\mu_A(x), N\left(\mu_B(x)\right)\right).
$$
