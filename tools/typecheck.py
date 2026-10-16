# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Strict modern-source and installed-package static typing gates.

The default command checks the scalar modern scope in `mypy.ini`; `--extra numpy`
adds the optional batch module and consumer to the same strict configuration. The
installed mode copies consumer probes outside the checkout and requires an
installed package with a `py.typed` marker before checking their contracts.
Mypy diagnostics reach stdout and stderr unchanged; failures retain a nonzero
exit status. Temporary consumer copies and caches are removed on completion.
"""

import argparse
import configparser
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPTIONAL_SOURCES = {"numpy": ("fuzzyroutines/batches.py",)}


def ConsumerPaths(projectRoot: Path = PROJECT_ROOT, extras: Sequence[str] = ()) -> tuple[Path, ...]:
    """Return core consumers and explicitly selected optional consumers.

    Args:
        projectRoot: Checkout whose `tests/typing` directory supplies probes.
        extras: Optional dependency scopes selected by the caller.
    """

    consumerRoot = projectRoot / "tests" / "typing"
    paths = list(consumerRoot.glob("*.py"))

    for extra in extras:
        if extra not in OPTIONAL_SOURCES:
            raise ValueError(f"Unknown typing extra: {extra}")

        optionalPaths = tuple((consumerRoot / "optional" / extra).glob("*.py"))

        if not optionalPaths:
            raise ValueError(f"No typing consumers were found for extra: {extra}")

        paths.extend(optionalPaths)

    return tuple(sorted(set(paths)))


def CheckInstalled(projectRoot: Path = PROJECT_ROOT, extras: Sequence[str] = ()) -> int:
    """Check isolated consumers against the active installed package.

    Args:
        projectRoot: Checkout containing the checker configuration and probes.
        extras: Optional dependency consumers to include alongside core probes.

    Returns:
        Zero when the installed marker and every consumer contract pass;
        otherwise the failed subprocess status or one for an invalid boundary.
    """

    with TemporaryDirectory(prefix="fuzzyroutines-typing-") as temporaryDirectory:
        consumerRoot = Path(temporaryDirectory)
        checkerEnvironment = os.environ.copy()
        checkerEnvironment.pop("MYPYPATH", None)
        checkerEnvironment.pop("PYTHONPATH", None)
        installedProbe = subprocess.run(
            [
                sys.executable,
                "-I",
                "-c",
                "import fuzzyroutines; print(fuzzyroutines.__file__)",
            ],
            cwd=consumerRoot,
            env=checkerEnvironment,
            text=True,
            capture_output=True,
            check=False,
        )

        if installedProbe.returncode:
            print(installedProbe.stderr, file=sys.stderr, end="")

            return installedProbe.returncode

        packagePath = Path(installedProbe.stdout.strip()).resolve()

        if packagePath.is_relative_to(projectRoot.resolve()):
            print("Installed typing gate resolved the source checkout", file=sys.stderr)

            return 1

        if not packagePath.with_name("py.typed").is_file():
            print("Installed package is missing py.typed", file=sys.stderr)

            return 1

        consumers = ConsumerPaths(projectRoot, extras)

        if not consumers:
            print("No typing consumer probes were found", file=sys.stderr)

            return 1

        for consumer in consumers:
            shutil.copyfile(consumer, consumerRoot / consumer.name)

        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-m",
                "mypy",
                "--config-file",
                str(projectRoot / "mypy.ini"),
                "--no-incremental",
                "--cache-dir",
                str(consumerRoot / "cache"),
                *(str(consumerRoot / consumer.name) for consumer in consumers),
            ],
            cwd=consumerRoot,
            env=checkerEnvironment,
            check=False,
        )

        if result.returncode == 0:
            print(f"Installed modern typing consumers: PASS ({packagePath})")

        return result.returncode


def Main(arguments: Sequence[str] | None = None) -> int:
    """Run source or installed typing checks with the active interpreter.

    Args:
        arguments: Command arguments; `None` reads the process command line.

    Returns:
        The checker status, preserving failure diagnostics for CI.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--installed",
        action="store_true",
        help="check copied consumers outside the checkout against the installed package",
    )
    parser.add_argument(
        "--extra", action="append", choices=tuple(OPTIONAL_SOURCES), default=[],
        help="include an explicitly installed optional dependency scope",
    )
    options = parser.parse_args(arguments)

    if options.installed:
        return CheckInstalled(extras=options.extra)

    command = [sys.executable, "-m", "mypy", "--config-file", str(PROJECT_ROOT / "mypy.ini"), "--no-incremental"]

    if options.extra:
        configuration = configparser.ConfigParser()
        configuration.read(PROJECT_ROOT / "mypy.ini")
        targets = [target.strip() for target in configuration["mypy"]["files"].split(",")]

        for extra in options.extra:
            targets.extend(OPTIONAL_SOURCES[extra])

        targets.extend(str(path.relative_to(PROJECT_ROOT)) for path in ConsumerPaths(extras=options.extra))
        command.extend(dict.fromkeys(targets))

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(Main())
