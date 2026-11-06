# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Local resources for the versioned configuration format."""

import json
from importlib import resources


def ReadConfigV1Schema() -> dict[str, object]:
    """Read a fresh copy of the canonical schema from the installed package.

    Returns:
        Trusted JSON Schema data shared by model and project validation.

    Raises:
        TypeError: The packaged schema root is not an object.
    """

    resource = resources.files("fuzzyroutines").joinpath("config-v1.schema.json")
    schema = json.loads(resource.read_bytes())

    if not isinstance(schema, dict):
        raise TypeError("The packaged v1 configuration schema must be an object.")

    return schema
