<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 小型神经网络的模糊输入与输出

本可执行示例结合历史通用模糊标度、显式编码器 `LinguisticCodec` 与基于
CPU 的小型 PyTorch 网络，采用全新生成的合成数据。隶属函数和质心积分区间
保持固定，训练仅调整网络权重。本示例展示神经网络集成，**并非可训练的
模糊规则系统**，也不是经过验证的风险评估模型。

## 运行完整实验

请使用包含 2.1 示例的仓库工作副本，将匹配的 2.1 软件包安装到独立环境中。
脚本会检查导入对象是否为已安装的软件包。以下命令适用于 Linux CPU 环境：

```bash
python -m venv .venv-neural
. .venv-neural/bin/activate
python -m pip install .
python -m pip install --index-url https://download.pytorch.org/whl/cpu -r examples/neural/requirements.txt
python -I examples/neural/run.py --verify-installed --output neural-report.json
```

[完整源代码](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/neural/run.py)
生成观测数据、训练四个网络，并将 JSON 输出到标准输出及指定文件。无需
Docker、GPU、外部数据集或预训练模型。PyTorch 是该示例的可选依赖，固定为
2.14.1；导入 FuzzyRoutines 不会导入 PyTorch。记录的运行环境为 CPython
3.14.8、PyTorch 2.14.1+cpu、Linux x86_64、float64 和单 CPU 线程。在开发主机上，
重复运行约需 21 秒，首次冷启动运行约需 86 秒。上述时间不含安装过程，
不构成性能保证。

可通过减少样本量和训练轮数进行简短的安装冒烟测试：

```bash
python -I examples/neural/run.py --verify-installed --epochs 30 --samples 90 --output neural-smoke.json
```

请参阅官方[安装说明](https://pytorch.org/get-started/locally/)、
[Python 兼容性矩阵](https://github.com/pytorch/pytorch/blob/main/RELEASE.md)和
[可复现性说明](https://docs.pytorch.org/docs/2.14/notes/randomness.html)。
固定随机种子不保证不同 PyTorch 版本或平台之间的结果完全一致。

## 任务与输入表示

严重程度和暴露程度已表示为归一化坐标 $s,e\in[0,1]$，不拟合额外的
归一化器。示意性的连续评分定义为

$$
y=0.05+0.65s+0.30e.
$$

以 $\mu_i$ 表示五个历史隶属函数，其顺序为 `Min, Low, Med, High, Max`。
选定语言项的索引及其代表值为

$$
q(x)=\max\{i:\mu_i(x)=\max_j\mu_j(x)\},\qquad
c_i=\frac{\int_{a_i}^{b_i}x\mu_i(x)\,dx}{\int_{a_i}^{b_i}\mu_i(x)\,dx}.
$$

最大隶属度精确相等时，显式采用最后一项优先的策略。原积分区间为
`(0, .23), (.17, .40), (.34, .66), (.60, .83), (.77, 1)`。
`EncodeLabel()` 计算这些代表值；**它们是输入或目标坐标，并非学习得到的
网络权重**。未知标签会显式报错。三个标量实验分别使用

$$
z_{\mathrm{raw}}=(s,e),\qquad
z_{\mathrm{centroid}}=(c_{q(s)},c_{q(e)}),\qquad
z_{\mathrm{grades}}=(\mu_1(s),\ldots,\mu_5(s),\mu_1(e),\ldots,\mu_5(e)).
$$

所有标量模型均预测**同一个质心编码目标** $t=c_{q(y)}$：

$$
\widehat t=f_\theta(z),\qquad
L_{\mathrm{scalar}}=\frac1N\sum_{n=1}^{N}(\widehat t_n-t_n)^2.
$$

`DecodePrediction()` 返回预测坐标的各项隶属度、置信度及选定标签。
超出 `[0, 1]` 的输出仍参与数值误差计算，并记为解码失败，绝不隐式截断。
区间端点有效。报告包含 `-0.05` 和 `1.05` 两个明确拒绝的预测示例。

![固定输入语言项、训练与验证损失、预测截面及解码后的输出隶属度](../../en/assets/figures/neural-integration.svg)

## 固定评估方案

默认实验使用种子 1729 生成 600 对相互独立的均匀分布输入。训练之前，
另以种子 1730 打乱样本索引，固定划分为 360 个训练样本、120 个验证样本
和 120 个留出测试样本。所有网络采用初始化种子 1731、两个各含 16 个
单元的 tanh 隐藏层、学习率为 0.01 的 Adam，以及 400 轮全批量训练。
依据最小验证 MSE 选择检查点，留出标签不参与选择。标量输出层为线性层。
输入维数不同，因此原始坐标与质心网络各有 337 个参数，完整隶属度向量
网络有 465 个参数。

JSON 记录数据划分索引、数据与示例源码的 SHA-256、运行环境、学习曲线、
检查点及留出预测。[参考报告](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/neural/reference.json)
中这一固定实验的结果如下：

| 输入表示     | 质心目标 RMSE     | 连续评分 RMSE     | 解码标签准确率        |
| -------- | ------------- | ------------- | -------------- |
| 训练目标均值   | 0.2295        | 0.2215        | 37.5%          |
| 原始坐标     | 0.0690        | 0.0120        | 93.3%          |
| 标签质心     | 0.0868        | 0.0476        | 78.3%          |
| 完整隶属度向量  | 0.0990        | 0.0773        | 75.8%          |

以训练集多数标签为固定预测的基线准确率也为 37.5%。本次运行中，三个
已训练标量模型的留出预测均未超出定义域。连续评分 RMSE 仅作为单独的
诊断指标，训练目标始终是质心坐标。此处原始输入表现最佳。这些结果用于
说明集成方法及信息损失，单次合成数据划分不能证明任何表示具有普遍的
精度优势。

## 信息损失

输入 `(0.4, 0.9)` 与 `(0.6, 0.9)` 均映射为 `(Med, Max)` 对应的同一质心对，
但连续评分分别为 0.58 和 0.71，对应目标标签 `Med` 和 `High`。仅接收该
相同质心对的确定性模型无法区分这两个样本。即使保留完整向量，两者的
差异也小于 $10^{-10}$：较宽的 `Med` 平台抹去了大部分坐标信息，仅有
`Min` 的微小尾部值不同。因此，保留全部隶属度并不保证可获得数值上有效
的逆映射。

在坐标 0.17 处，历史隶属度之和约为 0.00213，除 `Min` 外其余各项均为零。
这表示覆盖较弱，而非概率分布。示例保留这一性质，不将向量归一化，也不
替换历史标度。在实际应用中，应先明确量纲、归一化方法与可接受的覆盖
程度，再对观测值编码。

## 单独的输出隶属度实验

第四个网络接收十个输入隶属度，使用 sigmoid 输出层预测五个相互独立的
有界隶属度：

$$
g_i=\mu_i(y),\qquad \widehat g_i=\sigma(h_{\theta,i}(z_{\mathrm{grades}})),\qquad
L_{\mathrm{grades}}=\frac1{5N}\sum_{n=1}^{N}\sum_{i=1}^{5}(\widehat g_{ni}-g_{ni})^2.
$$

这些目标是**连续评分**的隶属度，并非标签质心的隶属度。它们既不是独热
类别，也不是类别概率；不使用 softmax，也不要求各项之和为一。该网络
含 533 个参数，预测目标不同，因此单独报告结果，不与标量 RMSE 直接
排序比较。其留出隶属度 RMSE 为 0.1675，预测隶属度之和介于 0.1315 与
1.3377。图中的弱覆盖探针显示了明显偏差。五个有界输出不一定对应某一
坐标的精确隶属度向量。后续代表值加权平均或决策必须另外声明策略；
该操作并非逆映射，也不是模糊规则推理机制。

![留出标量误差与标签准确率、参考标签区域，以及弱覆盖条件下单独的隶属度输出结果](../../en/assets/figures/neural-ablation.svg)

## 重现插图

绘图程序读取报告中的实际结果，并通过标量 API 计算固定参考曲线。
它不会重新训练，也不会导入 PyTorch：

```bash
python -m pip install -r docs/requirements-plots.txt
python -I tools/generate_neural_figures.py --report neural-report.json --output-directory neural-figures
```

默认读取仓库中保存的参考报告；`--check` 只比较生成的 SVG 字节，不写入
文件。源码哈希检查可防止误用其他示例版本生成的报告。测试独立验证解析
任务、数据划分隔离、编码碰撞、边界错误，以及替换留出目标后检查点仍
保持不变。有关编码契约及代表值平均与模糊集合质心的区别，参见
[语言编码](linguistic-encoding.md)。
