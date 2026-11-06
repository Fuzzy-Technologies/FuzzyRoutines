<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 科学绘图导出 {#scientific-plot-export}

使用经过审核且包含 `fuzzyroutines.plotting` 的 FuzzyRoutines 2.2 wheel，
并在 `FUZZYROUTINES_WHEEL` 中指定其绝对路径。普通标量计算使用基础安装。

```bash
: "${FUZZYROUTINES_WHEEL:?Set the absolute path to the reviewed wheel}"
python -m pip install "${FUZZYROUTINES_WHEEL}[plot]"
```

将标度导出为 SVG，并明确标注无量纲坐标轴。临时目录让示例可以重复运行。
第二次导出展示如何查明单个采样点计算失败的原因。

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from fuzzyroutines import CreateUniversalFuzzyScale, DiscreteUniverse, ScalarFuzzySet
from fuzzyroutines.plotting import ExportMembershipPlot, PlotSamplingError

def UnavailableGrade(coordinate):
    """Report an unavailable observation at the requested coordinate."""

    raise ValueError(f"No observation at {coordinate}")

scale = CreateUniversalFuzzyScale()
with TemporaryDirectory() as temporaryDirectory:
    folder = Path(temporaryDirectory)
    figure = ExportMembershipPlot(
        scale, folder / "membership.svg", coordinateLabel="Normalized coordinate x",
    )
    assert figure.read_bytes().startswith(b"<?xml")

    incomplete = ScalarFuzzySet(DiscreteUniverse((0, 1)), UnavailableGrade)
    failedFigure = folder / "missing.svg"
    try:
        ExportMembershipPlot(incomplete, failedFigure)
    except PlotSamplingError as error:
        sampleFailure = error
    else:
        raise AssertionError("An unavailable scalar sample must fail the export.")

    assert isinstance(sampleFailure.__cause__, ValueError) and not failedFigure.exists()
```

- 对无界论域，请指定有限的 `displayWindow=(left, right)`。该区间决定图上
  可见的范围。支撑集和积分边界各自保留原有的数学含义。
- `sampleCount` 设置每个可见连续区段的基础采样网格。导出时会纳入已知节点。
  离散论域上的取值和连续性未知的自定义函数用互不相连的标记表示。
  有限网格决定绘图分辨率。
- 使用 `.png` 或 `.svg` 并设置 `transparent=True` 可获得透明背景。JPEG
  需要显式指定不透明的 `background`，例如 `"#121829"`。SVG 默认保留
  可编辑文本。设置 `svgTextAsPaths=True` 可导出字形轮廓。
- 父目录必须已存在。设置 `overwrite=True` 可在渲染成功后替换已有文件。
  文件扩展名必须与显式指定的 `formatName` 一致。

有关标量计算失败的约定，请参阅 [API 参考](../api/modern/plotting.md)。
