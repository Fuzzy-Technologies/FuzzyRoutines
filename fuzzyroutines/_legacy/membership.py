# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Mutable historical membership registry adapting canonical family kernels."""

import fuzzyroutines.membership as _membership
from fuzzyroutines._legacy.utilities import _RequireFiniteReal


class MFunction(_membership._LegacyAnalyticalAdapter):
    """Represent one historical analytical membership-function family.

    Args:
        userFunc: Registered family identifier. Compatibility aliases include
            `"gaussian"`, `"logistic"`, `"sShoulder"`, and
            `"harringtonDesirability"`.
        **membershipFunctionParams: Exact parameter set required by the chosen
            family. Every value must be a finite built-in `int` or `float`;
            `bool` is excluded.

    Raises:
        ValueError: If the family or its parameter set is invalid.

    Attributes:
        accuracy: Preserved mutable compatibility attribute. Modern centroid
            defuzzification deliberately ignores it.
        mju: Bound evaluator for the selected family.
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

        validated_parameters = _membership._ValidateFamilyParameters(self.mju.__name__, parameters)

        for parameter_name, parameter_value in validated_parameters.items():
            _RequireFiniteReal(parameter_value, parameter_name)

        return validated_parameters

    def _AnalyticalSnapshot(self):
        """Freeze current validated parameters for modern analytical operations."""

        if self.mju not in self._functions.values():
            raise ValueError("exact analytical evidence requires an unchanged registered evaluator")

        parameters = self._ValidateParameters(self._parameters)

        return _membership._AnalyticalSource(self.name, tuple(parameters.items()))

    @property
    def name(self):
        """Return the canonical bound-method name for this family."""

        return self.mju.__name__  # membership function method name

    def __str__(self):
        """Return the historical human-readable function representation."""

        # return view of function: Function_name(**parameters). Example: Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}
        function_view = '{}({})'.format(self.name, 'y' if self.name == 'Desirability' else 'x, {}'.format(
            '{' + ', '.join('"{}": {}'.format(*val) for val in [(k, self._parameters[k])
                                                                for k in sorted(self._parameters)]) + '}'))

        return function_view

    @property
    def parameters(self):
        """Return the mutable parameter mapping used during evaluation."""

        return self._parameters  # all membership function parameters

    @parameters.setter
    def parameters(self, value):
        """Validate and replace the complete parameter mapping.

        Raises:
            ValueError: If `value` does not contain the exact parameter set or
                any value is not a finite built-in `int` or `float` accepted
                by the selected family.
        """

        self._parameters = self._ValidateParameters(value)

    def Hyperbolic(self, x):
        """Evaluate the right-tailed hyperbolic membership function at `x`.

        Args:
            x: Finite built-in `int` or `float` coordinate; `bool` is excluded.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not a supported finite built-in number.
            OverflowError: If a finite input produces an unrepresentable
                intermediate power.
        """

        _RequireFiniteReal(x, 'x')

        return _membership._Hyperbolic(self._parameters, x)

    def Bell(self, x):
        """Evaluate the finite bell membership function at `x`.

        Args:
            x: Finite built-in `int` or `float` coordinate; `bool` is excluded.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not a supported finite built-in number.
            OverflowError: If a finite input produces an unrepresentable
                intermediate square.
        """

        _RequireFiniteReal(x, 'x')

        return _membership._Bell(self._parameters, x)

    def Parabolic(self, x):
        """Evaluate the rising parabolic shoulder at `x`.

        Args:
            x: Finite built-in `int` or `float` coordinate; `bool` is excluded.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not a supported finite built-in number.
            OverflowError: If a finite input produces an unrepresentable
                intermediate square.
        """

        _RequireFiniteReal(x, 'x')

        return _membership._Parabolic(self._parameters, x)

    def Triangle(self, x):
        """Evaluate the triangular membership function at `x`.

        Args:
            x: Finite built-in `int` or `float` coordinate; `bool` is excluded.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not a supported finite built-in number.
        """

        _RequireFiniteReal(x, 'x')

        return _membership._Triangle(self._parameters, x)

    def Trapezium(self, x):
        """Evaluate the trapezoidal membership function at `x`.

        Args:
            x: Finite built-in `int` or `float` coordinate; `bool` is excluded.

        Returns:
            Membership degree in $[0, 1]$.

        Raises:
            ValueError: If `x` is not a supported finite built-in number.
        """

        _RequireFiniteReal(x, 'x')

        return _membership._Trapezium(self._parameters, x)

    def Exponential(self, x):
        """Evaluate the Gaussian-shaped exponential function at `x`.

        Args:
            x: Finite built-in `int` or `float` coordinate; `bool` is excluded.

        Returns:
            Representable membership degree in $[0, 1]$. Mathematically the
            function is positive, but sufficiently distant finite inputs can
            underflow to exactly zero.

        Raises:
            ValueError: If `x` is not a supported finite built-in number.
        """

        _RequireFiniteReal(x, 'x')

        return _membership._Exponential(self._parameters, x)

    def Sigmoidal(self, x):
        """Evaluate the numerically stable logistic function at `x`.

        Args:
            x: Finite built-in `int` or `float` coordinate; `bool` is excluded.

        Returns:
            Representable membership degree in $[0, 1]$. Floating-point
            underflow and rounding can produce either endpoint for finite
            inputs with sufficiently large magnitude.

        Raises:
            ValueError: If `x` is not a supported finite built-in number.
        """

        _RequireFiniteReal(x, 'x')

        return _membership._Sigmoidal(self._parameters, x)

    def Desirability(self, y):
        """Evaluate Harrington's desirability function at `y`.

        Args:
            y: Finite built-in `int` or `float` desirability coordinate;
                `bool` is excluded.

        Returns:
            Representable membership degree in $[0, 1]$. Sufficiently
            negative values underflow deterministically to zero, while
            sufficiently positive values round to one.

        Raises:
            ValueError: If `y` is not a supported finite built-in number.
        """

        _RequireFiniteReal(y, 'y')

        return _membership._Desirability(self._parameters, y)
