<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

无效输入及无法完成的数学操作所对应的公共错误类型。

每个类别均保留适用的内置异常捕获契约。
用户定义的隶属函数回调保留自己的异常；核心不会转换任意求值器错误。
历史适配器保留其文档规定的具体异常。
