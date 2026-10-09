<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

定义在一个显式论域上的不可变标量模糊集。

Attributes:
    universe: 连续或离散标量坐标约定。
    membershipFunction: 在验证坐标属于论域后执行的可调用对象；结果必须为 $[0, 1]$ 内的有限隶属度。[MembershipCallable][fuzzyroutines.membership.MembershipCallable] 描述无需继承的结构约定。构造时只检查可调用性，不检查签名或结果。
