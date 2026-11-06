<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 绘图导出 {#plot-export-api}

从 `fuzzyroutines.plotting` 导入导出函数。绘图时才加载可选后端。
[导出指南](../../guides/plot-export.md)介绍安装、显示区间和格式选项。

::: fuzzyroutines.plotting
    options:
      members:
        - ExportMembershipPlot

## `PlotSamplingError` {#plot-sampling-error}

可见坐标上的标量计算失败时，可捕获 `fuzzyroutines.plotting.PlotSamplingError`。
错误消息标明数据系列和坐标，`__cause__` 保留原始异常。只有采样和渲染均成功后，
导出函数才会发布文件。
