# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Replace documentation in Griffe's static model without modifying Python sources."""

import json
from pathlib import Path

from griffe import Extension

REDUNDANTINITIALIZERS = {
    "fuzzyroutines._legacy.membership.MFunction.__init__": "Initialize and validate a historical membership function.",
    "fuzzyroutines._legacy.sets.FuzzySet.__init__": "Initialize the historical mutable fuzzy-set wrapper.",
    "fuzzyroutines._legacy.scales.FuzzyScale.__init__": "Initialize the default three-level scale.",
    "fuzzyroutines._legacy.scales.UniversalFuzzyScale.__init__": "Initialize the fixed five-level universal scale.",
}


class LocaleDocstrings(Extension):
    """Apply source-validated translation fragments to authored object identities."""

    def __init__(self, *, translationMap):
        """Load one builder-produced mapping inside the isolated docs environment."""

        self.translations = json.loads(Path(translationMap).read_text(encoding="utf-8"))

    def on_instance(self, *, node, obj, agent, **kwargs):
        """Handle Griffe's upstream callback; signatures and source remain untouched."""

        translated = self.translations.get(obj.path)

        if obj.name == "__init__" and obj.parent.path in self.translations and obj.docstring is not None:
            # These four one-line summaries duplicate the translated class text.
            # Changed or newly authored constructor contracts must enter inventory.
            if obj.docstring.value.strip() != REDUNDANTINITIALIZERS.get(obj.path):
                raise ValueError(f"constructor documentation needs explicit translation inventory: {obj.path}")

            obj.docstring.value = ""
            return

        if translated is not None and obj.docstring is not None:
            obj.docstring.value = translated
