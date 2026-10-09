<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 组合两个传感器判据 {#combine-two-sensor-criteria}

**问题：**80 °C 的温度和 10 mm/s 的振动，在多大程度上满足两个示意预警判据？先将每个物理测量值转换为各自的无量纲隶属度，再进行组合。该模型不推断故障概率。

```python
from fuzzyroutines import SNormPolicy, SShoulder, TNormPolicy, Triangle

temperatureGrade = SShoulder(60, 100)(80)
vibrationGrade = Triangle(0, 8, 16)(10)
minimumAnd = TNormPolicy("logic").Evaluate(temperatureGrade, vibrationGrade)
productAnd = TNormPolicy("algebraic").Evaluate(temperatureGrade, vibrationGrade)
maximumOr = SNormPolicy("logic").Evaluate(temperatureGrade, vibrationGrade)
algebraicOr = SNormPolicy("algebraic").Evaluate(temperatureGrade, vibrationGrade)
assert (temperatureGrade, vibrationGrade) == (0.5, 0.75)
assert (minimumAnd, productAnd, maximumOr, algebraicOr) == (0.5, 0.375, 0.75, 0.875)
print(minimumAnd, productAnd, maximumOr, algebraicOr)
```


[![两个输入隶属度及四种显式组合策略的结果](../../en/assets/figures/sensors.svg)](../../en/assets/figures/sensors.svg)

最小值合取保留较弱的隶属度：$\min(0.5,0.75)=0.5$。乘积合取得到 $0.5\times0.75=0.375$。最大值析取得到 0.75；代数析取得到

$$
0.5+0.75-0.5\times0.75=0.875.
$$


这些是不同的模糊运算选择，并非互相竞争的性能模式。使用乘积 T-范数并不能确立概率独立性。

**工程检查：**两个输入具有不同单位和论域，因此这里使用标量策略的 `Evaluate`。集合层面的 `Intersection` 和 `Union` 要求集合具有相同论域。完整的温度—振动规则库还需要显式定义多变量推理层，本例没有实现该层。

**项目用法：**将所选策略与判据阈值一起记录。四个结果说明，即使测量值不变，更换策略也可能改变后续决策。

```bash
python -I examples/guide.py --scenario sensors
```


继续阅读[维护预警区域](alarm.md)。
