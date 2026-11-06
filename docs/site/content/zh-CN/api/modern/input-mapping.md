<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 仿射输入映射 {#affine-input-mapping}

`AffineInputMapping` 将物理观测值转换为现有有限闭连续论域中的坐标。
创建映射时应声明两种单位以及物理范围的上下界。无量纲坐标使用 `1`。
单位标签必须完全一致。超出声明区间的观测值会被拒绝，缺失的观测值会引发
`MissingObservationError`。

本示例将 10–50 °C 工作区间内的 30 °C 映射为单位区间中的 0.5，
逆映射返回 30 °C。端点映射是精确的。区间内部的坐标会舍入为 binary64，
因此往返转换的精度可能受到限制。v1 项目场景接收量表坐标，请在创建场景前
应用映射。

```python
from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.input_mapping import AffineInputMapping, MissingObservationError

universe = ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True)
mapping = AffineInputMapping(10, 50, universe, "°C", "1")
coordinate = mapping.Forward(30, unit="°C")
assert coordinate == 0.5
assert universe.Contains(coordinate)
assert mapping.Inverse(coordinate, unit="1") == 30

try:
    mapping.Forward(None, unit="°C")
except MissingObservationError as error:
    missing = error
else:
    raise AssertionError("Expected a missing-observation error.")
```

::: fuzzyroutines.input_mapping
