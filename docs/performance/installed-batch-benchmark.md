<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Installed NumPy candidate measurement protocol

This protocol closes the artifact-identity gap left by the earlier
[source batch study](public-batch-comparison.md) and
[public consumer test replays](public-consumer-batch-replay.md). It prepares a
separate measurement of an actual CI wheel. No performance result is implied
by a prepared runner or a passing harness unit test. Keep all previous raw
records unchanged.

## Artifacts and reproducible execution

First publish the harness code, fetch that public commit, and use a clean
checkout at its exact revision. The package commit and harness commit are
separate identities. The release coordinator supplies the actual successful
CI wheel, its SHA-256, the built package source commit, the saved successful
GitHub workflow run JSON, the artifact API metadata JSON, and the downloaded
artifact ZIP. Set `artifact_metadata_json` and `artifact_archive` to those last
two files. The API artifact must identify the same workflow run and head, and
its archive digest must match the downloaded ZIP. The extracted wheel must be
byte-identical to the wheel inside that archive.

The archive's `source-revision.txt` and `reproducibility.json` must identify
`source_commit`; both independent-build wheel hashes and its unique
`SHA256SUMS` entry must match the actual wheel digest. A pull-request workflow
can build a synthetic merge instead of the branch commit in `head_sha`. In that
case the built Git commit must have exactly two parents, with the immutable
workflow head as its second parent. Mutable PR head/base snapshots are not
used. The report retains the built source, workflow head, archive identity and
wheel identity separately.

Copy the [configuration template](../../experiments/installed_batch_config.template.json)
outside the checkout and fill the missing identities and absolute local paths.
The NumPy entry pins the Linux CPython 3.14 NumPy 2.3.5 wheel used by this study;
another platform requires its own explicitly verified wheel identity. Both
wheels must already be downloaded. The run itself performs no network access,
package build, or documentation build.

```bash
python -I experiments/installed_batch_benchmark.py --config /tmp/installed-batch-config.json
python -I experiments/installed_batch_benchmark.py --config /tmp/installed-batch-config.json --run
```

Use CPython 3.14. The first command only prints a plan. The second requires an
unused output directory outside the clean checkout. It creates an isolated
environment, installs the supplied candidate and NumPy wheels offline with
`--no-deps`, and retains the effective config and installation command. Do not
run another benchmark concurrently on the shared host; coordinate the window
with the separate 2.0-versus-candidate scalar comparison.

The shared [verifier](../../experiments/installed_wheel_evidence.py) binds the
wheel checksum, distribution identity, provenance JSON, and every package
`.py`/`py.typed` file to its declared Git source. It checks the installed copies,
metadata location, resolved import origin, and loaded submodule origins. The
source checkout never enters `sys.path`: only the `experiments` namespace is
exposed to the isolated worker. Memory and import subprocesses use the same
installed interpreter with `-I`; source-oriented `-m` workers are not used.

Workflow metadata is supporting provenance, not a cryptographic artifact
attestation. The coordinator must obtain the wheel from that workflow. The
retained checksum identifies the bytes actually measured. If later report-only
commits change archive timestamps or ZIP bytes, that later wheel has a different
identity. Any claim of equivalent package code must separately compare the
package payload manifest; it must not relabel the measured wheel checksum.

## Measurement boundary

The runner reuses `BuildOperation`, numerical parity checks, `MeasurePair`,
`MemoryWorker`, and dependency-cost mechanics from the existing public batch
study. It replaces only source-oriented subprocess dispatch and provenance.
Both scalar and NumPy operations come from the same installed candidate.

- Twenty-four synthetic combinations: Gaussian, Bell and the historical
  Universal Fuzzy Scale; shapes `(1,)`, `(16,)`, `(32, 32)`, `(10000,)`;
  prepared-array and conversion-inclusive inputs.
- Four consumer-replay combinations: the ordered 17 `RiskLong` and 13
  `RiskShort` public test inputs, each in both input modes. The pinned fixture
  preserves independent expected labels and rounded percentages. These thirty
  cases are grouped test replays, not observed production batch sizes.
- One warmup and at least seven paired repeats with alternating backend order.
  Wall and process-CPU raw samples, medians, minima, maxima and inclusive IQR
  remain available. The report writer independently recomputes all summaries
  and speed ratios; there is no speed acceptance threshold.
- Numerical tolerance is absolute `1e-12`, relative zero; scale selection/tie
  masks and upstream replay labels/percentages must match exactly before timing.
  Both APIs return full membership and decision evidence.
- Models are constructed before timing. Scalar inputs are flat Python lists.
  NumPy inputs are either prepared float64 arrays or Python lists, nested for
  the matrix case. Conversion, validation, output allocation and ownership
  guarantees stay inside the public call.
- Isolated memory observations cover the smallest and largest synthetic
  shapes and each consumer replay. Whole-process RSS and separately traced
  allocation are single observations, not memory distributions. RSS includes
  the interpreter, verification harness and imports.
- Fresh-process package/NumPy imports and seven offline NumPy wheel installs
  are measured once in the synthetic run. Import timing excludes startup and
  package verification; verification reads package bytes before timing and
  filesystem caches are not flushed. Installation timing excludes environment
  creation, network download and bytecode compilation.

The new files are `public-batches-installed-python314.json` and
`public-consumer-replays-installed-python314.json`. The replay record links the
exact SHA-256 of its accompanying synthetic dependency-cost record. Reports
retain wheel identity, installed origins, package source hashes, clean harness
commit and execution-file hashes separately. A final successful completion
record is written only after both studies and post-run identity checks pass.

Host scheduling and shared resource contention remain limitations. No result
establishes a universal switching threshold, FMA/robot speedup, application
throughput or production trading behavior. Supporting test fixtures identify
specific public consumer-shaped workloads only.
