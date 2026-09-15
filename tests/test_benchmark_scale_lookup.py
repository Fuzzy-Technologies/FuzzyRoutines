from tools.benchmark_scale_lookup import BuildReport, LOOKUPSAMPLES, MINIMUMSAMPLES, Measure, SCALES


def test_BenchmarkScaleReportSeparatesConstructionAndLookup():
    report = BuildReport()

    assert report["sample_count"] == MINIMUMSAMPLES
    assert set(report["workloads"]) == set(SCALES)

    defaultLookup = report["workloads"]["default"]["repeated_lookup"]["result"]
    universalLookup = report["workloads"]["universal"]["repeated_lookup"]["result"]

    assert defaultLookup["lookups_per_sample"] == LOOKUPSAMPLES
    assert universalLookup["lookups_per_sample"] == LOOKUPSAMPLES
    assert defaultLookup["membership_evaluations"] == 4 * LOOKUPSAMPLES
    assert universalLookup["membership_evaluations"] == 8 * LOOKUPSAMPLES


def test_BenchmarkScaleRejectsInsufficientSamples():
    try:
        Measure(lambda: None, MINIMUMSAMPLES - 1)

    except ValueError:
        pass

    else:
        raise AssertionError("expected an explicit sample-count error")
