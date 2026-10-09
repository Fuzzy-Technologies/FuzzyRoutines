<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 严重程度标签与拒绝分类 {#severity-labels-and-abstention}

**问题：**当最高隶属度仅为 0.4 时，是否应为严重程度评分 65 分配标签？这个评分是 0–100 范围内的示意工程指标，不是事件概率，也不是经过医学验证的风险估计。

```python
from math import isclose
from fuzzyroutines import (
    ContinuousUniverse, FuzzificationPolicy, LinguisticScale,
    LinguisticTerm, ScalarFuzzySet, SShoulder, Triangle,
)

universe = ContinuousUniverse(0, 100, leftClosed=True, rightClosed=True)
scale = LinguisticScale((
    LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(0, 20, 50))),
    LinguisticTerm("Moderate", ScalarFuzzySet(universe, Triangle(25, 50, 75))),
    LinguisticTerm("High", ScalarFuzzySet(universe, SShoulder(50, 90))),
))
result = scale.Fuzzify(65)
cautious = scale.Fuzzify(65, FuzzificationPolicy(minimumConfidence=0.45))
grades = {item.term.name: item.grade for item in result.memberships}
assert isclose(grades["Moderate"], 0.4)
assert grades["High"] == 0.28125
assert result.selectedTerms[0].name == "Moderate"
assert not cautious.isMatch
print(grades, cautious.isMatch)
```


[![严重程度曲线与 0.45 的选择阈值](../../en/assets/figures/risk.svg)](../../en/assets/figures/risk.svg)

默认结果选择 *Moderate*，其三角形下降边给出

$$
\mu_{\mathrm{Moderate}}(65)=\frac{75-65}{75-50}=0.4.
$$


上升肩形曲线对 *High* 给出 $2(15/40)^2=0.28125$，*Low* 为零。`confidence` 字段是最大隶属度，不是经过校准的统计置信度。当 `minimumConfidence=0.45` 时，系统不选择标签，但保留所有隶属度。隶属度**等于**阈值时也拒绝选择；选择要求严格高于阈值。

**项目用法：**将没有匹配词项的观测交给人工复核，或转入预先定义的后备处理流程。根据应用要求选择阈值，并用代表性观测进行验证。FuzzyRoutines 不会替你估计或验证该阈值。

```bash
python -I examples/guide.py --scenario risk
```


继续阅读[传感器判据组合](sensors.md)。
