import inspect

import fuzzyroutines.FuzzyRoutines as fr


EXPECTED_FUNCTION_SIGNATURES = {
    "DiapasonParser": "(diapason)",
    "IsNumber": "(value)",
    "IsCorrectFuzzyNumberValue": "(value)",
    "FuzzyNOT": "(fuzzyNumber, alpha=0.5)",
    "FuzzyNOTParabolic": "(fuzzyNumber, alpha=0.5, epsilon=0.001)",
    "FuzzyAND": "(aNumber, bNumber)",
    "FuzzyOR": "(aNumber, bNumber)",
    "TNorm": "(aFuzzyNumber, bFuzzyNumber, normType='logic')",
    "TNormCompose": "(*fuzzyNumbers, normType='logic')",
    "SCoNorm": "(aFuzzyNumber, bFuzzyNumber, normType='logic')",
    "SCoNormCompose": "(*fuzzyNumbers, normType='logic')",
}

EXPECTED_CLASS_SIGNATURES = {
    "MFunction": "(userFunc, **membershipFunctionParams)",
    "FuzzySet": "(membershipFunction, supportSet=(0.0, 1.0), linguisticName='FuzzySet')",
    "FuzzyScale": "()",
    "UniversalFuzzyScale": "()",
}

EXPECTED_PUBLIC_MEMBERS = {
    "MFunction": {
        "name",
        "parameters",
        "Hyperbolic",
        "Bell",
        "Parabolic",
        "Triangle",
        "Trapezium",
        "Exponential",
        "Sigmoidal",
        "Desirability",
    },
    "FuzzySet": {"name", "mFunction", "supportSet", "defuzValue", "Defuz"},
    "FuzzyScale": {"name", "levels", "Fuzzy", "GetLevelByName"},
    "UniversalFuzzyScale": {
        "name",
        "levels",
        "Fuzzy",
        "GetLevelByName",
        "levelsNames",
        "levelsNamesUpper",
    },
}

EXPECTED_MEMBERSHIP_IDENTIFIERS = {
    "hyperbolic",
    "bell",
    "parabolic",
    "triangle",
    "trapezium",
    "exponential",
    "sigmoidal",
    "desirability",
}


def test_legacy_top_level_function_signatures():
    for name, expected in EXPECTED_FUNCTION_SIGNATURES.items():
        obj = getattr(fr, name)
        assert str(inspect.signature(obj)) == expected


def test_legacy_class_constructor_signatures():
    for name, expected in EXPECTED_CLASS_SIGNATURES.items():
        obj = getattr(fr, name)
        assert str(inspect.signature(obj)) == expected


def test_legacy_public_class_members_exist():
    for class_name, expected_members in EXPECTED_PUBLIC_MEMBERS.items():
        actual_members = set(dir(getattr(fr, class_name)))
        assert expected_members <= actual_members


def test_historical_membership_identifiers_are_registered():
    instances = [
        fr.MFunction("hyperbolic", a=1, b=1, c=0),
        fr.MFunction("bell", a=0, b=0.5, c=0.75),
        fr.MFunction("parabolic", a=0, b=1),
        fr.MFunction("triangle", a=0, b=1, c=0.5),
        fr.MFunction("trapezium", a=0, b=1, c=0.25, d=0.75),
        fr.MFunction("exponential", a=0.5, b=0.1),
        fr.MFunction("sigmoidal", a=1, b=0.5),
        fr.MFunction("desirability"),
    ]
    registered = {instance.name.lower() for instance in instances}
    assert registered == EXPECTED_MEMBERSHIP_IDENTIFIERS


def test_readme_wildcard_import_observation_is_recorded():
    assert not hasattr(fr, "__all__")

    namespace = {}
    exec("from fuzzyroutines.FuzzyRoutines import *", namespace)

    protected_names = (
        set(EXPECTED_FUNCTION_SIGNATURES)
        | set(EXPECTED_CLASS_SIGNATURES)
    )
    assert protected_names <= set(namespace)

    # Historical implementation leaks imported helper modules through wildcard
    # import because __all__ is absent. This is observed behavior, not a
    # declaration that these helpers are protected domain API.
    assert {"math", "copy", "traceback"} <= set(namespace)
