<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 隶属函数 {#membership-functions}

专门的隶属函数模块负责标量解析公式，其不可变的可调用定义可直接传给 `ScalarFuzzySet`。`Triangle` 采用通常的 left、peak、right 顺序；`Trapezoid` 采用 left、plateau start、plateau end、right。历史 `MFunction` 标识符通过显式适配器保留原参数约定。

## 自定义标量求值器 {#custom-scalar-evaluators}

`MembershipCallable` 是自定义函数、lambda、绑定方法和可调用对象的带类型结构约定，不要求继承、包装或注册。求值器接受一个位置参数：有限的 `numbers.Real` 坐标；返回 `[0, 1]` 内的有限实数隶属度。输入和输出都排除布尔值。

在注解中，`MembershipScalar` 显式包含 `float | numbers.Real`；静态检查器也通过数值提升到 `float` 接受内置整数。这避免把运行时注册当作静态继承：在常见类型检查器中，单独使用 `numbers.Real` 并不接受普通 `float` 值。仅注解为 `float -> float` 的自定义函数缩小了更广的约定，无法保证支持每种实数标量。输入应使用 `MembershipScalar`，输出可使用该别名或 `float`。

构造 `ScalarFuzzySet` 时只检查可调用性，不执行函数。`Membership` 在调用前根据声明的论域验证坐标，再验证返回隶属度，不进行强制类型转换或截断。错误签名在调用时失败，自定义异常直接传播。该协议不提供运行时值验证或签名检查；直接调用自定义求值器时，采用它自身的验证行为。

```python
from fuzzyroutines.defuzzification import Centroid
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipCallable, MembershipScalar


def RisingGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a linear grade for coordinates in the closed unit interval."""

    return coordinate


membershipFunction: MembershipCallable = RisingGrade
fuzzySet = ScalarFuzzySet(
    ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
    membershipFunction,
)
centroid = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))
assert abs(centroid - 2 / 3) < 1e-12
```


质心为 `2 / 3`，通过显式有界积分域上的自适应数值积分求得。一般可调用对象不会因该协议而获得精确连续支集、核、高度或解析面积矩。函数必须对所选积分策略足够规则，并在求值期间保持隶属度一致。只要不改变隶属度，允许可变的记账行为，例如统计调用次数。不会自动创建可调用对象快照。可执行示例见 [`custom_membership.py`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/migration/custom_membership.py)。

可额外安装 mypy，复现隔离的静态调用方检查：

```bash
python -m mypy --python-version 3.13 --strict --follow-imports silent --warn-unused-ignores tests/typing/custom_membership.py
```


该检查涵盖内置浮点和整数调用、解析求值器及绑定方法，并拒绝过窄的输入类型、非数值结果和缺失的位置参数。通过 `--follow-imports silent` 有意隐藏导入模块的诊断，因为这里检查调用方约定。任务 #95 提供的更广泛的已安装包与源码类型检查，见[类型约定](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/public-typing.md)。这些注解不能证明运行时的有限性、布尔排除或隶属度范围。

## 应用示例 {#worked-examples}

[隶属函数图集](../../guides/membership-families.md)展示每个函数族；[自定义模型](../../guides/custom.md)使用带类型的可调用对象。

::: fuzzyroutines.membership
    options:
      members:
        - MembershipCallable
        - MembershipScalar
        - MembershipFunction
        - Hyperbolic
        - Bell
        - SShoulder
        - Triangle
        - Trapezoid
        - Gaussian
        - Logistic
        - HarringtonDesirability
