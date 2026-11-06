<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# JSON 配置 {#json-configuration}

安装 `fuzzyroutines[config]` 即可加载和保存独立的版本 1 JSON 模型。
`LoadModel` 读取 UTF-8 字节并返回不可变的标度、Mamdani 或 Sugeno 定义。
`AssembleModel` 将现有运行时对象绑定到显式 ID，`DumpModel` 返回规范化字节。
文件访问和模型求值由调用方显式控制。项目文档采用独立的接口契约。

`ConfigurationError` 提供错误类别和 RFC 6901 JSON 指针。导出器会拒绝
自定义求值器及无法无损表示的数值。验证器按需加载，标量计算无需安装此扩展。

::: fuzzyroutines.configuration
    options:
      members:
        - LoadModel
        - DumpModel
        - AssembleModel
        - ModelConfiguration
        - ScaleDefinition
        - ScaleRepresentatives
        - MamdaniBinding
        - MamdaniCentroid
        - SugenoBinding
        - ConfigurationError
