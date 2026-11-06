<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

在无图形界面的环境中将标量隶属数据导出为科学图形。

离散取值和连续性未知的可调用对象以独立标记显示。支持的内置公式在已知间断处
断开曲线。隶属度来自标量模糊集的求值接口，叠加图保留术语顺序以及调用方声明的
共同坐标单位。

Args:
    source: 标量模糊集、有序标度或独立的隶属函数。
    destination: 以 `.png`、`.jpg`、`.jpeg` 或 `.svg` 结尾的显式输出路径。
    universe: 仅在使用独立可调用对象时必填的论域。
    displayWindow: 有限、递增且包含端点的显示区间。默认覆盖各术语的有界论域，只有一个点时扩展坐标轴。
    sampleCount: 每个可见连续区段的基础采样数，至少为二。
    title: 图形标题及 SVG 元数据中的标题。
    coordinateLabel: 坐标轴标签，包含已知的单位。
    formatName: 可选格式，须与文件扩展名一致。
    background: JPEG 必须显式指定的不透明 `#RRGGBB` 颜色。
    transparent: PNG 或 SVG 的画布和绘图区是否透明。
    overwrite: 是否允许原子替换目标文件。
    svgTextAsPaths: 将 SVG 文字导出为字形轮廓。

Returns:
    已保存图形的绝对路径。

Raises:
    InvalidParameterTypeError: 源对象、论域或坐标类型不符合约定。
    InvalidParameterError: 采样数、标签或格式选项无效。
    InvalidDomainError: 显示区间或网格无效，或区间内没有样本。
    PlotSamplingError: 可见坐标上的标量求值失败。
    ImportError: 可选的 Matplotlib 后端不可用。
    OSError: 无法发布目标文件，例如目标已存在。
