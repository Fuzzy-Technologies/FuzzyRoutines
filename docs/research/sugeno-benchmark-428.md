<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Multiseed Sugeno benchmark protocol

This first slice of [Task #428](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/428)
fixes the observation and evaluation protocol for the synthetic benchmark from
[ADR-0020](../adr/0020-differentiable-sugeno-feasibility.md). The existing
synthetic severity/exposure relation is illustrative. Its centroid targets use
the historical term order, windows and winner policy.

Use the same 600 rows and identical 360/120/120 train, validation and held-out
identities for every model within one seed. Fit from the training partition,
select checkpoints by validation MSE, and score the held-out partition once
the checkpoint is fixed. The three seed triplets are 1729/1730/1731,
2729/2730/2731 and 3729/3730/3731 for data, split and MLP initialization.
These are separate synthetic draws, not a test of transfer across datasets.

From the repository root, write evidence to a directory outside the checkout.
The plan command works without Torch. Run training in an isolated environment
with the optional CPU Torch version used for the experiment.

```sh
evidence_dir=$(mktemp -d)
python -m research.plan_sugeno_428 > "$evidence_dir/plan.json"
for seed in 1729 2729 3729; do
    python -m research.run_sugeno --seed "$seed" --samples 600 --epochs 400 \
        --measure-dependencies --output "$evidence_dir/run-$seed.json"
done
```

Match each report's dataset and split hashes and exact split arrays to its plan
entry. Compare fixed rules, fixed memberships with trained affine
consequences, trained zero-order and first-order rules, and the raw-input MLP.
Report centroid RMSE, latent RMSE, label accuracy, no-match and out-of-domain
counts by seed. Compare fixed and trained memberships at the same affine
consequent order. Retain raw predictions and source hashes. Record wall time,
CPU/thread settings, installed dependency size and import time separately from
scientific results. Repeat in the same environment and compare scientific
values after excluding timing and dependency measurements.

The plan records no new training metrics. Sourced datasets, chronological
splits where applicable, sparse TSK/PyTSK comparisons, independent gradient
and scalar parity evidence and the research decision remain open. The existing
production API and dependency policy remain governed by ADR-0020.
