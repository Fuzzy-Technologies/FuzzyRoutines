<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 温度舒适度 {#temperature-comfort}

**问题：**24 °C 的测量值与 *Comfort* 和 *Warm* 两个概念有多相容？可按照[快速入门](../quick-start.md)中的独立示例构造尺度并计算两个隶属度。

在 `Triangle(16, 22, 28)` 的下降边上，舒适度为

$$
\mu_{\mathrm{Comfort}}(24)=\frac{28-24}{28-22}=\frac{2}{3}.
$$


二次肩形曲线的前半段给出

$$
\mu_{\mathrm{Warm}}(24)=2\left(\frac{24-22}{30-22}\right)^2=\frac{1}{8}.
$$


[![温度模型与测量值对应的隶属度](../../en/assets/figures/temperature.svg)](../../en/assets/figures/temperature.svg)

最高隶属度使结果选择 *Comfort*。这不表示舒适的概率为 66.7%。两个隶属度是在不同定义下对同一测量值的描述，其和不受等于一的约束。

**工程检查：**论域包含两个端点，因此可以计算 0 和 40 °C 的隶属度。论域之外的坐标会引发域错误。这个仅含两个标签的尺度存在低温覆盖空缺：温度不高于 16 °C 时，两个隶属度都为零。如果要求完整覆盖，应增加表示低温的语言术语并审查尺度。

**项目用法：**为仪表板或后续策略计算保留完整的隶属度向量；仅在单个标签有用时采用 `selectedTerms`。不要丢弃胜出词项隶属度仍然很低这一信息。下一个场景演示拒绝分类。

```bash
python -I examples/guide.py --scenario temperature
```


继续阅读[严重程度标签与拒绝分类](risk.md)。
