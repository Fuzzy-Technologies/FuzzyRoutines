<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 从历史 API 迁移到现代 API 的示例 {#historical-to-modern-api-migration-examples}

- 状态：当前 `develop` 的实现边界
- 相关任务：#99
- 规范入口：[兼容与迁移](../../../../COMPATIBILITY.md)
- 兼容决策：[ADR-0001](../../../../adr/0001-backward-compatibility-contract.md)
- 精确实现边界：[当前状态](../../../../current-status.md)

## 迁移规则 {#migration-rule}

历史名称仍受支持。现有用户不必仅为采用版本 2 而重命名 `MFunction`、
`FuzzySet`、`FuzzyScale`、`UniversalFuzzyScale`、`Defuz` 或标量算子函数。
当专门 API 已提供应用所需行为时，再逐个领域迁移。

当前现代 API 覆盖显式域、不可变标量模糊集、集合代数、关系、派生属性、α 截集、
基于精确高度的归一化，以及带类型的语言术语和有序尺度表示。
专门的不可变隶属函数工厂也已通过 `fuzzyroutines.membership` 提供。
精确及 Unicode 不区分大小写的带类型尺度查找、显式模糊化策略均可用。
显式网格上的覆盖、重叠、空缺和分割诊断也可用，且不改变隶属函数系数。
现代质心解模糊化通过显式积分域与数值策略提供。
以下示例明确保留尚存的缺口，不虚构未来调用形式。

| 领域   | 历史 API 仍受支持                          | 当前可用的推荐路径                                                                       |
| ---- | ------------------------------------ | ------------------------------------------------------------------------------- |
| 算子   | `FuzzyNOT`、`TNorm`、`SCoNorm` 及组合函数   | `NegationPolicy`、`TNormPolicy` 和 `SNormPolicy`；集合操作要求显式策略                       |
| 隶属函数 | `MFunction` 及每个受保护的历史标识符             | `fuzzyroutines.membership` 中的不可变可调用工厂，包括常规顺序的 `Triangle` 和 `Trapezoid`          |
| 模糊集  | 可变 `FuzzySet` 及历史 `supportSet` 积分区间  | 不可变 `ScalarFuzzySet`，显式指定 `ContinuousUniverse` 或 `DiscreteUniverse`             |
| 尺度   | `FuzzyScale` 和 `UniversalFuzzyScale` | 通过 `LinguisticScale` 提供带类型表示、查找、模糊化和采样诊断                                        |
| 派生操作 | 没有等价的统一现代接口                          | `DeriveProperties`、`AlphaCut`、`SampleAlphaCut`、`Height` 和 `Normalize` 保留显式精确性边界 |
| 解模糊化 | `FuzzySet.Defuz()` 和 `defuzValue`    | `Centroid()`，显式指定 `ScalarFuzzySet`、`IntegrationDomain` 及可选 `CentroidPolicy`     |

## 算子 {#operators}

历史标量调用通过字符串选择函数族：

```python
from fuzzyroutines.FuzzyRoutines import FuzzyNOT, SCoNorm, TNorm

conjunction = TNorm(0.4, 0.7, normType="algebraic")
disjunction = SCoNorm(0.4, 0.7, normType="logic")
negated = FuzzyNOT(0.4)
```

现代标量及模糊集路径将所选策略表示为不可变值：

```python
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

conjunction = TNormPolicy("algebraic").Evaluate(0.4, 0.7)
disjunction = SNormPolicy("logic").Evaluate(0.4, 0.7)
negated = NegationPolicy("standard").Evaluate(0.4)
```

`TNormCompose` 和 `SCoNormCompose` 尚无专门的现代对应函数。
需要 n 元组合时保留这些历史名称，不要替换为未记录的 API。

## 隶属函数 {#membership-functions}

历史工厂及参数约定仍是可执行 API：

```python
from fuzzyroutines.FuzzyRoutines import MFunction

# Historical order is preserved: a = left foot, c = apex, b = right foot.
membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
grade = membershipFunction.mju(0.25)
```

新代码应直接使用不可变现代可调用对象：

```python
from fuzzyroutines import ContinuousUniverse, ScalarFuzzySet
from fuzzyroutines.membership import Triangle

membershipFunction = Triangle(left=0.0, peak=0.5, right=1.0)
universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction)
```

附加注册表名称 `gaussian`、`logistic`、`sShoulder` 和 `harringtonDesirability`
可用，但迁移不要求重命名 `exponential`、`sigmoidal`、`parabolic` 或 `desirability`。
更改任何标识符之前，请参阅[隶属函数契约](../../../../mathematics/membership-function-contracts.md)，
因为某些历史参数顺序有意保留。

现代 `Triangle(left, peak, right)` 契约有意不同于
历史 `MFunction("triangle", a=left, b=right, c=peak)`。
同样，现代 `Trapezoid(left, plateauStart, plateauEnd, right)`
不同于历史 `trapezium` 的关键字映射。
不要在 API 之间直接传递位置参数元组，必须显式转换。
共享标量公式保留已接受的历史边界，包括现有高值三角形术语的 `peak == right`。

早期 v2 开发快照将平台参数命名为 `plateau_start` 和 `plateau_end`。
现在，`Bell`、`Trapezoid` 以及 `MembershipFunction` 只读参数映射中的规范名称为
`plateauStart` 和 `plateauEnd`。
构造函数和直接函数族构造仍在运行时接受旧关键字拼写；
同时指定别名及规范拼写会被拒绝。位置顺序、参数含义和数值结果不变。
新代码及静态类型使用规范 camelCase 名称。

## 模糊集 {#fuzzy-sets}

历史构造将隶属函数对象、可变名称和历史称为 `supportSet` 的元组组合起来：

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(
    membershipFunction,
    supportSet=(0.0, 1.0),
    linguisticName="Medium",
)
```

对于新的集合代数，单独声明论域，并传入隶属函数可调用对象：

```python
from fuzzyroutines import (
    Complement,
    ContinuousUniverse,
    NegationPolicy,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
membershipFunction = Triangle(left=0.0, peak=0.5, right=1.0)
fuzzySet = ScalarFuzzySet(universe, membershipFunction)
complement = Complement(fuzzySet, NegationPolicy("standard"))

assert complement.Membership(0.25) == 0.5
```

`ScalarFuzzySet` 没有语言名称字段，也没有数值积分区间。
`IntegrationDomain` 是独立操作值，不是数学支集。

## 尺度 {#scales}

继续使用受保护的历史类：

```python
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

scale = UniversalFuzzyScale()
level = scale.Fuzzy(0.5)
assert level["name"] == "Med"
```

现代 API 可以表示名称、模糊集及显式术语顺序，不会静默继承历史字典形状：

```python
from fuzzyroutines import FuzzificationPolicy, LinguisticScale, LinguisticTerm

modernScale = LinguisticScale((LinguisticTerm("Medium", fuzzySet),))
term = modernScale.GetTermByName("medium", exactMatching=False)
result = modernScale.Fuzzify(
    0.5,
    FuzzificationPolicy(tiePolicy="last", minimumConfidence=0.05),
)
```

现代查找仅匹配完整名称。默认模式精确且区分大小写；
`exactMatching=False` 使用 Unicode 不区分大小写比较。
它不执行模糊、前缀或子串名称匹配。
现代 `Fuzzify()` 返回所有有序隶属度分数，并以最大分数作为置信度。
其策略显式指定无匹配阈值、并列容差，以及 `first`、`last` 或 `all` 选择。
历史调用者可以保留 `FuzzyScale` 或 `UniversalFuzzyScale`；
`tiePolicy="last"` 提供历史后者胜出规则的现代等价方式，而不改变 `Fuzzy()`。

## 解模糊化 {#defuzzification}

现有代码可以继续使用会重新计算的兼容入口：

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))
centroid = fuzzySet.Defuz()
```

`Defuz()` 现在使用现代解析/自适应策略，忽略保留的兼容属性 `MFunction.accuracy`。
历史 `supportSet` 元组是有限数值积分区间，不是精确支集。
新代码可以显式表达相同操作：

```python
from fuzzyroutines import Centroid, ContinuousUniverse, IntegrationDomain, ScalarFuzzySet

integrationDomain = IntegrationDomain.FromLegacyInterval(fuzzySet.supportSet)
modernSet = ScalarFuzzySet(ContinuousUniverse(), membershipFunction.mju)
centroid = Centroid(modernSet, integrationDomain)
```

关于解析函数族、自适应容差、零面积行为和收敛失败，参见
[质心解模糊化](../../../../mathematics/centroid-defuzzification.md)。

## 可执行示例 {#executable-examples}

两个示例仅导入包的公共入口，不操作源代码树路径：

```bash
python examples/migration/historical_compatibility.py
python examples/migration/modern_supported.py
```

- [`historical_compatibility.py`](../../../../../examples/migration/historical_compatibility.py)
  检查全部五个历史领域。
- [`modern_supported.py`](../../../../../examples/migration/modern_supported.py)
  检查显式算子策略和不可变模糊集，明确使用专门的不可变隶属函数工厂，
  不导入历史模块。

示例测试从临时工作目录运行每个脚本。
包工作流独立安装 wheel 和源代码分发包，移除 `PYTHONPATH`，
确认导入来源位于干净环境中，并通过 shell 可见的入口运行相同脚本。
完整产物及退出码契约见
[`Executable Tests, Tools, Benchmarks, and Examples`](../../../../executable-tests-tools-and-examples.md)。
