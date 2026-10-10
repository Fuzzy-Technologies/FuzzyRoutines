<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

计算并返回当前隶属函数曲线下方面积的质心坐标。

Raises:
    ValueError: 隶属函数下方的面积为零或不是有限值。
    CentroidConvergenceError: 自适应积分无法满足显式的默认容差。
