<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 图形来源与复现 {#figure-provenance-and-reproduction}

仓库中的十幅 SVG 是科学教学图，由 `tools/generate_guide_figures.py` 根据真实标量 API 求值生成，并非生成式艺术图像。生成器先执行八个场景中的全部断言，再绘制模型和注释。场景代码及数值预期位于 `examples/guide.py`。

## 所有语言共用一套图形 {#one-figure-set-for-all-languages}

英文、俄文和简体中文文档共用这些 SVG。图内文字保持英文，包括标题、坐标轴、图例、注释和单位。翻译页面通过本地化图注、正文和描述性替代文字解释这些标签，不另行生成翻译图片。

规范文件位于 `docs/site/content/en/assets/figures/`。各语言构建可以复制文件以保持相对链接有效，但副本必须与原文件逐字节一致。俄文和中文页面在发布前仍需各自的语言及科学审阅。文档约定见[多语言架构](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/architecture/multilingual-documentation-pipeline.md)。

## 复现资源 {#reproduce-the-assets}

在已安装 FuzzyRoutines 的仓库工作副本中，使用 CPython 3.14 和固定版本的文档工具链：

```bash
python -m pip install -r docs/requirements-plots.txt
python tools/generate_guide_figures.py --output-directory docs/site/content/en/assets/figures
python tools/generate_guide_figures.py --output-directory docs/site/content/en/assets/figures --check
```


`--check` 对每个预期 SVG 进行逐字节比较，不写入文件。文档 CI 在 Python 3.14 上使用固定工具链执行此检查。SVG 标识符采用固定哈希盐，元数据省略生成日期，标签使用固定字体族。复现保证仅针对该工具链，不承诺在不同绘图库或字体版本之间逐字节一致。

编辑审阅时，可显式指定 `--preview-directory PATH`，额外将 PNG 写入所选目录。默认只在 `--output-directory` 下写入 SVG。依赖安装完毕后，命令不访问网络。缺少依赖、图形过期、场景断言失败或写入失败均会返回非零退出状态。

Matplotlib 及其依赖（包括 NumPy）仅属于文档工具链。安装或导入 FuzzyRoutines 不需要它们；默认示例脚本也不导入它们。

## 独立验证科学内容 {#verify-scientific-content-independently}

SVG 字节比较可以发现过期资源，但不能证明其数学正确性。`tests/test_guide_figures.py` 使用基本分段或指数公式，独立检查 26 条曲线各自的全部 401 个坐标，还检查散点坐标、六个传感器柱形、阈值、使用精确有理数运算的四节点质心计算，以及标题和图例布局。参考计算不调用库的隶属函数。文档 CI 安装绘图依赖，先针对已安装的标量 API 运行这些测试，再比较 SVG 文件。

## 正确理解图形 {#interpret-the-pictures-correctly}

- 连续模型曲线使用 401 个显示采样点。它们是示意图，不是精确几何的证明，也不是 `Centroid` 使用的求积策略。
- α-截集中的点表示指定的九点网格；带轮廓的点表示穷尽检查五点离散论域后符合条件的坐标。
- 尺度诊断使用包含端点的十一个坐标。图中的平滑曲线与诊断观测属于不同类型的证据。
- 归一化图只画离散点，不使用插值连线，也不暗示论域包含中间坐标。
- 质心图比较解析面积矩和单独的用户侧四点梯形计算。显示曲线的密度和粗略计算都不配置库的自适应积分。
- 运算图将第二个输入隶属度固定为 0.6，横轴改变第一个隶属度；两个轴都不是物理测量值。

每幅图均有描述性的 Markdown 替代文字以及 SVG 标题和说明。配套页面用文字给出数值结果，因此即使无法辨色或无法显示图片，也能理解示例。模型参数和标签是示意性的，不是经验校准数据。

图形使用 [Matplotlib 的 SVG 后端](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/backends/backend_svg.py)以及 [savefig 元数据支持](https://matplotlib.org/3.11.0/api/_as_gen/matplotlib.pyplot.savefig.html)。
