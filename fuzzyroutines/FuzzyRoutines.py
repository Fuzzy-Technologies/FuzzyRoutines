# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Expose historical fuzzy-logic names through explicit compatibility adapters.

Canonical membership formulas, operators, domains, and numerical policies live
in the focused modern modules. Private adapters retain historical argument order,
mutable state, default scales, and return identities. New code should import the
focused modules or the modern package API.

The literal `__all__` list retains the fifteen supported historical symbols.
Imported helpers and private adapters are outside this compatibility surface.
"""

from fuzzyroutines._legacy.membership import MFunction
from fuzzyroutines._legacy.operators import (
    FuzzyAND,
    FuzzyNOT,
    FuzzyNOTParabolic,
    FuzzyOR,
    SCoNorm,
    SCoNormCompose,
    TNorm,
    TNormCompose,
)
from fuzzyroutines._legacy.scales import FuzzyScale, UniversalFuzzyScale
from fuzzyroutines._legacy.sets import FuzzySet
from fuzzyroutines._legacy.utilities import (
    DiapasonParser,
    IsCorrectFuzzyNumberValue,
    IsNumber,
)

__all__ = [
    "DiapasonParser",
    "FuzzyAND",
    "FuzzyNOT",
    "FuzzyNOTParabolic",
    "FuzzyOR",
    "FuzzyScale",
    "FuzzySet",
    "IsCorrectFuzzyNumberValue",
    "IsNumber",
    "MFunction",
    "SCoNorm",
    "SCoNormCompose",
    "TNorm",
    "TNormCompose",
    "UniversalFuzzyScale",
]

# Serialized historical objects must continue resolving the original module path.
# Adapters are private implementation details, not a replacement public namespace.
for _historicalSymbol in (
    DiapasonParser, IsNumber, IsCorrectFuzzyNumberValue,
    FuzzyNOT, FuzzyNOTParabolic, FuzzyAND, FuzzyOR,
    TNorm, TNormCompose, SCoNorm, SCoNormCompose,
    MFunction, FuzzySet, FuzzyScale, UniversalFuzzyScale,
):
    _historicalSymbol.__module__ = __name__

del _historicalSymbol
