<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 语言输入与数值预测 {#linguistic-inputs-and-numeric-predictions}

语言标签、隶属度向量与数值代表值携带的信息不同。2.1 API 的 `LinguisticCodec`
显式规定这些转换，无需依赖神经网络框架。每次操作处理一个样本；由应用程序
负责将元组转换为所用框架的数组或张量。

## 观测编码与预测解释 {#encode-observations-and-decode-predictions}

对于语言项 $i$，$D_i$ 为显式指定的重心积分区间，$\mu_i$ 为隶属函数。
其数值代表值与完整特征向量分别为

$$
c_i=\frac{\int_{D_i}x\mu_i(x)\,\mathrm{d}x}{\int_{D_i}\mu_i(x)\,\mathrm{d}x},
\qquad
\mathbf{g}(x)=(\mu_1(x),\ldots,\mu_N(x)).
$$

重心可用于表示输入标签或训练目标，但**不是网络权重**；网络权重由训练过程学习。
数值观测与预测必须已经采用尺度的坐标单位。历史预设的定义域为闭区间 `[0, 1]`。
具体归一化规则由应用程序显式确定；若归一化参数需从数据估计，应仅使用训练集。

```python
from math import isclose
from fuzzyroutines import (
    CreateUniversalFuzzyScale, LinguisticCodec,
    UniversalFuzzyScaleDomains, UniversalFuzzyScalePolicy,
)

codec = LinguisticCodec(
    CreateUniversalFuzzyScale(),
    UniversalFuzzyScaleDomains(),
    UniversalFuzzyScalePolicy(),
)
assert codec.termNames == ("Min", "Low", "Med", "High", "Max")
representative = codec.EncodeLabel("Low")
assert isclose(representative, 0.285, abs_tol=1e-12)
grades = codec.EncodeMemberships(0.17)
assert 0 < sum(grades) < 0.003
prediction = codec.DecodePrediction(0.75)
assert prediction.selectedTerms[0].name == "High"
print(representative, grades, prediction.selectedTerms[0].name)
```

输出包括约为 `0.285` 的代表值、按 Min/Low/Med/High/Max 排列的五个隶属度以及
标签 `High`。坐标 `0.17` 处的隶属度总和很小，此弱覆盖特征应予保留，而不应将其
重新归一化为概率分布。预测解释结果保留全部隶属度、并列最大值和无匹配信息。
通过显式 `FuzzificationPolicy` 可选择并列处理规则或设置拒绝分类的阈值。

`EncodeLabel` 要求区分大小写的完整标签；未知标签引发错误，不会转换成零。
标量操作拒绝数组、非有限数值以及超出任一语言项论域的坐标。
`AverageRepresentatives` 仅接受包含 N 个隶属度的单一元组；嵌套向量及隐式批次
均被拒绝。编码器不会截断预测值，也不保存隐藏的拟合状态。

## 代表值加权平均与聚合模糊集的重心 {#representative-averaging-and-aggregate-centroids}

两种操作的含义不同：

$$
y_{\mathrm{rep}}=\frac{\sum_i g_i c_i}{\sum_i g_i}
\qquad\text{and}\qquad
y_{\mathrm{set}}=\frac{\int_D x\mu_{\mathrm{aggregate}}(x)\,\mathrm{d}x}
{\int_D\mu_{\mathrm{aggregate}}(x)\,\mathrm{d}x}.
$$

前者以给定隶属度为权重，对代表坐标进行平均；后者计算显式构造的模糊集的面积
重心。即使隶属度均为 `(1, 1)`，当各语言项面积不同时，两种结果仍可能不同。

[![两个不重叠三角形的中心为 1 和 4、面积为 1 和 2；等隶属度代表值平均为 2.5，而最大值并集的重心为 3。](../../en/assets/figures/linguistic-encoding.svg)](../../en/assets/figures/linguistic-encoding.svg)

```python
from math import isclose
from fuzzyroutines import (
    Centroid, ContinuousUniverse, FuzzificationPolicy, IntegrationDomain,
    LinguisticCodec, LinguisticScale, LinguisticTerm, ScalarFuzzySet,
    SNormPolicy, Triangle, Union,
)

universe = ContinuousUniverse(0, 6, leftClosed=True, rightClosed=True)
small = ScalarFuzzySet(universe, Triangle(0, 1, 2))
large = ScalarFuzzySet(universe, Triangle(2, 4, 6))
codec = LinguisticCodec(
    LinguisticScale((LinguisticTerm("Small", small), LinguisticTerm("Large", large))),
    (IntegrationDomain(0, 2), IntegrationDomain(2, 6)),
    FuzzificationPolicy(),
)
representative = codec.AverageRepresentatives((1, 1))
aggregate = Union(small, large, SNormPolicy("logic"))
aggregateCentroid = Centroid(aggregate, IntegrationDomain(0, 6))
assert representative == 2.5
assert isclose(aggregateCentroid, 3, abs_tol=1e-10)
print(representative, aggregateCentroid)
```

两三角形的解析面积分别为 1 和 2，故聚合集的重心为 $(1\cdot1+2\cdot4)/3=3$，
代表值平均则为 $(1+4)/2=2.5$。`AverageRepresentatives` 不要求隶属度之和为一。
全零向量引发 `UndefinedResultError`；具有正隶属度的语言项若面积为零，同样显式
报错。零隶属度项不产生贡献，因此无需计算其重心。对聚合模糊集调用 `Centroid`
时，聚合算子、积分域以及零面积处理均须由调用方明确确定。

## 为什么两种转换通常不可逆 {#why-the-conversions-are-not-inverses}

选取标签会舍弃其余隶属度；将标签替换为重心，则把整条曲线压缩为一个坐标。
再次分类时，甚至可能得到不同标签。例如，顶点为 `0, 1, 6` 的三角形重心为
`7/3`；若另一语言项在 `7/3` 处达到峰值，分类该坐标时后者就可能胜出。
这是信息压缩的固有限制，并不构成往返恢复保证。

若这些差异对任务重要，应保留完整隶属度向量。围绕神经网络使用固定的模糊
预处理，并不自动形成可训练的模糊规则，也不保证保留自动微分梯度。

## 复现图形 {#reproduce-the-figure}

安装匹配的 2.1 软件包及 `docs/requirements-plots.txt` 中固定的绘图依赖后执行：

```bash
python -m tools.generate_encoding_figure --output-directory docs/site/content/en/assets/figures
python -m tools.generate_encoding_figure --output-directory docs/site/content/en/assets/figures --check
```

曲线坐标由公共标量 API 计算，两种代表坐标均通过上述独立解析值校验。
原始积分区间见[历史尺度指南](universal-fuzzy-scale.md)，完整编码契约见
[API 参考](../api/modern/linguistic.md)。
