<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 异常 {#exceptions}

从 `fuzzyroutines.exceptions` 显式导入现代异常类别。`FuzzyRoutinesError` 捕获数学核心有意抛出的错误；原有的 `TypeError`、`ValueError` 和 `ArithmeticError` 处理器仍然有效。

| 类别                          | 含义                 | 内置处理类别                          |
| --------------------------- | ------------------ | ------------------------------- |
| `InvalidParameterTypeError` | 对象类型错误，包括布尔标量输入    | `TypeError`                     |
| `InvalidParameterError`     | 值、隶属度、函数族或策略违反约定   | `ValueError`                    |
| `InvalidDomainError`        | 区间几何、坐标顺序或论域之间存在冲突 | `ValueError`                    |
| `NumericalError`            | 数学操作无法确定结果         | `ArithmeticError`               |
| `UndefinedResultError`      | 零面积质心、零高度归一化或非有限结果 | `ValueError`, `ArithmeticError` |

`InvalidDomainError` 属于 `InvalidParameterError`。标量有限性检查使用 `InvalidParameterError`；域错误描述已通过其他验证的值之间的几何和关系问题。`UndefinedResultError` 属于 `NumericalError`，同时保留历史上用 `ValueError` 处理未定义结果的方式。[CentroidConvergenceError][fuzzyroutines.defuzzification.CentroidConvergenceError] 仍定义在 `fuzzyroutines.defuzzification` 中，保留现有根导出和对象身份；现在它既是 `NumericalError`，也是 `ArithmeticError`。

```python
from fuzzyroutines.domain import IntegrationDomain
from fuzzyroutines.exceptions import InvalidDomainError

try:
    IntegrationDomain(1.0, 0.0)

except InvalidDomainError:
    pass
```


用户隶属度求值器保留自己的异常对象，即使异常碰巧属于该层次结构。现代操作和历史质心适配器都不会包装任意回调失败。

历史隶属函数几何验证器保留具体的 `ValueError`。历史模糊集区间的构造函数和 setter 仅将自身的域验证失败显式转换为具体的 `TypeError` 或 `ValueError`。历史质心适配器仅对引擎的零面积和非有限结果检查选用具体的 `ValueError`，并原样保留回调异常和 `CentroidConvergenceError`。其他历史验证约定，包括文档记载的通用 `Exception` 错误，仍受兼容性保护。

## 应用示例 {#worked-examples}

[未定义结果处理](../../guides/api-recipes.md#handle-a-mathematically-undefined-result)展示零隶属面积。[错误处理示例](../../guides/errors.md)解释捕获关系和真实的自适应收敛失败。

::: fuzzyroutines.exceptions
    options:
      members:
        - FuzzyRoutinesError
        - InvalidParameterTypeError
        - InvalidParameterError
        - InvalidDomainError
        - NumericalError
        - UndefinedResultError
