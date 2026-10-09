<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

覆盖、重叠、空缺和分割质量的不可变采样记录。

结果仅描述已声明的有限网格，不能证明采样坐标之间的连续属性。

Attributes:
    analysisDomain: 诊断所采样的有限闭区间。
    policy: 诊断使用的网格大小和容差策略。
    points: 每个等间距网格坐标的有序记录。
