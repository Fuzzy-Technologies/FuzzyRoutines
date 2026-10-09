<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回完整名称与查询匹配的术语。

Args:
    termName: 要获取的完整术语名称。
    exactMatching: 为 `True` 时区分大小写；否则使用 Unicode 大小写折叠比较名称。

Returns:
    已声明的术语对象；若没有完整名称匹配，则返回 `None`。

Raises:
    TypeError: `termName` 不是字符串，或 `exactMatching` 不是布尔值。

Notes:
    此操作绝不进行子串、前缀、近似或基于隶属度的匹配。
