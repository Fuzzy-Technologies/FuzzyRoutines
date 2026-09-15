import json

from tools.benchmark_scale_lookup import (
    LOOKUPSAMPLES,
    MINIMUMSAMPLES,
    SCALES,
    BuildReport,
    Main,
    Measure,
)


def test_BenchmarkScaleReportSeparatesConstructionAndLookup():
    report = BuildReport()

    assert report["sample_count"] == MINIMUMSAMPLES
    assert set(report["workloads"]) == set(SCALES)

    defaultLookup = report["workloads"]["default"]["repeated_lookup"]["result"]
    universalLookup = report["workloads"]["universal"]["repeated_lookup"]["result"]

    assert defaultLookup["lookups_per_sample"] == LOOKUPSAMPLES
    assert universalLookup["lookups_per_sample"] == LOOKUPSAMPLES
    assert defaultLookup["membership_evaluations"] == 3 * LOOKUPSAMPLES
    assert universalLookup["membership_evaluations"] == 5 * LOOKUPSAMPLES


def test_BenchmarkScaleRejectsInsufficientSamples():
    try:
        Measure(lambda: None, MINIMUMSAMPLES - 1)

    except ValueError:
        pass

    else:
        raise AssertionError("expected an explicit sample-count error")


def test_BenchmarkScaleMainEmitsJson(capsys):
    Main()
    report = json.loads(capsys.readouterr().out)

    for scaleName, scaleClass in SCALES.items():
        constructionResult = report["workloads"][scaleName]["construction"]["result"]

        assert constructionResult["class"] == scaleClass.__name__, "construction evidence identifies the wrong scale"
        assert constructionResult["level_count"] > 0, "construction evidence lost the scale levels"
