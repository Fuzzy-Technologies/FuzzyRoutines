<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

导出可移植项目，整个过程无需读取文件或对场景求值。

Args:
    project: 通过加载 v1 项目得到的已验证快照。
    formatName: 显式指定的输出格式，默认为 JSON。

Returns:
    经过验证的 UTF-8 字节，末尾带有换行符。相同输入的输出逐字节一致。

Raises:
    ConfigurationError: 无法将该快照表示为有效的 v1 项目。
    ImportError: 缺少所需的配置或 YAML 可选依赖。
    ValueError: 不支持所选格式。
