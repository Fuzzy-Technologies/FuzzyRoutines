# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public errors for invalid inputs and unresolved mathematical operations.

Every category preserves the applicable built-in catch contract. User-defined
membership callbacks keep their own exceptions; the core does not translate
arbitrary evaluator failures. Historical adapters retain their documented
concrete exceptions.
"""

__all__ = [
    "FuzzyRoutinesError",
    "InvalidDomainError",
    "InvalidParameterError",
    "InvalidParameterTypeError",
    "NumericalError",
    "UndefinedResultError",
]


class FuzzyRoutinesError(Exception):
    """Base class for errors explicitly raised by the modern mathematical API."""


class InvalidParameterTypeError(TypeError, FuzzyRoutinesError):
    """A supplied object has the wrong kind; also catchable as `TypeError`."""


class InvalidParameterError(ValueError, FuzzyRoutinesError):
    """A supplied value violates a contract; also catchable as `ValueError`."""


class InvalidDomainError(InvalidParameterError):
    """An interval, coordinate collection, or universe relationship is invalid."""


class NumericalError(ArithmeticError, FuzzyRoutinesError):
    """A mathematical result cannot be resolved; catchable as `ArithmeticError`."""


class UndefinedResultError(ValueError, NumericalError):
    """A result is undefined or non-finite under the requested operation.

    Inheriting `ValueError` preserves existing zero-area and zero-height catch
    behavior; inheriting `NumericalError` also permits one numerical-failure
    handler alongside centroid convergence failures.
    """
