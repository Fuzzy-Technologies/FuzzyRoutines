<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0020: Bounded differentiable Sugeno feasibility

## Status

Accepted on 2026-10-14 for the bounded repository research in Task #329.
**No-go for public tensor support in 2.1**; the optional prototype is retained
as reproducible evidence.
No public tensor backend or package dependency is introduced.

## Context

A fixed fuzzy encoder before an MLP changes the representation of the data.
It does not make the encoder's membership parameters trainable. A differentiable
Sugeno model instead places membership functions, product rule firing,
normalization and rule consequences inside a single automatic-differentiation
computation graph. Its parameters can then receive gradients from prediction
error.

[Jang's ANFIS paper](https://doi.org/10.1109/21.256541) describes an adaptive
network implementing fuzzy rules and a hybrid learning procedure. The present
experiment studies a small gradient-trained Sugeno network; it does not claim
to reproduce that hybrid learning algorithm.

## Bounded experiment

- Repository-only PyTorch CPU float64 code, separate from `fuzzyroutines`.
- Two normalized scalar inputs, two Gaussian terms per input, four Cartesian
  product rules and one scalar output.
- Trainable ordered centers derived from positive normalized gaps, and positive
  widths constrained to a fixed finite interval. No historical preset is changed.
- Explicit constant and affine consequences; unconstrained finite outputs.
- Positive rule firing is normalized in log space. Zero rule weights disable
  rules; all-zero weights raise `UndefinedResultError`. Invalid coordinates,
  shapes, dtypes or non-finite parameters fail before a prediction is returned.
- Forward arithmetic remains entirely in Torch. Calling scalar `Defuz()`,
  converting to NumPy or detaching intermediate values would sever the relevant
  gradient path and is outside this model.
- Frozen-parameter parity with `SugenoModel` and numerical gradient checks over
  input, membership and consequence parameters precede training evidence.
- Shared synthetic data, split identities and baseline protocol with Task #328;
  validation may select an epoch, but held-out samples never tune the model.
- Compare against a fully fixed rule model and the shared small MLP. Report
  metrics, timings, parameter counts and optional dependency costs.

The [PyTorch 2.14 autograd contract](https://docs.pytorch.org/docs/2.14/notes/autograd.html)
distinguishes recorded gradient operations from no-grad execution. Training
keeps the forward graph; no-grad is reserved for evaluation and optimizer work.
[Gradcheck](https://docs.pytorch.org/docs/2.14/notes/gradcheck.html) compares the
autograd Jacobian with central finite differences; tests use float64 and
interior inputs, away from domain validation boundaries.

## Promotion criteria

A public backend needs a separate decision covering tensor shapes and devices,
dtype/range/parity policies, differentiability of every exposed operation,
serialization, dependency isolation, sustained maintenance and real consumer
benefit. Passing this small synthetic experiment alone cannot establish those
contracts or justify replacing the dependency-free scalar core.

## Decision and evidence

The graph is feasible: frozen zero/first-order calculations agree with the
scalar engine and an independent Gaussian weighted-average reference within
absolute `1e-12`. CPU float64 numerical Jacobian checks cover inputs, membership
parameters and consequences. Fixed zero weights disable rules; all-zero weights
fail explicitly. The prototype rejects trainable rule weights. Subnormal
positive fixed weights are normalized in log space, so a product that would
underflow in scalar arithmetic does not falsely report no firing. Scalar parity
is claimed where the scalar firing strengths remain representable, not across
that intentionally different underflow policy. Saturated constrained parameters
remain valid; finite parameters can still produce affine overflow, which fails.

`research/run_sugeno.py` at experiment revision `588f31c` reuses Task #328's data
generator, split function, codec, metrics and MLP trainer. The artifact
`research/results/differentiable-sugeno.json` records exact source-file SHA-256
hashes, split identities, predictions, selected parameters and learning curves.
The dataset hash is
`269ecf533ab25d3371f2b0b208173adb6d2655eb1c30ba51c7776e37d5f000d2`.

There are 600 uniform two-input observations; the illustrative latent score is
`0.05 + 0.65 * severity + 0.30 * exposure`. The primary target is the selected
historical term's centroid computed by the modern API over its original
integration window. Data/split/network seeds
are 1729/1730/1731, with 360 training, 120 validation and 120 held-out rows.
Every trainable model uses full-batch Adam, learning rate 0.01, 400 epochs and
minimum validation MSE checkpoint selection. No held-out tuning occurred.
Two default executions reproduced all scientific values exactly; timing and
dependency measurement are separately machine-dependent. Tests also perturb
held-out targets and require identical trained parameters and checkpoints.

| Model                                            | Trainable scalars | Held-out centroid RMSE | Label accuracy | Out-of-domain outputs |
| ---                                              | ---:              | ---:                   | ---:           | ---:                  |
| Fixed four-rule model                            | 0                 | 0.093063               | 68.33%         | 0/120                 |
| Trainable zero-order Sugeno                      | 14                | 0.068779               | 94.17%         | 0/120                 |
| Trainable first-order Sugeno                     | 22                | 0.067643               | 91.67%         | 2/120                 |
| Fixed memberships, trainable affine consequences | 12                | 0.065600               | 88.33%         | 0/120                 |
| Shared raw-input MLP, 2–16–16–1                  | 337               | 0.069001               | 93.33%         | 0/120                 |

Counts are stored trainable scalar parameters, not identifiable degrees of
freedom: each three-logit gap vector has an additive invariance. The fixed
rule baseline uses declared constants `(0.15, 0.4, 0.6, 0.85)` and is not a tuned
expert system. After fitting, scalar parity error is at most `3.34e-16` across
the recorded held-out evaluations. Output-domain violations are reported,
never clipped. Lower scalar RMSE and better label classification are different
objectives; neither column establishes a universal winner.

The recorded Linux x86_64 CPU run uses Python 3.14.8 and Torch 2.14.1+cpu, one
thread. Training took 2.21 s / 2.50 s / 1.88 s for zero-order / first-order /
fixed-membership variants and 2.43 s for the MLP. The entire measured experiment
took 25.21 s, including its dependency probe. A fresh-process Torch import took
9.03 s including Python startup with existing OS caches. Installed Torch files
occupy 715,535,767 bytes (about 682 MiB), excluding transitive dependencies.
These are observations from one shared machine, not portable speed guarantees.

**Decision:** keep the dependency-free scalar package and publish no trainable
tensor API. The bounded graph is scientifically testable, but this one synthetic
task shows no reduction in centroid-target RMSE from training memberships over
its fixed-membership control. The learned zero/first-order models do achieve
higher label accuracy, so the two objectives must not be conflated. The
first-order graph also needs an explicit downstream output-domain
policy. A future public proposal needs real consumer datasets, multiple seeds,
output and numerical contracts, device/dtype coverage, serialization and an
owner for the framework/dependency maintenance burden. No claim is made about
ANFIS hybrid training or superiority of either fuzzy models or MLPs in general.
