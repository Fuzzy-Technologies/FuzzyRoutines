# Packaging modernization notes

This document tracks the packaging migration scope.

The initial step introduces modern PEP 517/518 metadata through `pyproject.toml` while preserving the existing runtime package layout.

No mathematical behavior, public API, or legacy compatibility contract is changed by this step.

Follow-up work will cover build validation, wheel/sdist checks, CI publishing and Trusted Publishing.
