# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Strict modern-source and installed-package static typing gates.

The default command checks the explicit modern scope in `mypy.ini`. The
installed mode copies consumer probes outside the checkout and requires an
installed package with a `py.typed` marker before checking their contracts.
Mypy diagnostics reach stdout and stderr unchanged; failures retain a nonzero
exit status. Temporary consumer copies and caches are removed on completion.
"""

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ConsumerPaths(projectRoot: Path = PROJECT_ROOT) -> tuple[Path, ...]:
    """Return every static consumer probe, including future additions.

    Args:
        projectRoot: Checkout whose `tests/typing` directory supplies probes.
    """

    return tuple(sorted((projectRoot / "tests" / "typing").glob("*.py")))


def CheckInstalled(projectRoot: Path = PROJECT_ROOT) -> int:
    """Check isolated consumers against the active installed package.

    Args:
        projectRoot: Checkout containing the checker configuration and probes.

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

        consumers = ConsumerPaths(projectRoot)

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
    options = parser.parse_args(arguments)

    if options.installed:
        return CheckInstalled()

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--config-file", str(PROJECT_ROOT / "mypy.ini"), "--no-incremental"],
        cwd=PROJECT_ROOT,
        check=False,
    )

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(Main())
