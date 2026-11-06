<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# JSON configuration

Install `fuzzyroutines[config]` to load and save standalone v1 JSON models.
`LoadModel` reads UTF-8 bytes into immutable scale, Mamdani, or Sugeno
definitions. `AssembleModel` binds existing runtime objects to explicit IDs,
and `DumpModel` returns canonical bytes. The caller manages file access
and invokes evaluation explicitly. Project envelopes are covered by the
project format and use a separate API contract.

A `ConfigurationError` supplies a category and an RFC 6901 JSON Pointer.
The exporter rejects custom evaluators and source numbers that would lose
precision. The validator loads on demand, so scalar use needs no extra.

::: fuzzyroutines.configuration
    options:
      members:
        - LoadModel
        - DumpModel
        - AssembleModel
        - ModelConfiguration
        - ScaleDefinition
        - ScaleRepresentatives
        - MamdaniBinding
        - MamdaniCentroid
        - SugenoBinding
        - ConfigurationError
