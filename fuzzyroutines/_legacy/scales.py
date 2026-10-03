# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Historical mutable scale defaults and identity-preserving lookup adapters.

Uppercase lookup, last-wins ties including zero coverage, mutable dictionaries,
and the universal read-only property differ intentionally from modern scales.
Membership mathematics is owned by the modern core through the adapters."""

from fuzzyroutines._legacy.membership import MFunction
from fuzzyroutines._legacy.sets import FuzzySet


class FuzzyScale():
    """Represent the mutable three-level historical linguistic scale.

    Each level is a dictionary with a unique string `name` and an `fSet`
    containing a [FuzzySet][fuzzyroutines.FuzzyRoutines.FuzzySet]. The default
    scale contains `Min`, `Med`, and `High` levels.
    """

    def __init__(self):
        """Initialize the default three-level scale."""

        self._name = 'DefaultScale'  # default scale contains 3 levels, DefaultScale = {Min, Med, High}:

        self._levels = [{'name': 'Min',
                         'fSet': FuzzySet(membershipFunction=MFunction('hyperbolic', **{'a': 7, 'b': 4, 'c': 0}),
                                          supportSet=(0., 1.),
                                          linguisticName='Minimum')},
                        {'name': 'Med',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.35, 'b': 0.5, 'c': 0.6}),
                                          supportSet=(0., 1.),
                                          linguisticName='Medium')},
                        {'name': 'High',
                         'fSet': FuzzySet(membershipFunction=MFunction('triangle', **{'a': 0.7, 'b': 1, 'c': 1}),
                                          supportSet=(0., 1.),
                                          linguisticName='High')}]

        self._levelsNames = self._GetLevelsNames()  # dictionary with only levels' names
        self._levelsNamesUpper = self._GetLevelsNamesUpper()  # dictionary with only level's names in upper cases

    def __str__(self):
        """Return the historical multiline scale representation."""

        # return view of fuzzy scale - name = {**levels} and levels interpreter. Example:
        # DefaultScale = {Min, Med, High}
        #     Minimum = <Hyperbolic(x, {"a": 7, "b": 4, "c": 0}), [0.0, 1.0]>
        #     Medium = <Bell(x, {"a": 0.35, "b": 0.5, "c": 0.6}), [0.0, 1.0]>
        #     High = <Triangle(x, {"a": 0.7, "b": 1, "c": 1}), [0.0, 1.0]>
        all_levels_name = self._levels[0]['name']
        all_levels = '\n    {}'.format(self._levels[0]['fSet'].__str__())

        for level in self._levels[1:]:
            all_levels_name += ', {}'.format(level['name'])
            all_levels += '\n    {}'.format(str(level['fSet']))

        scale_view = '{} = {{{}}}{}'.format(self._name, all_levels_name, all_levels)

        return scale_view

    @property
    def name(self):
        """Return the scale name."""

        return self._name

    @name.setter
    def name(self, value):
        """Replace the scale name with a string value.

        Raises:
            Exception: If `value` is not a string.
        """

        if isinstance(value, str):
            self._name = value

        else:
            raise Exception("Name of Fuzzy Scale must be a string value!")

    @property
    def levels(self):
        """Return the mutable ordered list of level dictionaries."""

        return self._levels

    @levels.setter
    def levels(self, value):
        """Validate and replace the non-empty ordered level list.

        Raises:
            Exception: If the list is empty, a level has the wrong shape or
                value types.
            ValueError: If level names collide ignoring case.
        """

        if value:
            for level in value:
                if isinstance(level, dict) and set(level) == {'name', 'fSet'}:
                    if not isinstance(level['name'], str):
                        raise Exception("Level name - 'name' parameter - must be a string value!")

                    if not isinstance(level['fSet'], FuzzySet):
                        raise Exception("Fuzzy set - 'fSet' parameter - must be an instance of FuzzySet class!")

                else:
                    raise Exception("Level of fuzzy scale must be 2-dim dictionary looks like {'name': 'level_name', 'fSet': FuzzySet_instance}!")

            level_names = [level['name'].upper() for level in value]

            if len(set(level_names)) != len(level_names):
                raise ValueError("The scale contains level names that are not unique ignoring case!")

            self._levels = value  # set up new list of fuzzy levels
            self._levelsNames = self._GetLevelsNames()  # updating dictionary with only levels' names
            self._levelsNamesUpper = self._GetLevelsNamesUpper()  # updating dictionary with only level's names in upper cases

        else:
            raise Exception('Fuzzy scale must contain at least one linguistic variable!')

    def _GetLevelsNames(self):
        """
        Returns dictionary with only fuzzy levels' names and it's fuzzy set.
        Example: {'Min': <fSet_Object>, 'Med': <fSet_Object>, 'High': <fSet_Object>}
        """

        return dict([(x['name'], self._levels[lvl]) for lvl, x in enumerate(self._levels)])

    def _GetLevelsNamesUpper(self):
        """
        Returns dictionary with only fuzzy levels' names in upper cases and it's fuzzy set.
        Example: {'MIN': <fSet_Object>, 'MED': <fSet_Object>, 'HIGH': <fSet_Object>}
        """

        return dict([(x['name'].upper(), self._levels[lvl]) for lvl, x in enumerate(self._levels)])

    def Fuzzy(self, realValue):
        """Return the level with the greatest membership at `realValue`.

        Ties are resolved in favor of the later level in scale order.

        Args:
            realValue: Finite built-in `int` or `float` coordinate evaluated by
                every level membership function; `bool` is excluded.

        Returns:
            The selected mutable level dictionary.

        Raises:
            ValueError: If `realValue` is not a supported finite built-in
                number.
        """

        fuzzy_level = self._levels[0]
        fuzzy_membership = fuzzy_level['fSet'].mFunction.mju(realValue)

        for level in self._levels[1:]:
            level_membership = level['fSet'].mFunction.mju(realValue)

            if fuzzy_membership <= level_membership:
                fuzzy_level = level
                fuzzy_membership = level_membership

        return fuzzy_level

    def GetLevelByName(self, levelName, exactMatching=True):
        """Look up a level by its complete exact or case-insensitive name.

        Args:
            levelName: Name to retrieve.
            exactMatching: Use exact case when `True`; otherwise compare
                uppercase forms.

        Returns:
            The matching level dictionary, or `None` when absent.

        Notes:
            Case-insensitive lookup uses the historical uppercase-name map.
            Neither mode performs substring, prefix, or approximate matching.
        """

        if exactMatching:
            return self._levelsNames.get(levelName)

        else:
            return self._levelsNamesUpper.get(levelName.upper())


class UniversalFuzzyScale(FuzzyScale):
    """Represent the five-level historical universal scale without a setter.

    The ordered levels are `Min`, `Low`, `Med`, `High`, and `Max`. The inherited
    lookup and fuzzification methods remain available, while `levels` has no
    public setter on this subclass. The returned list, lookup dictionaries, and
    contained compatibility objects remain mutable.
    """

    def __init__(self):
        """Initialize the fixed five-level universal scale."""

        self._name = 'FuzzyScale'  # default universal fuzzy scale contains 5 levels, FuzzyScale = {Min, Low, Med, High, Max}:

        self._levels = [{'name': 'Min',
                         'fSet': FuzzySet(membershipFunction=MFunction('hyperbolic', **{'a': 8, 'b': 20, 'c': 0}),
                                          supportSet=(0., 0.23),
                                          linguisticName='Min')},
                        {'name': 'Low',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.17, 'b': 0.23, 'c': 0.34}),
                                          supportSet=(0.17, 0.4),
                                          linguisticName='Low')},
                        {'name': 'Med',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.34, 'b': 0.4, 'c': 0.6}),
                                          supportSet=(0.34, 0.66),
                                          linguisticName='Med')},
                        {'name': 'High',
                         'fSet': FuzzySet(membershipFunction=MFunction('bell', **{'a': 0.6, 'b': 0.66, 'c': 0.77}),
                                          supportSet=(0.6, 0.83),
                                          linguisticName='High')},
                        {'name': 'Max',
                         'fSet': FuzzySet(membershipFunction=MFunction('parabolic', **{'a': 0.77, 'b': 0.95}),
                                          supportSet=(0.77, 1.),
                                          linguisticName='Max')}]

        self._levelsNames = self._GetLevelsNames()  # dictionary with only universal fuzzy scale levels' names
        self._levelsNamesUpper = self._GetLevelsNamesUpper()  # dictionary with only level's names in upper cases

    @property
    def levels(self):
        """Return the ordered universal-scale level list."""

        return self._levels  # only readable levels and it's fuzzy set for Universal Fuzzy Scale

    @property
    def levelsNames(self):
        """Return the exact-name lookup dictionary."""

        return self._levelsNames  # only levels' names of Universal Fuzzy Scale

    @property
    def levelsNamesUpper(self):
        """Return the uppercase-name lookup dictionary."""

        return self._levelsNamesUpper  # only levels' names of Universal Fuzzy Scale in upper cases
