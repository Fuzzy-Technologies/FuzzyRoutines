<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0019: Optional Neural Integration with Fixed Fuzzy Encodings

- Status: Accepted on 2026-10-14 after independent scientific and implementation review
- Date: 2026-10-14
- Related tasks: [#327](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/327), [#328](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/328)
- Related Feature: [#320](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/320)
- Prerequisite: [ADR-0016](0016-linguistic-encodings-and-historical-preset.md)

## Context

Users need a current, executable demonstration of linguistic labels and
membership vectors as neural inputs and interpretable outputs. Historical
classifiers are conceptual context only: their source, architecture, models,
data and dependencies are not carried into this example. The core library
must remain framework-neutral, and examples must distinguish fixed fuzzy
preprocessing from learned fuzzy rules.

## Decision

Provide a standalone CPU PyTorch example in `examples/neural/run.py`, with its
optional dependency pinned separately in `examples/neural/requirements.txt`.
No Torch imports, dependency, public tensor types or trainable API enter the
core. The example uses existing `LinguisticCodec` and historical preset contracts.
The current verified environment is CPython 3.14.8, PyTorch 2.14.1+cpu and
Linux x86_64; the dependency is supported on CPython 3.14 according to the
official release matrix and available CPU wheels.

### Fixed scientific protocol

Generate 600 independent uniform pairs $(s,e)\in[0,1]^2$ with local random
seed 1729 and the illustrative relation $y=0.05+0.65s+0.30e$. A separate
seed 1730 creates disjoint 60/20/20 train/validation/held-out identities before
training. There is no fitted normalization. Membership functions, exact-last
tie policy and original per-term centroid windows are fixed.

Compare raw coordinates, label-centroid pairs and ten ordered membership
grades. All three predict the same target: the centroid of the selected label
of $y$. Each network has two 16-unit tanh layers, a linear scalar output,
float64 CPU tensors, one thread, deterministic algorithms, initialization seed
1731, Adam learning rate 0.01 and 400 full-batch epochs. The minimum validation
MSE selects a checkpoint. Report parameter counts because input dimensions
differ; never inspect held-out labels to select a checkpoint.

Report held-out centroid-target RMSE, separately named continuous-score RMSE,
decoded-label accuracy, out-of-domain/no-match counts, training-mean-target
and training-majority-label baselines. Preserve out-of-domain numeric errors
without clipping. Explicitly show valid endpoints, unknown-label errors and
historical weak coverage. No claim of guaranteed fuzzy improvement is made.

A separate ten-input, five-sigmoid-output experiment predicts independent
memberships of continuous $y$, using mean squared grade error. Those targets
are not centroid memberships, one-hot classes or class probabilities. Its
different task is reported separately from scalar regression. Grade sums need
not be one, and the output vector need not lie on the membership curve of any
single scalar coordinate.

### Evidence and reproducibility

JSON records source and dataset SHA-256 values, split identities, environment,
selected epochs, loss histories, numeric predictions and boundary probes.
The committed reference is a measured illustration, not an accuracy threshold.
The first and repeated default runs produced identical numeric reports on the
recorded environment. Cross-version/platform bitwise equality is not promised.
Two SVG figures render actual recorded model outputs and scalar reference
curves without importing Torch or retraining. Source hashes reject stale
example/report combinations; SVG comparison detects rendering drift.

Focused tests use an analytical task oracle, disjoint split identities,
an encoding collision with unequal target labels, weak coverage, unchanged
weights after held-out-target poisoning, independent recomputation of selected
validation loss, explicit tensor-shape checks and a bounded headless CLI run.
The direct CLI has an installed-package guard. Candidate-wheel execution is
an optional-dependency CI responsibility; a source run is not presented as
installed-artifact evidence.

The three locale guides contain runnable shell commands and mathematical
explanations. Torch-dependent code remains in the versioned script, not in
core-only executable documentation snippets.

## Consequences

- Centroids are representative input/target coordinates, never learned
  network weights. Fixed fuzzy encodings are lossy and are not differentiated.
- Raw inputs perform best in this measured task. Identical centroid encodings
  can correspond to different targets, while full vectors may differ only in
  a numerically tiny membership tail. Both limitations are documented.
- Real applications must define units, normalization, coverage and output
  decisions explicitly. The synthetic relation is not a validated risk model.
- Differentiable memberships, rule training and a supported neural backend
  require a separate feasibility decision and public contract.
