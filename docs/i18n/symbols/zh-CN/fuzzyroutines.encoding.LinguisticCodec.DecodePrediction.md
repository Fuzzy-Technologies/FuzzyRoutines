<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

以完整隶属度证据解释单次数值预测。

Args:
    prediction: 已采用尺度坐标且属于每个项论域的有限标量。

Returns:
    按配置策略得到的有序隶属度、最大隶属度、并列项及选定项。无匹配时 `selectedTerms` 为空元组。

Raises:
    TypeError: 预测不是实数标量。
    ValueError: 预测非有限或位于任一论域之外。
