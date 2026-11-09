<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

从单个大小受限的 v1 项目中恢复具名模型和设置。

Args:
    encoded: 所选格式的 UTF-8 项目字节。
    formatName: 显式指定的输入格式，默认为 JSON。

Returns:
    只读快照，其中包含显式声明的默认项和尚未求值的场景。

Raises:
    ConfigurationError: 文档解析失败或未通过离线 v1 验证。
    ImportError: 缺少所需的配置或 YAML 可选依赖。
    ValueError: 不支持所选格式。
