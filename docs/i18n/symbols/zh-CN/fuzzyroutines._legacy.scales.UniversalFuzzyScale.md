<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

表示没有设置器的历史五级通用尺度。

级别顺序为 `Min`、`Low`、`Med`、`High`、`Max`。
继承的查找和模糊化方法仍可使用，但此子类中的 `levels` 没有公共设置器。
返回的列表、查找字典以及其中的兼容对象仍然可变。
