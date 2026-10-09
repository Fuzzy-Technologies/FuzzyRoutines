<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在可证明时，返回隶属度的精确上确界。

离散论域采用穷尽求值。连续论域需要内部保留的精确证据、现代解析 [MembershipFunction][fuzzyroutines.membership.MembershipFunction]，或由 [DeriveProperties][fuzzyroutines.properties.DeriveProperties] 支持的已注册历史 [MFunction][fuzzyroutines.FuzzyRoutines.MFunction] 求值器。该函数绝不会把有限样本的最大值提升为精确高度。

Args:
    fuzzySet: 请求精确高度的标量模糊集。

Returns:
    隶属度的精确上确界。

Raises:
    TypeError: `fuzzySet` 不是标量模糊集。
    ValueError: 无法获得精确连续高度。
