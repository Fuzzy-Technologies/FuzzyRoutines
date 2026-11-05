<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 构建有界语言尺度

如果需要相邻语言项互相重叠，请使用
`fuzzyroutines.scale_builders.BuildLinearScale(terms, lower, upper)`。
传入有序的“标签、峰值坐标”对以及有限闭区间的两端。两个相邻峰值之间，
一项的隶属度线性下降，另一项的隶属度线性上升。首项和末项各自从峰值
延伸到相应的端点，期间隶属度恒为 1。峰值可以与端点重合。只有一项时，
该项在整个论域中的隶属度都为 1。

如果每个坐标只应归入一个区间，请使用
`fuzzyroutines.scale_builders.BuildIntervalScale(labels, boundaries)`。
边界的数量比标签多一个。内部边界归入其右侧区间，最后一个区间包含上端点。

两个函数都返回 `LinguisticScale`，并保留标签顺序。峰值坐标和边界必须
有限且严格递增。标签不得为空或全为空白，按 Unicode 大小写折叠比较时
也不得重复。对闭区间以外的坐标执行模糊化会引发通常的论域错误。

当峰值坐标为 0、2、7 时，坐标 3 的隶属度依次为 `(0, 4/5, 1/5)`。
如果区间边界为 −2、0、2、9，则得到 `(0, 0, 1)`。在论域内，
隶属度之和为 1。线性插值使用整数、有理数和 binary64 数值的精确比值。
其他实数标量类型在插值时采用其 binary64 表示。
