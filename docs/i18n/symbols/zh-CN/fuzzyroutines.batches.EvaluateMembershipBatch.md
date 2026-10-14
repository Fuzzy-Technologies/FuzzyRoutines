<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

批量计算内置隶属函数，并返回新的 float64 数组。

Args:
    function: 未重写求值器的内置函数族；int/float 参数须可由 float64 精确表示。
    values: 秩至少为一的数值数组或矩形序列。允许空数组和非连续切片。坐标复制为 float64；拒绝布尔、复数、对象、字符串及非有限值。
    backend: 显式选择的后端；仅支持 `"numpy"`。

Returns:
    与输入形状相同、具有独立存储的可写 float64 数组。输入不被修改或保留引用，隶属度不进行归一化。

Raises:
    ImportError: 未安装 NumPy；消息给出可选依赖的安装命令。
    TypeError: 不支持的输入类型、求值器或参数表示。
    ValueError: 后端、坐标或隶属度不符合约定。
    OverflowError: 实际执行分支发生溢出或无效中间运算。
    ZeroDivisionError: 实际执行的二次分支中，宽度平方下溢为零。

Notes:
    与标量计算的比较使用转换后的 float64 坐标，绝对容差为 1e-12，相对容差为零。失败时不返回部分结果，也不自动回退到标量循环。
