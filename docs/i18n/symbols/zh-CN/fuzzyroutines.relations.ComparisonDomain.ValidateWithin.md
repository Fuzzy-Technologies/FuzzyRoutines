<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

证明每个点都属于论域后，返回本比较域。

Args:
    universe: 预期包含全部点的连续论域。

Returns:
    验证成功后返回原比较域，不作修改。

Raises:
    TypeError: `universe` 不是连续论域。
    ValueError: 任一比较点位于论域之外。
