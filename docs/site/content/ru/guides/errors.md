<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Недопустимые входы и неразрешённые численные задачи {#handle-invalid-input-and-unresolved-mathematics}

Перехватывайте категории, которые приложение умеет обработать. Недопустимые типы объектов отличаются от недопустимых значений и областей; неопределённый результат — от исчерпания численного уточнения. Сохраняйте эти различия в журнале и сообщениях пользователю. Категории находятся в `fuzzyroutines.exceptions`; `CentroidConvergenceError` также относится к API дефаззификации.

## Иерархия категорий {#understand-the-category-hierarchy}

Следующие явно созданные экземпляры демонстрируют отношения перехвата; они не имитируют фактически возникший сбой интегрирования.

```python
from fuzzyroutines import CentroidConvergenceError
from fuzzyroutines.exceptions import (
    FuzzyRoutinesError, InvalidDomainError, InvalidParameterError,
    InvalidParameterTypeError, NumericalError, UndefinedResultError,
)

errors = (
    FuzzyRoutinesError("project error"), InvalidParameterTypeError("wrong kind"),
    InvalidParameterError("invalid value"), InvalidDomainError("invalid domain"),
    NumericalError("unresolved calculation"), UndefinedResultError("undefined result"),
    CentroidConvergenceError("refinement exhausted"),
)
assert all(isinstance(error, FuzzyRoutinesError) for error in errors)
assert isinstance(errors[1], TypeError) and isinstance(errors[2], ValueError)
assert isinstance(errors[3], InvalidParameterError)
assert isinstance(errors[5], ValueError) and isinstance(errors[5], NumericalError)
assert isinstance(errors[6], ArithmeticError)
print(tuple(type(error).__name__ for error in errors))
```


`UndefinedResultError` обозначает нулевую площадь или результат, который невозможно представить для запрошенной операции. Он сохраняет контракты перехвата как `ValueError`, так и численных ошибок. Пользовательские функции сохраняют собственные исключения; библиотека не переименовывает произвольные ошибки приложения в свои категории.

## Настоящий отказ сходимости без запасного результата {#observe-a-real-convergence-failure-without-accepting-a-fallback}

```python
from math import exp
from fuzzyroutines import (
    Centroid, CentroidConvergenceError, CentroidPolicy, ContinuousUniverse,
    IntegrationDomain, ScalarFuzzySet,
)


def DecayingGrade(coordinate: float) -> float:
    """Return a smooth valid grade on the declared nonnegative interval."""

    return exp(-coordinate)


fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True), DecayingGrade)
policy = CentroidPolicy(absoluteTolerance=1e-14, relativeTolerance=1e-14, maximumDepth=1)
try:
    Centroid(fuzzySet, IntegrationDomain(0, 1), policy)
except CentroidConvergenceError:
    print("Refinement exhausted: revise the domain or numerical policy")
else:
    raise AssertionError("the deliberately shallow integration unexpectedly converged")
```


Гладкая функция запрашивает строгие допуски при намеренно недостаточной глубине. В реальном проекте следует обосновать область и бюджет уточнения, затем проверить результат по независимому эталону. Одно лишь увеличение глубины не доказывает, что конечные вычисления обнаружили каждую узкую особенность. Обработка нулевой площади показана в [рецепте API](api-recipes.md#handle-a-mathematically-undefined-result).
