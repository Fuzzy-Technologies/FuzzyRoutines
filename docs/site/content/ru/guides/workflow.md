<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# От модели к объяснённому результату {#from-a-model-to-an-explained-result}

Библиотека предоставляет явные строительные блоки. Начните с физического смысла, единиц и допустимого универсального множества, затем выберите модели принадлежности и операцию, отвечающую на ваш вопрос. Библиотека не придумывает правила, не калибрует пороги и не выбирает вычислительное ядро автоматически.

## Два пути современного API {#two-routes-through-the-modern-api}

```mermaid
flowchart TD
    U["Universe, units and model parameters"] --> M["Membership functions or a typed callback"]
    M --> F["ScalarFuzzySet"]
    F --> T["Named LinguisticTerm objects"]
    T --> S["LinguisticScale.Fuzzify with a selection policy"]
    S --> R["All grades, selected labels or abstention"]
    F --> C["Complement, Intersection, Union or Difference"]
    C --> D["Finite IntegrationDomain and CentroidPolicy"]
    D --> V["Centroid coordinate or an explicit numerical error"]
```


[Температурный пример](temperature.md) следует ветви классификации: одно физическое измерение оценивается относительно каждого именованного терма. [Пример центроида](centroid.md) следует ветви композиции: множества на общем универсальном множестве дают представительную координату в заданном конечном окне. Это разные вопросы, даже если исходная модель совпадает.

## Объединение отдельных измерений датчиков на уровне степеней {#combine-separate-sensor-measurements-at-the-grade-level}

```mermaid
flowchart TD
    A["Temperature measurement in °C"] --> B["Temperature membership grade"]
    C["Vibration measurement in mm/s"] --> D["Vibration membership grade"]
    B --> E["Chosen TNormPolicy or SNormPolicy"]
    D --> E
    E --> F["Combined grade with the policy recorded"]
```


Это [сценарий датчиков](sensors.md). Разные физические величины сохраняют собственные универсальные множества. Сначала вычислите степени, затем объедините их явной скалярной политикой. Пересечение на уровне множеств, напротив, оценивает множества в одной координате общего универсального множества. См. [сравнение операторов](operators.md).

## Граница исторического API {#the-historical-boundary}

```mermaid
flowchart TD
    A["Existing 1.x consumer"] --> B["fuzzyroutines.FuzzyRoutines facade"]
    B --> C["Mutable MFunction, FuzzySet and scale adapters"]
    D["New consumer"] --> E["Immutable modern models and explicit policies"]
    C --> F["Reviewed scalar mathematics and centroid engine"]
    E --> F
```


Фасад сохраняет проверенные имена и соглашения вызовов. Он оставляет изменяемую модель объектов, выбор последнего терма при равенстве максимумов и исторические имена вроде `supportSet` для окна интегрирования. Современные объекты явно задают универсальные множества и политики выбора, сравнения и интегрирования. Перед заменой существующего вызова прочитайте [исторические рецепты](historical-recipes.md): одинаковый математический замысел не гарантирует одинакового порядка параметров или обработки равных максимумов.

Схемы описывают текущие пути скалярного API. Необязательный прототип NumPy — экспериментальное сравнение нагрузок, а не автоматически выбираемая среда исполнения. [Записи результатов](results.md) сохраняют происхождение данных, а [обработка ошибок](errors.md) помогает отличать недопустимый ввод от неразрешённой математической задачи.
