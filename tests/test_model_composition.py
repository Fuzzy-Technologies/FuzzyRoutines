# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contract checks for the private named model composition prototype."""

from dataclasses import replace
from fractions import Fraction
from math import isclose as IsClose
from unittest import TestCase

from examples.inference import BuildModels
from fuzzyroutines import IntegrationDomain, ScalarFuzzySet
from fuzzyroutines._model_composition import (
    CompositionEvaluationError,
    ModelComposition,
    OutputBinding,
    OutputFailure,
)
from fuzzyroutines.defuzzification import CentroidPolicy
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
    UndefinedResultError,
)
from fuzzyroutines.inference import MamdaniResult


class ModelCompositionTests(TestCase):
    """Preserve scalar semantics and enforce explicit composition boundaries."""

    def test_MixedOutputsRetainScalarResultsAndOrder(self):
        """Compare all ordered numerical and trace evidence to scalar calls."""

        mamdani, sugeno, _ = BuildModels()
        domain = IntegrationDomain(0, 1)
        composition = ModelComposition((
            OutputBinding("response", mamdani, (("risk", "riskScore"),), domain),
            OutputBinding("score", sugeno, (("risk", "riskScore"),)),
            OutputBinding("aggregate", mamdani, (("risk", "riskScore"),)),
        ), "fail-fast")
        coordinate = Fraction(1, 4)
        outputs = composition.Evaluate({"riskScore": coordinate})

        self.assertEqual(composition.inputIds, ("riskScore",))
        self.assertEqual(tuple(output.outputId for output in outputs), ("response", "score", "aggregate"))
        self.assertEqual(outputs[1].outcome, sugeno.Evaluate({"risk": coordinate}))

        for record, integrationDomain in ((outputs[0], domain), (outputs[2], None)):
            direct = mamdani.Evaluate({"risk": coordinate}, integrationDomain)
            outcome = record.outcome
            self.assertIsInstance(outcome, MamdaniResult)
            self.assertEqual(outcome.value, direct.value)
            self.assertEqual(outcome.method, direct.method)
            self.assertEqual(outcome.inputGrades, direct.inputGrades)
            self.assertIsInstance(outcome.inputGrades[0].coordinate, Fraction)
            self.assertEqual(
                tuple(trace.firingStrength for trace in outcome.rules),
                tuple(trace.firingStrength for trace in direct.rules),
            )
            self.assertEqual(
                tuple(outcome.outputSet.Membership(point) for point in (0, 0.25, 0.5, 0.75, 1)),
                tuple(direct.outputSet.Membership(point) for point in (0, 0.25, 0.5, 0.75, 1)),
            )

        self.assertTrue(IsClose(outputs[0].outcome.value, 37 / 96, rel_tol=0, abs_tol=1e-12))
        self.assertTrue(IsClose(outputs[1].outcome.value, 7 / 20, rel_tol=0, abs_tol=1e-15))
        self.assertIsNone(outputs[2].outcome.value)

    def test_ExactAliasesDoNotDependOnInputMapOrder(self):
        """Keep same-named scalar inputs independent unless an alias is shared."""

        _, sugeno, _ = BuildModels()
        composition = ModelComposition((
            OutputBinding("risk", sugeno, (("risk", "risk"),)),
            OutputBinding("Risk", sugeno, (("risk", "Risk"),)),
        ), "fail-fast")
        observations = {"Risk": 0.75, "risk": 0.25}
        outputs = composition.Evaluate(observations)

        self.assertEqual(composition.inputIds, ("risk", "Risk"))
        self.assertEqual(outputs, composition.Evaluate(dict(reversed(tuple(observations.items())))))
        self.assertEqual(outputs[0].outcome, sugeno.Evaluate({"risk": 0.25}))
        self.assertEqual(outputs[1].outcome, sugeno.Evaluate({"risk": 0.75}))

    def test_InvalidInputsNeverInvokeCallbacks(self):
        """Reject missing, extra, misspelled, and invalid values before any output."""

        calls = []

        def CountLow(coordinate):
            """Record membership calls while evaluating the existing ramp."""

            calls.append(coordinate)

            return 1 - coordinate

        _, sugeno, _ = BuildModels()
        variable = sugeno.inputs[0]
        low, high = variable.terms
        counted = replace(low, fuzzySet=ScalarFuzzySet(low.fuzzySet.universe, CountLow))
        tracked = replace(sugeno, inputs=(replace(variable, terms=(counted, high)),))
        composition = ModelComposition((
            OutputBinding("left", tracked, (("risk", "leftValue"),)),
            OutputBinding("right", tracked, (("risk", "rightValue"),)),
        ), "per-output")

        for inputs in (
            {"leftValue": 0.25},
            {"leftValue": 0.25, "rightValue": 0.25, "extra": 1},
            {"leftValue": 0.25, "RightValue": 0.25},
            {"leftValue": 0.25, "rightValue": float("nan")},
        ):
            with self.assertRaises(InvalidParameterError):
                composition.Evaluate(inputs)

        with self.assertRaises(InvalidParameterTypeError):
            composition.Evaluate({"leftValue": 0.25, "rightValue": True})

        self.assertEqual(calls, [])
        composition.Evaluate({"rightValue": 0.75, "leftValue": 0.25})
        self.assertEqual(calls, [0.25, 0.75])

    def test_OutputFailurePoliciesPreserveCausesAndLaterResults(self):
        """Stop or continue in output order without inventing a result."""

        _, sugeno, _ = BuildModels()
        silent = replace(sugeno, rules=tuple(replace(rule, weight=0) for rule in sugeno.rules))
        bindings = (
            OutputBinding("domain", sugeno, (("risk", "outside"),)),
            OutputBinding("undefined", silent, (("risk", "inside"),)),
            OutputBinding("success", sugeno, (("risk", "inside"),)),
        )
        inputs = {"inside": 0.25, "outside": 2}
        outputs = ModelComposition(bindings, "per-output").Evaluate(inputs)

        self.assertEqual(tuple(output.outputId for output in outputs), ("domain", "undefined", "success"))
        self.assertIsInstance(outputs[0].outcome, OutputFailure)
        self.assertEqual(outputs[0].outcome.category, "domain")
        self.assertEqual(outputs[1].outcome.category, "undefined")
        self.assertEqual(outputs[2].outcome, sugeno.Evaluate({"risk": 0.25}))

        for selected, outputId, errorType in (
            (bindings, "domain", InvalidDomainError),
            (bindings[1:], "undefined", UndefinedResultError),
        ):
            with self.assertRaises(CompositionEvaluationError) as error:
                selectedInputs = inputs if outputId == "domain" else {"inside": 0.25}
                ModelComposition(selected, "fail-fast").Evaluate(selectedInputs)

            self.assertEqual(error.exception.outputId, outputId)
            self.assertIsInstance(error.exception.__cause__, errorType)

    def test_UnexpectedCallbackFailurePropagates(self):
        """Propagate unexpected user exceptions even in per-output mode."""

        def Broken(_):
            """Raise an application error outside the documented scalar errors."""

            raise RuntimeError("callback failed")

        _, sugeno, _ = BuildModels()
        variable = sugeno.inputs[0]
        low, high = variable.terms
        broken = replace(low, fuzzySet=ScalarFuzzySet(low.fuzzySet.universe, Broken))
        failing = replace(sugeno, inputs=(replace(variable, terms=(broken, high)),))
        composition = ModelComposition((OutputBinding("score", failing, (("risk", "risk"),)),), "per-output")

        with self.assertRaisesRegex(RuntimeError, "callback failed"):
            composition.Evaluate({"risk": 0.25})

    def test_InvalidBindingAndOutputCollisionFailEarly(self):
        """Reject colliding outputs, invalid IDs, routing, and centroid options."""

        mamdani, sugeno, _ = BuildModels()
        binding = OutputBinding("score", sugeno, (("risk", "risk"),))

        with self.assertRaisesRegex(InvalidParameterError, "unique"):
            ModelComposition((binding, binding), "fail-fast")

        for routes in ((), (("Risk", "risk"),), (("risk", "risk"), ("risk", "other"))):
            with self.assertRaisesRegex(InvalidParameterError, "declared scalar names"):
                OutputBinding("score", sugeno, routes)

        for outputId in (" score", "é", "a" * 65):
            with self.assertRaisesRegex(InvalidParameterError, "ASCII"):
                OutputBinding(outputId, sugeno, (("risk", "risk"),))

        with self.assertRaisesRegex(InvalidParameterError, "Sugeno"):
            OutputBinding("score", sugeno, (("risk", "risk"),), IntegrationDomain(0, 1))

        with self.assertRaisesRegex(InvalidParameterError, "requires integrationDomain"):
            OutputBinding("response", mamdani, (("risk", "risk"),), centroidPolicy=CentroidPolicy())

    def test_ResourceLimitsAcceptBoundaryAndRejectNextSize(self):
        """Exercise the first excluded output, external input, and binding counts."""

        _, sugeno, _ = BuildModels()
        bindings = tuple(OutputBinding(f"o{index}", sugeno, (("risk", "risk"),)) for index in range(65))
        self.assertEqual(len(ModelComposition(bindings[:64], "fail-fast").outputs), 64)

        with self.assertRaisesRegex(InvalidParameterError, "1–64"):
            ModelComposition(bindings, "fail-fast")

        extraVariables = tuple(replace(sugeno.inputs[0], name=f"x{index}") for index in range(1, 257))
        routes = (("risk", "risk"),) + tuple((variable.name, variable.name) for variable in extraVariables)
        largeModel = replace(sugeno, inputs=sugeno.inputs + extraVariables)
        boundedModel = replace(largeModel, inputs=largeModel.inputs[:-1])
        self.assertEqual(len(ModelComposition((
            OutputBinding("score", boundedModel, routes[:-1]),
        ), "fail-fast").inputIds), 256)

        with self.assertRaisesRegex(InvalidParameterError, "distinct input limit"):
            ModelComposition((OutputBinding("score", largeModel, routes),), "fail-fast")

        wideModel = replace(largeModel, inputs=largeModel.inputs[:65])
        wideRoutes = tuple((variable.name, "risk") for variable in wideModel.inputs)
        prefix = tuple(OutputBinding(f"w{index}", wideModel, wideRoutes) for index in range(63))
        self.assertEqual(len(ModelComposition(prefix + bindings[:1], "fail-fast").outputs), 64)
        twoInputs = replace(largeModel, inputs=largeModel.inputs[:2])
        oneTooMany = OutputBinding("last", twoInputs, (("risk", "risk"), ("x1", "risk")))

        with self.assertRaisesRegex(InvalidParameterError, "binding limit"):
            ModelComposition(prefix + (oneTooMany,), "fail-fast")
