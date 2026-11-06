<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Конфигурация проекта в YAML

Для преобразования проектных документов установите `fuzzyroutines[config,yaml]`.
Опция `[yaml]` подключает парсер, а `[config]` добавляет проверку по локальной
схеме v1. Обе функции принимают и возвращают байты UTF-8 с ограничением размера.
Файлы открывает и сохраняет вызывающий код. При преобразовании проверяется
схема и разрешаются ссылки внутри проекта. Вывод и сценарии не запускаются.

YAML допускает один документ данных со строковыми ключами. Повторяющиеся
ключи, явные теги, якоря, псевдонимы и ключи слияния вызывают
[`ConfigurationError`](configuration.md#fuzzyroutines.configuration.ConfigurationError).
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
