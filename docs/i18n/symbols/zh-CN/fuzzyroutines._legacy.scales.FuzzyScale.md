<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

表示可变的历史三级语言尺度。

每个级别都是字典，具有唯一的字符串 `name`，以及包含
[FuzzySet][fuzzyroutines.FuzzyRoutines.FuzzySet] 的 `fSet`。
默认尺度包含 `Min`、`Med` 和 `High` 级别。
