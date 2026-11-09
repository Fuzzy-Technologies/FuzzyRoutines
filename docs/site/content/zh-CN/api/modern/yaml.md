<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 可移植的模糊项目配置

使用 `LoadProject` 和 `DumpProject` 加载并保存通过 v1 验证的项目快照。
快照包含带名称的内嵌模型，以及可选的默认选择、显示单位、绘图设置和
求值场景。单独加载或保存一个模型时，请使用
[`LoadModel` 和 `DumpModel`](configuration.md)。

## 保留数值写法的文档转换

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

## 加载和保存带类型的项目快照

处理 JSON 时安装 `fuzzyroutines[config]`。如果还需处理 YAML，请安装
`fuzzyroutines[config,yaml]` 并传入 `formatName="yaml"`。默认格式为 JSON。
读取和导出都使用随包提供的 v1 模式。模型的数学定义与显示设置分别保存。
加载时会检查整个项目中的引用。执行推理或绘图需要单独调用相应接口。
两个函数都以字节为输入或输出。调用方负责选择文件路径及读写文件。
v1 项目文档不含包含指令、外部引用或输出路径。

模型标识符区分大小写。`SelectModel("score")` 按标识符选择该模型。
`SelectModel()` 使用已声明的默认模型。没有默认模型时，即使项目中
只有一个模型，也会引发 `KeyError`。

示例验证每种格式的导出结果都可复现。恢复 YAML 后，先检查语言标度
的术语顺序、显示单位、绘图颜色和保存的输入，再显式执行推理。
该输入使唯一一条 Sugeno 规则激活，计算结果为 `0.75`.

```python
from fuzzyroutines.configuration import SugenoBinding
from fuzzyroutines.project_configuration import DumpProject, LoadProject

projectJson = b'''{
  "kind": "project", "schemaVersion": 1,
  "models": {"score": {
    "kind": "model", "schemaVersion": 1,
    "universes": {"unit": {
      "kind": "continuous", "left": 0, "right": 1,
      "leftClosed": true, "rightClosed": true
    }},
    "memberships": {
      "middle": {"family": "triangle", "parameters": {"left": 0, "peak": 0.5, "right": 1}},
      "high": {"family": "s_shoulder", "parameters": {"left": 0, "right": 1}}
    },
    "scales": {"risk": {"universe": "unit", "terms": [
      {"id": "middle", "name": "Middle", "membership": "middle"},
      {"id": "high", "name": "High", "membership": "high"}
    ]}},
    "inference": {
      "kind": "sugeno", "outputUniverse": "unit",
      "inputs": [{"id": "risk", "name": "Risk", "scale": "risk"}],
      "policy": {"conjunction": "logic", "disjunction": "logic", "negation": {"family": "standard"}},
      "rules": [{
        "id": "respond", "name": "Respond", "weight": 1,
        "antecedent": {"kind": "term", "input": "risk", "term": "high"},
        "consequent": {"kind": "constant", "value": 0.75}
      }]
    }
  }},
  "defaults": {"model": "score", "plot": "curve", "evaluation": "quarter"},
  "presentation": {
    "units": {"score": {"unit": "ratio"}},
    "plots": {"curve": {"model": "score", "scale": "risk", "termColors": {"high": "#8E44AD"}}}
  },
  "evaluations": {"quarter": {"model": "score", "inputs": {"risk": 0.25}, "trace": true}}
}'''
snapshot = LoadProject(projectJson)
yamlBytes = DumpProject(snapshot, formatName="yaml")
restored = LoadProject(yamlBytes, formatName="yaml")

assert DumpProject(restored, formatName="yaml") == yamlBytes
assert DumpProject(restored) == DumpProject(snapshot)

defaults = restored.defaults
assert defaults is not None
assert (defaults.modelId, defaults.plotId, defaults.evaluationId) == ("score", "curve", "quarter")
model = restored.SelectModel()
assert model.scales["risk"].termIds == ("middle", "high")
assert restored.units["score"]["unit"] == "ratio"
assert restored.plots["curve"].termColors["high"] == "#8E44AD"

scenario = restored.evaluations["quarter"]
assert scenario.trace
binding = model.inference
assert isinstance(binding, SugenoBinding)
result = binding.model.Evaluate({"Risk": scenario.inputs["risk"]})
assert result.value == 0.75
```

::: fuzzyroutines.project_configuration
    options:
      members:
        - LoadProject
        - DumpProject
        - ProjectSnapshot
        - ProjectDefaults
        - ProjectPlot
        - ProjectEvaluation
