<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

连续域上有限坐标处的近似观测结果。

`SampleProperties` 生成均匀网格，并根据对应的隶属度推导所有记录的区域。
直接构造会验证表格形状、端点覆盖、区域子集及高度，
但不会重新验证等间距，也不会重新计算所记录的三个区域。

Attributes:
    analysisDomain: 网格覆盖的闭区间。
    sampleCount: 坐标数量，包含两个端点。
    coordinates: 覆盖 `analysisDomain` 的严格递增坐标。
    grades: 与 `coordinates` 对应的已验证隶属度。
    positiveSupportSamples: 已记录的采样坐标子集；`SampleProperties` 选择隶属度大于零的点。
    coreSamples: 已记录的采样坐标子集；`SampleProperties` 选择隶属度等于一的点。
    boundarySamples: 已记录的采样坐标子集；`SampleProperties` 选择隶属度严格介于零和一之间的点。
    heightEstimate: 观测到的最大隶属度，不构成精确上确界的证明。
    method: 非空的采样来源标签。`SampleProperties` 使用 `"uniform-grid"`。
