"""Run one end-to-end example through the protected historical API."""

import json

from fuzzyroutines.FuzzyRoutines import (
    FuzzySet,
    MFunction,
    TNorm,
    UniversalFuzzyScale,
)


def Main():
    """Print stable observations from every historical migration area."""

    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
    fuzzySet = FuzzySet(
        membershipFunction,
        supportSet=(0.0, 1.0),
        linguisticName="Medium",
    )
    scale = UniversalFuzzyScale()

    result = {
        "defuzzification": fuzzySet.Defuz(),
        "fuzzySet": {
            "name": fuzzySet.name,
            "supportSet": fuzzySet.supportSet,
        },
        "membership": membershipFunction.mju(0.5),
        "operator": TNorm(0.4, 0.7, normType="algebraic"),
        "scale": scale.Fuzzy(0.5)["name"],
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    Main()
