# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Dispatch standalone JSON calculator commands through the scalar API."""

import argparse
import json
import sys
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal, NoReturn, TextIO

from ._config_json import _MAX_BYTES, _NUMBER, DecodeConfigJson, JsonNumber
from .configuration import ConfigurationError, LoadModel, MamdaniBinding, ModelConfiguration, ScaleDefinition
from .encoding import LinguisticCodec
from .exceptions import FuzzyRoutinesError
from .inference import MamdaniResult, MamdaniRuleTrace, SugenoResult, SugenoRuleTrace
from .linguistic import FuzzificationPolicy

type _ErrorCategory = Literal["usage", "configuration", "evaluation", "io", "capability"]

_EXIT_CODES: dict[_ErrorCategory, int] = {
    "usage": 2, "configuration": 3, "evaluation": 4, "io": 5, "capability": 6,
}


class _CommandError(Exception):
    """Command failure classified by the calculator contract."""

    def __init__(self, category: _ErrorCategory, message: str) -> None:
        """Retain the exit category and diagnostic wording."""

        super().__init__(message)
        self.category = category


class _ArgumentParser(argparse.ArgumentParser):
    """Report syntax failures through the machine diagnostic stream."""

    def _Error(self, message: str) -> NoReturn:
        """Raise the syntax error for canonical stderr formatting."""

        raise _CommandError("usage", message)

    # Preserve the hook name imposed by argparse.
    error = _Error


def _Write(stream: TextIO, record: dict[str, object]) -> None:
    """Write one sorted, finite JSON object and LF."""

    stream.write(json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


def _ParseNumber(token: str) -> float:
    """Decode one JSON number using the wire codec's binary64 checks."""

    try:
        number = DecodeConfigJson(token.encode("ascii"))

    except (ConfigurationError, UnicodeEncodeError) as error:
        raise _CommandError("usage", f"Invalid JSON number: {token!r}.") from error

    if not isinstance(number, JsonNumber) or number.token != token:
        raise _CommandError("usage", f"Invalid JSON number: {token!r}.")

    return number.binary64


def _InputOptions(
    numberOptions: Sequence[str], termOptions: Sequence[str],
) -> dict[str, float | str]:
    """Parse explicit bindings and reject duplicates across both option types."""

    values: dict[str, float | str] = {}

    for options, operand in ((numberOptions, "NUMBER"), (termOptions, "TERM")):
        for option in options:
            name, separator, token = option.partition("=")

            if not separator or not name or not token or name in values:
                raise _CommandError("usage", f"Expected a unique ID={operand} input: {option!r}.")

            values[name] = _ParseNumber(token) if operand == "NUMBER" else token

    return values


def _Arguments(arguments: Sequence[str]) -> argparse.Namespace:
    """Parse supported calculator commands and their syntax-level values."""

    parser = _ArgumentParser(prog="fuzzyroutines", allow_abbrev=False)
    parser.add_argument("--version", action="store_true", help="show the installed package version")
    commands = parser.add_subparsers(dest="command")

    for name in ("validate", "membership", "fuzzify", "infer"):
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument("--project", required=True, type=Path)

        if name != "validate":
            command.add_argument("--model")

        if name in ("membership", "fuzzify"):
            command.add_argument("--scale", required=True)
            command.add_argument("--x", required=True)

        if name == "membership":
            command.add_argument("--term", required=True)

        if name == "infer":
            command.add_argument("--evaluation")
            command.add_argument("--input", action="append", default=[])
            command.add_argument("--term-input", dest="termInput", action="append", default=[])
            command.add_argument("--encoding", choices=("representative-centroid",))
            command.add_argument("--explain", action="store_true")

    # argparse treats a negative exponent token as an option. Bind any valid
    # negative JSON number to --x before dispatching to the shared decoder.
    normalized = list(arguments)

    for index in range(len(normalized) - 1):
        token = normalized[index + 1]

        if normalized[index] == "--x" and token.startswith("-") and _NUMBER.fullmatch(token):
            normalized[index:index + 2] = [f"--x={token}"]
            break

    parsed = parser.parse_args(normalized)

    if parsed.version == (parsed.command is not None):
        raise _CommandError("usage", "Choose a command or --version.")

    if parsed.command in ("membership", "fuzzify"):
        parsed.x = _ParseNumber(parsed.x)

    if parsed.command == "infer":
        if bool(parsed.termInput) != (parsed.encoding is not None):
            raise _CommandError("usage", "--term-input and --encoding representative-centroid require each other.")

        parsed.input = _InputOptions(parsed.input, parsed.termInput)

    return parsed


def _Load(path: Path) -> ModelConfiguration:
    """Load one bounded standalone JSON file with lazy codec validation."""

    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        raise _CommandError("capability", "YAML project loading is not available in this command.")

    if suffix != ".json":
        raise _CommandError("configuration", f"Unsupported configuration suffix: {suffix!r}.")

    try:
        with path.open("rb") as source:
            encoded = source.read(_MAX_BYTES + 1)

    except OSError as error:
        raise _CommandError("io", str(error)) from error

    try:
        return LoadModel(encoded)

    except ImportError as error:
        raise _CommandError("capability", str(error)) from error


def _ScaleResult(command: argparse.Namespace, model: ModelConfiguration) -> dict[str, object]:
    """Return membership or ordered fuzzification evidence using wire IDs."""

    definition = model.scales.get(command.scale)

    if definition is None:
        raise _CommandError("usage", f"Unknown scale ID: {command.scale!r}.")

    terms = dict(zip(definition.termIds, definition.scale.terms, strict=True))
    result: dict[str, object] = {"scale": command.scale, "coordinate": command.x}

    if command.command == "membership":
        term = terms.get(command.term)

        if term is None:
            raise _CommandError("usage", f"Unknown term ID: {command.term!r}.")

        result.update(term=command.term, grade=float(term.fuzzySet.Membership(command.x)))

        return result

    fuzzified = definition.scale.Fuzzify(command.x, definition.fuzzification)
    idsByName = {term.name: termId for termId, term in terms.items()}
    result.update(
        memberships=[
            {"term": idsByName[item.term.name], "grade": float(item.grade)} for item in fuzzified.memberships
        ],
        confidence=float(fuzzified.confidence),
        tiedTerms=[idsByName[term.name] for term in fuzzified.tiedTerms],
        selectedTerms=[idsByName[term.name] for term in fuzzified.selectedTerms],
        match=fuzzified.isMatch,
    )

    return result


def _Representative(definition: ScaleDefinition, termName: str, inputId: str) -> float:
    """Encode an exact label using its declared scale windows and centroid policy."""

    representatives = definition.representatives

    if representatives is None:
        raise _CommandError("evaluation", f"Input {inputId!r} has no declared representative windows.")

    codec = LinguisticCodec(
        definition.scale, representatives.domains, definition.fuzzification or FuzzificationPolicy(),
        representatives.policy,
    )

    return float(codec.EncodeLabel(termName))


def _Infer(
    model: ModelConfiguration, values: dict[str, float | str], explain: bool,
) -> dict[str, object]:
    """Evaluate a standalone rule model and render its optional wire-ID trace."""

    binding = model.inference

    if binding is None:
        raise _CommandError("usage", "The selected model has no inference rules.")

    inputIds = {inputId for inputId, _ in binding.inputs}

    if values.keys() != inputIds:
        missing = sorted(inputIds - values.keys())
        unknown = sorted(values.keys() - inputIds)

        raise _CommandError("usage", f"Input IDs must match the model. Missing: {missing}; unknown: {unknown}.")

    variables = tuple(zip(binding.inputs, binding.model.inputs, strict=True))
    inputs: dict[str, float] = {}
    termBindings: list[tuple[str, ScaleDefinition, str, str]] = []

    for (inputId, scaleId), variable in variables:
        value = values[inputId]

        if isinstance(value, str):
            definition = model.scales[scaleId]
            termNames = {termId: term.name for termId, term in zip(definition.termIds, definition.scale.terms, strict=True)}
            termName = termNames.get(value)

            if termName is None:
                raise _CommandError("usage", f"Unknown term ID {value!r} for input {inputId!r}.")

            termBindings.append((variable.name, definition, termName, inputId))

        else:
            inputs[variable.name] = value

    for variableName, definition, termName, inputId in termBindings:
        inputs[variableName] = _Representative(definition, termName, inputId)

    evaluated: MamdaniResult | SugenoResult

    if isinstance(binding, MamdaniBinding):
        centroid = binding.centroid
        evaluated = binding.model.Evaluate(
            inputs, None if centroid is None else centroid.domain, None if centroid is None else centroid.policy,
        )
        kind = "mamdani"

    else:
        evaluated = binding.model.Evaluate(inputs)
        kind = "sugeno"

    result: dict[str, object] = {
        "kind": kind,
        "method": evaluated.method,
        "value": None if evaluated.value is None else float(evaluated.value),
    }

    if not explain:
        return result

    inputTerms = {
        (variable.name, term.name): (inputId, termId)
        for ((inputId, scaleId), variable) in variables
        for termId, term in zip(model.scales[scaleId].termIds, model.scales[scaleId].scale.terms, strict=True)
    }
    grades = []

    for item in evaluated.inputGrades:
        inputId, termId = inputTerms[(item.variable, item.term)]
        grades.append({"input": inputId, "term": termId, "grade": float(item.grade)})

    ruleTraces: Sequence[MamdaniRuleTrace | SugenoRuleTrace] = evaluated.rules
    rules = [
        {"rule": ruleId, "antecedentGrade": float(rule.antecedentGrade),
         "weight": float(rule.weight), "firingStrength": float(rule.firingStrength)}
        for ruleId, rule in zip(binding.ruleIds, ruleTraces, strict=True)
    ]

    if isinstance(evaluated, SugenoResult):
        for row, rule in zip(rules, evaluated.rules, strict=True):
            row.update(
                consequentValue=float(rule.consequentValue),
                normalizedStrength=float(rule.normalizedStrength),
                contribution=float(rule.contribution),
            )

    result["trace"] = {"inputGrades": grades, "rules": rules}

    return result


def _Dispatch(command: argparse.Namespace) -> dict[str, object]:
    """Load the document before resolving targets and running evaluation."""

    model = _Load(command.project)

    if command.command == "validate":
        return {"kind": "model", "schemaVersion": 1}

    if command.model is not None or getattr(command, "evaluation", None) is not None:
        raise _CommandError("usage", "Standalone models do not accept model or evaluation selectors.")

    if command.command == "infer":
        return _Infer(model, command.input, command.explain)

    return _ScaleResult(command, model)


def Main(arguments: Sequence[str] | None = None) -> int:
    """Run the standalone JSON command checkpoint and return its exit status."""

    try:
        command = _Arguments(sys.argv[1:] if arguments is None else arguments)

        if command.version:
            try:
                packageVersion = version("fuzzyroutines")

            except PackageNotFoundError:
                packageVersion = "(uninstalled)"

            print(f"fuzzyroutines {packageVersion}")

            return 0

        result = _Dispatch(command)
        _Write(sys.stdout, {"resultVersion": 1, "command": command.command, "result": result})

    except SystemExit as error:
        return int(error.code or 0)

    except _CommandError as error:
        _Write(sys.stderr, {"resultVersion": 1, "error": {"category": error.category, "message": str(error)}})

        return _EXIT_CODES[error.category]

    except ConfigurationError as error:
        _Write(sys.stderr, {"resultVersion": 1, "error": {
            "category": "configuration", "message": str(error),
            "detailCategory": error.category, "pointer": error.pointer,
        }})

        return _EXIT_CODES["configuration"]

    except FuzzyRoutinesError as error:
        _Write(sys.stderr, {"resultVersion": 1, "error": {"category": "evaluation", "message": str(error)}})

        return _EXIT_CODES["evaluation"]

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
