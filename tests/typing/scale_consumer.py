# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Installed-consumer type contracts for modern-scale factories and encodings."""

from typing import assert_type as assertType

from fuzzyroutines import (
    CreateUniversalFuzzyScale,
    FuzzificationPolicy,
    FuzzificationResult,
    IntegrationDomain,
    LinguisticCodec,
    LinguisticScale,
    MembershipScalar,
    UniversalFuzzyScaleDomains,
    UniversalFuzzyScalePolicy,
)


def CheckScaleFactories() -> None:
    """Require explicit modern types without weakening the legacy facade."""

    assertType(CreateUniversalFuzzyScale(), LinguisticScale)
    assertType(UniversalFuzzyScalePolicy(), FuzzificationPolicy)
    assertType(UniversalFuzzyScaleDomains(), tuple[IntegrationDomain, ...])


def CheckLinguisticCodec() -> None:
    """Keep scalar, vector and immutable configuration types explicit."""

    codec = LinguisticCodec(
        CreateUniversalFuzzyScale(),
        UniversalFuzzyScaleDomains(),
        UniversalFuzzyScalePolicy(),
    )
    assertType(codec.termNames, tuple[str, ...])
    assertType(codec.EncodeLabel("Med"), MembershipScalar)
    assertType(codec.EncodeMemberships(0.5), tuple[MembershipScalar, ...])
    assertType(codec.DecodePrediction(0.5), FuzzificationResult)
    assertType(codec.AverageRepresentatives((0, 0, 1, 0, 0)), float)
    codec.EncodeLabel(0.5)  # type: ignore[arg-type]
    codec.EncodeMemberships([0.5])  # type: ignore[arg-type]
    codec.AverageRepresentatives([0, 0, 1, 0, 0])  # type: ignore[arg-type]
    codec.scale = CreateUniversalFuzzyScale()  # type: ignore[misc]
