<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 独立 JSON 模型计算器 {#standalone-json-calculator}

安装后可使用 `fuzzyroutines` 命令验证独立的 v1 JSON 模型、计算单个隶属度、
对坐标进行分类，或运行标量 Mamdani、Sugeno 推理。当前 2.2 检查点支持独立的
`.json` 模型。项目文件、YAML 和绘图命令另行跟踪。

## 安装命令 {#install}

在新的 CPython 3.13 或 3.14 环境中，将 `FUZZYROUTINES_WHEEL` 设为包含该命令的
已审阅 wheel 的绝对路径。通过 `config` 可选依赖安装模式验证器。
基础 wheel 也能将帮助和版本以纯文本写入 stdout。版本来自 wheel 的元数据。

```bash
: "${FUZZYROUTINES_WHEEL:?Set the absolute path to the reviewed CLI wheel}"
python -m pip install "${FUZZYROUTINES_WHEEL}[config]"
fuzzyroutines --help
fuzzyroutines --version
```

## 创建模型文件 {#model}

在 POSIX shell 中保存下面的 Sugeno 模型。文件名含 Unicode 字符和空格，请保留引号。
相对路径以当前工作目录为基准。

```bash
cat > 'модель α.json' <<'JSON'
{
  "kind": "model",
  "schemaVersion": 1,
  "universes": {"unit": {"kind": "continuous", "left": 0, "right": 1, "leftClosed": true, "rightClosed": true}},
  "memberships": {"triangle": {"family": "triangle", "parameters": {"left": 0, "peak": 0.5, "right": 1}}},
  "scales": {
    "risk": {
      "universe": "unit",
      "terms": [{"id": "middle", "name": "Middle", "membership": "triangle"}],
      "representatives": {
        "windows": {"middle": {"left": 0, "right": 1}},
        "policy": {"absoluteTolerance": 1e-12, "relativeTolerance": 1e-10, "maximumDepth": 20}
      }
    }
  },
  "inference": {
    "kind": "sugeno",
    "inputs": [{"id": "risk", "name": "Risk", "scale": "risk"}],
    "policy": {"conjunction": "logic", "disjunction": "logic", "negation": {"family": "standard"}},
    "rules": [{
      "id": "balanced",
      "name": "Balanced",
      "antecedent": {"kind": "term", "input": "risk", "term": "middle"},
      "consequent": {"kind": "constant", "value": 0.25},
      "weight": 1
    }],
    "outputUniverse": "unit"
  }
}
JSON
```

三角隶属函数在 0.5 处达到峰值，在 0.25 处的隶属度为 0.5。唯一的规则一旦触发，
模型就返回 0.25。

## 运行命令 {#evaluate}

即使文件只包含一个独立模型，也要用 `--project` 指定它。使用区分大小写的 ID
`risk` 和 `middle`，其中 `Middle` 是语言项的显示名称。独立模型无需且不接受
`--model` 或 `--evaluation`。

```bash
fuzzyroutines validate --project 'модель α.json'
fuzzyroutines membership --project 'модель α.json' --scale risk --term middle --x 0.25
fuzzyroutines fuzzify --project 'модель α.json' --scale risk --x 0.25
fuzzyroutines infer --project 'модель α.json' --input 'risk=0.5'
```

下方按命令顺序列出 stdout 的结果，每条命令输出一行。JSON 键按顺序排列，
每行以 LF 结尾。数组元素保留模型中的顺序。

```json
{"command":"validate","result":{"kind":"model","schemaVersion":1},"resultVersion":1}
{"command":"membership","result":{"coordinate":0.25,"grade":0.5,"scale":"risk","term":"middle"},"resultVersion":1}
{"command":"fuzzify","result":{"confidence":0.5,"coordinate":0.25,"match":true,"memberships":[{"grade":0.5,"term":"middle"}],"scale":"risk","selectedTerms":["middle"],"tiedTerms":["middle"]},"resultVersion":1}
{"command":"infer","result":{"kind":"sugeno","method":"normalized-weighted-average","value":0.25},"resultVersion":1}
```

## 显式编码语言项 {#representatives}

`--term-input` 按输入量表中的 ID 选择语言项，并要求指定
`--encoding representative-centroid`。在已声明的 `[0, 1]` 窗口上，
该对称三角形的质心为 0.5。编码后的坐标与数值输入采用相同的论域验证。
每个输入只能绑定一次，可选用数值或语言项。加上 `--explain` 可查看按顺序记录的
隶属度和规则触发详情。

```bash
fuzzyroutines infer --project 'модель α.json' --term-input 'risk=middle' --encoding representative-centroid --explain
```

```json
{"command":"infer","result":{"kind":"sugeno","method":"normalized-weighted-average","trace":{"inputGrades":[{"grade":1.0,"input":"risk","term":"middle"}],"rules":[{"antecedentGrade":1.0,"consequentValue":0.25,"contribution":0.25,"firingStrength":1.0,"normalizedStrength":1.0,"rule":"balanced","weight":1.0}]},"value":0.25},"resultVersion":1}
```

## 在脚本中处理错误 {#errors}

退出码 `0` 表示成功。失败时 stdout 为空，stderr 只写入一个 JSON 对象。
根据退出码和 `error.category` 处理错误，诊断消息的文字可能变化。

- `2`（`usage`）：选项、数值或输入绑定无效。
- `3`（`configuration`）：配置无效或不受支持。编解码器还会提供
  `detailCategory` 和 RFC 6901 `pointer`。
- `4`（`evaluation`）：坐标超出论域、代表值未定义或没有规则触发。
- `5`（`io`）：文件访问失败。
- `6`（`capability`）：缺少所需的可选功能。

在坐标 0 处，唯一的语言项隶属度为零，因此推理以代码 `4` 退出。

```bash
fuzzyroutines infer --project 'модель α.json' --input 'risk=0'
```

```json
{"error":{"category":"evaluation","message":"inference is undefined because no rule fires"},"resultVersion":1}
```

如果只安装了基础 wheel，没有安装 `[config]`，验证有效模型时会以代码 `6` 退出，
并写入以下诊断。

```json
{"error":{"category":"capability","message":"Install fuzzyroutines[config] to validate model configuration."},"resultVersion":1}
```

安装 `[config]` 后，文档中的重复 `kind` 键会导致退出码 `3`。
指针指向重复字段。

```bash
printf '{"kind":"model","kind":"model"}\n' > 'ошибка α.json'
fuzzyroutines validate --project 'ошибка α.json'
```

```json
{"error":{"category":"configuration","detailCategory":"malformed-document","message":"Duplicate JSON object key.","pointer":"/kind"},"resultVersion":1}
```

如需在 Python 中加载或保存模型，请参阅
[JSON 配置 API](../../../content/zh-CN/api/modern/configuration.md)。
