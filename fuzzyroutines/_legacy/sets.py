# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Mutable historical fuzzy-set state adapting modern domain and centroid policies."""

import fuzzyroutines.domain as _domain
from fuzzyroutines._legacy.membership import MFunction
from fuzzyroutines.defuzzification import _Centroid
from fuzzyroutines.exceptions import InvalidParameterError, InvalidParameterTypeError
from fuzzyroutines.fuzzysets import ScalarFuzzySet as _ScalarFuzzySet


class FuzzySet():
    """Represent a mutable historical fuzzy set and integration interval.

    Args:
        membershipFunction: A configured [MFunction][fuzzyroutines.FuzzyRoutines.MFunction].
        supportSet: Two-item tuple used as the numerical integration domain.
        linguisticName: Human-readable set name.

    Raises:
        Exception: If `linguisticName` is not a string or
            `membershipFunction` is not an `MFunction`.
        TypeError: If `supportSet` is not a tuple or contains non-real
            endpoints.
        ValueError: If `supportSet` does not contain two finite increasing
            endpoints.

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

        self.supportSet = supportSet

        self._defuzValue = None

    def __str__(self):
        """Return the historical name/function/interval representation."""

        # return view of fuzzy set - name = <mju(x|y, params), supportSet>. Example: FuzzySet = <Bell(x, a, b), [0, 1]>
        set_view = '{} = <{}, [{}, {}]>'.format(
            self._name,
            self._mFunction,
            self._integrationDomain.left,
            self._integrationDomain.right,
        )

        return set_view

    @property
    def name(self):
        """Return the linguistic name."""

        return self._name

    @name.setter
    def name(self, value):
        """Replace the linguistic name with a string value.

        Raises:
            Exception: If `value` is not a string.
        """

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
        """Replace the membership function with an `MFunction` instance.

        Raises:
            Exception: If `value` is not an `MFunction`.
        """

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
        """Validate and replace the two numerical integration endpoints.

        Raises:
            TypeError: If `value` is not a tuple or contains non-real
                endpoints.
            ValueError: If `value` does not contain two finite increasing
                endpoints.
        """

        # This adapter retains the documented concrete built-in input errors.
        # Domain construction runs no user callbacks, so only owned failures translate.
        try:
            integration_domain = _domain.IntegrationDomain.FromLegacyInterval(value)

        except InvalidParameterTypeError as error:
            raise TypeError(str(error)) from error

        except InvalidParameterError as error:
            raise ValueError(str(error)) from error

        self._integrationDomain = integration_domain

    @property
    def defuzValue(self):
        """Calculate and return the current center-of-area value.

        Raises:
            ValueError: If membership area is zero or non-finite.
            CentroidConvergenceError: If adaptive integration cannot satisfy
                its explicit default tolerance.
        """

        self._defuzValue = self._Defuz()

        return self._defuzValue

    def _Defuz(self):
        """Calculate centroid defuzzification over the integration domain.

        Returns:
            Analytical centroid for supported stable families, otherwise the
            deterministic adaptive-quadrature result.

        Raises:
            ValueError: If membership area is zero or non-finite.
            CentroidConvergenceError: If adaptive integration cannot satisfy
                its explicit default tolerance.
        """

        fuzzy_set = _ScalarFuzzySet(
            _domain.ContinuousUniverse(),
            self._mFunction.mju,
        )

        # Select the historical result contract inside the engine, where callback
        # failures can propagate without being mistaken for an undefined result.
        return _Centroid(fuzzy_set, self._integrationDomain, None, ValueError)

    def Defuz(self):
        """Return `defuzValue` through the historical method alias.

        Raises:
            ValueError: If membership area is zero or non-finite.
            CentroidConvergenceError: If adaptive integration cannot satisfy
                its explicit default tolerance.
        """

        return self.defuzValue
