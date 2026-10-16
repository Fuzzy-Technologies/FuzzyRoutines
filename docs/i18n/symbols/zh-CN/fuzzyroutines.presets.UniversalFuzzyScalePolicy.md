<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回选择最后一个精确最大值且不附加置信阈值的策略。

Returns:
    设置 `tiePolicy="last"`、`tieTolerance=0` 和 `minimumConfidence=0` 的策略。零覆盖仍表示无匹配；历史尺度的 Min 正尾部覆盖整个归一化论域。

Notes:
    数学上对称的中点经 binary64 计算后，隶属度未必精确相等。本策略不引入舍入或近似并列容差。
