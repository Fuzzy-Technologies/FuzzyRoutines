<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

具有显式策略和不可变轨迹的标量 Mamdani 与 Sugeno 模糊推理。

规则通过类型化表达式树定义，不使用可执行字符串。模型具有一个标量输出及一个或多个
命名的标量输入。容器不可变；用户隶属函数仍由调用者管理其状态，应为纯函数以保证
计算可复现。隶属度不是概率。
