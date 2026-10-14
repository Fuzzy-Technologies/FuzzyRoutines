<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# AI 智能体快速入门 {#agent-quick-start}

将本页提供给助手，即可让它安装 FuzzyRoutines、了解功能、计算隶属度或绘制可复现图形。
实际计算需要可执行 Python 的环境。只能进行文本对话的助手可以解释示例，但不能声称已经执行并验证。
无需本地电脑、Docker、GPU 或专用智能体框架。

## 可直接使用的请求

> 请阅读 https://fuzzy-technologies.github.io/FuzzyRoutines/api/latest/zh-CN/agent-quickstart/ 。首先检查 Python 版本，安装指定版本 FuzzyRoutines 2.0.0，使用已支持的现代 API 构造历史通用模糊标度，并运行标度及示意性风险等级示例。返回包版本、输入、五个隶属度、选定的语言项或无匹配结果，以及数值验证结果。如果具备绘图环境，请在无图形界面的条件下生成图形。解释 0.17 附近的弱覆盖区，并说明隶属度为何不等于概率。若无法执行代码，请明确说明并给出命令，不要将预期结果表述为已验证结果。

## 版本与功能索引

示例针对**已发布的 2.0.0** API，使用 CPython **3.13 或 3.14**。
`/latest/` 文档会更新；精确的包版本约束和 JSON 中的 `environment` 字段用于标识实际执行环境。
独立脚本基于已安装的 wheel 运行，无需导入仓库中的模块。

| 功能                         | 已发布版本 2.0.0 的入口                                                                             | 示例                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 模糊集与隶属函数                   | `ScalarFuzzySet`, `Triangle`, `Bell`, `Hyperbolic`, `SShoulder`                             | [隶属函数图集](guides/membership-families.md)                                   |
| 语言项分类                      | `LinguisticScale.Fuzzify`, `FuzzificationPolicy`                                            | [历史通用模糊标度](guides/universal-fuzzy-scale.md)                               |
| 模糊逻辑基本运算                   | `TNormPolicy`, `SNormPolicy`, `NegationPolicy` 及集合运算                                        | [算子](guides/operators.md)                                                 |
| 截集与数值输出                    | `AlphaCut`, `SampleAlphaCut`, `Centroid`                                                    | [α-截集](guides/alpha-cuts.md)、[质心](guides/centroid.md)                     |
| 规则推理与神经网络集成                | 计划用于 2.1；不属于已发布的 2.0.0 API                                                                  | [2.1 计划](https://github.com/Fuzzy-Technologies/FuzzyRoutines/milestone/8) |
| 可选 NumPy 批量计算              | 计划用于 2.1；2.0.0 使用无外部运行时依赖的标量核心                                                              | [2.1 计划](https://github.com/Fuzzy-Technologies/FuzzyRoutines/milestone/8) |

具体契约以 [API 参考](api/index.md)和[应用场景](guides/index.md)为准。
不要将规划中的接口名称或旧版包的接口当作当前已支持的 API。

## 无需检出仓库即可运行

在新建环境中依次执行以下命令。预检在安装前拒绝不受支持的 Python；脚本随后要求精确匹配已安装的包版本，防止将旧版 `1.0.3` 误认为现代 API。

```bash
python -c "import platform, sys; sys.exit(0 if platform.python_implementation() == 'CPython' and sys.version_info[:2] in ((3, 13), (3, 14)) else 'Use CPython 3.13 or 3.14; do not install on 3.12.')"
python -m pip install fuzzyroutines==2.0.0
curl -fLo agent_recipe.py https://fuzzy-technologies.github.io/FuzzyRoutines/recipes/agent_recipe.py
python -I agent_recipe.py --expect-version 2.0.0 --output scale.json > scale.stdout.json
python -I agent_recipe.py --expect-version 2.0.0 --scenario risk --output risk.json > risk.stdout.json
python -I agent_recipe.py --expect-version 2.0.0 --scenario risk --value 17 --output weak.json > weak.stdout.json
```

第一次运行计算 `x=0.2`：**Low ≈ 0.5**，同时保留 Min 的微小正尾部，选定语言项为 **Low**。
风险示例显式采用 0–100 的示意性评分，并除以 100：**75 → 0.75 → High = 1**。
对于 **17 → 0.17**，最大隶属度仅约为 **0.00212959**；因此，阈值 `0.1` 导致**无匹配**，而不是可靠地判为 Min。

命令将有效 JSON 写入 stdout；指定 `--output` 时，同一 JSON 也写入文件。
报告包括 Python 与包版本、输入归一化、原始系数、历史质心积分域、选择策略，以及独立分段公式的数值检查。
绝对容差为 `1e-12`，相对容差为零。失败时返回退出码 2，诊断信息写入 stderr。
`--help` 在安装包之前即可运行。有限测试点提供回归验证，不能证明所有实数输入上的性质。

风险评分由调用方提供；本库不推断事件概率，也不制定处置策略。
实际应用须自行定义并验证归一化规则。超出规定范围的输入会被拒绝，不会被静默截断。
各隶属度之和不必为一。策略选择**最后一个精确最大值**；浮点数近似相等不等于精确相等。
当最大隶属度**等于**阈值时，同样判为无匹配。

## 绘图与结果解释

绘图是可选步骤，使用单独的依赖版本锁定文件。
渲染无需图形界面；将 `risk.svg` 替换为 `risk.png` 即可输出 PNG。
图中并列展示五条历史隶属函数曲线、给定输入的隶属度条形图及分类结果。
JSON 还记录图像哈希和 Matplotlib 版本。使用相同输入和锁定的工具版本，重复运行将生成字节一致的图像。

```bash
curl -fLo requirements-plots.txt https://fuzzy-technologies.github.io/FuzzyRoutines/recipes/requirements-plots.txt
python -m pip install -r requirements-plots.txt
python -I agent_recipe.py --expect-version 2.0.0 --scenario risk --value 17 --plot risk.svg > plot.stdout.json
```

[![历史曲线与输入 0.17 对应的五个隶属度；所有值均低于 0.1 阈值。](../en/assets/figures/agent-risk.svg)](../en/assets/figures/agent-risk.svg)

验证开发版时，安装确切的 wheel，并在 `--expect-version` 中填写其版本，例如 `2.1.0.dev0`。
这用于显式验证候选构建，不表示可从 PyPI 安装尚未发布的版本。
报告结果时，请同时保留 JSON 和图像，以便复现。
