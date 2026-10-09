<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 历史抛物型否定的解析推导 {#analytical-derivation-of-the-legacy-parabolic-negation}

- 状态：任务 #56 的数学契约
- 相关 ADR：[ADR-0004](../../../../adr/0004-operator-and-negation-contracts.md)
- 历史可调用函数：`FuzzyNOTParabolic(x, alpha, epsilon)`

## 范围与术语 {#scope-and-terminology}

历史可调用函数由隐式对称关系定义

```text
2*alpha - x - y = (2*alpha - 1) * (y - x)**2
```

本文推导其有效解析分支。审查中找到的来源均未将这一精确方程确认为具有规范名称的函数族；
因此，项目必须保留历史名称 `FuzzyNOTParabolic`，不能将其描述为已发表的标准“抛物型否定”。

端点、反单调性和对合性要求遵循通常的强模糊否定契约；
有关模糊否定的形式化处理，参见
[Bedregal et al. (2017)](https://arxiv.org/abs/1707.08617)。

## 推导 {#derivation}

令 `k = 2*alpha - 1`，`d = y - x`，关系变为

```text
k*d**2 + d + 2*(x - alpha) = 0
```

当 `alpha != 1/2` 时，通过不动点 `(alpha, alpha)` 的分支为

```text
D = 1 - 8*k*(x - alpha)
d = (-1 + sqrt(D)) / (2*k)
y = x + d
```

数值稳定的等价形式如下，并且在 `alpha = 1/2` 时也给出连续极限：

```text
y = x + 4*(alpha - x) / (1 + sqrt(D))
```

当 `alpha = 1/2` 时，此式精确化为 `y = 1 - x`。

## 有效参数域 {#valid-parameter-domain}

通过不动点的分支仅在 `alpha >= 1/4` 时满足 `N(0) = 1`，
且仅在 `alpha <= 3/4` 时满足 `N(1) = 0`。在闭区间

```text
alpha in [1/4, 3/4]
```

上，判别式对于 `x in [0, 1]` 非负；所选分支连续、单调递减、保持 `alpha` 不动，
并具有对合性。最后一个性质来自定义关系关于 `x` 与 `y` 的对称性，
以及所选分支是唯一有效输出分支这一事实。

在此区间之外，通过不动点的分支至少违反一个端点要求，
因此不属于本项目契约规定的强模糊否定。

## 结论 {#consequences}

- 暴力 `epsilon` 扫描在数学上没有必要，已由任务 #57 移除。
- 任务 #57 实现上述稳定闭式表达式，不使用扫描循环。
- 抛物型函数族要求 `alpha in [1/4, 3/4]`，
  不同于独立分段线性 `FuzzyNOT` 函数族的 `0 < alpha < 1` 域。
- 任务 #58 验证端点、不动点、单调递减、对合性及两个域外区域。
