# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic checks for format validation and atomic plot output."""

import errno
from pathlib import Path

import pytest

from fuzzyroutines._plot_export import WritePlotExport
from fuzzyroutines.exceptions import InvalidParameterError


@pytest.fixture(name="outputRoot")
def OutputRoot(tmpPath: Path) -> Path:
    """Create an empty destination separate from pytest state and temp data."""

    directory = tmpPath / "plots"
    directory.mkdir()
    return directory


def _Encode(formatName: str) -> bytes:
    """Return path-independent test bytes for the selected format."""

    return formatName.encode("ascii")


@pytest.mark.parametrize(
    ("suffix", "formatName", "background", "expected"),
    [
        (".PNG", None, None, b"png"),
        (".JpG", "JPEG", "#ffffff", b"jpeg"),
        (".jpeg", "jpg", "#ABC123", b"jpeg"),
        (".SVG", "svg", None, b"svg"),
    ],
)
def test_EncodeUsingExplicitOutputFormat(outputRoot, suffix, formatName, background, expected):
    """Resolve the format case-insensitively without passing filenames to the encoder."""

    parent = outputRoot / "review figures \u6e29\u5ea6"
    parent.mkdir()
    first = parent / f"first{suffix}"
    second = parent / f"second{suffix}"

    assert WritePlotExport(first, _Encode, formatName=formatName, background=background) == first
    WritePlotExport(second, _Encode, formatName=formatName, background=background)

    assert first.read_bytes() == second.read_bytes() == expected
    assert set(parent.iterdir()) == {first, second}, "Staging files must be removed after success."


@pytest.mark.parametrize(
    ("filename", "options", "message"),
    [
        ("plot", {}, "Unsupported plot output suffix"),
        ("plot.png", {"formatName": "gif"}, "disagrees with output suffix"),
        ("plot.png", {"formatName": "svg"}, "disagrees with output suffix"),
        ("plot.jpg", {}, "explicit opaque"),
        ("plot.jpg", {"background": "#ffffff00"}, "explicit opaque"),
        ("plot.jpg", {"background": "#ffffff", "transparent": True}, "does not support transparency"),
    ],
)
def test_InvalidFormatNeverRenders(outputRoot, filename, options, message):
    """Reject bad format or JPEG options before calling the encoder."""

    def UnexpectedRender(formatName: str) -> bytes:
        """Fail if validation allows rendering."""

        pytest.fail(f"Invalid export requested {formatName} encoding.")

    with pytest.raises(InvalidParameterError, match=message):
        WritePlotExport(outputRoot / filename, UnexpectedRender, **options)

    assert not list(outputRoot.iterdir()), "An invalid request must leave the directory empty."


def test_PreservePreviousFileOnRenderError(outputRoot):
    """Keep the previous bytes when rendering fails with overwrite requested."""

    destination = outputRoot / "existing.svg"
    destination.write_bytes(b"previous")

    def FailedRender(formatName: str) -> bytes:
        """Simulate a deterministic encoder failure."""

        raise RuntimeError(f"Failed to encode {formatName}.")

    with pytest.raises(RuntimeError, match="Failed to encode svg"):
        WritePlotExport(destination, FailedRender, overwrite=True)

    assert destination.read_bytes() == b"previous", "A failed render must not truncate the old file."
    assert list(outputRoot.iterdir()) == [destination], "A failed render must not leave staging files."

    WritePlotExport(destination, _Encode, overwrite=True)

    assert destination.read_bytes() == b"svg", "Successful overwrite must replace the old bytes."


def test_RejectDestinationCreatedDuringRendering(outputRoot):
    """Fail atomically when another writer wins after preflight."""

    destination = outputRoot / "race.png"

    def ConcurrentRender(formatName: str) -> bytes:
        """Place the other writer's result before returning the new bytes."""

        destination.write_bytes(b"other writer")
        return _Encode(formatName)

    with pytest.raises(FileExistsError) as failure:
        WritePlotExport(destination, ConcurrentRender)

    assert Path(failure.value.filename) == destination
    assert destination.read_bytes() == b"other writer", "A race must preserve the winning file."
    assert list(outputRoot.iterdir()) == [destination], "A collision must remove the staging file."


def test_RejectPreflightFileErrors(outputRoot):
    """Report the requested target for an existing file or a missing parent."""

    existing = outputRoot / "existing.svg"
    existing.write_bytes(b"previous")
    missing = outputRoot / "missing" / "plot.svg"

    def UnexpectedRender(formatName: str) -> bytes:
        """Fail if an output preflight error allows rendering."""

        pytest.fail(f"Unwritable output requested {formatName} encoding.")

    with pytest.raises(FileExistsError) as collision:
        WritePlotExport(existing, UnexpectedRender)

    with pytest.raises(FileNotFoundError) as absent:
        WritePlotExport(missing, UnexpectedRender)

    assert Path(collision.value.filename) == existing
    assert Path(absent.value.filename) == missing
    assert existing.read_bytes() == b"previous"
    assert list(outputRoot.iterdir()) == [existing]


def test_StageIsCleanedIfAtomicPublicationFails(outputRoot, monkeypatch):
    """Preserve destination absence and report its path after a link failure."""

    destination = outputRoot / "plot.svg"

    def RejectLink(source: Path, target: Path) -> None:
        """Simulate a filesystem without hard-link support."""

        assert source.read_bytes() == b"svg", "Publication must only see complete data."
        assert target == destination, "Publication must target the requested path."
        raise OSError(errno.EPERM, "Link not supported", source)

    monkeypatch.setattr("fuzzyroutines._plot_export.os.link", RejectLink)

    with pytest.raises(PermissionError) as failure:
        WritePlotExport(destination, _Encode)

    assert Path(failure.value.filename) == destination
    assert not list(outputRoot.iterdir()), "A rejected publication must remove the staging file."
