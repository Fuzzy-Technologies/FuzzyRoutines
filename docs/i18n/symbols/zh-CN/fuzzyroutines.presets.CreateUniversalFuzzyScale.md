<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

返回定义在闭单位区间上的历史五等级尺度。

Returns:
    按 `Min`、`Low`、`Med`、`High`、`Max` 顺序创建的不可变语言项，保留原始隶属函数系数。

Notes:
    Min 的正尾部以及 0.17 附近的弱覆盖均为刻意保留的特征。隶属度不是概率，其和不必等于一。工厂不会改变通用模糊化接口选择首个最大值的默认行为；如需历史选择规则，应传入 [UniversalFuzzyScalePolicy][fuzzyroutines.presets.UniversalFuzzyScalePolicy]。闭单位区间以外的坐标将被拒绝，不会被截断。
