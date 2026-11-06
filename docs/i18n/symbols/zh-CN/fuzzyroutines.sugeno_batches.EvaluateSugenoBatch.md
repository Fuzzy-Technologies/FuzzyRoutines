<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

对有序观测行计算零阶和一阶 Sugeno 规则。

Args:
    model: 标准标量 Sugeno 模型，使用支持的解析隶属函数和内置运算符，且模型参数可由 binary64 精确表示。
    values: 普通二维实数 ndarray 或矩形列表或元组。每行对应一次观测。空 ndarray 保留输入特征轴，空列表或元组的宽度由 featureNames 指定。
    featureNames: 按输入列顺序给出的唯一名称。其名称集合必须与模型输入名称完全一致。
    backend: 显式选择的可选后端。仅支持 "numpy"。
    onError: 在第一条失败行处抛出异常，或保留所有行及其状态。
    trace: 关闭追踪、保留激活情况摘要，或按模型声明顺序保留完整追踪数据。
    chunkSize: 每块观测行数，使用内置 int 类型的正整数。

Returns:
    按原始行顺序返回独立的只读值数组、有效性数组和状态数组。追踪数组按模型输入、语言项和规则的声明顺序排列。

Raises:
    ImportError: NumPy 不可用。
    InvalidParameterTypeError: 不支持输入数据或模型的类型。
    InvalidParameterError: 形状、名称或调用选项无效，或在 "raise" 模式下某行包含非有限坐标。
    InvalidDomainError: 在 "raise" 模式下，某行超出输入或输出论域。
    UndefinedResultError: 在 "raise" 模式下，某行没有激活任何规则。
    NumericalError: 在 "raise" 模式下，某行计算发生数值错误。

Notes:
    每次将一个块的输入坐标转换为 binary64。状态 1 表示坐标非有限，2 表示输入超出论域，3 表示没有规则激活，4 表示输出超出论域，5 表示数值错误。导入本模块不会加载 NumPy，也不会改变标量计算。
