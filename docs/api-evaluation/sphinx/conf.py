# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Sphinx configuration for the API-documentation comparison spike."""

import sys
from pathlib import Path

PROJECTROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECTROOT))

project = "FuzzyRoutines API evaluation"
author = "Fuzzy Technologies"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
html_theme = "alabaster"
html_theme_options = {
    "description": "Technologies · Knowledge · Science",
    "github_button": True,
    "github_repo": "FuzzyRoutines",
    "github_user": "Fuzzy-Technologies",
}
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
