<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 有限标量输入策略 {#finite-scalar-input-policy}

## 状态 {#status}

已实现的标量契约。任务 #62 定义此策略，任务 #63 消除了公共标量算子
和内置隶属函数求值中的静默哨兵值以及将异常转换为零的路径。

## 规则 {#rule}

每个经过验证的标量输入必须有限；隶属度还必须位于闭区间 `[0, 1]`。
布尔值绝不作为标量数值接受。历史门面接受内置 `int` 和 `float`。
现代 API 使用更广泛的 `numbers.Real` 契约，包括 `Fraction`，
不会仅为类型检查而转换有效输入。其公共类型别名为 `MembershipScalar`。

无效标量输入包括 NaN、正无穷、负无穷、`True`、`False` 和非数值。
历史算子和隶属函数求值器抛出 `ValueError` 并附带可读的诊断信息。
现代标量验证区分 `InvalidParameterTypeError`（也是 `TypeError`）
和 `InvalidParameterError`（也是 `ValueError`）；解析函数族构造函数
保留文档规定的、与 `ValueError` 兼容的参数验证。
无效输入绝不会产生 NaN、无穷或静默的 `None` 哨兵值。

## 适用范围 {#scope}

- FuzzyNOT、FuzzyNOTParabolic、FuzzyAND、FuzzyOR、TNorm 和 SCoNorm 应用隶属度规则。
- 组合辅助函数在求值之前验证每个传入的隶属度。
- 隶属函数接受有限实数坐标及各函数特有的有限参数；
  其域约束由各个隶属函数契约规定。
- 此策略不强制转换字符串、布尔值、`Decimal` 或数组。
  直接调用用户提供的求值器时，保留该求值器自身的行为；
  `ScalarFuzzySet.Membership` 验证输入及返回的隶属度。
  用户回调内部抛出的异常会原样传播。

## 验证依据 {#evidence}

`tests/test_finite_number_policy.py` 中的测试覆盖公共算子和隶属函数的边界、
显式错误行为、极端有限坐标以及内部编程错误的传播。
组合操作的专门覆盖保留在 `tests/test_composition_validation.py` 中。
现代契约、已注册实数标量和错误类别由 `tests/test_public_typing_runtime.py`、
`tests/test_fuzzy_set_operations.py` 及 `tests/test_domain_exceptions.py` 覆盖。
