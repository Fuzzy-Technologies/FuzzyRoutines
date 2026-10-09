<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

解析以逗号分隔的整数以及包含两端的整数区间。

Args:
    diapason: 例如 `"1,3-5"` 的文本。

Returns:
    排序后的不重复整数列表。输入无效时打印历史诊断信息并返回空列表。

Examples:
    ```python
    DiapasonParser("8-10, 1-3, 3")
    # [1, 2, 3, 8, 9, 10]
    ```
