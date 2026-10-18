<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

显式选择的 NumPy 批量隶属函数与语言标度计算。

导入本模块不会加载 NumPy。只有调用批量接口才选择 float64 数组计算；标量调用不会自动切换后端。解析定义与参数校验来自标量核心，适用范围由 ADR-0018 规定。
