<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

为受支持的标量论域推导精确的模糊集属性。

连续情形要求使用现代
[MembershipFunction][fuzzyroutines.membership.MembershipFunction] 或历史
[MFunction][fuzzyroutines.FuzzyRoutines.MFunction] 适配器。
精确解析结果的依据来自经过验证的公式来源；任意可调用对象都不能作为连续支集或高度的证明。
离散论域上的结果是精确的，因为会计算每一个已声明的坐标。
若要对连续情形进行明确标注为近似的查询，请使用
[SampleProperties][fuzzyroutines.properties.SampleProperties]。

Args:
    membershipFunction: 现代解析函数族，或受支持的历史解析适配器。
    universe: 要分析的连续或离散标量论域。

Returns:
    与论域类型对应的精确连续解析属性，或通过穷举得到的离散属性。

Raises:
    TypeError: 任一参数的契约类型不受支持。
    ValueError: 解析函数族不受支持，或求值产生了无效隶属度。
