# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Replace documentation in Griffe's static model without modifying Python sources."""

import json
from pathlib import Path

from griffe import Extension


class LocaleDocstrings(Extension):
    """Apply source-validated translation fragments to authored object identities."""

    def __init__(self, *, translationMap):
        """Load one builder-produced mapping inside the isolated docs environment."""

        self.translations = json.loads(Path(translationMap).read_text(encoding="utf-8"))

    def on_instance(self, *, node, obj, agent, **kwargs):
        """Handle Griffe's upstream callback; signatures and source remain untouched."""

        translated = self.translations.get(obj.path)

        if translated is not None and obj.docstring is not None:
            obj.docstring.value = translated
