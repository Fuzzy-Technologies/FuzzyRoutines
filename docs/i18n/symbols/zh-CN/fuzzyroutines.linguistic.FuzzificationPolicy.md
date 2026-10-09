<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

显式规定并列处理和最低置信度的分类策略。

Attributes:
    tiePolicy: 最大隶属度相等或在容差范围内等价时的选择规则：
        `"first"`、`"last"` 或 `"all"`。
    minimumConfidence: 若最大隶属度小于或等于此阈值，则不选择任何术语。
        默认仅排除覆盖度为零的情况。
    tieTolerance: 与最大隶属度之间被视为并列的绝对差值容限。
