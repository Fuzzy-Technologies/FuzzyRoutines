"""Parity tests for single-evaluation fuzzy scale lookup."""

from fuzzyroutines.FuzzyRoutines import FuzzyScale, FuzzySet, MFunction


def test_ScaleLookupPreservesLaterLevelTiePolicy():
    scale = FuzzyScale()
    sharedParameters = {"a": 0.0, "b": 1.0}
    scale.levels = [
        {
            "name": "First",
            "fSet": FuzzySet(MFunction("parabolic", **sharedParameters)),
        },
        {
            "name": "Second",
            "fSet": FuzzySet(MFunction("parabolic", **sharedParameters)),
        },
    ]

    assert scale.Fuzzy(0.5)["name"] == "Second", (
        "Single-evaluation lookup must preserve the historical later-level tie policy."
    )
