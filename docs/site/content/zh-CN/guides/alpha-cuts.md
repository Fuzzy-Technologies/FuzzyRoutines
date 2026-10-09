<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 质量 α-截集 {#quality-alpha-cuts}

**问题：**哪些已声明的质量评分达到 0.5 的隶属度阈值？三角形容差模型在 12 时完全隶属，在 10 和 14 时隶属度为零。弱截集包含等于阈值的情形。

```python
from fuzzyroutines import (
    AlphaCut, ContinuousUniverse, DeriveProperties, DiscreteUniverse,
    IntegrationDomain, SampleAlphaCut, ScalarFuzzySet, Triangle,
)

model = Triangle(10, 12, 14)
discrete = ScalarFuzzySet(DiscreteUniverse((10, 11, 12, 13, 14)), model)
assert AlphaCut(discrete, 0.5).points == (11, 12, 13)
assert AlphaCut(discrete, 0).points == (10, 11, 12, 13, 14)
assert AlphaCut(discrete, 1).points == (12,)
universe = ContinuousUniverse(10, 14, leftClosed=True, rightClosed=True)
continuous = ScalarFuzzySet(universe, model)
sampled = SampleAlphaCut(continuous, 0.5, IntegrationDomain(10, 14), sampleCount=9)
properties = DeriveProperties(model, universe)
assert sampled.cutSamples.points == (11, 11.5, 12, 12.5, 13)
assert not sampled.isExact and properties.isExact
assert not properties.positiveSupport.Contains(10)
assert properties.supportClosure.Contains(10)
assert properties.core.Contains(12)
print(sampled.cutSamples.points)
```


[![连续三角形、九个网格观测以及精确离散截集的点](../../en/assets/figures/alpha-cuts.svg)](../../en/assets/figures/alpha-cuts.svg)

精确的**离散**截集为 $\{11,12,13\}$，因为声明的离散论域中的每个坐标都被检查。α 为零时，截集包含所有声明的点，包括隶属度为零的点。

连续示例以 0.5 的间距采样九个坐标，报告五个符合条件的观测以及 `isExact=False`；这些观测不构成精确的连续区域。对于这个已知的特定三角形，独立求解两个线性不等式可得连续截集 $[11,13]$。`SampleAlphaCut` 不会进行该符号求解。

`DeriveProperties` 使用已知的解析函数族：模糊集的支集为 $(10,14)$，其闭包为 $[10,14]$，核为 $\{12\}$。注意支集与其闭包为何对端点采用不同的包含方式。

**项目用法：**对于有限个允许设置，采用精确离散截集；对于连续模型的探索，采用采样结果，并在报告中保留采样域和网格点数。更密的网格增加观测数量，却不能证明不存在未观察到的细节。

```bash
python -I examples/guide.py --scenario alpha-cuts
```


继续阅读[质心与数值精度](centroid.md)。
