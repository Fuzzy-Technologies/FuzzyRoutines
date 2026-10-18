<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

连续尺度及其代表值的不可变配置。

每次操作处理一个样本。隶属度向量是按声明顺序排列、长度为 `len(scale.terms)` 的显式元组，不包含批次维度。输入与预测须已采用尺度坐标；物理单位转换及拟合预处理由调用方负责。方法不会截断输入、拟合状态或将未知标签静默替换为零。重心用于编码数据或目标，而非网络学习权重。

Attributes:
    scale: 有序连续语言项，其论域均须包含待计算坐标。
    integrationDomains: 按尺度顺序为各语言项显式指定的重心积分区间，且位于相应论域内部。
    selectionPolicy: 预测解释使用的显式并列与无匹配策略。
    centroidPolicy: 可选的数值积分限制；`None` 使用标量重心默认策略。

Notes:
    标签约简与重心编码会损失信息；模糊化和解模糊通常不是互逆映射。用户提供的隶属函数保留自身的状态及所有权契约；冻结配置不会使回调自动成为纯函数。
