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


def ConsumerPaths(project_root: Path = PROJECT_ROOT) -> tuple[Path, ...]:
    """Return every static consumer probe, including future additions.

    Args:
        project_root: Checkout whose `tests/typing` directory supplies probes.
    """

    return tuple(sorted((project_root / "tests" / "typing").glob("*.py")))


def CheckInstalled(project_root: Path = PROJECT_ROOT) -> int:
    """Check isolated consumers against the active installed package.

    Args:
        project_root: Checkout containing the checker configuration and probes.

    Returns:
        Zero when the installed marker and every consumer contract pass;
        otherwise the failed subprocess status or one for an invalid boundary.
    """

    with TemporaryDirectory(prefix="fuzzyroutines-typing-") as temporary_directory:
        consumer_root = Path(temporary_directory)
        checker_environment = os.environ.copy()
        checker_environment.pop("MYPYPATH", None)
        checker_environment.pop("PYTHONPATH", None)
        installed_probe = subprocess.run(
            [
                sys.executable,
                "-I",
                "-c",
                "import fuzzyroutines; print(fuzzyroutines.__file__)",
            ],
            cwd=consumer_root,
            env=checker_environment,
            text=True,
            capture_output=True,
            check=False,
        )

        if installed_probe.returncode:
            print(installed_probe.stderr, file=sys.stderr, end="")

            return installed_probe.returncode

        package_path = Path(installed_probe.stdout.strip()).resolve()

        if package_path.is_relative_to(project_root.resolve()):
            print("Installed typing gate resolved the source checkout", file=sys.stderr)

            return 1

        if not package_path.with_name("py.typed").is_file():
            print("Installed package is missing py.typed", file=sys.stderr)

            return 1

        consumers = ConsumerPaths(project_root)

        if not consumers:
            print("No typing consumer probes were found", file=sys.stderr)

            return 1

        for consumer in consumers:
            shutil.copyfile(consumer, consumer_root / consumer.name)

        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-m",
                "mypy",
                "--config-file",
                str(project_root / "mypy.ini"),
                "--no-incremental",
                "--cache-dir",
                str(consumer_root / "cache"),
                *(str(consumer_root / consumer.name) for consumer in consumers),
            ],
            cwd=consumer_root,
            env=checker_environment,
            check=False,
        )

        if result.returncode == 0:
            print(f"Installed modern typing consumers: PASS ({package_path})")

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
