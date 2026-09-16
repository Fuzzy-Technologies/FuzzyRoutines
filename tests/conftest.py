"""Provide process-safe test resources for the FuzzyRoutines suite."""

from __future__ import annotations

import socket
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass(frozen=True)
class ReservedTcpPort:
    """Keep an ephemeral TCP port reserved until the owning test releases it."""

    port: int
    reservation: socket.socket

    def Close(self) -> None:
        """Release the reservation exactly when the test is ready to bind it."""

        self.reservation.close()


@pytest.fixture(autouse=True)
def isolatedStateRoot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Give every test an isolated temporary and mutable-state root."""

    stateRoot = tmp_path / "state"
    tempRoot = tmp_path / "temp"
    stateRoot.mkdir()
    tempRoot.mkdir()
    previousTempRoot = tempfile.tempdir
    tempfile.tempdir = str(tempRoot)
    monkeypatch.setenv("FUZZYROUTINES_TEST_STATE_ROOT", str(stateRoot))
    monkeypatch.setenv("FUZZYROUTINES_TEST_DATABASE", str(stateRoot / "test.sqlite3"))
    monkeypatch.setenv("TMPDIR", str(tempRoot))
    monkeypatch.setenv("TEMP", str(tempRoot))
    monkeypatch.setenv("TMP", str(tempRoot))

    try:
        yield stateRoot

    finally:
        tempfile.tempdir = previousTempRoot


@pytest.fixture
def isolatedDatabasePath(isolatedStateRoot: Path) -> Path:
    """Return a unique database path owned by the current test."""

    return isolatedStateRoot / "test.sqlite3"


@pytest.fixture
def reservedPortFactory() -> Iterator[Callable[[], ReservedTcpPort]]:
    """Reserve unique loopback TCP ports without a discover-then-bind race."""

    reservations: list[ReservedTcpPort] = []

    def Reserve() -> ReservedTcpPort:
        reservation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        reservation.bind(("127.0.0.1", 0))
        reservedPort = ReservedTcpPort(
            port=reservation.getsockname()[1],
            reservation=reservation,
        )
        reservations.append(reservedPort)
        return reservedPort

    try:
        yield Reserve

    finally:
        for reservedPort in reservations:
            reservedPort.reservation.close()
