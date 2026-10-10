# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Historical parsing and built-in numeric validation contracts."""

import math


def DiapasonParser(diapason):
    """Parse comma-separated integers and inclusive integer ranges.

    Args:
        diapason: Text such as `"1,3-5"`.

    Returns:
        A sorted list of unique integers. Invalid input prints the historical
        diagnostic and returns an empty list.

    Examples:
        ```python
        DiapasonParser("8-10, 1-3, 3")
        # [1, 2, 3, 8, 9, 10]
        ```
    """

    fullDiapason = []

    try:
        for element in diapason.split(','):
            fullDiapason += [x for x in range(int(element.split('-')[0]), int(element.split('-')[-1]) + 1)]

    except Exception:
        print('"{}" is not correct diapason string!'.format(diapason))

        return []

    return sorted(list(set(fullDiapason)))


def IsNumber(value):
    """Return whether a value is a built-in integer or float, excluding booleans.

    Args:
        value: Value to inspect.

    Returns:
        `True` for `int` and `float` values other than `bool`; otherwise
        `False`.
    """

    return bool(not isinstance(value, bool) and (isinstance(value, int) or isinstance(value, float)))


def IsCorrectFuzzyNumberValue(value):
    """Return whether a value is a valid fuzzy degree in $[0, 1]$.

    Args:
        value: Candidate built-in `int` or `float` membership degree;
            `bool` is excluded.

    Returns:
        `True` for a supported built-in number in the closed unit interval. An
        unsupported numeric type or other non-numeric input prints the
        historical diagnostic and returns `False`; a supported number outside
        the interval returns `False` silently.
    """

    if IsNumber(value):
        return (0. <= value) and (value <= 1.)

    else:
        print('{} not a real number in [0, 1], type = {}'.format(str(value), type(value)))

        return False


def _RequireFiniteReal(value, parameterName):
    """Return a finite built-in integer or float, excluding booleans."""

    if not IsNumber(value) or not math.isfinite(value):
        raise ValueError(f"{parameterName} must be a finite real number")

    return value


def _RequireFuzzyDegree(value, parameterName):
    """Return a supported built-in number in the fuzzy-degree interval."""

    _RequireFiniteReal(value, parameterName)

    if not 0 <= value <= 1:
        raise ValueError(f"{parameterName} must be in the closed interval [0, 1]")

    return value
