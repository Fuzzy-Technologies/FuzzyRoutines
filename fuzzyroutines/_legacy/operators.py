# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Historical operator signatures adapting canonical modern formula kernels."""

import math

from fuzzyroutines._legacy.utilities import IsNumber, _RequireFuzzyDegree
from fuzzyroutines.operators import _EvaluateNegation, _EvaluateSNorm, _EvaluateTNorm


def FuzzyNOT(fuzzyNumber, alpha=0.5):
    """Evaluate the historical parametric fuzzy negation.

    For `alpha=0.5`, the result is the standard complement
    $1 - fuzzyNumber$.

    Args:
        fuzzyNumber: Built-in `int` or `float` membership degree in $[0, 1]$;
            `bool` is excluded.
        alpha: Built-in `int` or `float` fixed point in $(0, 1)$; `bool` is
            excluded.

    Returns:
        The complemented membership degree.

    Raises:
        ValueError: If either argument has an unsupported type, is non-finite,
            or lies outside its accepted range.
    """

    _RequireFuzzyDegree(fuzzyNumber, 'fuzzyNumber')

    if not IsNumber(alpha) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be a finite real number in the open interval (0, 1)")

    return _EvaluateNegation('parametric', alpha, fuzzyNumber)


def FuzzyNOTParabolic(fuzzyNumber, alpha=0.5, epsilon=0.001):
    """Return the valid branch of $2a-x-y=(2a-1)(y-x)^2$.

    Args:
        fuzzyNumber: Built-in `int` or `float` membership degree in $[0, 1]$;
            `bool` is excluded.
        alpha: Built-in `int` or `float` fixed point in $[1/4, 3/4]$; `bool`
            is excluded.
        epsilon: Deprecated compatibility argument; the analytical solution
            deliberately ignores it.

    Returns:
        The parabolic complement of `fuzzyNumber`.

    Raises:
        ValueError: If `fuzzyNumber` or `alpha` has an unsupported type, is
            non-finite, or lies outside its accepted range.
    """

    _RequireFuzzyDegree(fuzzyNumber, 'fuzzyNumber')

    if not IsNumber(alpha) or not math.isfinite(alpha) or not 0.25 <= alpha <= 0.75:
        raise ValueError("alpha must be a finite real number in the closed interval [1/4, 3/4]")

    return _EvaluateNegation('parabolic', alpha, fuzzyNumber)


def FuzzyAND(aNumber, bNumber):
    """Return the minimum of two fuzzy degrees.

    Args:
        aNumber: Left built-in `int` or `float` degree in $[0, 1]$.
        bNumber: Right built-in `int` or `float` degree in $[0, 1]$.

    Returns:
        `min(aNumber, bNumber)`.

    Raises:
        ValueError: If an operand is a `bool`, has another unsupported type,
            is non-finite, or lies outside $[0, 1]$.
    """

    _RequireFuzzyDegree(aNumber, 'aNumber')
    _RequireFuzzyDegree(bNumber, 'bNumber')

    return _EvaluateTNorm('logic', aNumber, bNumber)


def FuzzyOR(aNumber, bNumber):
    """Return the maximum of two fuzzy degrees.

    Args:
        aNumber: Left built-in `int` or `float` degree in $[0, 1]$.
        bNumber: Right built-in `int` or `float` degree in $[0, 1]$.

    Returns:
        `max(aNumber, bNumber)`.

    Raises:
        ValueError: If an operand is a `bool`, has another unsupported type,
            is non-finite, or lies outside $[0, 1]$.
    """

    _RequireFuzzyDegree(aNumber, 'aNumber')
    _RequireFuzzyDegree(bNumber, 'bNumber')

    return _EvaluateSNorm('logic', aNumber, bNumber)


def TNorm(aFuzzyNumber, bFuzzyNumber, normType='logic'):
    """Evaluate a binary t-norm from the historical family registry.

    Args:
        aFuzzyNumber: Left built-in `int` or `float` degree in $[0, 1]$.
        bFuzzyNumber: Right built-in `int` or `float` degree in $[0, 1]$.
        normType: One of `"logic"`, `"algebraic"`, `"boundary"`, or
            `"drastic"`.

    Returns:
        The conjunction of the two degrees under the selected family.

    Raises:
        ValueError: If an operand is not a finite supported built-in number in
            $[0, 1]$ or the family is unknown.
    """

    _RequireFuzzyDegree(aFuzzyNumber, 'aFuzzyNumber')
    _RequireFuzzyDegree(bFuzzyNumber, 'bFuzzyNumber')

    return _EvaluateTNorm(normType, aFuzzyNumber, bFuzzyNumber)


def TNormCompose(*fuzzyNumbers, normType='logic'):
    """Fold one t-norm over one or more fuzzy degrees.

    Args:
        *fuzzyNumbers: Built-in `int` or `float` degrees in $[0, 1]$;
            `bool` values are excluded.
        normType: One of `"logic"`, `"algebraic"`, `"boundary"`, or
            `"drastic"`.

    Returns:
        The left-associated conjunction of all operands.

    Raises:
        ValueError: If no operands are supplied, an operand is invalid, or the
            family is unknown.
    """

    if normType not in ('logic', 'algebraic', 'boundary', 'drastic'):
        raise ValueError(f"unknown t-norm family: {normType!r}")

    if not fuzzyNumbers:
        raise ValueError("TNormCompose requires at least one fuzzy degree")

    for operand_index, fuzzy_number in enumerate(fuzzyNumbers):
        _RequireFuzzyDegree(fuzzy_number, f'fuzzyNumbers[{operand_index}]')

    result = fuzzyNumbers[0]

    for fuzzy_number in fuzzyNumbers[1:]:
        result = TNorm(result, fuzzy_number, normType)

    return result


def SCoNorm(aFuzzyNumber, bFuzzyNumber, normType='logic'):
    """Evaluate a binary s-norm from the historical family registry.

    Args:
        aFuzzyNumber: Left built-in `int` or `float` degree in $[0, 1]$.
        bFuzzyNumber: Right built-in `int` or `float` degree in $[0, 1]$.
        normType: One of `"logic"`, `"algebraic"`, `"boundary"`, or
            `"drastic"`.

    Returns:
        The disjunction of the two degrees under the selected family.

    Raises:
        ValueError: If an operand is not a finite supported built-in number in
            $[0, 1]$ or the family is unknown.
    """

    _RequireFuzzyDegree(aFuzzyNumber, 'aFuzzyNumber')
    _RequireFuzzyDegree(bFuzzyNumber, 'bFuzzyNumber')

    return _EvaluateSNorm(normType, aFuzzyNumber, bFuzzyNumber)


def SCoNormCompose(*fuzzyNumbers, normType='logic'):
    """Fold one s-norm over one or more fuzzy degrees.

    Args:
        *fuzzyNumbers: Built-in `int` or `float` degrees in $[0, 1]$;
            `bool` values are excluded.
        normType: One of `"logic"`, `"algebraic"`, `"boundary"`, or
            `"drastic"`.

    Returns:
        The left-associated disjunction of all operands.

    Raises:
        ValueError: If no operands are supplied, an operand is invalid, or the
            family is unknown.
    """

    if normType not in ('logic', 'algebraic', 'boundary', 'drastic'):
        raise ValueError(f"unknown s-norm family: {normType!r}")

    if not fuzzyNumbers:
        raise ValueError("SCoNormCompose requires at least one fuzzy degree")

    for operand_index, fuzzy_number in enumerate(fuzzyNumbers):
        _RequireFuzzyDegree(fuzzy_number, f'fuzzyNumbers[{operand_index}]')

    result = fuzzyNumbers[0]

    for fuzzy_number in fuzzyNumbers[1:]:
        result = SCoNorm(result, fuzzy_number, normType)

    return result
