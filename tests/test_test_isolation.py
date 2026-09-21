# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Invariant tests for reusable process-safe test resources."""

import os
import tempfile
from pathlib import Path


def test_EveryTestReceivesAnIsolatedStateAndDatabaseRoot(isolatedStateRoot, isolatedDatabasePath):
    assert isolatedStateRoot.exists()
    assert isolatedDatabasePath.parent == isolatedStateRoot
    assert os.environ["FUZZYROUTINES_TEST_STATE_ROOT"] == str(isolatedStateRoot)
    assert os.environ["FUZZYROUTINES_TEST_DATABASE"] == str(isolatedDatabasePath)
    assert Path(tempfile.gettempdir()).parent == isolatedStateRoot.parent


def test_ReservedPortsRemainUniqueWhileHeld(reservedPortFactory):
    firstReservation = reservedPortFactory()
    secondReservation = reservedPortFactory()

    assert firstReservation.port != secondReservation.port
    assert firstReservation.reservation.fileno() >= 0
    assert secondReservation.reservation.fileno() >= 0
