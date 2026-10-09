<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 维护历史接口集成 {#maintain-historical-integrations}

这些示例用于已有的 1.x 调用方。历史兼容入口为 `fuzzyroutines.FuzzyRoutines`；新集成应从不可变的[现代 API](../api/modern/index.md)开始。受支持的解释器仍是 Python 3.13 或 3.14。兼容性保留已审阅的调用方式和名称；[迁移说明](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/migration/1.0.3-to-2.0.0.md)解释数学修正和已移除的辅助对象导入。每个代码块都可独立运行，并针对已安装发行包测试。

## 解析范围并验证历史标量值 {#parse-ranges-and-validate-historical-scalar-values}

```python
from fuzzyroutines.FuzzyRoutines import DiapasonParser, IsCorrectFuzzyNumberValue, IsNumber

assert DiapasonParser("1-3,5,3") == [1, 2, 3, 5]
assert IsNumber(0.5) and not IsNumber(True)
assert IsCorrectFuzzyNumberValue(0.5) and not IsCorrectFuzzyNumberValue(1.5)
print(DiapasonParser("1-3,5,3"))
```


这些历史标量谓词接受内置 `int` 和 `float`，但排除布尔值。`IsNumber` 是类型谓词，不保证数值有限。对于格式错误的文本，解析器保留历史行为：输出诊断并返回空列表。如果项目不能接受空范围，应检查这一结果。

## 组合历史隶属度 {#combine-historical-grades}

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import (
    FuzzyAND, FuzzyNOT, FuzzyNOTParabolic, FuzzyOR,
    SCoNorm, SCoNormCompose, TNorm, TNormCompose,
)

assert FuzzyAND(0.4, 0.7) == 0.4 and FuzzyOR(0.4, 0.7) == 0.7
assert isclose(FuzzyNOT(0.4), 0.6) and isclose(FuzzyNOTParabolic(0.4), 0.6)
expectedAnd = {"logic": 0.4, "algebraic": 0.28, "boundary": 0.1, "drastic": 0}
expectedOr = {"logic": 0.7, "algebraic": 0.82, "boundary": 1, "drastic": 1}
for family in expectedAnd:
    assert isclose(TNorm(0.4, 0.7, normType=family), expectedAnd[family], abs_tol=1e-12)
    assert isclose(SCoNorm(0.4, 0.7, normType=family), expectedOr[family], abs_tol=1e-12)
assert isclose(TNormCompose(0.4, 0.7, 0.9, normType="algebraic"), 0.252)
assert isclose(SCoNormCompose(0.4, 0.7, 0.9, normType="algebraic"), 0.982)
print(TNormCompose(0.4, 0.7, 0.9, normType="algebraic"))
```


组合按从左到右的顺序折叠。一个有效操作数返回自身；零个操作数则失败。所有操作数和策略都要验证，包括一元情况。`FuzzyNOT` 是历史参数化否定，默认 α 为 0.5 时退化为标准补运算。抛物线适配器保留 `epsilon` 作为经过验证的兼容参数，但它不改变结果精度。

## 求值所有历史函数族与别名 {#evaluate-all-historical-membership-families-and-aliases}

```python
from math import exp, isclose
from fuzzyroutines.FuzzyRoutines import MFunction

cases = (
    ("hyperbolic", {"a": 1, "b": 2, "c": 0}, 1),
    ("bell", {"a": -2, "b": -1, "c": 1}, 1),
    ("parabolic", {"a": -2, "b": 2}, 0.5),
    ("triangle", {"a": -2, "b": 2, "c": 0}, 1),
    ("trapezium", {"a": -2, "b": 2, "c": -1, "d": 1}, 1),
    ("exponential", {"a": 0, "b": 1}, 1),
    ("sigmoidal", {"a": 2, "b": 0}, 0.5),
    ("desirability", {}, exp(-1)),
)
for family, parameters, expected in cases:
    model = MFunction(family, **parameters)
    assert isclose(model.mju(0), expected)
    assert model.name == model.mju.__name__ and model.parameters == parameters
for alias, canonical, parameters in (
    ("sShoulder", "parabolic", {"a": -2, "b": 2}),
    ("gaussian", "exponential", {"a": 0, "b": 1}),
    ("logistic", "sigmoidal", {"a": 2, "b": 0}),
    ("harringtonDesirability", "desirability", {}),
):
    assert MFunction(alias, **parameters).mju(0) == MFunction(canonical, **parameters).mju(0)
triangle = MFunction("triangle", a=0, b=2, c=1)
triangle.parameters = {"a": 0, "b": 4, "c": 2}
assert triangle.mju(2) == 1
print(triangle.name, triangle.parameters)
```


`mju` 绑定到所选函数族的公共方法：`Hyperbolic`、`Bell`、`Parabolic`、`Triangle`、`Trapezium`、`Exponential`、`Sigmoidal` 或 `Desirability`。调用时传入一个坐标。别名选择相同方法，不定义新的数学。历史三角形顺序为 **a = 左底点，b = 右底点，c = 峰值**；现代 `Triangle` 使用 **left, peak, right**。历史梯形使用 **a = 左底点，b = 右底点，c = 平台起点，d = 平台终点**；现代 `Trapezoid` 使用几何上的从左到右顺序。可变参数的 setter 会重新验证整个映射。替换 `mju` 后，不应期待内置解析证书仍然适用。

## 模型或窗口改变后重新计算可变集合 {#recompute-a-mutable-set-after-changing-its-model-or-window}

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

model = MFunction("triangle", a=0, b=2, c=1)
fuzzySet = FuzzySet(model, supportSet=(0, 2), linguisticName="Preferred")
assert fuzzySet.name == "Preferred" and fuzzySet.mFunction is model
assert fuzzySet.supportSet == (0, 2)
assert isclose(fuzzySet.Defuz(), 1) and isclose(fuzzySet.defuzValue, 1)
replacement = MFunction("triangle", a=0, b=4, c=2)
fuzzySet.name = "Updated preference"
fuzzySet.mFunction = replacement
fuzzySet.supportSet = (0, 4)
assert fuzzySet.mFunction is replacement and fuzzySet.name == "Updated preference"
assert isclose(fuzzySet.Defuz(), 2) and isclose(fuzzySet.defuzValue, 2)
print(fuzzySet.name, fuzzySet.Defuz())
```


虽然使用了历史名称，`supportSet` 实际上是有限的**积分窗口**，不是解析支集。`Defuz()` 使用已审阅的现代数值策略重新计算质心。读取 `defuzValue` 也会重新计算当前结果；两种访问方式都会反映模型和窗口的变化。`MFunction.accuracy` 为兼容而保留，不配置现代质心求积。

## 有意识地读取和替换尺度等级 {#read-and-replace-scale-levels-deliberately}

```python
from fuzzyroutines.FuzzyRoutines import FuzzyScale, FuzzySet, MFunction, UniversalFuzzyScale

first = FuzzySet(MFunction("triangle", a=0, b=2, c=1), supportSet=(0, 2))
second = FuzzySet(MFunction("triangle", a=0, b=2, c=1), supportSet=(0, 2))
scale = FuzzyScale()
scale.name = "Two identical preferences"
scale.levels = [{"name": "First", "fSet": first}, {"name": "Second", "fSet": second}]
assert scale.name == "Two identical preferences" and len(scale.levels) == 2
assert scale.Fuzzy(1)["name"] == "Second"
assert scale.GetLevelByName("First")["fSet"] is first
assert scale.GetLevelByName("SECOND", exactMatching=False)["fSet"] is second
universal = UniversalFuzzyScale()
assert len(universal.levels) == len(universal.levelsNames) == len(universal.levelsNamesUpper)
assert universal.Fuzzy(0.5)["name"] in universal.levelsNames
assert {name.upper() for name in universal.levelsNames} == set(universal.levelsNamesUpper)
print(scale.Fuzzy(1)["name"], tuple(universal.levelsNames))
```


历史并列选择偏向**后面的**等级；现代默认选择第一个词项，其他行为需通过显式策略指定。历史尺度总会返回一个胜出等级，包括零覆盖情况；现代结果可以拒绝选择。通用预设保留历史几何和已知覆盖限制。应诊断新的实际尺度，而不能把预设名称视为完整覆盖的证据。
