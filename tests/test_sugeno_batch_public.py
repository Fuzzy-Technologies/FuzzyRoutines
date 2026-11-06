# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public Sugeno batch input, feature binding, and numerical evidence."""

from fractions import Fraction

import pytest

from fuzzyroutines.exceptions import InvalidParameterError, InvalidParameterTypeError
from fuzzyroutines.sugeno_batches import (
    EvaluateSugenoBatch,
    SugenoBatchFullTrace,
    SugenoBatchResult,
    SugenoBatchTrace,
)

np = pytest.importorskip("numpy", reason="Sugeno rule batches use the optional NumPy extra")

from experiments.sugeno_batch_contract_probe import ScalarModel

FEATURE_NAMES = ("risk", "exposure")


@pytest.mark.parametrize("order", ("constant", "affine", "mixed"))
@pytest.mark.parametrize("chunkSize", (1, 2, 8))
def test_PublicEntryPointBindsPermutedColumnsAndMatchesScalar(order, chunkSize):
    """Convert one source chunk at a time without losing trace or row order."""

    model = ScalarModel(order)
    source = np.array([[0.25, 0.25], [0.5, 0.75], [0.0, 0.25]], dtype=">f8")[::-1]
    source.setflags(write=False)
    result = EvaluateSugenoBatch(
        model, source, featureNames=FEATURE_NAMES[::-1], onError="mask", trace="full", chunkSize=chunkSize,
    )
    scalar = [model.Evaluate({"risk": float(risk), "exposure": float(exposure)}) for exposure, risk in source[[1, 2]]]

    assert isinstance(result, SugenoBatchResult), "The public entrypoint returns its documented result type"
    assert isinstance(result.trace, SugenoBatchTrace), "Full mode includes a public trace record"
    assert isinstance(result.trace.full, SugenoBatchFullTrace), "Full evidence has a public result type"
    assert result.featureNames == FEATURE_NAMES, "Trace metadata follows model declaration order"
    np.testing.assert_array_equal(result.status, [3, 0, 0])
    np.testing.assert_array_equal(result.validMask, [False, True, True])
    np.testing.assert_allclose(result.values[1:], [row.value for row in scalar], rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        result.trace.full.consequents[1:], [[rule.consequentValue for rule in row.rules] for row in scalar], rtol=0, atol=1e-12,
    )
    assert np.isnan(result.trace.full.inputGrades[0]).all(), "No-fire rows must not expose partial term traces"


@pytest.mark.parametrize("empty", ([], (), np.empty((0, 2))))
def test_EmptyInputRetainsFeatureAndTraceAxes(empty):
    """Accept only the supported empty shapes and preserve full trace dimensions."""

    result = EvaluateSugenoBatch(ScalarModel("constant"), empty, featureNames=FEATURE_NAMES, trace="full")

    assert result.values.shape == result.status.shape == (0,), "Empty input has no observations"
    assert result.trace is not None and result.trace.full is not None, "Full mode exposes empty trace arrays"
    assert result.trace.full.inputGrades.shape == (0, 4), "Empty input retains the declared term axis"


@pytest.mark.parametrize("values", (np.empty((0,)), np.empty((0, 1)), np.zeros((2, 2, 1)), [0.5, 0.5], [[0.5, 0.5], [0.5]]))
def test_InvalidShapesAreCallErrorsEvenInMaskMode(values):
    """Reject rank and width errors before any result allocation is observable."""

    with pytest.raises(InvalidParameterError):
        EvaluateSugenoBatch(ScalarModel("constant"), values, featureNames=FEATURE_NAMES, onError="mask")


@pytest.mark.parametrize("values", (
    np.zeros((1, 2), dtype=bool),
    np.zeros((1, 2), dtype=complex),
    np.zeros((1, 2), dtype=object),
    np.zeros((1, 2), dtype=[("value", "f8")]),
    np.ma.array([[0.5, 0.5]]),
    [[0.5, True]],
    [[0.5, np.bool_(False)]],
    [[0.5, np.timedelta64(1, "s")]],
    [[0.5, Fraction(1, 2)]],
    {"risk": 0.5, "exposure": 0.5},
))
def test_UnsupportedInputKindsAreNeverCoerced(values):
    """Reject boolean, complex, object and custom real inputs."""

    with pytest.raises(InvalidParameterTypeError):
        EvaluateSugenoBatch(ScalarModel("constant"), values, featureNames=FEATURE_NAMES, onError="mask")


@pytest.mark.parametrize("options", (
    {"featureNames": ("risk", "risk")},
    {"featureNames": ("risk", "Exposure")},
    {"featureNames": ("risk",)},
    {"featureNames": ["risk", "exposure"]},
    {"chunkSize": False},
    {"chunkSize": 0},
    {"backend": "auto"},
    {"onError": "ignore"},
    {"trace": "all"},
))
def test_EmptyInputStillValidatesColumnNamesAndOptions(options):
    """Validate the entire call contract even without observations."""

    with pytest.raises(InvalidParameterError):
        EvaluateSugenoBatch(ScalarModel("constant"), [], **({"featureNames": FEATURE_NAMES} | options))


def test_SequencesPreserveNumericScalarKindsAndClassifyConversionOverflow():
    """Classify a huge built-in integer locally, after all source kinds pass."""

    model = ScalarModel("constant")
    values = ((np.float32(0.25), np.float16(0.5)), (10**400, np.int32(0)), (0.75, 0.5))
    result = EvaluateSugenoBatch(model, values, featureNames=FEATURE_NAMES, onError="mask", chunkSize=2)

    np.testing.assert_array_equal(result.status, [0, 1, 0])
    assert np.isnan(result.values[1]), "Overflowing conversion must mark only its source row"

    with pytest.raises(InvalidParameterError, match=r"row 1 \(risk\):"):
        EvaluateSugenoBatch(model, values, featureNames=FEATURE_NAMES, chunkSize=1)

    with pytest.raises(InvalidParameterTypeError):
        EvaluateSugenoBatch(model, [[np.nan, 0.5], [0.5, True]], featureNames=FEATURE_NAMES, chunkSize=1)


def test_ExtendedPrecisionArrayOverflowRestoresAmbientNumpyPolicy():
    """Do not turn an overflowing conversion into a call-wide failure."""

    if np.finfo(np.longdouble).max <= np.finfo(np.float64).max:
        pytest.skip("Extended precision is not wider than binary64 on this platform")

    model = ScalarModel("constant")
    source = np.array([[0.25, 0.5], [np.finfo(np.longdouble).max, 0.5]], dtype=np.longdouble)

    with np.errstate(all="raise"):
        policy = np.geterr()
        result = EvaluateSugenoBatch(model, source, featureNames=FEATURE_NAMES, onError="mask")
        assert np.geterr() == policy, "Chunk conversion must restore the ambient NumPy policy"

    np.testing.assert_array_equal(result.status, [0, 1])
