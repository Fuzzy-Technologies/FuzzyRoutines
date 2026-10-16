<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

按等级顺序返回历史重心积分区间。

Returns:
    `Min`、`Low`、`Med`、`High`、`Max` 对应的闭积分区间：`(0, 0.23)`、`(0.17, 0.40)`、`(0.34, 0.66)`、`(0.60, 0.83)` 和 `(0.77, 1)`。

Notes:
    这些区间是积分边界，而非语言项的论域或支集。现代接口修正后的重心与 2.0 兼容接口一致，但不保证等于 1.0.3 的离散采样结果或过期缓存值。
