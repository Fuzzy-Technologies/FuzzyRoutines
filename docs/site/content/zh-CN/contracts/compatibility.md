<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 兼容性与迁移 {#compatibility-and-migration}

- 状态：为 `2.0.0` 发布候选准备的契约
- 主导决策：[ADR-0001](../../../../adr/0001-backward-compatibility-contract.md)
- 已观察的 1.0.3 接口：[历史公共 API 快照](../../../../compatibility/legacy-public-api-1.0.3.md)
- 已实现的 v2 接口：[公共 API 清单](../../../../public-api-documentation-inventory.md)
- 发布版专属变化：[从 1.0.3 到计划中 2.0.0 的迁移说明](../../../../migration/1.0.3-to-2.0.0.md)

本页是选择 API 接口及推进现有 FuzzyRoutines 代码的规范入口。
它区分 ADR-0001 保护的狭窄契约与目前仍实现并测试的更广泛 1.0.3 接口。
两类都不保留已知的数学、数值、验证或陈旧状态缺陷。

## 选择接口 {#choose-a-surface}

| 情况            | 受支持入口                         | 建议                                  |
| ------------- | ----------------------------- | ----------------------------------- |
| 现有 1.0.3 风格应用 | `fuzzyroutines.FuzzyRoutines` | 在专门的现代路径覆盖应用全部所需行为之前，保留历史调用。        |
| 具有显式数学契约的新代码  | `fuzzyroutines` 根导出           | 优先使用不可变论域、模糊集、策略、结果类型及显式数值域。        |
| 增量迁移          | 现代根导出及选定兼容对象                  | 每次迁移一项操作；目前支持将 `MFunction` 作为可调用来源。 |

新代码推荐使用现代包 API，但它不是要求现有调用者强制重命名的层。
除非后续获批 ADR 有意更改契约，否则历史名称继续按
[ADR-0001](../../../../adr/0001-backward-compatibility-contract.md) 受到支持。

## ADR 保护的历史契约 {#adr-protected-historical-contract}

ADR-0001 保护 `fuzzyroutines` 和 `fuzzyroutines.FuzzyRoutines` 的可导入性。
历史符号从后者导入：

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction, TNorm
```

受保护的符号及行为契约包括：

- 算子 `FuzzyNOT`、`FuzzyNOTParabolic`、`FuzzyAND`、`FuzzyOR`、`TNorm`、
  `TNormCompose`、`SCoNorm` 和 `SCoNormCompose`；
- 类 `MFunction`、`FuzzySet`、`FuzzyScale` 和 `UniversalFuzzyScale`；
- 已记录的方法 `Defuz()`、`Fuzzy()` 和 `GetLevelByName()`；
- 历史隶属函数标识符 `hyperbolic`、`bell`、`parabolic`、`triangle`、
  `trapezium`、`exponential`、`sigmoidal` 和 `desirability`；
- [隶属函数契约](../../../../mathematics/membership-function-contracts.md)
  记录的历史关键字名称、参数含义及顺序。

移除或更改此契约需要显式替代或修订 ADR，并提供消费者影响依据。
精确签名记录在 [1.0.3 快照](../../../../compatibility/legacy-public-api-1.0.3.md) 中，
由 [`test_legacy_public_api.py`](../../../../../tests/test_legacy_public_api.py)
和 [`test_legacy_import_compatibility.py`](../../../../../tests/test_legacy_import_compatibility.py) 强制检查。

## 当前支持的已观察接口 {#currently-supported-observed-surface}

当前兼容门面还实现并测试以下已观察到的 1.0.3 名称：

- 工具 `DiapasonParser`、`IsNumber` 和 `IsCorrectFuzzyNumberValue`；
- `MFunction` 成员 `name`、`parameters`、`mju`、`accuracy`、`Hyperbolic()`、`Bell()`、
  `Parabolic()`、`Triangle()`、`Trapezium()`、`Exponential()`、`Sigmoidal()` 和 `Desirability()`；
- `FuzzySet` 属性 `name`、`mFunction`、`supportSet` 和 `defuzValue`；
- `FuzzyScale` 属性 `name` 和 `levels`；
- `UniversalFuzzyScale` 属性 `levelsNames` 和 `levelsNamesUpper`。

这些名称由当前实现和回归套件支持，但 ADR-0001 并未独立授予每个列出的工具或属性
与上述显式契约相同的长期保护。[历史快照](../../../../compatibility/legacy-public-api-1.0.3.md)
记录这一更广泛接口，使未来兼容决策能够评估迁移影响，而不是静默假定或丢弃它。
通过历史通配符导入意外可见的辅助模块不属于项目 API 符号。
当前门面将 `__all__` 精确定义为十五个受支持函数和类；`math` 和 `copy` 不再由门面导入。
若旧代码依赖这一泄漏，请直接导入这些标准库模块。

`sShoulder`、`gaussian`、`logistic` 和 `harringtonDesirability` 是接受的附加 `MFunction` 标识符。
它们选择对应历史标识符的同一实现，只是可选便利名称，不是现有调用者必须采用的替代名称。

## 当前可用的现代路径 {#modern-paths-available-now}

| 需求       | 历史路径                               | 已实现的现代路径                                                                               | 边界                                     |
| -------- | ---------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------- |
| 二元标量算子   | `FuzzyNOT`、`TNorm`、`SCoNorm`       | `NegationPolicy`、`TNormPolicy`、`SNormPolicy`                                           | 策略对象公开 `Evaluate()`，且不可变。              |
| 可变参数标量组合 | `TNormCompose`、`SCoNormCompose`    | 无专门的 n 元替代                                                                             | 需要 n 元折叠时保留历史函数。                       |
| 隶属函数     | `MFunction`                        | `MembershipFunction`、`Triangle` 等语义工厂及 `MembershipCallable`                            | 现代工厂使用显式几何；`MFunction.mju` 仍为受支持可调用对象。 |
| 模糊集表示    | 可变 `FuzzySet`                      | `ScalarFuzzySet` 配合 `ContinuousUniverse` 或 `DiscreteUniverse`                          | `supportSet` 是积分区间，不是数学论域或精确支集。        |
| 集合代数     | 调用者代码应用标量算子                        | 带显式策略对象的 `Complement`、`Intersection`、`Union` 和 `Difference`                            | 二元操作要求论域精确兼容。                          |
| 集合派生信息   | 无统一历史结果                            | `DeriveProperties`、`SampleProperties`、`AlphaCut`、`SampleAlphaCut`、`Height`、`Normalize` | 精确依据和采样依据使用不同结果契约。                     |
| 关系       | 无专门历史接口                            | `EqualOnDomain`、`IncludedOnDomain`、`ComparisonPolicy`、`ComparisonDomain`               | 比较容差和检查域显式给出。                          |
| 语言表示     | `FuzzyScale`、`UniversalFuzzyScale` | `LinguisticTerm`、`LinguisticScale`、模糊化及采样诊断结果类型                                        | 查找、分数、置信度、并列策略及采样诊断均显式。                |
| 质心解模糊化   | `FuzzySet.Defuz()`、`defuzValue`    | `Centroid` 配合 `ScalarFuzzySet`、`IntegrationDomain` 及可选 `CentroidPolicy`                | 积分区间显式且有限。                             |

[`fuzzyroutines/__init__.py`](../../../../../fuzzyroutines/__init__.py) 中的根包导出列表
是判断已实现现代符号的权威依据。[当前实现状态](../../../../current-status.md)
将此接口与路线图工作区分开。

## 已修正行为不属于兼容承诺 {#corrected-behavior-is-not-a-compatibility-promise}

兼容契约保留有效用法，不保留缺陷结果。
因此，以下已实现修正可以改变失败方式或输出，同时保留历史名称和调用形式：

| 修正领域    | 当前行为                               |
| ------- | ---------------------------------- |
| 二元标量算子  | 拒绝无效、非有限和布尔操作数；选择函数族的函数拒绝未知函数族。    |
| 可变参数组合  | 对空输入、无效操作数和未知算子族显式抛出 `ValueError`。 |
| 参数化否定   | 强制执行已证明的参数域；抛物型否定使用有界解析分支。         |
| 隶属函数构造  | 要求准确的有限参数集合和有效函数族几何。               |
| Bell 求值 | 不修改调用者可见的参数映射。                     |
| 质心状态    | 根据当前隶属函数参数及积分边界重新计算，不返回陈旧状态。       |
| 尺度查找    | 每个术语求值一次，保留文档规定的较后术语胜出策略。          |
| 尺度名称    | 要求两个字典键，并一致拒绝不区分大小写查找时冲突的名称。       |

[已修复错误台账](../../../../compatibility/corrected-bug-ledger.md) 提供变化历史及合并依据。
未来修正必须加入该台账；有意移除或修改签名则要求 ADR-0001 规定的显式 ADR
及消费者影响流程。已知下游依据单独记录在[消费者清单](../../../../compatibility/legacy-consumers.md) 中。

## 迁移示例 {#migration-examples}

现有代码仍有效：

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))
centroid = fuzzySet.Defuz()
```

同一隶属函数定义可通过 `MFunction.mju` 连接已实现的现代集合及解模糊化契约。
新代码也可改用已提供的不可变现代 `Triangle` 工厂；
[详细指南](../../../../migration/historical-to-modern.md#membership-functions) 展示其不同参数约定：

```python
from fuzzyroutines import Centroid, ContinuousUniverse, IntegrationDomain, ScalarFuzzySet
from fuzzyroutines.FuzzyRoutines import MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction.mju)
centroid = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))
```

按领域划分的详细说明见[历史到现代迁移指南](../../../../migration/historical-to-modern.md)。
其完整可执行场景为：

- [`historical_compatibility.py`](../../../../../examples/migration/historical_compatibility.py)；
- [`modern_supported.py`](../../../../../examples/migration/modern_supported.py)。

针对已安装包运行：

```console
python examples/migration/historical_compatibility.py
python examples/migration/modern_supported.py
```

[`test_migration_examples.py`](../../../../../tests/test_migration_examples.py) 验证导入及确定性结果。
仓库文档检查还验证本页的本地链接和 Markdown 表格对齐。
