<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 现代公共 API 的类型支持 {#public-modern-typing}

现代 API 提供内联类型注解及符合 [PEP 561](https://peps.python.org/pep-0561/)
的 `fuzzyroutines/py.typed` 标记。支持 CPython 3.13 和 3.14。
可从 `fuzzyroutines` 或专门模块导入现代名称；两条路径保留相同类型和运行时对象。

`MembershipScalar` 接受内置浮点数及 `numbers.Real` 实现，包括整数和 `fractions.Fraction`。
联合类型显式包含 `float`，因为静态检查器不会把所有内置数值都建模为 `numbers.Real` 子类。
运行时验证仍拒绝布尔值、非有限坐标和无效隶属度。静态注解不编码这些数值限制。

`MembershipCallable` 是结构化契约：函数、可调用对象或绑定方法必须接受每个
`MembershipScalar` 坐标，并返回 `MembershipScalar`。
仅标注为接受 `float` 的回调所承诺的范围小于完整域。
自定义隶属函数回调应使用公共标量别名：

```python
from fractions import Fraction

from fuzzyroutines import (
    ContinuousUniverse,
    MembershipCallable,
    MembershipScalar,
    ScalarFuzzySet,
)


def CustomMembership(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a constant rational membership grade."""

    return Fraction(1, 2)


membership: MembershipCallable = CustomMembership
fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 1, True, True), membership)
grade: MembershipScalar = fuzzySet.Membership(0.5)
```

标量结果保持为 `MembershipScalar`，因此注解不要求将有理数或其他实数算术强制转换为浮点数。
解析属性操作要求标准 `MembershipFunction` 或可信解析来源；
一般回调不具备这些操作需要的解析依据。
`DeriveProperties` 根据传入论域选择 `ContinuousFuzzyProperties` 或 `DiscreteFuzzyProperties`。
采样操作返回独立的采样依据类型。尺度查找返回 `LinguisticTerm | None`，
因此调用者必须处理术语缺失情况。

Typeshed 通过兼容复数的接口建模 `numbers.Real` 算术，推断的结果类型比实数标量操作更宽。
在已经验证的内部算术边界，较窄的 `cast(float, value)` 为检查器提供实数算术视图。
`typing.cast` 在运行时返回同一对象，不调用 `float(value)`，也不改变有理数算术。
公共结果保留更广泛的标量契约，现代诊断仍接受完整类型检查。

不可变 dataclass 字段和只读隶属函数参数映射对检查器可见。
算子及分析函数要求各自特定的策略和域类型；传入其他策略族属于类型错误。

## 可复现检查 {#reproducible-gate}

将固定版本的检查器与运行时依赖分开安装：

```bash
python -m pip install -r requirements-typing.txt
python -m tools.typecheck
```

固定的 mypy 1.19.1 支持声明的 Python 版本和 PEP 695 别名；
其传递依赖也固定在同一文件中。源代码检查禁用增量复用，
成功结果不依赖先前缓存。CI wheel 构建器及构建后端也采用固定的开发依赖版本，
并禁用构建隔离。

`mypy.ini` 使用严格检查、诊断代码和未生效的忽略指令报告，
显式覆盖包根、每个现代模块（包括内部数值验证）、检查命令及全部静态调用方。
没有全局错误抑制。历史 `FuzzyRoutines` 门面、`_legacy` 适配器
和可执行 `Examples` 模块具有范围严格限定的跳过导入边界。
它们保留运行时兼容契约，但不属于现代类型支持承诺。

`tests/typing` 中的调用方样例包含有效导入、数值输入、自定义回调、策略使用、
不可变结果及精确返回类型断言。预期无效的调用和赋值标注具体诊断代码。
如果签名变为 `Any`，或以其他方式开始接受无效用法，
原先必要的忽略指令会变为多余，从而使检查失败。

## 已安装 wheel 的边界 {#installed-wheel-boundary}

`Public modern typing` 工作流在两个受支持 Python 版本上检查源契约并构建 wheel。
它将 wheel 和固定检查器安装到新的虚拟环境，然后运行：

```bash
/path/to/isolated/environment/bin/python /path/to/checkout/tools/typecheck.py --installed
```

此模式验证 Python 解析到工作树之外的包，并确认安装包包含 `py.typed`。
它将全部调用方样例复制到仓库之外的临时目录，在那里以隔离 Python 路径、
清空 `MYPYPATH` 与 `PYTHONPATH`、使用全新缓存的方式运行 mypy。
因此调用方样例检查的是 wheel 注解，而不是偶然找到工作树中的源文件。
临时探针在成功或失败后均删除；导入与检查器失败保留非零退出码。
