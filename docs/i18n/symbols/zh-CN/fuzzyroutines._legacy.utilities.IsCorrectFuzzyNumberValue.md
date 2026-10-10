<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回一个值是否是 $[0, 1]$ 内的有效隶属度。

Args:
    value: 待检验的内置 `int` 或 `float` 隶属度；不接受 `bool`。

Returns:
    对于闭单位区间内受支持的内置数值返回 `True`。
    不受支持的数值类型或非数值输入会打印历史诊断信息并返回 `False`；
    受支持但超出区间的数值会静默返回 `False`。
