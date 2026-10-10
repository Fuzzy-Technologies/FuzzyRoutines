<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 快速入门 {#quick-start}

计算测得的温度对各语言概念的隶属度，再选择标签。FuzzyRoutines 提供标量模糊集、八类隶属函数、显式组合策略、语言尺度、α-截集和连续模型的质心。现代 API 要求 **CPython 3.13 或 3.14**，不强制依赖 NumPy 或绘图库。

## 安装 {#install}

创建隔离环境：

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

对于 PyPI 上的稳定版 2.0.0 软件包：

```bash
python -m pip install fuzzyroutines==2.0.0
```

较早的 1.x 版本不提供此现代 API。

开发时，或候选版本尚未发布时，请改为从已审阅的 Git 修订安装：

```bash
python -m pip install "fuzzyroutines @ git+https://github.com/Fuzzy-Technologies/FuzzyRoutines.git@develop"
```

此命令需要 Git，并跟随持续变化的 `develop` 分支。为了复现实验，请将 `develop` 替换为已审阅提交的完整 SHA。这里使用的现代公共 API 已在提交 `bd239d2b0972a796c4084498676042bdb7016bed` 中提供。准备好候选版本本身并不表示 PyPI 发布已经完成。

## 用几行代码完成测量与分类 {#measure-and-classify-in-a-few-lines}

假设室温为 24 °C。我们用一个示意三角形定义 *Comfort*：在 22 °C 时完全隶属，在 16 和 28 °C 时隶属度为零。*Warm* 在 22 至 30 °C 之间平滑上升。应与了解应用领域的人员一起选择这些阈值；它们是模型假设，并非由库训练得到的参数。

```python
from math import isclose
from fuzzyroutines import (
    ContinuousUniverse, LinguisticScale, LinguisticTerm,
    ScalarFuzzySet, SShoulder, Triangle,
)

universe = ContinuousUniverse(0, 40, leftClosed=True, rightClosed=True)
scale = LinguisticScale((
    LinguisticTerm("Comfort", ScalarFuzzySet(universe, Triangle(16, 22, 28))),
    LinguisticTerm("Warm", ScalarFuzzySet(universe, SShoulder(22, 30))),
))
result = scale.Fuzzify(24)
grades = {item.term.name: item.grade for item in result.memberships}
assert isclose(grades["Comfort"], 2 / 3)
assert grades["Warm"] == 0.125
assert result.selectedTerms[0].name == "Comfort"
print(grades, result.selectedTerms[0].name)
```


结果为 `Comfort ≈ 0.667`、`Warm = 0.125`，选中的标签是 `Comfort`。隶属度表示观测值与所定义概念的相容程度，**不是概率**，各隶属度之和也不必等于一。`Fuzzify` 返回全部隶属度；标签选择遵循显式策略，默认选择隶属度最高的第一个词项。

[![Comfort 与 Warm 隶属曲线，标出了 24 °C 的观测值](../en/assets/figures/temperature.svg)](../en/assets/figures/temperature.svg)

曲线展示声明的 0–40 °C 论域上的模型。虚线表示测量值，两个点表示计算得到的隶属度。这个双标签示例有意未覆盖某些温度。在将其作为完整的实际尺度使用前，应检查覆盖情况。

## 组合、检查并解释结果 {#combine-inspect-and-explain-a-result}

接着阅读[九个完整场景](guides/index.md)。它们涵盖物理测量、策略选择、拒绝分类、有向模糊差、α-截集、质心、尺度诊断和自定义模型。每个场景都包含可独立运行的代码、预期数值和图形。[隶属函数图集](guides/membership-families.md)可以帮助选择曲线。

脚本 [`examples/guide.py`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/guide.py)运行全部九个场景，并检查独立确定的数值预期。在已安装软件包的仓库工作副本中运行：

```bash
python -I examples/guide.py
python -I examples/guide.py --scenario centroid
```


可以将场景复制到自己的项目中。标量计算仅使用 FuzzyRoutines 和 Python 标准库；查看仓库中的 SVG 无需安装绘图库。若要从工作副本重新生成图形，请安装 `docs/requirements-plots.txt`，并按照[图形来源说明](guides/figures.md)运行 `tools/generate_guide_figures.py`。

对于使用 `MFunction`、`FuzzySet` 和 `FuzzyScale` 的旧代码，请先阅读[历史兼容接口](api/legacy/index.md)。现代集合和策略不可变；历史兼容接口则有意保留可变对象的兼容性约定。
