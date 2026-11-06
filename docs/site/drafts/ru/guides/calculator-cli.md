<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Калькулятор для отдельной JSON-модели {#standalone-json-calculator}

Установленная команда `fuzzyroutines` проверяет отдельные JSON-модели v1,
вычисляет степень принадлежности, классифицирует координату и выполняет
скалярный вывод Мамдани или Сугено. На текущем этапе 2.2 доступны отдельные
модели в `.json`. Поддержка проектных файлов, YAML и графиков ведётся отдельно.

## Установка команды {#install}

В новом окружении CPython 3.13 или 3.14 задайте в `FUZZYROUTINES_WHEEL`
абсолютный путь к проверенному wheel с этой командой. Дополнение `config`
устанавливает валидатор схемы. Справка и версия работают и с базовым wheel,
выводят обычный текст в stdout. Версия берётся из метаданных пакета.

```bash
: "${FUZZYROUTINES_WHEEL:?Set the absolute path to the reviewed CLI wheel}"
python -m pip install "${FUZZYROUTINES_WHEEL}[config]"
fuzzyroutines --help
fuzzyroutines --version
```

## Файл модели {#model}

Сохраните модель Сугено в POSIX-оболочке. Кавычки защищают имя файла с
Unicode-символами и пробелом. Относительные пути отсчитываются от текущего
каталога.

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

Вершина треугольной функции находится в точке 0.5. В точке 0.25 степень
принадлежности равна 0.5. Если единственное правило срабатывает, модель
возвращает 0.25.

## Вычисления из командной строки {#evaluate}

Даже для отдельной модели путь передаётся через `--project`. Укажите
идентификаторы `risk` и `middle` с учётом регистра. `Middle` служит
подписью терма. Параметры `--model` и `--evaluation` для отдельной модели
не применяются.

```bash
fuzzyroutines validate --project 'модель α.json'
fuzzyroutines membership --project 'модель α.json' --scale risk --term middle --x 0.25
fuzzyroutines fuzzify --project 'модель α.json' --scale risk --x 0.25
fuzzyroutines infer --project 'модель α.json' --input 'risk=0.5'
```

Ниже по одной строке stdout на каждую команду. Ключи JSON упорядочены,
каждая строка заканчивается LF. Элементы массивов идут в порядке модели.

```json
{"command":"validate","result":{"kind":"model","schemaVersion":1},"resultVersion":1}
{"command":"membership","result":{"coordinate":0.25,"grade":0.5,"scale":"risk","term":"middle"},"resultVersion":1}
{"command":"fuzzify","result":{"confidence":0.5,"coordinate":0.25,"match":true,"memberships":[{"grade":0.5,"term":"middle"}],"scale":"risk","selectedTerms":["middle"],"tiedTerms":["middle"]},"resultVersion":1}
{"command":"infer","result":{"kind":"sugeno","method":"normalized-weighted-average","value":0.25},"resultVersion":1}
```

## Явное кодирование терма {#representatives}

Через `--term-input` укажите идентификатор терма на шкале входа и явно
задайте `--encoding representative-centroid`. Для симметричного
треугольника на заданном окне `[0, 1]` центр тяжести равен 0.5. Полученная
координата проходит те же проверки области определения, что и числовой
вход. Каждый вход можно задать один раз: числом или термом. Флаг `--explain`
добавляет степени принадлежности и сведения о срабатывании правил.

```bash
fuzzyroutines infer --project 'модель α.json' --term-input 'risk=middle' --encoding representative-centroid --explain
```

```json
{"command":"infer","result":{"kind":"sugeno","method":"normalized-weighted-average","trace":{"inputGrades":[{"grade":1.0,"input":"risk","term":"middle"}],"rules":[{"antecedentGrade":1.0,"consequentValue":0.25,"contribution":0.25,"firingStrength":1.0,"normalizedStrength":1.0,"rule":"balanced","weight":1.0}]},"value":0.25},"resultVersion":1}
```

## Обработка ошибок в скриптах {#errors}

Код завершения `0` означает успех. При ошибке stdout пуст, а в stderr
записывается один объект JSON. Для обработки используйте код завершения
и поле `error.category`. Текст сообщения может меняться.

- `2` (`usage`) — неверный параметр, число или привязка входа.
- `3` (`configuration`) — недопустимая или неподдерживаемая конфигурация.
  Кодек также возвращает `detailCategory` и указатель `pointer` по RFC 6901.
- `4` (`evaluation`) — выход за область определения, неопределённый
  представитель терма или отсутствие сработавших правил.
- `5` (`io`) — ошибка доступа к файлу.
- `6` (`capability`) — отсутствует необходимое дополнение.

В точке 0 степень принадлежности единственного терма равна нулю, поэтому
вывод завершается с кодом `4`.

```bash
fuzzyroutines infer --project 'модель α.json' --input 'risk=0'
```

```json
{"error":{"category":"evaluation","message":"inference is undefined because no rule fires"},"resultVersion":1}
```

В окружении с базовым wheel без `[config]` проверка корректной модели
завершается с кодом `6` и выдаёт такую диагностику.

```json
{"error":{"category":"capability","message":"Install fuzzyroutines[config] to validate model configuration."},"resultVersion":1}
```

После установки `[config]` повтор ключа `kind` в документе приводит к
коду `3`. Указатель показывает, в каком поле найден повтор.

```bash
printf '{"kind":"model","kind":"model"}\n' > 'ошибка α.json'
fuzzyroutines validate --project 'ошибка α.json'
```

```json
{"error":{"category":"configuration","detailCategory":"malformed-document","message":"Duplicate JSON object key.","pointer":"/kind"},"resultVersion":1}
```

Загрузка и сохранение моделей из Python описаны в
[справочнике API конфигурации](../../../content/ru/api/modern/configuration.md).
