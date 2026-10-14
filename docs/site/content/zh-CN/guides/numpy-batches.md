<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# NumPy 批量计算

批量接口适用于使用同一隶属函数或语言标度处理大量坐标的情形。普通标量调用仍不依赖 NumPy。安装可选依赖：

```bash
python -m pip install 'fuzzyroutines[numpy]'
```

```python
from fuzzyroutines import CreateUniversalFuzzyScale, Triangle, UniversalFuzzyScalePolicy
from fuzzyroutines.batches import EvaluateMembershipBatch, FuzzifyBatch

grades = EvaluateMembershipBatch(Triangle(0.0, 0.5, 1.0), [0.0, 0.25, 0.5], backend="numpy")
assert grades.tolist() == [0.0, 0.5, 1.0]
result = FuzzifyBatch(CreateUniversalFuzzyScale(), [0.0, 0.3, 0.5, 0.7, 1.0], UniversalFuzzyScalePolicy(), backend="numpy")
assert result.termNames == ("Min", "Low", "Med", "High", "Max")
assert result.memberships.shape == (5, 5)
assert result.selected.argmax(axis=-1).tolist() == [0, 1, 2, 3, 4]
```

每个坐标均保留五个隶属度，`selected` 掩码标识选中的语言项。一般情况下，使用 `argmax` 前应检查 `result.selected.any(axis=-1)`；未匹配行的掩码全部为 `False`。当 `tiePolicy="all"` 时，应读取完整掩码。即使 `first` 或 `last` 仅选择一项，`tied` 仍保留全部并列项。`UniversalFuzzyScalePolicy()` 实现历史上的末项优先规则；现代接口的默认规则仍为首项优先。

输入形状为 `(rows, columns)` 时，隶属度和掩码的形状为 `(rows, columns, terms)`，最大隶属度的形状为 `(rows, columns)`。末轴顺序由 `termNames` 给定。输入复制为 float64；允许空数组和非连续切片。单个隶属函数返回可写的新数组，分类记录中的数组分别拥有独立存储且默认只读；修改前使用 `.copy()`。

支持八类内置隶属函数及由其组成的标度。参数和论域端点必须是可由 float64 精确表示的 int/float。拒绝布尔、复数、字符串/对象类型及非有限坐标。自定义、归一化或复合隶属函数仍使用标量接口。每个坐标必须属于所有语言项的论域。接口不裁剪坐标，不自动选择后端，也不将隶属度归一化或解释为概率。

基准验证配置为 Python 3.13/3.14 与 NumPy 2.3.5；可选依赖允许兼容的 NumPy 2.x 版本。异常约定见 [API](../api/modern/batches.md)，实测规模和资源开销见[性能报告](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/performance/public-batch-comparison.md)。小批量可能更慢，预先构造的数组与 Python 列表的转换成本不同；不存在通用的切换阈值。

[![标量与批量计算的实测时间比](../../en/assets/figures/numpy-batch-speed.svg)](../../en/assets/figures/numpy-batch-speed.svg)
