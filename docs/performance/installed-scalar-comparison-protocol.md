<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Installed scalar comparison protocol

Task #337 compares the actual PyPI 2.0.0 wheel with the final successful CI candidate. The default runner mode only prints the plan. A Markdown draft explicitly contains no measured values. The same shared standard-library artifact verifier serves the scalar and optional batch runners.

## Inputs to supply after final CI succeeds

Copy `experiments/installed-scalar-comparison.template.json` to a separate final config and fill both artifact records. Set `harness_commit` to the published commit of this runner and its shared artifact verifier. Keep `workload_commit` pinned unless the mathematical workload itself must be deliberately revised. Its three scripts are byte-identical at release commit `49c9aee67a60cad74bc9494943b8745b72d2f43c` and prepared branch commit `383d8cdf491f918194d60c6032abc0c3b95e93c5`.

- Baseline: actual PyPI 2.0.0 wheel, expected SHA256, and a saved response from `https://pypi.org/pypi/fuzzyroutines/2.0.0/json`. The saved JSON must identify this exact filename and digest.
- Candidate: actual successful final CI wheel, expected SHA256, exact wheel metadata version, full built source commit, successful GitHub workflow run JSON and its `html_url`, artifact API metadata JSON (`artifact_metadata_json`), and downloaded artifact ZIP (`artifact_archive`). The artifact API run ID/head must match the successful package workflow, and its digest must match the ZIP. The supplied wheel must be byte-identical to the archived wheel.

The archive's `source-revision.txt` and `reproducibility.json` must both identify the candidate's built `source_commit`. Both independent-build wheel hashes and its unique `SHA256SUMS` entry must equal the measured wheel digest. For a direct checkout, the built source equals workflow `head_sha`. A pull-request workflow can build a synthetic merge: require exactly two Git parents with the immutable workflow head as the second parent. Mutable PR head/base snapshots are never used. Built source, workflow head, artifact ZIP and wheel remain separate identities in the report.
- Both Git source commits must exist in the configured repository. The runner compares every wheel package `.py` file and `py.typed` byte-for-byte against the declared commit. It then verifies the installed copies against those same hashes.
- Select a new output directory; the runner refuses to overwrite an existing run. Use the same existing CPython 3.14 interpreter to coordinate both isolated installations. That interpreter needs pip for `pip --python`; the measured environments contain only each wheel, installed offline with `--no-deps` and no optional NumPy.

The workflow JSON and digest-bound artifact records support provenance; they are not a cryptographic artifact attestation. The recorded wheel SHA256 plus exact Python-source comparison identifies the bytes actually tested. The release coordinator obtains the run JSON and artifact metadata from GitHub and the final ZIP from that workflow.

The candidate is the CI-built `2.1.0` package after feature integration and release preparation, before merging to `master`. A later report-only commit can change `SOURCE_DATE_EPOCH` and wheel archive timestamps. Retain the measured artifact's own archive digest and Python payload manifest. A later release artifact needs a separate payload comparison; matching code payloads do not establish identical wheel archive bytes.

## Read-only planning and draft generation

Run from the repository root with an existing CPython 3.14 interpreter:

```bash
python3.14 -I experiments/benchmark_installed_scalar.py --config experiments/installed-scalar-comparison.template.json
python3.14 -I tools/render_installed_scalar_comparison.py --draft experiments/installed-scalar-comparison.template.json --output comparison-draft.md
```

After the coordinator supplies both final artifacts and provenance:

```bash
python3.14 -I experiments/benchmark_installed_scalar.py --config config.final.json --run
python3.14 -I tools/render_installed_scalar_comparison.py --input results-final/comparison.json --output results-final/comparison.md
```

No network access occurs during these commands. No package or documentation build is performed. Missing provenance or inconsistent wheel/source/installed bytes abort before timing.

## What is measured

Thirty separate rows: process startup, fresh-process import of the package and compatibility facade, eight memberships, eight operators, two scale constructions, two scale lookups, four fuzzy-set constructions, and four centroid recalculations. Inputs are the literal fixtures in the existing three pinned `tools/benchmark_*.py` scripts; no random generator or synthetic new workload is introduced.

The common wrapper reuses only their workload builders. Their `GetGitMetadata()` reads the harness checkout, not the imported package, and is deliberately never called. The report records package source commits, wheel hashes, installed origins, historical workload commit, and published wrapper commit under separate fields. The wrapper must execute from its exact clean published Git revision; its own file, the shared verifier, and the table renderer are compared against committed bytes. Historical workload scripts are extracted from immutable Git objects, so their snapshot has no working-tree overlay. Every harness file also has a recorded SHA256.

Each artifact first passes an untimed preflight. Each of seven paired rounds starts a fresh worker process for each artifact, alternating baseline/candidate order. Operations have explicit untimed warmups. Timed loops exclude parity checks, object summarization, tracing, and process startup. Scale lookup includes the existing membership-counting instrumentation and is divided by its fixed 100 lookups per invocation. Fuzzy-set construction timing excludes its independent centroid observation. Process startup has an explicit warmup and separate `python -I -c pass` control; it includes launch and teardown overhead. Import is timed inside the worker and excludes startup.

Old scale/centroid harness `Measure()` functions combine tracemalloc with timing and lack the full warmup/IQR/independent-parity protocol. They are deliberately not reused. Therefore these new untraced measurements must not be compared numerically to previously published traced samples.

## Numerical gates

- The existing membership/operator builders contain independent analytical expectations; absolute tolerance `1e-12`, relative tolerance zero.
- Scale construction must preserve ordered term names. Lookup at 0.5 must select `Med`, with exactly 300 or 500 membership evaluations for 100 lookups.
- Centroid references are independent closed forms over `[0, 1]`: triangle `1/2`, symmetric bell `11/20`, quadratic S-shoulder `17/24`, and the hyperbolic ratio of first moment `atan(49)/98` to the closed-form integral of `1/(1 + (7x)^4)`. Absolute tolerance `1e-10`, relative tolerance zero.
- Both artifacts must pass their own independent gates, then their observed results must agree within the same tolerances before any timed round starts. Gates also run in each fresh measured worker.

Raw samples, minimum, median, inclusive IQR, per-round order, installed dependency inventory, interpreter executable digest, CPU/OS/memory/cgroup/affinity/thread environment, invocation commands, provenance hashes, and artifact identities are retained in `comparison.json`. Per-round JSON is saved as progress evidence. The table renderer independently recomputes summaries and ratios from raw samples before formatting.

The result applies only to this shared host and these fixed scalar workloads. There are no timing thresholds in CI and no extrapolation to production throughput. Optional NumPy evidence remains in its separately reviewed reports.
