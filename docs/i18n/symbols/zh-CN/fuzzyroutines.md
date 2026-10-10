<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

为模糊集论域及其属性提供显式契约的现代公共 API。

字面量 `__all__` 列表规定了经过筛选的现代 API，包含不可变隶属函数工厂、类型契约、
论域、集合和策略。历史可变对象仅通过 `fuzzyroutines.FuzzyRoutines` 提供；
导入包不会执行求值、输入输出或配置更改。
