<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 历史兼容接口 {#historical-compatibility-facade}

`fuzzyroutines.FuzzyRoutines` 模块保留 1.0.3 版本已观察到的公共 API。其名称和可变对象模型继续供现有软件使用，但新代码应优先采用[现代 API](../modern/index.md)。

[历史接口示例](../../guides/historical-recipes.md)演示所有受支持函数族、标量运算、可变集合和尺度，包括参数顺序、积分窗口以及并列时后者胜出的规则。

::: fuzzyroutines.FuzzyRoutines
    options:
      members:
        - DiapasonParser
        - IsNumber
        - IsCorrectFuzzyNumberValue
        - FuzzyNOT
        - FuzzyNOTParabolic
        - FuzzyAND
        - FuzzyOR
        - TNorm
        - TNormCompose
        - SCoNorm
        - SCoNormCompose
        - MFunction
        - FuzzySet
        - FuzzyScale
        - UniversalFuzzyScale
