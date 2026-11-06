# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Validate scientific plot output and publish complete encoded bytes."""

import errno
import os
import re
from collections.abc import Callable
from pathlib import Path
from stat import S_ISDIR
from tempfile import NamedTemporaryFile
from typing import Literal

from fuzzyroutines.exceptions import InvalidParameterError

type _PlotFormat = Literal["png", "jpeg", "svg"]

_SUFFIX_FORMATS: dict[str, _PlotFormat] = {
    ".png": "png",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".svg": "svg",
}


def _ResolvePlotFormat(
    destination: Path, formatName: str | None, background: str | None, transparent: bool,
) -> _PlotFormat:
    """Resolve the suffix and validate the normalized JPEG background option."""

    suffixFormat = _SUFFIX_FORMATS.get(destination.suffix.lower())

    if suffixFormat is None:
        raise InvalidParameterError(f"Unsupported plot output suffix: {destination}")

    if formatName is not None and _SUFFIX_FORMATS.get(f".{formatName.lower()}") != suffixFormat:
        raise InvalidParameterError(f"Plot format {formatName!r} disagrees with output suffix: {destination}")

    if suffixFormat == "jpeg":
        _RequireJpegBackground(background, transparent)

    return suffixFormat


def _RequireJpegBackground(background: str | None, transparent: bool) -> str:
    """Return the explicit opaque JPEG background after validating it."""

    if transparent:
        raise InvalidParameterError("JPEG does not support transparency.")

    if background is None or re.fullmatch(r"#[0-9a-fA-F]{6}", background) is None:
        raise InvalidParameterError("JPEG requires an explicit opaque #RRGGBB background.")

    return background


def _CheckDestination(destination: Path, overwrite: bool) -> None:
    """Reject a missing parent or an existing directory entry before rendering."""

    try:
        if not S_ISDIR(destination.parent.stat().st_mode):
            raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR))

    except OSError as error:
        raise OSError(error.errno, error.strerror, destination) from error

    if overwrite:
        return

    try:
        destination.lstat()

    except FileNotFoundError:
        return

    raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), destination)


def WritePlotExport(
    destination: Path,
    render: Callable[[_PlotFormat], bytes],
    *,
    formatName: str | None = None,
    background: str | None = None,
    transparent: bool = False,
    overwrite: bool = False,
) -> Path:
    """Render without a filename and publish a complete plot atomically.

    Args:
        destination: Explicit output filename with a supported suffix.
        render: Encoder receiving the resolved format and returning complete
            bytes. The caller binds its validated rendering options.
        formatName: Optional explicit format, which must match the suffix.
        background: Normalized opaque color for JPEG in `#RRGGBB` form.
        transparent: Whether to request transparent canvas and axes.
        overwrite: Whether to allow atomic replacement of the destination.

    Returns:
        The absolute destination used for publication.

    Raises:
        InvalidParameterError: If the suffix or format options are invalid.
        OSError: If the filesystem rejects staging or atomic publication,
            including a collision when overwrite is false.

    Notes:
        Rendering errors propagate before any staging write. No-overwrite
        publication uses a hard link, and fails closed on filesystems that
        cannot provide this operation.
    """

    target = destination.absolute()
    outputFormat = _ResolvePlotFormat(target, formatName, background, transparent)
    _CheckDestination(target, overwrite)
    encoded = render(outputFormat)
    staged: Path | None = None

    try:
        with NamedTemporaryFile(dir=target.parent, prefix=".fuzzy-plot-", delete=False) as stream:
            staged = Path(stream.name)
            stream.write(encoded)

        if overwrite:
            staged.replace(target)

        else:
            os.link(staged, target)

    except OSError as error:
        raise OSError(error.errno, error.strerror, target) from error

    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)

    return target
