<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

带完整来源信息的连续 α-截集有限观测。

Attributes:
    alpha: $[0, 1]$ 内的弱隶属度阈值。
    analysisDomain: 网格覆盖的闭区间。
    sampleCount: 网格坐标数量，包括两个端点。
    coordinates: 跨越 `analysisDomain` 的严格递增坐标。`SampleAlphaCut` 生成均匀网格；直接构造不会重新验证等间距。
    grades: 与 `coordinates` 对应的、经过验证的隶属度。
    cutSamples: 隶属度满足 $\mathrm{grade} \geq \alpha$ 的坐标。
    method: 必需的来源标签，目前始终为 `"uniform-grid"`。标签记录受支持的产生函数约定，但自身不能证明直接构造实例的坐标等距。
