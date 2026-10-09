<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

证明本积分域包含于连续论域后，返回本积分域。

Args:
    universe: 预期包含两个端点的连续论域。

Returns:
    验证成功后返回原积分域，不作修改。

Raises:
    TypeError: `universe` 不是连续论域。
    ValueError: 任一端点位于论域之外。
