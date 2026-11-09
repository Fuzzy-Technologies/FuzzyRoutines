<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

加载项目后得到的只读快照，包含具名模型和项目设置。

Attributes:
    models: 按项目中模型的确切标识符索引的独立配置。
    defaults: 显式选定的默认项（若源文档中已声明）。
    units: 用于显示的标签，先按模型标识符、再按局部论域标识符索引。
    plots: 按绘图标识符索引的显示设置。
    evaluations: 按求值场景标识符索引的尚未求值场景。
