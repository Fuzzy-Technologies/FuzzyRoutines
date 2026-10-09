<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 隶属函数公式与参数契约 {#membership-function-formula-and-parameter-contracts}

- 状态：任务 #50 的契约参考
- 相关 ADR：[ADR-0003](../../../../adr/0003-membership-function-contracts.md)
- 相关可执行接口：`fuzzyroutines.FuzzyRoutines.MFunction`

## 目的 {#purpose}

本表记录历史工厂标识符当前公开的数学内容，区分受保护的历史标识符
与标准数学名称，不会静默重定义已有参数约定。

隶属函数将输入映射到 `[0, 1]` 内的隶属度，遵循
[Zadeh (1965)](https://doi.org/10.1016/S0019-9958(65)90241-X) 提出的模糊集表述。
任务 #51 在构造及公共参数设置器中强制执行以下准确参数集合、有限实数值和几何约束。

## 契约表 {#contract-table}

| 历史标识符          | 规范数学描述                             | 历史公式与参数含义                                                                                                                 | 非退化域                                             | 别名策略                                            |
| -------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------- |
| `hyperbolic`   | 有理幂形式的递减右肩部；不是标准双曲线名称              | 当 `x <= c` 时为 `1`；否则为 `1 / (1 + (a * (x - c)) ** b)`。`c` 为左侧截止点，`a` 为尺度，`b` 为指数。                                          | `x, a, b, c` 有限；`a > 0`、`b > 0`。                 | 保留 `hyperbolic`；不添加错误的标准名称别名。                   |
| `bell`         | 平顶分段二次钟形；不是 Jang (1993) 的广义钟形      | 从 `a` 到 `b` 为递增二次肩部，`b` 到 `c` 为平台，随后为镜像递减肩部，终止于 `c + b - a`。                                                              | `a, b, c` 有限；`a < b <= c`。                       | 保留 `bell`；不设 `generalizedBell` 别名。              |
| `parabolic`    | 二次 S 形递增肩部                         | 令 `t = (x - a) / (b - a)`。当 `x <= a` 时为 `0`；`0 < t <= 1/2` 时为 `2t**2`；`1/2 < t < 1` 时为 `1 - 2(1 - t)**2`；`x >= b` 时为 `1`。 | `a, b` 有限；`a < b`。                               | `sShoulder` 是相同实现与参数的完全等价附加别名。                  |
| `triangle`     | 使用历史参数顺序的三角形隶属函数                   | `a` 为左底点，**`c` 为顶点**，`b` 为右底点。几何顺序为 `a < c <= b`，不同于历史参数顺序。                                                               | `a, b, c` 有限；`a < c <= b`。边界 `c = b` 保留历史默认高值术语。 | 保留 `triangle(a, b, c)`；采用常规顺序的别名必须有不同的显式名称。     |
| `trapezium`    | 使用历史参数顺序的梯形隶属函数                    | `a` 为左底点，`c` 为平台起点，`d` 为平台终点，`b` 为右底点。几何顺序为 `a < c <= d < b`。                                                             | `a, b, c, d` 有限；`a < c <= d < b`。                | 保留 `trapezium(a, b, c, d)`；采用常规顺序的别名必须有不同的显式名称。 |
| `exponential`  | 高斯隶属函数                             | `exp(-0.5 * ((x - a) / b)**2)`。`a` 为中心，`b` 为尺度。                                                                           | `x, a, b` 有限；规范尺度 `b > 0`。对于非零 `b`，历史公式不受其符号影响。  | `gaussian` 是相同实现与参数的完全等价附加别名。                   |
| `sigmoidal`    | Logistic S 形函数                     | `1 / (1 + exp(-a * (x - b)))`。`a` 为斜率参数，`b` 为中点。正 `a` 递增，负 `a` 递减。                                                        | `x, a, b` 有限；`a != 0`。                           | `logistic` 是相同实现与参数的完全等价附加别名。                   |
| `desirability` | Harrington 单侧期望度 / Gumbel 累积分布函数变换 | `exp(-exp(-y))`。直接接受输入 `y`，不保存参数。                                                                                         | `y` 有限。                                          | `harringtonDesirability` 是相同实现的完全等价附加别名。        |

## 文献中的命名 {#reference-naming}

标准参数化广义钟形函数具有宽度、斜率和中心三个参数，
与历史平顶二次 `bell` 实现不是同一公式。
Jang 的原始 ANFIS 论文定义三参数广义钟形，并明确中心、半宽和斜率的作用：
[Jang (1993)](https://doi.org/10.1109/21.256541)。
历史 `exponential` 公式恰好为高斯形，而历史 `parabolic` 是递增二次肩部，并非高斯函数。

## 过渡兼容注册表名称 {#transitional-compatibility-registry-names}

目前通过历史 `MFunction` 工厂提供的面向现代用法的名称是附加注册表键，而非不同公式：

| 注册表名称                    | 历史标识符          | 过渡参数契约     |
| ------------------------ | -------------- | ---------- |
| `sShoulder`              | `parabolic`    | 相同的 `a, b` |
| `gaussian`               | `exponential`  | 相同的 `a, b` |
| `logistic`               | `sigmoidal`    | 相同的 `a, b` |
| `harringtonDesirability` | `desirability` | 无参数        |

每个别名都解析为对应历史标识符的同一绑定方法，因此验证与求值共享同一实现。
这不使历史方法成为规范方法。专门的现代模块负责公式实现及常规参数契约；
历史工厂标识符是别名或显式兼容适配器。

不为 `bell`、`triangle` 或 `trapezium` 添加别名：若没有独立的现代 API 契约，
其历史形状或参数顺序会使常规名称产生歧义。

期望度变换归于 E. C. Harrington，*The Desirability Function*，
*Industrial Quality Control* 21(10)，494–498 (1965)。
这一来源由同行评审期刊 *Metrika* 的
[Trautmann and Weihs (2006)](https://doi.org/10.1007/s00184-005-0012-0) 记录。

## 兼容规则 {#compatibility-rule}

历史工厂标识符、关键字名称和参数顺序仍属于公共兼容接口。
无效配置在构造隶属函数或重新赋值整个参数映射时被拒绝，
不会被转换成看似合理的零隶属度。
