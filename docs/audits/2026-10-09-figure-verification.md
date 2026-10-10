<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# PR #301 scientific figure verification — 2026-10-09

This second AI-assisted review examined the nine committed SVGs and their
canonical English examples at head `863a0194c8680abdfe98f4ab0cfce568763950d5`.
It independently recomputed the mathematical values and inspected the SVGs
after rendering them with CairoSVG, separately from the Matplotlib exporter.
It does not represent an independent human review, native-language approval,
or completion of the all-module mathematical audit in Task #298.

## Numerical and formula findings

No mathematical discrepancy was found in the illustrated models or worked
results. The formulas use dollar-delimited GitHub-compatible math and match
the executable snippets. The following oracles were checked independently:

| Figure               | Independent reference                                                                                                                                                    | Interpretation checked                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Temperature          | At 24 °C, descending triangle grade $(28-24)/6=2/3$; S-shoulder grade $2((24-22)/8)^2=1/8$                                                                               | Measured markers lie on their respective curves; grades are not probabilities.                        |
| Risk                 | At score 65, moderate grade $(75-65)/25=2/5$; high grade $2(15/40)^2=9/32$                                                                                               | Winning grade 0.4 is below the 0.45 abstention threshold.                                             |
| Sensors              | Inputs $1/2,3/4$; minimum $1/2$, product $3/8$, maximum $3/4$, algebraic sum $7/8$                                                                                       | Physical quantities are measured separately before combining dimensionless grades.                    |
| Alarm                | Directed difference is $\min(\mu_W,1-\mu_C)$; at 100 °C it is $1/2$                                                                                                      | The result is not arithmetic subtraction; the entire yellow curve obeys the declared policies.        |
| Alpha cuts           | Continuous weak cut is $[11,13]$; discrete cut is $\{11,12,13\}$                                                                                                         | Nine grid observations do not become an exact continuous cut; endpoints at grade 0.5 are included.    |
| Centroid             | Triangle area $4$, moment $40/3$, centroid $10/3$; four-node area $32/9$, moment $1024/81$, ratio $32/9$                                                                 | Error is $2/9$, relative error $1/15$; the displayed grid does not configure library quadrature.      |
| Scale audit          | At 5, both overlap grades are $1/4$; gappy grid zeros are $0,4,5,6,10$                                                                                                   | Gap fraction $5/11$ counts observations, not continuous interval length.                              |
| Custom normalization | Discrete grades $0,1/4,1/2$ divide by height $1/2$ to give $0,1/2,1$                                                                                                     | Only declared discrete points are drawn; the original is preserved.                                   |
| Membership families  | Piecewise triangle, trapezoid, quadratic shoulders and bell; hyperbolic $1/(1+\max(x,0)^2)$; Gaussian $e^{-x^2/2}$; logistic $1/(1+e^{-2x})$; desirability $e^{-e^{-x}}$ | Parameters and family names agree with the eight panels; the displayed window is not a support claim. |

The accompanying centroid scenario also agrees with the disjoint-triangle
moment oracle $44/9$. The custom continuous ramp has area $50$, first moment
$10000/3$, and centroid $200/3$. These results are distinct from the separate
discrete normalization illustrated in the custom-model figure.

## Presentation corrections

- Added a four-entry centroid legend: analytical curve, four samples, analytical
  centroid, and four-point moment ratio. Numbers now come from the computations
  used to position the lines, rather than a separate hard-coded annotation.
- Separated the two scale-audit panel headings from their legends. A layout
  check detected overlapping text boxes in the original arrangement.
- Expanded the centroid explanation with explicit coarse area and first moment
  so the ratio and its relative error can be reconstructed directly.
- Adopted one English-labelled SVG set for EN/RU/zh-CN. Captions, explanations,
  and descriptive alternatives remain translated and reviewed with each page.

## Repeatable verification

`tests/test_guide_figures.py` checks 22 curves at 401 coordinates each (8,822
grades) against elementary mathematical references that do not use the library
evaluators. It checks the actual Matplotlib line, scatter, and bar data exported
to SVG; measurement markers, alpha-cut boundaries, audit gaps, and exact rational
centroid moments are included. It also checks title/legend bounds and separation.
Documentation CI explicitly installs the pinned plotting dependencies, executes
these checks against the installed scalar API, and compares committed SVG bytes.
Ordinary tests without the optional plotting dependencies skip this module.

The corrected SVGs require visual inspection as well as numerical and byte
checks. Full supported-Python, strict-site, package, and regression gates remain
CI responsibilities. Translation completeness and rendered locale asset parity
remain tracked acceptance work under Tasks #295, #296, and #297.
