# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Provide the historical fuzzy-logic compatibility API.

This module preserves the original function names, mutable classes, argument
names, and return shapes for existing consumers. New code should prefer the
immutable public API exported by [fuzzyroutines][fuzzyroutines].
"""

import copy
import math

import fuzzyroutines.domain as _domain


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
        value: Candidate membership degree.

    Returns:
        `True` for a supported number in the closed unit interval. Invalid
        input prints the historical diagnostic and returns `False`.
    """
    if IsNumber(value):
        return (0. <= value) and (value <= 1.)

    else:
        print('{} not a real number in [0, 1], type = {}'.format(str(value), type(value)))
        return False


def _RequireFiniteReal(value, parameterName):
    """Return a finite real scalar or raise the public numeric-domain error."""

    if not IsNumber(value) or not math.isfinite(value):
        raise ValueError(f"{parameterName} must be a finite real number")

    return value


def _RequireFuzzyDegree(value, parameterName):
    """Return a finite scalar in the closed fuzzy-degree interval."""

    _RequireFiniteReal(value, parameterName)

    if not 0 <= value <= 1:
        raise ValueError(f"{parameterName} must be in the closed interval [0, 1]")

    return value


def FuzzyNOT(fuzzyNumber, alpha=0.5):
    """Evaluate the historical parametric fuzzy negation.

    For `alpha=0.5`, the result is the standard complement
    $1 - fuzzyNumber$.

    Args:
        fuzzyNumber: Membership degree in $[0, 1]$.
        alpha: Fixed point of the negation in $(0, 1)$.

    Returns:
        The complemented membership degree.

    Raises:
        ValueError: If either argument is outside its accepted finite range.
    """
    _RequireFuzzyDegree(fuzzyNumber, 'fuzzyNumber')

    if not IsNumber(alpha) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be a finite real number in the open interval (0, 1)")

    if fuzzyNumber <= alpha:
        return fuzzyNumber * (alpha - 1) / alpha + 1

    return (fuzzyNumber - 1) * alpha / (alpha - 1)


def FuzzyNOTParabolic(fuzzyNumber, alpha=0.5, epsilon=0.001):
    """Return the valid branch of $2a-x-y=(2a-1)(y-x)^2$.

    Args:
        fuzzyNumber: Membership degree in $[0, 1]$.
        alpha: Fixed point in $[1/4, 3/4]$.
        epsilon: Deprecated compatibility argument; the analytical solution
            deliberately ignores it.

    Returns:
        The parabolic complement of `fuzzyNumber`.

    Raises:
        ValueError: If `fuzzyNumber` or `alpha` is outside its accepted finite
            range.
    """
    _RequireFuzzyDegree(fuzzyNumber, 'fuzzyNumber')

    if not IsNumber(alpha) or not math.isfinite(alpha) or not 0.25 <= alpha <= 0.75:
        raise ValueError("alpha must be a finite real number in the closed interval [1/4, 3/4]")

    if fuzzyNumber == 0:
        return 1.0

    if fuzzyNumber == 1:
        return 0.0

    # The split discriminants stay non-negative on their half-domains. The
    # rationalized root avoids cancellation and the alpha=1/2 singularity;
    # see docs/mathematics/parabolic-negation-derivation.md.
    if alpha <= 0.5:
        discriminant = (4 * alpha - 1) ** 2 + 8 * (1 - 2 * alpha) * fuzzyNumber

    else:
        discriminant = (4 * alpha - 3) ** 2 + 8 * (2 * alpha - 1) * (1 - fuzzyNumber)

    return fuzzyNumber + 4 * (alpha - fuzzyNumber) / (1 + math.sqrt(discriminant))


def FuzzyAND(aNumber, bNumber):
    """Return the minimum of two fuzzy degrees.

    Args:
        aNumber: Left fuzzy degree in $[0, 1]$.
        bNumber: Right fuzzy degree in $[0, 1]$.

    Returns:
        `min(aNumber, bNumber)`.

    Raises:
        ValueError: If an operand is not a finite fuzzy degree.
    """
    _RequireFuzzyDegree(aNumber, 'aNumber')
    _RequireFuzzyDegree(bNumber, 'bNumber')
    return min(aNumber, bNumber)


def FuzzyOR(aNumber, bNumber):
    """Return the maximum of two fuzzy degrees.

    Args:
        aNumber: Left fuzzy degree in $[0, 1]$.
        bNumber: Right fuzzy degree in $[0, 1]$.

    Returns:
        `max(aNumber, bNumber)`.

    Raises:
        ValueError: If an operand is not a finite fuzzy degree.
    """
    _RequireFuzzyDegree(aNumber, 'aNumber')
    _RequireFuzzyDegree(bNumber, 'bNumber')
    return max(aNumber, bNumber)


def TNorm(aFuzzyNumber, bFuzzyNumber, normType='logic'):
    """Evaluate a binary t-norm from the historical family registry.

    Args:
        aFuzzyNumber: Left fuzzy degree in $[0, 1]$.
        bFuzzyNumber: Right fuzzy degree in $[0, 1]$.
        normType: One of `"logic"`, `"algebraic"`, `"boundary"`, or
            `"drastic"`.

    Returns:
        The conjunction of the two degrees under the selected family.

    Raises:
        ValueError: If an operand is invalid or the family is unknown.
    """
    _RequireFuzzyDegree(aFuzzyNumber, 'aFuzzyNumber')
    _RequireFuzzyDegree(bFuzzyNumber, 'bFuzzyNumber')

    if normType == 'logic':
        return min(aFuzzyNumber, bFuzzyNumber)

    if normType == 'algebraic':
        return aFuzzyNumber * bFuzzyNumber

    if normType == 'boundary':
        return max(aFuzzyNumber + bFuzzyNumber - 1, 0)

    if normType == 'drastic':
        if aFuzzyNumber == 1:
            return bFuzzyNumber

        if bFuzzyNumber == 1:
            return aFuzzyNumber

        return 0

    raise ValueError(f"unknown t-norm family: {normType!r}")


def TNormCompose(*fuzzyNumbers, normType='logic'):
    """Fold one t-norm over one or more fuzzy degrees.

    Args:
        *fuzzyNumbers: Fuzzy degrees in $[0, 1]$.
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

    for operandIndex, fuzzyNumber in enumerate(fuzzyNumbers):
        _RequireFuzzyDegree(fuzzyNumber, f'fuzzyNumbers[{operandIndex}]')

    result = fuzzyNumbers[0]

    for fuzzyNumber in fuzzyNumbers[1:]:
        result = TNorm(result, fuzzyNumber, normType)

    return result


def SCoNorm(aFuzzyNumber, bFuzzyNumber, normType='logic'):
    """Evaluate a binary s-norm from the historical family registry.

    Args:
        aFuzzyNumber: Left fuzzy degree in $[0, 1]$.
        bFuzzyNumber: Right fuzzy degree in $[0, 1]$.
        normType: One of `"logic"`, `"algebraic"`, `"boundary"`, or
            `"drastic"`.

    Returns:
        The disjunction of the two degrees under the selected family.

    Raises:
        ValueError: If an operand is invalid or the family is unknown.
    """
    _RequireFuzzyDegree(aFuzzyNumber, 'aFuzzyNumber')
    _RequireFuzzyDegree(bFuzzyNumber, 'bFuzzyNumber')

    if normType == 'logic':
        return max(aFuzzyNumber, bFuzzyNumber)

    if normType == 'algebraic':
        return aFuzzyNumber + bFuzzyNumber - aFuzzyNumber * bFuzzyNumber

    if normType == 'boundary':
        return min(aFuzzyNumber + bFuzzyNumber, 1)

    if normType == 'drastic':
        if aFuzzyNumber == 0:
            return bFuzzyNumber

        if bFuzzyNumber == 0:
            return aFuzzyNumber

        return 1

    raise ValueError(f"unknown s-norm family: {normType!r}")


def SCoNormCompose(*fuzzyNumbers, normType='logic'):
    """Fold one s-norm over one or more fuzzy degrees.

    Args:
        *fuzzyNumbers: Fuzzy degrees in $[0, 1]$.
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

    for operandIndex, fuzzyNumber in enumerate(fuzzyNumbers):
        _RequireFuzzyDegree(fuzzyNumber, f'fuzzyNumbers[{operandIndex}]')

    result = fuzzyNumbers[0]

    for fuzzyNumber in fuzzyNumbers[1:]:
        result = SCoNorm(result, fuzzyNumber, normType)

    return result


class MFunction():
    """Represent one historical analytical membership-function family.

    Args:
        userFunc: Registered family identifier. Compatibility aliases include
            `"gaussian"`, `"logistic"`, `"sShoulder"`, and
            `"harringtonDesirability"`.
        **membershipFunctionParams: Exact parameter set required by the chosen
            family.

    Attributes:
        accuracy: Number of right-endpoint rectangles used by legacy
            defuzzification.
        mju: Bound evaluator for the selected family.

    Raises:
        ValueError: If the family or its parameter set is invalid.
    """

    def __init__(self, userFunc, **membershipFunctionParams):
        """Initialize and validate a historical membership function."""
        self.accuracy = 1000  # Line of numbers divided by points, affect on accuracy, using in integral calculating
        # Registry values are bound methods; exact aliases must share one implementation.
        self._functions = {'hyperbolic': self.Hyperbolic,
                           'bell': self.Bell,
                           'parabolic': self.Parabolic,
                           'sShoulder': self.Parabolic,
                           'triangle': self.Triangle,
                           'trapezium': self.Trapezium,
                           'exponential': self.Exponential,
                           'gaussian': self.Exponential,
                           'sigmoidal': self.Sigmoidal,
                           'logistic': self.Sigmoidal,
                           'desirability': self.Desirability,
                           'harringtonDesirability': self.Desirability}

        if userFunc not in self._functions:
            raise ValueError("unknown membership-function identifier: {!r}".format(userFunc))

        self.mju = self._functions[userFunc]  # Calculate result of define membership function
        self._parameters = self._ValidateParameters(membershipFunctionParams)

    def _ValidateParameters(self, parameters):
        """
        Validate and copy the exact parameter mapping for the selected family.

        Triangle keeps the historical `a`, `b`, and `c` argument names:
        geometrically `a` is the left foot, `c` is the apex, and `b` is the
        right foot.
        """
        functionName = self.mju.__name__
        requiredParameters = {
            'Hyperbolic': ('a', 'b', 'c'),
            'Bell': ('a', 'b', 'c'),
            'Parabolic': ('a', 'b'),
            'Triangle': ('a', 'b', 'c'),
            'Trapezium': ('a', 'b', 'c', 'd'),
            'Exponential': ('a', 'b'),
            'Sigmoidal': ('a', 'b'),
            'Desirability': (),
        }[functionName]

        if not isinstance(parameters, dict) or set(parameters) != set(requiredParameters):
            raise ValueError(
                "{} membership function requires exactly these parameters: {}".format(
                    functionName,
                    ', '.join(requiredParameters) if requiredParameters else 'none',
                )
            )

        for parameterName in requiredParameters:
            parameterValue = parameters[parameterName]

            if not IsNumber(parameterValue) or not math.isfinite(parameterValue):
                raise ValueError(
                    "{} parameter {!r} must be a finite real number".format(
                        functionName,
                        parameterName,
                    )
                )

        if functionName == 'Hyperbolic':
            if parameters['a'] <= 0 or parameters['b'] <= 0:
                raise ValueError("Hyperbolic parameters must satisfy a > 0 and b > 0")

        elif functionName == 'Bell':
            if not parameters['a'] < parameters['b'] <= parameters['c']:
                raise ValueError("Bell parameters must satisfy a < b <= c")

        elif functionName == 'Parabolic':
            if not parameters['a'] < parameters['b']:
                raise ValueError("Parabolic parameters must satisfy a < b")

        elif functionName == 'Triangle':
            if not parameters['a'] < parameters['c'] <= parameters['b']:
                raise ValueError("Triangle parameters must satisfy a < c <= b")

        elif functionName == 'Trapezium':
            if not parameters['a'] < parameters['c'] <= parameters['d'] < parameters['b']:
                raise ValueError("Trapezium parameters must satisfy a < c <= d < b")

        elif functionName == 'Exponential':
            if parameters['b'] <= 0:
                raise ValueError("Exponential parameter b must satisfy b > 0")

        elif functionName == 'Sigmoidal':
            if parameters['a'] == 0:
                raise ValueError("Sigmoidal parameter a must be non-zero")

        return dict(parameters)

    @property
    def name(self):
        """Return the canonical bound-method name for this family."""
        return self.mju.__name__  # membership function method name

    def __str__(self):
        """Return the historical human-readable function representation."""
        # return view of function: Function_name(**parameters). Example: Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}
        funcView = '{}({})'.format(self.name, 'y' if self.name == 'Desirability' else 'x, {}'.format(
            '{' + ', '.join('"{}": {}'.format(*val) for val in [(k, self._parameters[k])
                                                                for k in sorted(self._parameters)]) + '}'))
        return funcView

    @property
    def parameters(self):
        """Return the mutable parameter mapping used during evaluation."""
        return self._parameters  # all membership function parameters

    @parameters.setter
    def parameters(self, value):
        """Validate and replace the complete parameter mapping."""
        self._parameters = self._ValidateParameters(value)

    def Hyperbolic(self, x):
        """Evaluate the right-tailed hyperbolic membership function at `x`.

        Args:
            x: Finite scalar coordinate.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not finite and real.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']

        if x <= c:
            return 1

        return 1 / (1 + (a * (x - c)) ** b)

    def Bell(self, x):
        """Evaluate the finite bell membership function at `x`.

        Args:
            x: Finite scalar coordinate.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not finite and real.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']

        if x < b:
            return self.Parabolic(x)

        if x <= c:
            return 1

        rightBoundary = c + b - a
        rightMidpoint = (c + rightBoundary) / 2

        if x <= rightMidpoint:
            return 1 - (2 * (x - c) ** 2) / (rightBoundary - c) ** 2

        if x < rightBoundary:
            return (2 * (x - rightBoundary) ** 2) / (rightBoundary - c) ** 2

        return 0

    def Parabolic(self, x):
        """Evaluate the rising parabolic shoulder at `x`.

        Args:
            x: Finite scalar coordinate.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not finite and real.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']

        if x <= a:
            return 0

        if x <= (a + b) / 2:
            return (2 * (x - a) ** 2) / (b - a) ** 2

        if x < b:
            return 1 - (2 * (x - b) ** 2) / (b - a) ** 2

        return 1

    def Triangle(self, x):
        """Evaluate the triangular membership function at `x`.

        Args:
            x: Finite scalar coordinate.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not finite and real.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']

        if x <= a:
            return 0

        if x <= c:
            return (x - a) / (c - a)

        if x < b:
            return (b - x) / (b - c)

        return 0

    def Trapezium(self, x):
        """Evaluate the trapezoidal membership function at `x`.

        Args:
            x: Finite scalar coordinate.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not finite and real.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']
        d = self._parameters['d']

        if x <= a:
            return 0

        if x < c:
            return (x - a) / (c - a)

        if x <= d:
            return 1

        if x <= b:
            return (b - x) / (b - d)

        return 0

    def Exponential(self, x):
        """Evaluate the Gaussian-shaped exponential function at `x`.

        Args:
            x: Finite scalar coordinate.

        Returns:
            Membership degree in $(0, 1]$.

        Raises:
            ValueError: If `x` is not finite and real.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        scaledDistance = (x - a) / b
        # Binary64 underflow may produce zero far from the centre; analytical
        # support is derived from the formula, never from this sampled value.
        return math.exp(-0.5 * scaledDistance * scaledDistance)

    def Sigmoidal(self, x):
        """Evaluate the numerically stable logistic function at `x`.

        Args:
            x: Finite scalar coordinate.

        Returns:
            Membership degree in $(0, 1)$.

        Raises:
            ValueError: If `x` is not finite and real.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        exponent = a * (x - b)

        # Algebraically equivalent branches keep the exp argument non-positive,
        # preventing overflow for every finite exponent. See the numerical
        # derivation in docs/mathematics/source-algorithm-invariants.md.
        if exponent >= 0:
            return 1 / (1 + math.exp(-exponent))

        exponential = math.exp(exponent)
        return exponential / (1 + exponential)

    def Desirability(self, y):
        """Evaluate Harrington's desirability function at `y`.

        Args:
            y: Finite scalar desirability coordinate.

        Returns:
            Membership degree in $[0, 1)$; sufficiently negative values
            underflow deterministically to zero.

        Raises:
            ValueError: If `y` is not finite and real.
        """
        _RequireFiniteReal(y, 'y')

        # Beyond this binary64 bound the inner exponential overflows while the
        # representable value of exp(-exp(-y)) is already exactly zero. See
        # docs/mathematics/source-algorithm-invariants.md.
        if y < -math.log(float.fromhex('0x1.fffffffffffffp+1023')):
            return 0.0

        return math.exp(-math.exp(-y))


class FuzzySet():
    """Represent a mutable historical fuzzy set and integration interval.

    Args:
        membershipFunction: A configured [MFunction][fuzzyroutines.FuzzyRoutines.MFunction].
        supportSet: Two-item tuple used as the numerical integration domain.
        linguisticName: Human-readable set name.

    Notes:
        The legacy `supportSet` name denotes integration bounds, not the exact
        mathematical support. New code should use
        [ScalarFuzzySet][fuzzyroutines.ScalarFuzzySet].
    """

    def __init__(self, membershipFunction, supportSet=(0., 1.), linguisticName='FuzzySet'):
        """Initialize the historical mutable fuzzy-set wrapper."""
        if isinstance(linguisticName, str):
            self._name = linguisticName

        else:
            raise Exception("Linguistic name of Fuzzy Set must be a string value!")

        if isinstance(membershipFunction, MFunction):
            self._mFunction = membershipFunction  # instance of MembershipFunction class

        else:
            raise Exception('Not MFunction class instance was given!')

        self._integrationDomain = _domain.IntegrationDomain.FromLegacyInterval(supportSet)

        self._defuzValue = None

    def __str__(self):
        """Return the historical name/function/interval representation."""
        # return view of fuzzy set - name = <mju(x|y, params), supportSet>. Example: FuzzySet = <Bell(x, a, b), [0, 1]>
        fSetView = '{} = <{}, [{}, {}]>'.format(
            self._name,
            self._mFunction,
            self._integrationDomain.left,
            self._integrationDomain.right,
        )
        return fSetView

    @property
    def name(self):
        """Return the linguistic name."""
        return self._name

    @name.setter
    def name(self, value):
        """Replace the linguistic name with a string value."""
        if isinstance(value, str):
            self._name = value

        else:
            raise Exception("Linguistic name of Fuzzy Set must be a string value!")

    @property
    def mFunction(self):
        """Return the configured historical membership function."""
        return self._mFunction  # current membership

    @mFunction.setter
    def mFunction(self, value):
        """Replace the membership function with an `MFunction` instance."""
        if isinstance(value, MFunction):
            self._mFunction = value

        else:
            raise Exception('Not MFunction class instance was given!')

    @property
    def supportSet(self):
        """Return the two numerical integration endpoints."""
        return self._integrationDomain.ToLegacyInterval()

    @supportSet.setter
    def supportSet(self, value):
        """Validate and replace the two numerical integration endpoints."""
        self._integrationDomain = _domain.IntegrationDomain.FromLegacyInterval(value)

    @property
    def defuzValue(self):
        """Calculate and return the center-of-gravity defuzzified value."""
        self._defuzValue = self._Defuz()
        return self._defuzValue

    def _Defuz(self):
        """Approximate centroid defuzzification over the integration domain.

        Returns:
            The ratio of right-endpoint rectangle sums for $xμ(x)$ and
            $μ(x)$.

        Raises:
            ZeroDivisionError: If all sampled membership grades are zero.
        """
        left = self._integrationDomain.left
        right = self._integrationDomain.right
        step = (right - left) / self._mFunction.accuracy

        numeratorIntegral = 0
        denominatorIntegral = 0

        # The common rectangle width cancels from the centroid ratio. This
        # preserves the historical O(n)-time, O(1)-space right-endpoint sum;
        # it is compatibility behavior, not an adaptive convergence claim.
        for iteration in range(self._mFunction.accuracy):
            x = left + (iteration + 1) * step
            mjuValue = self._mFunction.mju(x)

            numeratorIntegral += x * mjuValue
            denominatorIntegral += mjuValue

        return numeratorIntegral / denominatorIntegral

    def Defuz(self):
        """Return `defuzValue` through the historical method alias."""
        return self.defuzValue


class FuzzyScale():
    """Represent the mutable three-level historical linguistic scale.

    Each level is a dictionary with a unique string `name` and an `fSet`
    containing a [FuzzySet][fuzzyroutines.FuzzyRoutines.FuzzySet]. The default
    scale contains `Min`, `Med`, and `High` levels.
    """

    def __init__(self):
        """Initialize the default three-level scale."""
        self._name = 'DefaultScale'  # default scale contains 3 levels, DefaultScale = {Min, Med, High}:

        self._levels = [{'name': 'Min',
                         'fSet': FuzzySet(membershipFunction=MFunction('hyperbolic', **{'a': 7, 'b': 4, 'c': 0}),
                                          supportSet=(0., 1.),
                                          linguisticName='Minimum')},
                        {'name': 'Med',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.35, 'b': 0.5, 'c': 0.6}),
                                          supportSet=(0., 1.),
                                          linguisticName='Medium')},
                        {'name': 'High',
                         'fSet': FuzzySet(membershipFunction=MFunction('triangle', **{'a': 0.7, 'b': 1, 'c': 1}),
                                          supportSet=(0., 1.),
                                          linguisticName='High')}]

        self._levelsNames = self._GetLevelsNames()  # dictionary with only levels' names
        self._levelsNamesUpper = self._GetLevelsNamesUpper()  # dictionary with only level's names in upper cases

    def __str__(self):
        """Return the historical multiline scale representation."""
        # return view of fuzzy scale - name = {**levels} and levels interpreter. Example:
        # DefaultScale = {Min, Med, High}
        #     Minimum = <Hyperbolic(x, {"a": 7, "b": 4, "c": 0}), [0.0, 1.0]>
        #     Medium = <Bell(x, {"a": 0.35, "b": 0.5, "c": 0.6}), [0.0, 1.0]>
        #     High = <Triangle(x, {"a": 0.7, "b": 1, "c": 1}), [0.0, 1.0]>
        allLevelsName = self._levels[0]['name']
        allLevels = '\n    {}'.format(self._levels[0]['fSet'].__str__())

        for level in self._levels[1:]:
            allLevelsName += ', {}'.format(level['name'])
            allLevels += '\n    {}'.format(str(level['fSet']))

        scaleView = '{} = {{{}}}{}'.format(self._name, allLevelsName, allLevels)

        return scaleView

    @property
    def name(self):
        """Return the scale name."""
        return self._name

    @name.setter
    def name(self, value):
        """Replace the scale name with a string value."""
        if isinstance(value, str):
            self._name = value

        else:
            raise Exception("Name of Fuzzy Scale must be a string value!")

    @property
    def levels(self):
        """Return the mutable ordered list of level dictionaries."""
        return self._levels

    @levels.setter
    def levels(self, value):
        """Validate and replace the non-empty ordered level list."""
        if value:
            for level in value:
                if isinstance(level, dict) and (len(level) == 2) and ('name' and 'fSet' in level.keys()):
                    if not isinstance(level['name'], str):
                        raise Exception("Level name - 'name' parameter - must be a string value!")

                    if not isinstance(level['fSet'], FuzzySet):
                        raise Exception("Fuzzy set - 'fSet' parameter - must be an instance of FuzzySet class!")

                    nameCount = 0  # check for unique name:
                    for otherLevel in value:
                        if otherLevel['name'] == level['name']:
                            nameCount += 1

                    if nameCount > 1:
                        raise Exception("The scale contains no unique levels! Warning for: {}".format(level['name']))

                else:
                    raise Exception("Level of fuzzy scale must be 2-dim dictionary looks like {'name': 'level_name', 'fSet': FuzzySet_instance}!")

            self._levels = value  # set up new list of fuzzy levels
            self._levelsNames = self._GetLevelsNames()  # updating dictionary with only levels' names
            self._levelsNamesUpper = self._GetLevelsNamesUpper()  # updating dictionary with only level's names in upper cases

        else:
            raise Exception('Fuzzy scale must contain at least one linguistic variable!')

    def _GetLevelsNames(self):
        """
        Returns dictionary with only fuzzy levels' names and it's fuzzy set.
        Example: {'Min': <fSet_Object>, 'Med': <fSet_Object>, 'High': <fSet_Object>}
        """
        return dict([(x['name'], self._levels[lvl]) for lvl, x in enumerate(self._levels)])

    def _GetLevelsNamesUpper(self):
        """
        Returns dictionary with only fuzzy levels' names in upper cases and it's fuzzy set.
        Example: {'MIN': <fSet_Object>, 'MED': <fSet_Object>, 'HIGH': <fSet_Object>}
        """
        return dict([(x['name'].upper(), self._levels[lvl]) for lvl, x in enumerate(self._levels)])

    def Fuzzy(self, realValue):
        """Return the level with the greatest membership at `realValue`.

        Ties are resolved in favor of the later level in scale order.

        Args:
            realValue: Coordinate evaluated by every level membership function.

        Returns:
            The selected mutable level dictionary.
        """
        fuzzyLevel = self._levels[0]
        fuzzyMembership = fuzzyLevel['fSet'].mFunction.mju(realValue)

        for level in self._levels[1:]:
            levelMembership = level['fSet'].mFunction.mju(realValue)

            if fuzzyMembership <= levelMembership:
                fuzzyLevel = level
                fuzzyMembership = levelMembership

        return fuzzyLevel

    def GetLevelByName(self, levelName, exactMatching=True):
        """Look up a level by exact or case-insensitive name.

        Args:
            levelName: Name to retrieve.
            exactMatching: Use exact case when `True`; otherwise compare
                uppercase forms.

        Returns:
            The matching level dictionary, or `None` when absent.
        """
        if exactMatching:
            return self._levelsNames.get(levelName)

        else:
            return self._levelsNamesUpper.get(levelName.upper())


class UniversalFuzzyScale(FuzzyScale):
    """Represent the read-only five-level historical universal scale.

    The ordered levels are `Min`, `Low`, `Med`, `High`, and `Max`. The inherited
    lookup and fuzzification methods remain available, while `levels` has no
    public setter on this subclass.
    """

    def __init__(self):
        """Initialize the fixed five-level universal scale."""
        self._name = 'FuzzyScale'  # default universal fuzzy scale contains 5 levels, FuzzyScale = {Min, Low, Med, High, Max}:

        self._levels = [{'name': 'Min',
                         'fSet': FuzzySet(membershipFunction=MFunction('hyperbolic', **{'a': 8, 'b': 20, 'c': 0}),
                                          supportSet=(0., 0.23),
                                          linguisticName='Min')},
                        {'name': 'Low',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.17, 'b': 0.23, 'c': 0.34}),
                                          supportSet=(0.17, 0.4),
                                          linguisticName='Low')},
                        {'name': 'Med',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.34, 'b': 0.4, 'c': 0.6}),
                                          supportSet=(0.34, 0.66),
                                          linguisticName='Med')},
                        {'name': 'High',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.6, 'b': 0.66, 'c': 0.77}),
                                          supportSet=(0.6, 0.83),
                                          linguisticName='High')},
                        {'name': 'Max',
                         'fSet': FuzzySet(membershipFunction=MFunction('parabolic', **{'a': 0.77, 'b': 0.95}),
                                          supportSet=(0.77, 1.),
                                          linguisticName='Max')}]

        self._levelsNames = self._GetLevelsNames()  # dictionary with only universal fuzzy scale levels' names
        self._levelsNamesUpper = self._GetLevelsNamesUpper()  # dictionary with only level's names in upper cases

    @property
    def levels(self):
        """Return the ordered universal-scale level list."""
        return self._levels  # only readable levels and it's fuzzy set for Universal Fuzzy Scale

    @property
    def levelsNames(self):
        """Return the exact-name lookup dictionary."""
        return self._levelsNames  # only levels' names of Universal Fuzzy Scale

    @property
    def levelsNamesUpper(self):
        """Return the uppercase-name lookup dictionary."""
        return self._levelsNamesUpper  # only levels' names of Universal Fuzzy Scale in upper cases


if __name__ == "__main__":
    pass
