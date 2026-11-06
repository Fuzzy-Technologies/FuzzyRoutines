<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# YAML 项目配置

转换项目文档时，安装 `fuzzyroutines[config,yaml]`。`[yaml]` 提供解析器，
`[config]` 提供离线 v1 架构验证。两个转换函数接收并返回有大小限制的
UTF-8 字节。文件由调用方打开和写入。转换会检查架构并解析项目引用，
不会执行推理或运行求值场景。

YAML 接受一份键为字符串的数据文档。重复键、显式标签、锚点、别名及
合并键会引发
[`ConfigurationError`](configuration.md)。
未知版本或 `include` 字段无法通过验证。错误提供类别和 JSON Pointer。
转换会保留数字写法及数组顺序，对映射键排序，原始文档保持原样。

示例对含三角标度的项目进行双向转换。带符号的零和指数记法均会保留。

```python
from fuzzyroutines.yaml_configuration import ConvertProjectJsonToYaml, ConvertProjectYamlToJson

projectJson = b'''{
  "kind": "project", "schemaVersion": 1,
  "models": {"score": {
    "kind": "model", "schemaVersion": 1,
    "universes": {"unit": {"kind": "continuous", "left": -0, "right": 1, "leftClosed": true, "rightClosed": true}},
    "memberships": {"middle": {"family": "triangle", "parameters": {"left": 0, "peak": 5e-1, "right": 1}}},
    "scales": {"score": {"universe": "unit", "terms": [{"id": "middle", "name": "Middle", "membership": "middle"}]}}
  }}
}'''
projectYaml = ConvertProjectJsonToYaml(projectJson)
canonicalJson = ConvertProjectYamlToJson(projectYaml)

assert b'"left":-0' in canonicalJson
assert b'"peak":5e-1' in canonicalJson
assert ConvertProjectJsonToYaml(canonicalJson) == projectYaml
```

::: fuzzyroutines.yaml_configuration
    options:
      members:
        - ConvertProjectJsonToYaml
        - ConvertProjectYamlToJson
