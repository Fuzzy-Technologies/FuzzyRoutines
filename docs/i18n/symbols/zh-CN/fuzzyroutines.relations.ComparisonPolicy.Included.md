<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

根据本策略，检验两个隶属度是否满足模糊包含关系的判据。

Args:
    subsetGrade: 候选子集的隶属度。
    supersetGrade: 候选超集的隶属度。

Returns:
    子集隶属度是否不大于超集隶属度；仅在 tolerance 模式允许数值接近。

Raises:
    TypeError: 任一隶属度不是实数标量。
    ValueError: 任一隶属度非有限或超出 $[0, 1]$。
