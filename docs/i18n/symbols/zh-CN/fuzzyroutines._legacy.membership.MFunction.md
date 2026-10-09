<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

表示一个历史解析隶属函数族。

Args:
    userFunc: 已注册的函数族标识符。兼容别名包括 `"gaussian"`、`"logistic"`、
        `"sShoulder"` 和 `"harringtonDesirability"`。
    **membershipFunctionParams: 所选函数族要求的准确参数集合。每个值必须是有限的
        内置 `int` 或 `float`；不接受 `bool`。

Raises:
    ValueError: 函数族或其参数集合无效。

Attributes:
    accuracy: 保留的可变兼容属性。现代质心解模糊化有意忽略此属性。
    mju: 所选函数族的绑定求值器。
