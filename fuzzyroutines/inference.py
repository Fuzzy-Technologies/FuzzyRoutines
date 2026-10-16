# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Explicit scalar Mamdani and Sugeno rule inference with immutable traces.

Rules use typed expression trees, never executable strings. Models have one
scalar output and one or more named scalar inputs. Container ownership is
immutable; custom membership callables retain their caller-owned state and must
be pure for reproducible evaluation. Membership grades are not probabilities.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from numbers import Rational
from typing import cast

from fuzzyroutines.defuzzification import (
    Centroid,
    CentroidPolicy,
    _IntegrationPoints,
    _PartitionedMembership,
)
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
    NumericalError,
    UndefinedResultError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal, _RequireGrade
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy


def _RequireName(value: object, label: str) -> None:
    """Reject empty or non-string exact identifiers."""

    if not isinstance(value, str):
        raise InvalidParameterTypeError(f"{label} must be a string")

    if not value.strip():
        raise InvalidParameterError(f"{label} must be non-empty")


def _RequireTuple(values: object, itemType: type, label: str) -> None:
    """Require a non-empty immutable collection of typed items."""

    if not isinstance(values, tuple) or not values:
        raise InvalidParameterTypeError(f"{label} must be a non-empty tuple")

    if not all(isinstance(value, itemType) for value in values):
        raise InvalidParameterTypeError(f"{label} contains an invalid item")


@dataclass(frozen=True, slots=True)
class FuzzyVariable:
    """Named scalar variable with ordered terms on one common universe.

    Attributes:
        name: Exact case-sensitive variable identifier.
        terms: Non-empty tuple of uniquely named linguistic terms with equal
            universes; membership callbacks are retained, not copied.
    """

    name: str
    terms: tuple[LinguisticTerm, ...]

    def __post_init__(self) -> None:
        """Validate names, term ownership and equal universes."""

        _RequireName(self.name, "variable name")
        _RequireTuple(self.terms, LinguisticTerm, "terms")

        if len({term.name for term in self.terms}) != len(self.terms):
            raise InvalidParameterError("term names must be unique within a variable")

        if any(term.fuzzySet.universe != self.terms[0].fuzzySet.universe for term in self.terms):
            raise InvalidDomainError("all variable terms must share the same universe")


@dataclass(frozen=True, slots=True)
class TermCondition:
    """Reference to one input variable's exact term name.

    Attributes:
        variable: Input variable identifier.
        term: Term identifier within that variable.
    """

    variable: str
    term: str

    def __post_init__(self) -> None:
        """Reject malformed references before model construction."""

        _RequireName(self.variable, "variable")
        _RequireName(self.term, "term")


@dataclass(frozen=True, slots=True)
class AllOf:
    """Ordered conjunction of at least two antecedents under the model t-norm.

    Attributes:
        operands: Immutable child expression tuple, evaluated without short circuiting.
    """

    operands: tuple[Antecedent, ...]

    def __post_init__(self) -> None:
        """Validate an explicit non-empty conjunction tree."""

        _ValidateOperands(self.operands)


@dataclass(frozen=True, slots=True)
class AnyOf:
    """Ordered disjunction of at least two antecedents under the model s-norm.

    Attributes:
        operands: Immutable child expression tuple, evaluated without short circuiting.
    """

    operands: tuple[Antecedent, ...]

    def __post_init__(self) -> None:
        """Validate an explicit non-empty disjunction tree."""

        _ValidateOperands(self.operands)


@dataclass(frozen=True, slots=True)
class NotCondition:
    """Negate one antecedent using the model's explicit negation policy.

    Attributes:
        operand: Typed child expression.
    """

    operand: Antecedent

    def __post_init__(self) -> None:
        """Reject an untyped child expression."""

        _References(self.operand)


type Antecedent = TermCondition | AllOf | AnyOf | NotCondition
"""Typed finite rule-expression tree; strings are never interpreted as code."""


def _References(expression: Antecedent) -> tuple[TermCondition, ...]:
    """Validate a finite typed expression and return its ordered leaves."""

    if isinstance(expression, TermCondition):
        return (expression,)

    if isinstance(expression, NotCondition):
        return _References(expression.operand)

    if isinstance(expression, (AllOf, AnyOf)):
        return tuple(leaf for child in expression.operands for leaf in _References(child))

    raise InvalidParameterTypeError("antecedent must be a typed condition")


def _ValidateOperands(operands: tuple[Antecedent, ...]) -> None:
    """Require two or more immutable typed children."""

    if not isinstance(operands, tuple) or len(operands) < 2:
        raise InvalidParameterTypeError("operands must be a tuple of at least two conditions")

    for operand in operands:
        _References(operand)


@dataclass(frozen=True, slots=True)
class InferencePolicy:
    """Explicit antecedent operators, separate from output activation/aggregation.

    Attributes:
        conjunction: T-norm for AND nodes.
        disjunction: S-norm for OR nodes.
        negation: Negation for NOT nodes.
    """

    conjunction: TNormPolicy
    disjunction: SNormPolicy
    negation: NegationPolicy

    def __post_init__(self) -> None:
        """Require immutable operator policies with validated parameters."""

        if not isinstance(self.conjunction, TNormPolicy):
            raise InvalidParameterTypeError("conjunction must be a TNormPolicy")

        if not isinstance(self.disjunction, SNormPolicy):
            raise InvalidParameterTypeError("disjunction must be an SNormPolicy")

        if not isinstance(self.negation, NegationPolicy):
            raise InvalidParameterTypeError("negation must be a NegationPolicy")


@dataclass(frozen=True, slots=True)
class ConstantConsequent:
    """Finite zero-order Sugeno consequent.

    Attributes:
        value: Constant output in the declared output universe's units.
    """

    value: MembershipScalar

    def __post_init__(self) -> None:
        """Reject non-real and non-finite coefficients."""

        object.__setattr__(self, "value", _RequireFiniteReal(self.value, "value"))


@dataclass(frozen=True, slots=True)
class AffineConsequent:
    r"""First-order Sugeno consequent $b+\sum_j a_j x_j$.

    The constant $b$ may be nonzero; this is an affine function of the inputs.

    Attributes:
        intercept: Finite constant $b$ in output units.
        coefficients: Immutable ordered `(inputName, coefficient)` pairs.
            Names must be unique; omitted input coefficients are zero.
    """

    intercept: MembershipScalar
    coefficients: tuple[tuple[str, MembershipScalar], ...]

    def __post_init__(self) -> None:
        """Validate finite coefficients and immutable unique input bindings."""

        object.__setattr__(self, "intercept", _RequireFiniteReal(self.intercept, "intercept"))

        if not isinstance(self.coefficients, tuple):
            raise InvalidParameterTypeError("coefficients must be an explicit tuple")

        names = []

        for pair in self.coefficients:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise InvalidParameterTypeError("each coefficient must be an (inputName, value) tuple")

            name, coefficient = pair
            _RequireName(name, "coefficient input name")
            _RequireFiniteReal(coefficient, "coefficient")
            names.append(name)

        if len(set(names)) != len(names):
            raise InvalidParameterError("coefficient input names must be unique")


@dataclass(frozen=True, slots=True)
class MamdaniRule:
    """Named rule producing one output linguistic term.

    Attributes:
        name: Unique rule identifier, preserved in result order.
        antecedent: Typed expression over input terms.
        consequent: Exact output term identifier.
        weight: Finite degree in $[0,1]$, multiplied by the antecedent grade.
    """

    name: str
    antecedent: Antecedent
    consequent: str
    weight: MembershipScalar = 1.0

    def __post_init__(self) -> None:
        """Validate rule shape independently from model bindings."""

        _RequireName(self.name, "rule name")
        _References(self.antecedent)
        _RequireName(self.consequent, "consequent")
        object.__setattr__(self, "weight", _RequireGrade(self.weight, "weight"))


@dataclass(frozen=True, slots=True)
class SugenoRule:
    """Named rule producing a constant or affine scalar consequence.

    Attributes:
        name: Unique rule identifier, preserved in result order.
        antecedent: Typed expression over input terms.
        consequent: Explicit zero- or first-order consequent.
        weight: Finite degree in $[0,1]$, multiplied by the antecedent grade.
    """

    name: str
    antecedent: Antecedent
    consequent: ConstantConsequent | AffineConsequent
    weight: MembershipScalar = 1.0

    def __post_init__(self) -> None:
        """Validate rule shape independently from model bindings."""

        _RequireName(self.name, "rule name")
        _References(self.antecedent)

        if not isinstance(self.consequent, (ConstantConsequent, AffineConsequent)):
            raise InvalidParameterTypeError("consequent must be constant or affine")

        object.__setattr__(self, "weight", _RequireGrade(self.weight, "weight"))


@dataclass(frozen=True, slots=True)
class InputGrade:
    """Recorded membership of one term at the supplied input coordinate.

    Attributes:
        variable: Exact input name.
        term: Exact term name.
        coordinate: Validated input coordinate.
        grade: Membership degree in $[0,1]$.
    """

    variable: str
    term: str
    coordinate: MembershipScalar
    grade: MembershipScalar


@dataclass(frozen=True, slots=True)
class MamdaniRuleTrace:
    """One rule's activation, before output aggregation.

    Attributes:
        name: Exact rule name in declaration order.
        antecedentGrade: Result of the typed antecedent expression.
        weight: Declared multiplicative rule weight.
        firingStrength: Product of weight and antecedent grade.
        activatedSet: Output contribution, evaluated on the output universe.
    """

    name: str
    antecedentGrade: MembershipScalar
    weight: MembershipScalar
    firingStrength: MembershipScalar
    activatedSet: ScalarFuzzySet


@dataclass(frozen=True, slots=True)
class SugenoRuleTrace:
    """One rule's normalized scalar contribution.

    Attributes:
        name: Exact rule name in declaration order.
        antecedentGrade: Result of the typed antecedent expression.
        weight: Declared multiplicative rule weight.
        firingStrength: Product of weight and antecedent grade.
        consequentValue: Constant or affine consequence at the supplied inputs.
        normalizedStrength: Firing strength divided by total firing strength.
        contribution: Product of normalized strength and consequent value.
    """

    name: str
    antecedentGrade: MembershipScalar
    weight: MembershipScalar
    firingStrength: MembershipScalar
    consequentValue: MembershipScalar
    normalizedStrength: MembershipScalar
    contribution: MembershipScalar


@dataclass(frozen=True, slots=True)
class MamdaniResult:
    """Immutable inference evidence and optionally a numerical centroid.

    Factory evaluation validates trace consistency. Direct construction only
    validates container ownership and output types, not the recorded mathematics.

    Attributes:
        inputGrades: Ordered snapshot of all declared input-term memberships.
        rules: Ordered rule activation traces.
        outputSet: Aggregated output set with no analytical certificate.
        value: Centroid when requested, otherwise `None`.
        integrationDomain: Requested centroid interval, otherwise `None`.
        centroidPolicy: Applied numerical policy, otherwise `None`.
        method: `"adaptive-simpson"` or `"fuzzy-set"`.
    """

    inputGrades: tuple[InputGrade, ...]
    rules: tuple[MamdaniRuleTrace, ...]
    outputSet: ScalarFuzzySet
    value: MembershipScalar | None
    integrationDomain: IntegrationDomain | None
    centroidPolicy: CentroidPolicy | None
    method: str

    def __post_init__(self) -> None:
        """Preserve immutable trace ownership and explicit result metadata."""

        _RequireTuple(self.inputGrades, InputGrade, "inputGrades")
        _RequireTuple(self.rules, MamdaniRuleTrace, "rules")

        if not isinstance(self.outputSet, ScalarFuzzySet):
            raise InvalidParameterTypeError("outputSet must be a ScalarFuzzySet")

        if self.value is None:
            if self.integrationDomain is not None or self.centroidPolicy is not None or self.method != "fuzzy-set":
                raise InvalidParameterError("an unevaluated centroid must have no numerical metadata")

        else:
            _RequireFiniteReal(self.value, "value")

            if not isinstance(self.integrationDomain, IntegrationDomain) or not isinstance(self.centroidPolicy, CentroidPolicy):
                raise InvalidParameterTypeError("a centroid requires a domain and policy")

            if self.method != "adaptive-simpson":
                raise InvalidParameterError("composed Mamdani outputs use adaptive-simpson")


@dataclass(frozen=True, slots=True)
class SugenoResult:
    """Immutable weighted-average result and its ordered rule contributions.

    Factory evaluation validates consistency; direct construction validates
    container ownership and a finite output, not the recorded mathematics.
    Rounded trace contributions may differ from `value` by round-off; a rational
    fallback restores the consequent convex hull when their sum escapes it.

    Attributes:
        inputGrades: Ordered snapshot of all declared input-term memberships.
        rules: Ordered scalar rule traces, including inactive rules.
        value: Finite normalized weighted-average output.
        method: Fixed `"normalized-weighted-average"` identifier.
    """

    inputGrades: tuple[InputGrade, ...]
    rules: tuple[SugenoRuleTrace, ...]
    value: MembershipScalar
    method: str = "normalized-weighted-average"

    def __post_init__(self) -> None:
        """Preserve immutable trace ownership and finite result metadata."""

        _RequireTuple(self.inputGrades, InputGrade, "inputGrades")
        _RequireTuple(self.rules, SugenoRuleTrace, "rules")
        _RequireFiniteReal(self.value, "value")

        if self.method != "normalized-weighted-average":
            raise InvalidParameterError("unknown Sugeno output method")


def _ValidateModel(
    inputs: tuple[FuzzyVariable, ...],
    rules: tuple[MamdaniRule | SugenoRule, ...],
    policy: InferencePolicy,
) -> None:
    """Validate unique named input/rule declarations and every leaf binding."""

    _RequireTuple(inputs, FuzzyVariable, "inputs")

    if not isinstance(policy, InferencePolicy):
        raise InvalidParameterTypeError("policy must be an InferencePolicy")

    if len({variable.name for variable in inputs}) != len(inputs):
        raise InvalidParameterError("input names must be unique")

    if len({rule.name for rule in rules}) != len(rules):
        raise InvalidParameterError("rule names must be unique")

    bindings = {(variable.name, term.name) for variable in inputs for term in variable.terms}

    for rule in rules:
        if any((leaf.variable, leaf.term) not in bindings for leaf in _References(rule.antecedent)):
            raise InvalidParameterError(f"unknown antecedent reference in rule {rule.name!r}")


def _PrepareInputs(
    variables: tuple[FuzzyVariable, ...],
    values: Mapping[str, MembershipScalar],
) -> tuple[dict[str, float], tuple[InputGrade, ...], dict[tuple[str, str], float]]:
    """Snapshot exact keys and evaluate every declared input term once."""

    if not isinstance(values, Mapping):
        raise InvalidParameterTypeError("inputs must be a mapping")

    if set(values) != {variable.name for variable in variables}:
        raise InvalidParameterError("inputs must contain exactly the declared variable names")

    coordinates = {variable.name: _RequireFiniteReal(values[variable.name], variable.name) for variable in variables}
    grades = tuple(
        InputGrade(variable.name, term.name, coordinates[variable.name], term.fuzzySet.Membership(coordinates[variable.name]))
        for variable in variables
        for term in variable.terms
    )

    return coordinates, grades, {(grade.variable, grade.term): cast(float, grade.grade) for grade in grades}


def _EvaluateCondition(
    expression: Antecedent,
    grades: dict[tuple[str, str], float],
    policy: InferencePolicy,
) -> float:
    """Evaluate an already validated expression in deterministic child order."""

    if isinstance(expression, TermCondition):
        return grades[(expression.variable, expression.term)]

    if isinstance(expression, NotCondition):
        return cast(float, policy.negation.Evaluate(_EvaluateCondition(expression.operand, grades, policy)))

    operator = policy.conjunction if isinstance(expression, AllOf) else policy.disjunction
    result = _EvaluateCondition(expression.operands[0], grades, policy)

    for child in expression.operands[1:]:
        result = cast(float, operator.Evaluate(result, _EvaluateCondition(child, grades, policy)))

    return result


def _Firings(
    rules: tuple[MamdaniRule | SugenoRule, ...],
    grades: dict[tuple[str, str], float],
    policy: InferencePolicy,
) -> tuple[tuple[float, float], ...]:
    """Return antecedent/firing pairs or explicitly reject no fired rules."""

    antecedents = tuple(_EvaluateCondition(rule.antecedent, grades, policy) for rule in rules)
    result = tuple((grade, grade * cast(float, rule.weight)) for rule, grade in zip(rules, antecedents, strict=True))

    if any(grade > 0 and cast(float, rule.weight) > 0 and strength == 0 for rule, (grade, strength) in zip(rules, result, strict=True)):
        raise NumericalError("positive rule firing strength underflowed to zero")

    if not any(strength > 0 for _, strength in result):
        raise UndefinedResultError("inference is undefined because no rule fires")

    return result


@dataclass(frozen=True, slots=True)
class _ActivatedMembership:
    """Retain an immutable firing snapshot, independent of future evaluations."""

    source: ScalarFuzzySet
    strength: float
    activation: TNormPolicy

    def __call__(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Apply the separately selected output-activation t-norm."""

        return self.activation.Evaluate(self.strength, self.source.Membership(coordinate))


@dataclass(frozen=True, slots=True)
class _AggregatedMembership:
    """Ordered aggregate of activated output sets without analytical metadata."""

    sources: tuple[ScalarFuzzySet, ...]
    aggregation: SNormPolicy

    def __call__(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Fold the configured s-norm from its zero identity."""

        result: MembershipScalar = 0.0

        for source in self.sources:
            result = self.aggregation.Evaluate(result, source.Membership(coordinate))

        return result


@dataclass(frozen=True, slots=True)
class MamdaniModel:
    """Scalar rule base with explicit output activation and aggregation.

    Attributes:
        inputs: Ordered immutable input variable tuple.
        output: Named output variable whose terms share a continuous universe.
        rules: Non-empty tuple of uniquely named Mamdani rules.
        policy: Explicit antecedent logic operators.
        activation: T-norm applying firing strength to each consequent set.
        aggregation: S-norm combining activated output sets.
    """

    inputs: tuple[FuzzyVariable, ...]
    output: FuzzyVariable
    rules: tuple[MamdaniRule, ...]
    policy: InferencePolicy
    activation: TNormPolicy
    aggregation: SNormPolicy

    def __post_init__(self) -> None:
        """Validate the complete rule base before any membership evaluation."""

        _RequireTuple(self.rules, MamdaniRule, "rules")
        _ValidateModel(self.inputs, self.rules, self.policy)

        if not isinstance(self.output, FuzzyVariable):
            raise InvalidParameterTypeError("output must be a FuzzyVariable")

        if not isinstance(self.output.terms[0].fuzzySet.universe, ContinuousUniverse):
            raise InvalidParameterTypeError("Mamdani output requires a ContinuousUniverse")

        if any(rule.consequent not in {term.name for term in self.output.terms} for rule in self.rules):
            raise InvalidParameterError("unknown output term in Mamdani rule")

        if not isinstance(self.activation, TNormPolicy) or not isinstance(self.aggregation, SNormPolicy):
            raise InvalidParameterTypeError("activation/aggregation require TNormPolicy/SNormPolicy")

    def Evaluate(
        self,
        inputs: Mapping[str, MembershipScalar],
        integrationDomain: IntegrationDomain | None = None,
        centroidPolicy: CentroidPolicy | None = None,
    ) -> MamdaniResult:
        """Return activated sets, aggregate and optional numerical centroid.

        Args:
            inputs: Exactly the declared input names and finite coordinates.
            integrationDomain: Finite output interval; `None` returns only a set.
            centroidPolicy: Adaptive quadrature settings, requiring a domain.

        Returns:
            Immutable trace snapshot; composed outputs are numerically integrated.

        Raises:
            InvalidParameterError: Missing/extra inputs or a policy without a domain.
            InvalidParameterTypeError: Malformed arguments or membership results.
            InvalidDomainError: Input or integration coordinate outside its universe.
            UndefinedResultError: No firing or zero/non-finite integrated area.
            NumericalError: A positive weighted firing product underflows to zero.
            CentroidConvergenceError: The requested quadrature did not converge.
        """

        universe = cast(ContinuousUniverse, self.output.terms[0].fuzzySet.universe)

        if integrationDomain is None:
            if centroidPolicy is not None:
                raise InvalidParameterError("centroidPolicy requires integrationDomain")

        else:
            if not isinstance(integrationDomain, IntegrationDomain):
                raise InvalidParameterTypeError("integrationDomain must be an IntegrationDomain")

            integrationDomain.ValidateWithin(universe)
            centroidPolicy = CentroidPolicy() if centroidPolicy is None else centroidPolicy

            if not isinstance(centroidPolicy, CentroidPolicy):
                raise InvalidParameterTypeError("centroidPolicy must be a CentroidPolicy")

        _, inputGrades, grades = _PrepareInputs(self.inputs, inputs)
        firings = _Firings(self.rules, grades, self.policy)
        terms = {term.name: term.fuzzySet for term in self.output.terms}
        traces = tuple(
            MamdaniRuleTrace(rule.name, antecedent, rule.weight, strength, ScalarFuzzySet(
                universe, _PartitionedMembership(
                    _ActivatedMembership(terms[rule.consequent], strength, self.activation),
                    _IntegrationPoints(terms[rule.consequent], strength if self.activation.family == "logic" else None),
                ),
            ))
            for rule, (antecedent, strength) in zip(self.rules, firings, strict=True)
        )
        points = tuple(sorted({point for trace in traces for point in _IntegrationPoints(trace.activatedSet)}))
        outputSet = ScalarFuzzySet(universe, _PartitionedMembership(
            _AggregatedMembership(tuple(trace.activatedSet for trace in traces), self.aggregation), points,
        ))
        value = None if integrationDomain is None else Centroid(outputSet, integrationDomain, centroidPolicy)

        return MamdaniResult(
            inputGrades, traces, outputSet, value, integrationDomain, centroidPolicy,
            "fuzzy-set" if integrationDomain is None else "adaptive-simpson",
        )


def _FiniteSum(values: tuple[float, ...]) -> float:
    """Reject non-finite intermediate arithmetic without clamping."""

    if not all(math.isfinite(value) for value in values):
        raise NumericalError("Sugeno intermediate arithmetic must be finite")

    try:
        result = math.fsum(values)

    except OverflowError as error:
        raise NumericalError("Sugeno sum overflowed") from error

    if not math.isfinite(result):
        raise NumericalError("Sugeno sum must be finite")

    return result


def _ExactRatio(value: MembershipScalar) -> Fraction:
    """Preserve supported rational values before representing other real scalars."""

    if isinstance(value, Rational):
        return Fraction(value)

    return Fraction(float(value))


def _WeightedAverage(traces: tuple[SugenoRuleTrace, ...]) -> float:
    """Preserve the consequent convex hull without clamping a numerical result."""

    consequences = tuple(cast(float, trace.consequentValue) for trace in traces)

    try:
        result = _FiniteSum(tuple(cast(float, trace.contribution) for trace in traces))

    except NumericalError:
        result = math.inf

    if min(consequences) <= result <= max(consequences):
        return result

    # Rare boundary round-off must not reject a valid closed-universe model.
    # Recompute the actual ratio instead of forcing an output to a boundary.
    strengths = tuple(_ExactRatio(trace.firingStrength) for trace in traces)
    numerator = sum((strength * _ExactRatio(value) for strength, value in zip(strengths, consequences, strict=True)), Fraction(0))
    denominator = sum(strengths, Fraction(0))

    return float(numerator / denominator)


@dataclass(frozen=True, slots=True)
class SugenoModel:
    """Scalar normalized weighted-average model with constant/affine outputs.

    Attributes:
        inputs: Ordered immutable input variable tuple.
        rules: Non-empty tuple of uniquely named Sugeno rules.
        policy: Explicit antecedent logic operators.
        outputUniverse: Allowed universe for each consequence and final output;
            use an unbounded continuous universe for unrestricted finite outputs.
    """

    inputs: tuple[FuzzyVariable, ...]
    rules: tuple[SugenoRule, ...]
    policy: InferencePolicy
    outputUniverse: ContinuousUniverse

    def __post_init__(self) -> None:
        """Reject malformed rules and unknown affine input coefficients."""

        _RequireTuple(self.rules, SugenoRule, "rules")
        _ValidateModel(self.inputs, self.rules, self.policy)

        if not isinstance(self.outputUniverse, ContinuousUniverse):
            raise InvalidParameterTypeError("outputUniverse must be a ContinuousUniverse")

        inputNames = {variable.name for variable in self.inputs}

        for rule in self.rules:
            if isinstance(rule.consequent, AffineConsequent):
                if any(name not in inputNames for name, _ in rule.consequent.coefficients):
                    raise InvalidParameterError("unknown input in affine consequent")

            elif not self.outputUniverse.Contains(rule.consequent.value):
                raise InvalidDomainError("constant consequent lies outside output universe")

    def Evaluate(self, inputs: Mapping[str, MembershipScalar]) -> SugenoResult:
        """Evaluate every consequence and normalized rule contribution.

        Args:
            inputs: Exactly the declared input names and finite coordinates.

        Returns:
            Immutable scalar result with all ordered rule contributions.

        Raises:
            InvalidParameterError: Input keys or values violate the contract.
            InvalidParameterTypeError: An input or membership has the wrong type.
            InvalidDomainError: A coordinate or consequence is outside its universe.
            UndefinedResultError: All weighted firing strengths are zero.
            NumericalError: A positive weighted firing product underflows, or
                intermediate affine arithmetic or summation is non-finite.
        """

        coordinates, inputGrades, grades = _PrepareInputs(self.inputs, inputs)
        firings = _Firings(self.rules, grades, self.policy)
        maximum = max(strength for _, strength in firings)
        scaled = tuple(strength / maximum for _, strength in firings)
        denominator = _FiniteSum(scaled)
        traces = []
        exactDenominator = None

        for rule, (antecedent, strength), scaledStrength in zip(self.rules, firings, scaled, strict=True):
            consequent = rule.consequent

            if isinstance(consequent, ConstantConsequent):
                value = cast(float, consequent.value)

            else:
                value = _FiniteSum((cast(float, consequent.intercept), *(
                    cast(float, coefficient) * coordinates[name] for name, coefficient in consequent.coefficients
                )))

            if not self.outputUniverse.Contains(value):
                raise InvalidDomainError(f"consequent of rule {rule.name!r} lies outside output universe")

            normalized: MembershipScalar = scaledStrength / denominator

            if strength > 0 and normalized < float.fromhex("0x1.0p-1022"):
                # MembershipScalar already admits exact Real values. Retain a
                # positive unrepresentable normalized weight in that contract,
                # so a large consequent can still have a finite contribution.
                if exactDenominator is None:
                    exactDenominator = sum((_ExactRatio(current) for _, current in firings), Fraction(0))

                normalized = _ExactRatio(strength) / exactDenominator
                contribution = float(normalized * _ExactRatio(value))

            else:
                contribution = cast(float, normalized) * value

            traces.append(SugenoRuleTrace(rule.name, antecedent, rule.weight, strength, value, normalized, contribution))

        result = _WeightedAverage(tuple(traces))

        if not self.outputUniverse.Contains(result):
            raise InvalidDomainError("Sugeno result lies outside output universe")

        return SugenoResult(inputGrades, tuple(traces), result)
