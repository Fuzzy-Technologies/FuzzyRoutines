<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

通过显式兼容适配器公开历史模糊逻辑名称。

规范隶属函数公式、算子、域和数值策略位于各个专门的现代模块中。
私有适配器保留历史参数顺序、可变状态、默认尺度和返回对象的身份。
新代码应导入专门模块或包的现代 API。

字面量 `__all__` 列表保留十五个受支持的历史符号。
导入的辅助对象和私有适配器不属于此兼容接口。
