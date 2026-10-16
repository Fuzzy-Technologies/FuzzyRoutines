<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 模糊规则能否通过数据学习

[神经网络示例](neural-integration.md)在网络前后使用固定的模糊表示，输入语言项并不参与训练。
本实验采用另一种结构：将隶属函数和 [Sugeno 规则](inference.md)纳入可训练的计算图，
使预测误差能够调整隶属函数的中心与宽度。这是仓库内的可选研究原型，
并非公开的张量 API。

## 小型可微模型

两个归一化输入分别表示严重程度和暴露程度，每个输入设有两个高斯语言项。
四种语言项组合构成四条规则。规则激活强度为两个隶属度与固定非负规则权重的乘积：

$$
\mu_{jk}(x_j)=\exp\!\left[-\frac{(x_j-c_{jk})^2}{2\sigma_{jk}^2}\right],\qquad
\alpha_i=w_i\prod_j\mu_{j,k(i,j)}(x_j).
$$

其中，$j$ 表示输入，$k$ 表示语言项，$i$ 表示规则。通过归一化正间隔参数化，
中心 $c$ 始终保持有序；宽度 $\sigma$ 被限制在 0.05 至 0.8 之间。
这些光滑语言项独立于历史通用模糊标度，后者的参数不作任何调整。

零阶模型的规则后件为常数，一阶模型的后件为输入的仿射函数：

$$
z_i=b_i+\sum_j a_{ij}x_j,\qquad
\bar\alpha_i=\frac{\alpha_i}{\sum_r\alpha_r},\qquad
\hat y=\sum_i\bar\alpha_i z_i.
$$

零阶模型令全部 $a_{ij}=0$。训练通过对整个表达式求导，最小化预测均方误差；
这里不计算输出模糊集的重心。前向计算完全在 Torch 中完成。
标量 `Defuz()`、转换为 NumPy 数组或分离中间张量，均不能保持这一梯度传递路径。
转换为标量仅用于独立的一致性验证。

![隶属函数变化、学习曲线与测试集比较](../../en/assets/figures/sugeno-research-learning.svg)

## 实验结果

实验与神经网络示例共用 600 个合成样本，按 360/120/120 划分训练集、验证集和测试集。
由简单的连续潜在得分确定历史标度中的标签，再以现代 API 在原有积分区间上
计算的相应语言项重心作为回归目标。
所有可训练模型均使用全批量 Adam，学习率为 0.01，训练 400 轮；
仅依据验证误差选择检查点，测试数据不参与模型调节。

| 模型             | 重心目标 RMSE | 标签准确率  | 无效输出  |
| ---            | ---:      | ---:   | ---:  |
| 固定规则           | 0.093063  | 68.33% | 0/120 |
| 可训练零阶模型        | 0.068779  | 94.17% | 0/120 |
| 可训练一阶模型        | 0.067643  | 91.67% | 2/120 |
| 固定隶属函数、可训练仿射后件 | 0.065600  | 88.33% | 0/120 |
| 原始输入 MLP       | 0.069001  | 93.33% | 0/120 |

该计算图可以训练，但学习隶属函数未能降低相对于固定隶属函数对照模型的重心目标 RMSE。
可训练零阶和一阶模型的标签准确率却更高，说明两个评价目标偏好的模型并不相同。
一阶模型的两个预测值超出了
解码器的定义域，实验将其记为无效输出，未进行截断。单个合成任务与单次初始化
不足以说明某一方法具有普遍优势。

![连续预测与显式标记的定义域越界输出](../../en/assets/figures/sugeno-research-predictions.svg)

## 运行与检查

在包含本实验的仓库工作副本中使用 Python 3.13 或更新版本。
安装测试工具及可选的 CPU 依赖，再将完整证据写入 JSON：

```bash
python -m pip install -r requirements.txt
python -m pip install --index-url https://download.pytorch.org/whl/cpu -r examples/neural/requirements.txt
python -m research.run_sugeno --output /tmp/sugeno.json --measure-dependencies
python -m pytest -q tests/test_differentiable_sugeno.py tests/test_sugeno_research.py
```

[运行脚本](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/research/run_sugeno.py)
记录随机种子、划分索引、源码与数据哈希、损失、预测值、参数数量及耗时。
已归档的 JSON 位于 `research/results/`。记录的单线程 CPU 运行中，
每个模型的训练约耗时 2–3 秒；仅已安装的 Torch 文件就占用约 682 MiB。
核心软件包不依赖 Torch。

固定参数后，原型与标量 Sugeno 引擎的绝对差异不超过 `1e-12`；
有限差分检验覆盖输入、隶属函数参数和后件参数的梯度。
全部规则权重为零时抛出 `UndefinedResultError`。在对数域中进行归一化，
可以保留那些乘积可能在标量运算中下溢为零的微小正权重；
与标量 API 的一致性承诺仅适用于规则激活强度仍可表示的区域。

[ADR-0020](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/adr/0020-differentiable-sugeno-feasibility.md)
记录了**不在 2.1 中引入公开张量支持**的决定。本原型使用梯度下降，
并未实现 [Jang 的 ANFIS 论文](https://doi.org/10.1109/21.256541)中的混合学习算法。
其计算图遵循 [PyTorch 自动微分契约](https://docs.pytorch.org/docs/2.14/notes/autograd.html)。
