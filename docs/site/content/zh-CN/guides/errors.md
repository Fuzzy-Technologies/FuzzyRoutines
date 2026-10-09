<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 处理无效输入与未解决的数值问题 {#handle-invalid-input-and-unresolved-mathematics}

捕获应用能够处理的异常类别。无效对象类型不同于无效值或无效域；未定义结果不同于数值细化耗尽。在日志和用户反馈中应保留这些区别。错误类别位于 `fuzzyroutines.exceptions`；`CentroidConvergenceError` 也属于解模糊 API。

## 理解类别层次 {#understand-the-category-hierarchy}

以下显式创建的实例用于展示捕获关系，并不声称触发了真实的积分失败。

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


`UndefinedResultError` 表示面积为零，或结果在所请求的操作中无法表示。它同时保留 `ValueError` 和数值异常的捕获约定。用户回调保留自己的异常；库不会将任意应用失败重新标记为自身的错误类别。

## 观察真实收敛失败，而不接受后备结果 {#observe-a-real-convergence-failure-without-accepting-a-fallback}

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


该平滑回调要求严格容差，但故意配置了不足的深度。实际项目应选择有依据的积分域和细化预算，再与独立参考结果核对。仅增加深度无法证明有限次求值发现了每个狭窄特征。零面积处理见 [API 示例](api-recipes.md#handle-a-mathematically-undefined-result)。
