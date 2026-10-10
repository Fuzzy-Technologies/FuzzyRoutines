<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回高度为一的新模糊集，不修改源集合。

归一化是逐点商 $\mu_A(x) / \mathrm{height}(A)$。高度为零时未定义；当前解析约定无法证明精确连续高度时，也不可使用。

Args:
    fuzzySet: 具有可证明非零精确高度的标量模糊集。

Returns:
    精确高度为一的新标量模糊集。

Raises:
    TypeError: `fuzzySet` 不是标量模糊集。
    ValueError: 精确高度不可得或等于零。
