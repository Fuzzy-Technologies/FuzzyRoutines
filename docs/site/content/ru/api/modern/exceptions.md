<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Исключения {#exceptions}

Импортируйте современные категории явно из `fuzzyroutines.exceptions`. `FuzzyRoutinesError` перехватывает ошибки, намеренно порождённые математическим ядром. Существующие обработчики `TypeError`, `ValueError` и `ArithmeticError` продолжают работать.

| Категория                   | Значение                                                                           | Встроенный обработчик           |
| --------------------------- | ---------------------------------------------------------------------------------- | ------------------------------- |
| `InvalidParameterTypeError` | Неверный тип объекта, включая логические скалярные входы                           | `TypeError`                     |
| `InvalidParameterError`     | Значение, степень, семейство или политика нарушают контракт                        | `ValueError`                    |
| `InvalidDomainError`        | Несогласованная геометрия интервала, порядок координат или универсальные множества | `ValueError`                    |
| `NumericalError`            | Математическая операция не может получить определённый результат                   | `ArithmeticError`               |
| `UndefinedResultError`      | Центроид нулевой площади, нормализация нулевой высоты или неконечный результат     | `ValueError`, `ArithmeticError` |

`InvalidDomainError` является `InvalidParameterError`. Проверки конечности скаляров используют `InvalidParameterError`; ошибки области описывают геометрию и отношения между значениями, прошедшими прочие проверки. `UndefinedResultError` является `NumericalError` и сохраняет исторические обработчики `ValueError` для неопределённых результатов. [CentroidConvergenceError][fuzzyroutines.defuzzification.CentroidConvergenceError] остаётся определённым в `fuzzyroutines.defuzzification`, сохраняет экспорт из корня и идентичность объекта; теперь это также `NumericalError`, как и `ArithmeticError`.

```python
from fuzzyroutines.domain import IntegrationDomain
from fuzzyroutines.exceptions import InvalidDomainError

try:
    IntegrationDomain(1.0, 0.0)

except InvalidDomainError:
    pass
```


Пользовательские вычислители принадлежности сохраняют собственные объекты исключений, даже если исключение относится к этой иерархии. Ни современные операции, ни исторические адаптеры центроида не оборачивают произвольные ошибки пользовательской функции.

Историческая проверка геометрии функции принадлежности сохраняет конкретный `ValueError`. Конструктор и сеттер исторического интервала нечёткого множества явно преобразуют только собственные ошибки проверки области в конкретные `TypeError` или `ValueError`. Исторический адаптер центроида выбирает конкретный `ValueError` только для проверок нулевой площади и неконечного результата в движке. Ошибки пользовательских функций и `CentroidConvergenceError` сохраняются без изменений. Остальные исторические контракты проверки, включая описанные общие ошибки `Exception`, защищены совместимостью.

## Практические примеры {#worked-examples}

[Обработка неопределённого результата](../../guides/api-recipes.md#handle-a-mathematically-undefined-result) показывает нулевую площадь принадлежности. [Рецепты обработки ошибок](../../guides/errors.md) объясняют отношения перехвата и настоящий отказ адаптивной сходимости.

::: fuzzyroutines.exceptions
    options:
      members:
        - FuzzyRoutinesError
        - InvalidParameterTypeError
        - InvalidParameterError
        - InvalidDomainError
        - NumericalError
        - UndefinedResultError
