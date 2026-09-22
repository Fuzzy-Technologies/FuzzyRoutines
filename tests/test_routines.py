# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Historical unit tests retained for compatibility evidence."""

import pytest
from fuzzyroutines.FuzzyRoutines import *


class TestBaseMethods():

    def test_DiapasonParser(self):
        testData = [
            # positive tests:
            ["1", [1]],
            ["1,5", [1, 5]],
            ["1-5", [1, 2, 3, 4, 5]],
            ["8-10, 1-5, 6", [1, 2, 3, 4, 5, 6, 8, 9, 10]],
            ["11, 11, 12, 12, 1-5, 3-7", [1, 2, 3, 4, 5, 6, 7, 11, 12]],
            # negative tests:
            [12345, []],
            ["", []],
            ["-", []],
            ["1-", []],
            [",", []],
            ["1,", []],
        ]
        for test in testData:
            assert DiapasonParser(test[0]) == test[1], 'Input: [ {} ] expected output: [ {} ]'.format(test[0], test[1])

    def test_IsNumber(self):
        testData = [
            # positive tests:
            [-1, True],
            [0, True],
            [1, True],
            [-2., True],
            [2., True],
            # negative tests:
            ['0', False],
            [True, False],
            [False, False],
            ['1', False],
            ['-2.', False],
            [[], False],
            [self, False],
        ]
        for test in testData:
            assert IsNumber(test[0]) is test[1], 'Input: [ {} ] expected output: [ {} ]'.format(test[0], test[1])

    def test_IsCorrectFuzzyNumberValue(self):
        testData = [
            # positive tests:
            [0, True],
            [0.5, True],
            [1, True],
            # negative tests:
            [-1.5, False],
            [1.5, False],
            ['0', False],
            [True, False],
            ['True', False],
            [False, False],
            ['False', False],
            [[], False],
            [self, False],
        ]
        for test in testData:
            assert IsCorrectFuzzyNumberValue(test[0]) is test[1], 'Input: [ {} ] expected output: [ {} ]'.format(test[0], test[1])

    def test_FuzzyNOT(self):
        # positive tests:
        testDataPositive = [
            [0., 0.5, 1.],
            [0.5, 0.5, 0.5],
            [1., 0.5, 0.],
            [0.25, 0.25, 0.25],
            [0.25, 0.75, 0.9166666666666666],
        ]
        for test in testDataPositive:
            assert FuzzyNOT(test[0], alpha=test[1]) == test[2], 'Input: [ {}, alpha={} ] expected output: [ {} ]'.format(test[0], test[1], test[2])

        for fuzzyNumber, alpha in [(1.1, 0.5), (-1.1, 0.5), (1.1, 0.25), (-1.1, 0.25)]:
            with pytest.raises(ValueError):
                FuzzyNOT(fuzzyNumber, alpha=alpha)

    def test_FuzzyNOTParabolic(self):
        # positive tests:
        testDataPositive = [
            [0., 0.5, 0.001, 1.],
            [0.5, 0.5, 0.001, 0.5],
            [1., 0.5, 0.001, 0.],
            [0., 0.25, 0., 1.],
            [0., 0.25, 1., 1.],
            [1., 0.25, 0., 0.],
            [1., 0.25, 1., 0.],
            [0., 0.75, 0., 1.],
            [1., 0.75, 1., 0.],
        ]
        for test in testDataPositive:
            assert round(FuzzyNOTParabolic(test[0], alpha=test[1], epsilon=test[2]), 5) == test[3], 'Input: [ {}, alpha={}, epsilon={} ] expected output: [ {} ]'.format(test[0], test[1], test[2], test[3])

        for fuzzyNumber in [-1.0, 2.0]:
            with pytest.raises(ValueError):
                FuzzyNOTParabolic(fuzzyNumber, alpha=0.5, epsilon=0.001)

    def test_FuzzyAND(self):
        # positive tests:
        testDataPositive = [
            [0., 0., 0.],
            [0., 1., 0.],
            [1., 0., 0.],
            [1., 1., 1.],
            [0.5, 0.6, 0.5],
            [0.7, 0.5, 0.5],
        ]
        for test in testDataPositive:
            assert FuzzyAND(test[0], test[1]) == test[2], 'Input: [ {}, {} ] expected output: [ {} ]'.format(test[0], test[1], test[2])

        # negative tests:
        testDataNegative = [
            [None, None, None],
            [self, 0., None],
            [[], 1., None],
            ['0.', '0.', None],
        ]
        for test in testDataNegative + [[-1., 0., None], [0., -1., None], [2., 2., None]]:
            with pytest.raises(ValueError):
                FuzzyAND(test[0], test[1])

    def test_FuzzyOR(self):
        # positive tests:
        testDataPositive = [
            [0., 0., 0.],
            [0., 1., 1.],
            [1., 0., 1.],
            [1., 1., 1.],
            [0.5, 0.6, 0.6],
            [0.7, 0.5, 0.7],
        ]
        for test in testDataPositive:
            assert FuzzyOR(test[0], test[1]) == test[2], 'Input: [ {}, {} ] expected output: [ {} ]'.format(test[0], test[1], test[2])

        # negative tests:
        testDataNegative = [
            [None, None, None],
            [self, 0., None],
            [[], 1., None],
            ['0.', '0.', None],
        ]
        for test in testDataNegative + [[-1., 0., None], [0., -1., None], [2., 2., None]]:
            with pytest.raises(ValueError):
                FuzzyOR(test[0], test[1])

    def test_TNorm(self):
        # positive tests:
        testDataPositive = [
            [0., 0., 'logic', 0.],
            [0., 1., 'logic', 0.],
            [1., 0., 'logic', 0.],
            [1., 1., 'logic', 1.],
            [0.5, 0.6, 'logic', 0.5],
            [0.6, 0.5, 'logic', 0.5],
            [0., 0., 'algebraic', 0.],
            [0., 1., 'algebraic', 0.],
            [1., 0., 'algebraic', 0.],
            [1., 1., 'algebraic', 1.],
            [0.5, 0.6, 'algebraic', 0.3],
            [0., 0., 'boundary', 0.],
            [0., 1., 'boundary', 0.],
            [1., 0., 'boundary', 0.],
            [1., 1., 'boundary', 1.],
            [0.5, 0.5, 'boundary', 0.],
            [0.6, 0.6, 'boundary', 0.2],
            [0., 0., 'drastic', 0.],
            [0., 1., 'drastic', 0.],
            [1., 0., 'drastic', 0.],
            [1., 1., 'drastic', 1.],
            [0.5, 0.5, 'drastic', 0.],
            [1., 0.6, 'drastic', 0.6],
            [0.7, 1., 'drastic', 0.7],
        ]
        for test in testDataPositive:
            assert round(TNorm(test[0], test[1], normType=test[2]), 5) == test[3], 'Input: [ {}, {}, normType={} ] expected output: [ {} ]'.format(test[0], test[1], test[2], test[3])

        # negative tests:
        testDataNegative = [
            [-1., 0., 'logic', None],
            [0., -1., 'logic', None],
            ["1.", 0., 'logic', None],
            [1., "1.", 'logic', None],
            [0.5, None, 'logic', None],
            [self, 0.5, 'logic', None],
            [1., [], 'logic', None],
            [-1., 0., 'algebraic', None],
            [0., -1., 'algebraic', None],
            ["1.", 0., 'algebraic', None],
            [1., "1.", 'algebraic', None],
            [0.5, None, 'algebraic', None],
            [self, 0.6, 'algebraic', None],
            [1., [], 'algebraic', None],
            [-1., 0., 'boundary', None],
            [0., -1., 'boundary', None],
            ["1.", 0., 'boundary', None],
            [1., "1.", 'boundary', None],
            [0.5, None, 'boundary', None],
            [self, 0.6, 'boundary', None],
            [1., [], 'boundary', None],
            [-1., 0., 'drastic', None],
            [0., -1., 'drastic', None],
            ["1.", 0., 'drastic', None],
            [1., "1.", 'drastic', None],
            [0.5, None, 'drastic', None],
            [self, 0.6, 'drastic', None],
            [1., [], 'drastic', None],
        ]
        for test in testDataNegative:
            with pytest.raises(ValueError):
                TNorm(test[0], test[1], normType=test[2])

    def test_TNormCompose(self):
        # positive tests:
        testDataPositive = [
            [0.1, 0.2, 0.3, 'logic', 0.1],
            [0.1, 0.2, 0.3, 'algebraic', 0.006],
            [0.9, 0.9, 0.9, 'boundary', 0.7],
            [0.1, 0.2, 1., 'drastic', 0.],
        ]
        for test in testDataPositive:
            assert round(TNormCompose(test[0], test[1], test[2], normType=test[3]), 5) == test[4], 'Input: [ {}, {}, {}, normType={} ] expected output: [ {} ]'.format(test[0], test[1], test[2], test[3], test[4])

        # negative tests:
        testDataNegative = [
            [[], None],
            [None, None],
            ['0.1', None],
            [self, None],
        ]
        for test in testDataNegative:
            with pytest.raises(ValueError):
                TNormCompose(test[0])

    def test_SCoNorm(self):
        # positive tests:
        testDataPositive = [
            [0., 0., 'logic', 0.],
            [0., 1., 'logic', 1.],
            [1., 0., 'logic', 1.],
            [1., 1., 'logic', 1.],
            [0.5, 0.6, 'logic', 0.6],
            [0.7, 0.6, 'logic', 0.7],
            [0., 0., 'algebraic', 0.],
            [0., 1., 'algebraic', 1.],
            [1., 0., 'algebraic', 1.],
            [1., 1., 'algebraic', 1.],
            [0.5, 0.6, 'algebraic', 0.8],
            [0., 0., 'boundary', 0.],
            [0., 1., 'boundary', 1.],
            [1., 0., 'boundary', 1.],
            [1., 1., 'boundary', 1.],
            [0.5, 0.5, 'boundary', 1.],
            [0.6, 0.6, 'boundary', 1.],
            [0., 0., 'drastic', 0.],
            [0., 1., 'drastic', 1.],
            [1., 0., 'drastic', 1.],
            [1., 1., 'drastic', 1.],
            [0.5, 0.5, 'drastic', 1.],
            [1., 0.6, 'drastic', 1.],
            [0.7, 1., 'drastic', 1.],
        ]
        for test in testDataPositive:
            assert round(SCoNorm(test[0], test[1], normType=test[2]), 5) == test[3], 'Input: [ {}, {}, normType={} ] expected output: [ {} ]'.format(test[0], test[1], test[2], test[3])

        # negative tests:
        testDataNegative = [
            [-1., 0., 'logic', None],
            [0., -1., 'logic', None],
            ["1.", 0., 'logic', None],
            [1., "1.", 'logic', None],
            [0.5, None, 'logic', None],
            [self, 0.5, 'logic', None],
            [1., [], 'logic', None],
            [-1., 0., 'algebraic', None],
            [0., -1., 'algebraic', None],
            ["1.", 0., 'algebraic', None],
            [1., "1.", 'algebraic', None],
            [0.5, None, 'algebraic', None],
            [self, 0.6, 'algebraic', None],
            [1., [], 'algebraic', None],
            [-1., 0., 'boundary', None],
            [0., -1., 'boundary', None],
            ["1.", 0., 'boundary', None],
            [1., "1.", 'boundary', None],
            [0.5, None, 'boundary', None],
            [self, 0.6, 'boundary', None],
            [1., [], 'boundary', None],
            [-1., 0., 'drastic', None],
            [0., -1., 'drastic', None],
            ["1.", 0., 'drastic', None],
            [1., "1.", 'drastic', None],
            [0.5, None, 'drastic', None],
            [self, 0.6, 'drastic', None],
            [1., [], 'drastic', None],
        ]
        for test in testDataNegative:
            with pytest.raises(ValueError):
                SCoNorm(test[0], test[1], normType=test[2])

    def test_SCoNormCompose(self):
        # positive tests:
        testDataPositive = [
            [0.1, 0.2, 0.3, 'logic', 0.3],
            [0.1, 0.5, 0.5, 'algebraic', 0.775],
            [0.5, 0.4, 0.05, 'boundary', 0.95],
            [0.1, 0.2, 0.3, 'drastic', 1.],
        ]
        for test in testDataPositive:
            assert round(SCoNormCompose(test[0], test[1], test[2], normType=test[3]), 5) == test[4], 'Input: [ {}, {}, {}, normType={} ] expected output: [ {} ]'.format(test[0], test[1], test[2], test[3], test[4])

        # negative tests:
        testDataNegative = [
            [[], None],
            [None, None],
            ['0.1', None],
            [self, None],
        ]
        for test in testDataNegative:
            with pytest.raises(ValueError):
                SCoNormCompose(test[0])
