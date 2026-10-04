<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Public modern typing

The modern API ships inline annotations and a `fuzzyroutines/py.typed` marker
under [PEP 561](https://peps.python.org/pep-0561/). Supported CPython versions are
3.13 and 3.14. Import modern names from `fuzzyroutines` or their focused modules;
both paths preserve the same types and runtime objects.

`MembershipScalar` accepts built-in floats and `numbers.Real` implementations,
including integers and `fractions.Fraction`. The union explicitly includes
`float` because static checkers do not model every built-in number as a
`numbers.Real` subclass. Runtime validation still rejects booleans, non-finite
coordinates, and invalid membership grades. Static annotations do not encode
these numerical restrictions.

`MembershipCallable` is structural: a function, callable object, or bound method
must accept every `MembershipScalar` coordinate and return a `MembershipScalar`.
A callback annotated only for `float` promises less than this complete domain.
Use the public scalar alias for custom membership callbacks:

```python
from fractions import Fraction

from fuzzyroutines import (
    ContinuousUniverse,
    MembershipCallable,
    MembershipScalar,
    ScalarFuzzySet,
)


def CustomMembership(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a constant rational membership grade."""

    return Fraction(1, 2)


membership: MembershipCallable = CustomMembership
fuzzy_set = ScalarFuzzySet(ContinuousUniverse(0, 1, True, True), membership)
grade: MembershipScalar = fuzzy_set.Membership(0.5)
```

Scalar results remain `MembershipScalar` so annotations do not require coercion
of rational or other real-valued arithmetic to floats. Analytical property
operations require a stock `MembershipFunction` or a trusted analytical source;
a generic callback does not carry the analytical evidence those operations
need. `DeriveProperties` selects `ContinuousFuzzyProperties` or
`DiscreteFuzzyProperties` according to the supplied universe. Sampled operations
return their distinct sampled evidence types. Scale lookup returns
`LinguisticTerm | None`, so callers must handle a missing term.

Typeshed models `numbers.Real` arithmetic through a complex-compatible
interface whose inferred results are wider than real scalar operations. At
validated internal arithmetic boundaries, a narrow `cast(float, value)` gives
the checker a real-arithmetic view. `typing.cast` returns the same object at
runtime; it does not call `float(value)` or change rational arithmetic. Public
results retain the broader scalar contract, and modern diagnostics remain
fully checked.

Immutable dataclass fields and read-only membership parameter mappings are
visible to the checker. Operator and analysis functions require their specific
policy and domain types; supplying a different policy family is a type error.

## Reproducible gate

Install the pinned checker separately from runtime dependencies:

```bash
python -m pip install -r requirements-typing.txt
python -m tools.typecheck
```

The fixed mypy 1.19.1 version supports the declared Python versions and PEP 695
aliases; its transitive checker dependencies are pinned in the same file.
Source checks disable incremental reuse, so successful results do not depend
on an earlier cache. The CI wheel builder and build backend also use fixed
development-only versions with build isolation disabled.

`mypy.ini` uses strict checking, diagnostic codes, and unused-ignore reporting.
It explicitly covers the package root, every modern module (including internal
numeric validation), the checker command, and all static consumers. It has no
global error suppression. The historical `FuzzyRoutines` facade, `_legacy`
adapters, and executable `Examples` module have a narrowly scoped skipped-import
boundary. They retain their runtime compatibility contract and are outside the
modern typing promise.

The consumer fixtures in `tests/typing` include valid imports, numeric inputs,
custom callbacks, policy use, immutable results, and exact return-type
assertions. Expected-invalid calls and assignments carry a specific diagnostic
code. If a signature becomes `Any` or otherwise accepts an invalid use, the
formerly necessary ignore becomes unused and the gate fails.

## Installed wheel boundary

The `Public modern typing` workflow checks source contracts and builds a wheel
on both supported Python versions. It installs that wheel and the pinned
checker in a new virtual environment, then runs:

```bash
/path/to/isolated/environment/bin/python /path/to/checkout/tools/typecheck.py --installed
```

This mode verifies that Python resolves a package outside the checkout and that
the installed package includes `py.typed`. It copies every consumer into a
temporary directory outside the repository and runs mypy there with isolated
Python path handling, cleared `MYPYPATH` and `PYTHONPATH`, and a fresh cache.
Consumers therefore exercise the wheel
annotations instead of accidentally finding source files in the checkout.
Temporary probes are removed after either success or failure; failed imports
and checker results preserve their nonzero exit status.
