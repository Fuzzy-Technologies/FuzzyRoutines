<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Optional batches

The [worked example](../../guides/numpy-batches.md) explains installation, array
shapes, ownership and no-match handling. Import this surface explicitly from
`fuzzyroutines.batches`; scalar calls remain independent of NumPy.

::: fuzzyroutines.batches
    options:
      members:
        - EvaluateMembershipBatch
        - FuzzifyBatch
        - ScaleBatchResult
