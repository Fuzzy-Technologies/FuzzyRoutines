<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Переносимая конфигурация нечёткого проекта

Функции `LoadProject` и `DumpProject` загружают и сохраняют снимок
проекта по схеме v1. В снимок входят именованные модели, настройки по
умолчанию, подписи единиц измерения, параметры графиков и сценарии
вычислений. Для отдельной модели используйте
[`LoadModel` и `DumpModel`](configuration.md).

## Преобразование документов с сохранением записи чисел

Для преобразования проектных документов установите `fuzzyroutines[config,yaml]`.
Опция `[yaml]` подключает парсер, а `[config]` добавляет проверку по локальной
схеме v1. Обе функции принимают и возвращают байты UTF-8 с ограничением размера.
Файлы открывает и сохраняет вызывающий код. При преобразовании проверяется
схема и разрешаются ссылки внутри проекта. Вывод и сценарии не запускаются.

YAML допускает один документ данных со строковыми ключами. Повторяющиеся
ключи, явные теги, якоря, псевдонимы и ключи слияния вызывают
[`ConfigurationError`](configuration.md).
Неизвестная версия или поле `include` не проходят проверку. Ошибка содержит
категорию и указатель JSON Pointer. Числовая запись и порядок элементов массивов
сохраняются, ключи сортируются, исходный документ остаётся прежним.

Пример преобразует проект с треугольной шкалой в обе стороны. Знак нуля и
экспоненциальная запись числа сохраняются.

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

## Загрузка и сохранение снимка проекта

Для JSON установите `fuzzyroutines[config]`, для работы с YAML —
`fuzzyroutines[config,yaml]`. Чтобы прочитать или получить байты YAML,
передайте `formatName="yaml"`. По умолчанию используется JSON. При
загрузке и сохранении действует одна и та же встроенная схема v1.
Настройки отображения хранятся отдельно от параметров моделей. При
загрузке проверяются ссылки во всём проекте, а вычисление вывода и
построение графиков выполняются отдельными вызовами. Обе функции
работают с байтами. Пути выбирает и файлы открывает вызывающий код.
В документе v1 отсутствуют директивы включения, внешние ссылки и
пути к выходным файлам.

Идентификаторы моделей чувствительны к регистру. Вызов
`SelectModel("score")` выбирает модель с этим идентификатором.
`SelectModel()` использует явно заданную модель по умолчанию. Если
она не задана, возникает `KeyError`, даже когда в проекте одна модель.

Пример проверяет воспроизводимость экспорта в каждом формате. После
загрузки из YAML проверяем порядок термов, подпись единицы измерения,
цвет на графике и сохранённый вход. Затем отдельно вычисляем вывод.
Единственное правило Сугено срабатывает на сохранённом входе и даёт
результат `0.75`.

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
