<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

请求操作下的结果未定义或不是有限值。

继承 `ValueError` 保留已有的零面积和零高度捕获行为；继承 `NumericalError` 则允许将其与质心收敛失败一起交给统一的数值失败处理器。
