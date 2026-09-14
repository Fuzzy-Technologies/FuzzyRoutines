# Packaging and release notes

## 2.0.0 development baseline

The build baseline is intentionally separate from the mathematical
modernisation work. It adopts the PEP 517/518 build interface and stores the
canonical development version, `2.0.0.dev0`, in `pyproject.toml`.

- The package supports Python 3.9 and later.
- `setuptools.build_meta` is the build backend.
- `setup.py` remains only as a legacy command-line compatibility shim; it owns
  neither package metadata nor versioning.
- Routine CI must build and install artifacts but cannot publish a release.
- The former Travis deployment configuration is retained until its replacement
  is verified and Task #46 retires it.

### Local verification

```bash
python -m build
python -m pip install --force-reinstall dist/fuzzyroutines-2.0.0.dev0-py3-none-any.whl
python -c "from fuzzyroutines.FuzzyRoutines import MFunction; print(MFunction('triangle', a=0, b=1, c=0.5))"
```

The release process, tag creation, GitHub release evidence, and PyPI Trusted
Publishing belong to the later release milestone. This baseline does not
publish artifacts and does not alter mathematical behaviour.
