<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 选择隶属度的组合方式 {#choose-how-grades-combine}

**问题：**两个部分满足的判据，是取较弱的隶属度，还是让部分满足程度相乘？这属于模型策略。先用各自的隶属函数处理每个物理量，再组合得到的无量纲隶属度。进行集合组合时，两个集合必须具有相同论域。

对于两个隶属度 $a,b\in[0,1]$，图中策略为

$$
T_{\mathrm{minimum}}(a,b)=\min(a,b),\qquad
T_{\mathrm{product}}(a,b)=ab,
$$


$$
S_{\mathrm{maximum}}(a,b)=\max(a,b),\qquad
S_{\mathrm{algebraic}}(a,b)=a+b-ab.
$$


[![第二个隶属度固定为 0.6 时的最小值和乘积合取、最大值和代数析取](../../en/assets/figures/operators.svg)](../../en/assets/figures/operators.svg)

横坐标使第一个隶属度从零变化到一，第二个固定为 0.6。左图的最小值在 0.6 处饱和，乘积则把第一输入乘以 0.6。右图的最大值始终不小于 0.6，代数析取连续上升至一。这些是显式模糊策略，不意味着测量值在统计上独立。

```python
from math import isclose
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

first, second = 0.4, 0.6
assert TNormPolicy("logic").Evaluate(first, second) == 0.4
assert isclose(TNormPolicy("algebraic").Evaluate(first, second), 0.24)
assert SNormPolicy("logic").Evaluate(first, second) == 0.6
assert isclose(SNormPolicy("algebraic").Evaluate(first, second), 0.76)
assert NegationPolicy("standard").Evaluate(first) == 0.6
print(0.4, 0.24, 0.6, 0.76)
```


标准否定为 $N(a)=1-a$。有向差将第一个隶属度与第二个隶属度的否定进行合取；采用最小值合取时，$\mu_{A\setminus B}(x)=\min(\mu_A(x),1-\mu_B(x))$。它不是普通减法。[预警场景](alarm.md)展示结果曲线。有界和剧烈备选策略，以及参数化、抛物线否定的可执行示例，见 [API 示例](api-recipes.md#choose-scalar-operator-families-deliberately)。

**项目用法：**将选定策略与模型一起保留，更换策略前先比较中间隶属度。乘积可能显著降低 AND 结果，这并不表示实现更慢或更不准确；它表达的是部分相容程度应如何组合。
