<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

按完整名称查找级别，支持精确或不区分大小写的比较。

Args:
    levelName: 要查找的名称。
    exactMatching: 为 `True` 时区分大小写；否则比较大写形式。

Returns:
    匹配级别的字典；不存在时返回 `None`。

Notes:
    不区分大小写的查找使用历史大写名称映射。
    两种模式均不执行子串、前缀或近似匹配。
