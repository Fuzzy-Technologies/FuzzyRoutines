# -*- coding: utf-8 -*-


# FuzzyRoutines library contains some routines for work with fuzzy logic operators, fuzzy datasets and fuzzy scales.
# Copyright (C) 2019, Timur Gilmullin (DevOpsHQ)
# e-mail: tim55667757@gmail.com


import math
import copy
import traceback


def DiapasonParser(diapason):
    """
    Parse input with diapason string and return sorted list of full and unique indexes in that diapason.
    Examples:
        String "1,5" converted to: [1, 5]
        String "1-5" converted to: [1, 2, 3, 4, 5]
        String "8-10, 1-5, 6" converted to: [1, 2, 3, 4, 5, 6, 8, 9, 10]
        String "11, 11, 12, 12, 1-5, 3-7" converted to: [1, 2, 3, 4, 5, 6, 7, 11, 12]
    """
    fullDiapason = []

    try:
        for element in diapason.split(','):
            fullDiapason += [x for x in range(int(element.split('-')[0]), int(element.split('-')[-1]) + 1)]

    except Exception:
        print('"{}" is not correct diapason string!'.format(diapason))
        return []

    return sorted(list(set(fullDiapason)))


def IsNumber(value):
    """
    Return True if value is float or integer number.
    """
    return bool(not isinstance(value, bool) and (isinstance(value, int) or isinstance(value, float)))


def IsCorrectFuzzyNumberValue(value):
    """
    All operations in fuzzy logic are executed with numbers in interval [0, 1].
    """
    if IsNumber(value):
        return (0. <= value) and (value <= 1.)

    else:
        print('{} not a real number in [0, 1], type = {}'.format(str(value), type(value)))
        return False


def FuzzyNOT(fuzzyNumber, alpha=0.5):
    """
    Fuzzy logic NOT operator. y = 1 - Fuzzy if alpha = 0.5
    """
    if not IsNumber(alpha) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be a finite real number in the open interval (0, 1)")

    result = None  # return None if errors

    if IsCorrectFuzzyNumberValue(fuzzyNumber):
        if (0 <= fuzzyNumber) and (fuzzyNumber <= alpha):
            result = fuzzyNumber * (alpha - 1) / alpha + 1

        else:
            result = (fuzzyNumber - 1) * alpha / (alpha - 1)

    return result


def FuzzyNOTParabolic(fuzzyNumber, alpha=0.5, epsilon=0.001):
    """
    Parabolic fuzzy NOT operator. 2a - x - y = (2a - 1)(y - x)^2.
    """
    result = None  # return None if errors

    if IsCorrectFuzzyNumberValue(fuzzyNumber) and IsCorrectFuzzyNumberValue(alpha) and IsCorrectFuzzyNumberValue(epsilon) and alpha > 0:
        if fuzzyNumber == 0:
            result = 1

        elif fuzzyNumber == 1:
            result = 0

        else:
            y = 0
            while (y <= 1) and abs((2 * alpha - fuzzyNumber - y) - (2 * alpha - 1) * (y - fuzzyNumber) ** 2) >= epsilon / 2:
                y += epsilon
            result = y

    return result


def FuzzyAND(aNumber, bNumber):
    """
    Fuzzy AND operator is minimum of two numbers.
    """
    if IsNumber(aNumber) and IsNumber(bNumber):
        return min(aNumber, bNumber)

    else:
        return None  # return None if errors


def FuzzyOR(aNumber, bNumber):
    """
    Fuzzy OR operator is maximum of two numbers.
    """
    if IsNumber(aNumber) and IsNumber(bNumber):
        return max(aNumber, bNumber)

    else:
        return None  # return None if errors


def TNorm(aFuzzyNumber, bFuzzyNumber, normType='logic'):
    """
    T-Norm conjunctive operators.
    normType is an operator's name:
        'logic' - result of fuzzy logic AND (min operator),
        'algebraic' - result of algebraic multiplication operation,
        'boundary' - result of boundary multiplication operation,
        'drastic' - result of drastic multiplication operation.
    """
    result = None  # return None if errors

    if IsCorrectFuzzyNumberValue(aFuzzyNumber) and IsCorrectFuzzyNumberValue(bFuzzyNumber):
        if normType == 'logic':
            result = FuzzyAND(aFuzzyNumber, bFuzzyNumber)

        if normType == 'algebraic':
            result = aFuzzyNumber * bFuzzyNumber

        if normType == 'boundary':
            result = FuzzyOR(aFuzzyNumber + bFuzzyNumber - 1, 0)

        if normType == 'drastic':
            if aFuzzyNumber == 1:
                result = bFuzzyNumber

            elif bFuzzyNumber == 1:
                result = aFuzzyNumber

            else:
                result = 0

    return result


def TNormCompose(*fuzzyNumbers, normType='logic'):
    """
    T-Norm compose of n numbers.
    normType is an operator's name:
        'logic' - result of fuzzy logic AND (min operator),
        'algebraic' - result of algebraic multiplication operation,
        'boundary' - result of boundary multiplication operation,
        'drastic' - result of drastic multiplication operation.
    """
    result = None  # return None if errors

    if normType not in ('logic', 'algebraic', 'boundary', 'drastic'):
        return result

    if len(fuzzyNumbers) >= 1 and all(IsCorrectFuzzyNumberValue(fuzzyNumber) for fuzzyNumber in fuzzyNumbers):
        result = fuzzyNumbers[0]

        for f in fuzzyNumbers[1:]:
            result = TNorm(result, f, normType)

    return result


def SCoNorm(aFuzzyNumber, bFuzzyNumber, normType='logic'):
    """
    S-coNorm disjunctive operators.
    normType is an operator's name:
        'logic' - result of fuzzy logic OR (max operator),
        'algebraic' - result of algebraic addition operation,
        'boundary' - result of boundary addition operation,
        'drastic' - result of drastic addition operation.
    """
    result = None  # return None if errors

    if IsCorrectFuzzyNumberValue(aFuzzyNumber) and IsCorrectFuzzyNumberValue(bFuzzyNumber):
        if normType == 'logic':
            result = FuzzyOR(aFuzzyNumber, bFuzzyNumber)

        if normType == 'algebraic':
            result = aFuzzyNumber + bFuzzyNumber - aFuzzyNumber * bFuzzyNumber

        if normType == 'boundary':
            result = FuzzyAND(aFuzzyNumber + bFuzzyNumber, 1)

        if normType == 'drastic':
            if aFuzzyNumber == 0:
                result = bFuzzyNumber

            elif bFuzzyNumber == 0:
                result = aFuzzyNumber

            else:
                result = 1

    return result


def SCoNormCompose(*fuzzyNumbers, normType='logic'):
    """
    S-coNorm compose of n numbers.
    normType is an operator's name:
        'logic' - result of fuzzy logic AND (min operator),
        'algebraic' - result of algebraic multiplication operation,
        'boundary' - result of boundary multiplication operation,
        'drastic' - result of drastic multiplication operation.
    """
    result = None  # return None if errors

    if normType not in ('logic', 'algebraic', 'boundary', 'drastic'):
        return result

    if len(fuzzyNumbers) >= 1 and all(IsCorrectFuzzyNumberValue(fuzzyNumber) for fuzzyNumber in fuzzyNumbers):
        result = fuzzyNumbers[0]

        for f in fuzzyNumbers[1:]:
            result = SCoNorm(result, f, normType)

    return result


class MFunction():
    """
    Routines for work with some default membership functions.
    """

    def __init__(self, userFunc, **membershipFunctionParams):
        self.accuracy = 1000  # Line of numbers divided by points, affect on accuracy, using in integral calculating
        self._functions = {'hyperbolic': self.Hyperbolic,
                           'bell': self.Bell,
                           'parabolic': self.Parabolic,
                           'triangle': self.Triangle,
                           'trapezium': self.Trapezium,
                           'exponential': self.Exponential,
                           'sigmoidal': self.Sigmoidal,
                           'desirability': self.Desirability}  # Factory registrator for all membership functions
        self.mju = self._functions[userFunc]  # Calculate result of define membership function

        if membershipFunctionParams or self.mju.__name__ == 'Desirability':
            self._parameters = membershipFunctionParams  # parameters for using in membership function

        else:
            raise Exception("You must specify all membership function's parameters!")

    @property
    def name(self):
        return self.mju.__name__  # membership function method name

    def __str__(self):
        # return view of function: Function_name(**parameters). Example: Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}
        funcView = '{}({})'.format(self.name, 'y' if self.name == 'Desirability' else 'x, {}'.format(
            '{' + ', '.join('"{}": {}'.format(*val) for val in [(k, self._parameters[k])
                                                                for k in sorted(self._parameters)]) + '}'))
        return funcView

    @property
    def parameters(self):
        return self._parameters  # all membership function parameters

    @parameters.setter
    def parameters(self, value):
        if value or self.mju.__name__ == 'Desirability':
            self._parameters = value

        else:
            raise Exception("You must specify all membership function's parameters!")

    def Hyperbolic(self, x):
        """
        This is hyperbolic membership function with real inputs x and parameters a, b, c.
        """
        a, b, c, result = 0, 0, 0, 0

        try:
            a = self._parameters['a']
            b = self._parameters['b']
            c = self._parameters['c']

            if x <= c:
                result = 1

            else:
                result = 1 / (1 + (a * (x - c)) ** b)

        except Exception:
            print(traceback.format_exc())
            print('Hyperbolic membership function use real inputs x and parameters a, b, c.')
            print('Your inputs: mju_hyperbolic({}, {}, {}, {})'.format(x, a, b, c))
            return 0

        return result

    def Bell(self, x):
        """
        This is bell membership function with real inputs x and parameters a, b, c.
        """
        a, b, c, result = 0, 0, 0, 0

        try:
            a = self._parameters['a']
            b = self._parameters['b']
            c = self._parameters['c']

            if x < b:
                result = self.Parabolic(x)

            elif (b <= x) and (x <= c):
                result = 1

            else:
                rightBoundary = c + b - a
                rightMidpoint = (c + rightBoundary) / 2

                if x <= rightMidpoint:
                    result = 1 - (2 * (x - c) ** 2) / (rightBoundary - c) ** 2

                elif x < rightBoundary:
                    result = (2 * (x - rightBoundary) ** 2) / (rightBoundary - c) ** 2

                else:
                    result = 0

        except Exception:
            print(traceback.format_exc())
            print('Bell membership function use real inputs x and parameters a, b, c.')
            print('Your inputs: mju_bell({}, {}, {}, {})'.format(x, a, b, c))
            return 0

        return result

    def Parabolic(self, x):
        """
        This is parabolic membership function with real inputs x and parameters a, b.
        """
        a, b, result = 0, 0, 0

        try:
            a = self._parameters['a']
            b = self._parameters['b']

            if x <= a:
                result = 0

            elif (a < x) and (x <= (a + b) / 2):
                result = (2 * (x - a) ** 2) / (b - a) ** 2

            elif ((a + b) / 2 < x) and (x < b):
                result = 1 - (2 * (x - b) ** 2) / (b - a) ** 2

            else:
                result = 1

        except Exception:
            print(traceback.format_exc())
            print('Parabolic membership function use real inputs x and parameters a, b.')
            print('Your inputs: mju_parabolic({}, {}, {})'.format(x, a, b))
            return 0

        return result

    def Triangle(self, x):
        """
        This is triangle membership function with real inputs x and parameters a, b, c.
        """
        a, b, c, result = 0, 0, 0, 0

        try:
            a = self._parameters['a']
            b = self._parameters['b']
            c = self._parameters['c']

            if x <= a:
                result = 0

            elif (a < x) and (x <= c):
                result = (x - a) / (c - a)

            elif (c < x) and (x < b):
                result = (b - x) / (b - c)

            else:
                result = 0

        except Exception:
            print(traceback.format_exc())
            print('Triangle membership function use real inputs x and parameters a, b, c.')
            print('Your inputs: mju_triangle({}, {}, {}, {})'.format(x, a, b, c))
            return 0

        return result

    def Trapezium(self, x):
        """
        This is trapezium membership function with real inputs x and parameters a, b, c, d.
        """
        a, b, c, d, result = 0, 0, 0, 0, 0

        try:
            a = self._parameters['a']
            b = self._parameters['b']
            c = self._parameters['c']
            d = self._parameters['d']

            if x < a:
                result = 0

            elif (a < x) and (x < c):
                result = (x - a) / (c - a)

            elif (c <= x) and (x <= d):
                result = 1

            elif (d < x) and (x <= b):
                result = (b - x) / (b - d)

            else:
                result = 0

        except Exception:
            print(traceback.format_exc())
            print('Trapezium membership function use real inputs x and parameters a, b, c, d.')
            print('Your inputs: mju_trapezium({}, {}, {}, {}, {})'.format(x, a, b, c, d))
            return 0

        return result

    def Exponential(self, x):
        """
        This is exponential membership function with real inputs x and parameters a, b.
        """
        a, b, result = 0, 0, 0

        try:
            a = self._parameters['a']
            b = self._parameters['b']

            if b != 0:
                result = math.exp(1) ** (-0.5 * ((x - a) / b) ** 2)

        except Exception:
            print(traceback.format_exc())
            print('Exponential membership function use real inputs x and parameters a, b.')
            print('Your inputs: mju_exponential({}, {}, {})'.format(x, a, b))
            return 0

        return result

    def Sigmoidal(self, x):
        """
        This is sigmoidal membership function with real inputs x and parameters a, b.
        """
        a, b, result = 0, 0, 0

        try:
            a = self._parameters['a']
            b = self._parameters['b']

            result = 1 / (1 + math.exp(1) ** (-a * (x - b)))

        except Exception:
            print(traceback.format_exc())
            print('Sigmoidal membership function use real inputs x and parameters a, b.')
            print('Your inputs: mju_sigmoidal({}, {}, {})'.format(x, a, b))
            return 0

        return result

    def Desirability(self, y):
        """
        This is Harrington's desirability membership function with real input y without any parameters.
        """
        try:
            result = math.exp(-math.exp(-y))

        except Exception:
            print(traceback.format_exc())
            print("Harrington's desirability membership function use only real input y without any parameters.")
            print('Your inputs: mju_desirability({})'.format(y))
            return 0

        return result


class FuzzySet():
    """
    Routines for work with fuzzy sets.
    Fuzzy set A = <membershipFunction, supportSet>
    """

    def __init__(self, membershipFunction, supportSet=(0., 1.), linguisticName='FuzzySet'):
        if isinstance(linguisticName, str):
            self._name = linguisticName

        else:
            raise Exception("Linguistic name of Fuzzy Set must be a string value!")

        if isinstance(membershipFunction, MFunction):
            self._mFunction = membershipFunction  # instance of MembershipFunction class

        else:
            raise Exception('Not MFunction class instance was given!')

        if isinstance(supportSet, tuple) and (len(supportSet) == 2) and (supportSet[0] < supportSet[1]):
            self._supportSet = supportSet  # support set of given membership function

        else:
            raise Exception('Support Set must be 2-dim tuple (a, b) with real a, b parameters, a < b!')

        self._defuzValue = None

    def __str__(self):
        # return view of fuzzy set - name = <mju(x|y, params), supportSet>. Example: FuzzySet = <Bell(x, a, b), [0, 1]>
        fSetView = '{} = <{}, [{}, {}]>'.format(self._name, self._mFunction, self._supportSet[0], self._supportSet[1])
        return fSetView

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value

        else:
            raise Exception("Linguistic name of Fuzzy Set must be a string value!")

    @property
    def mFunction(self):
        return self._mFunction  # current membership

    @mFunction.setter
    def mFunction(self, value):
        if isinstance(value, MFunction):
            self._mFunction = value

        else:
            raise Exception('Not MFunction class instance was given!')

    @property
    def supportSet(self):
        return self._supportSet

    @supportSet.setter
    def supportSet(self, value):
        if isinstance(value, tuple) and (len(value) == 2) and (value[0] < value[1]):
            self._supportSet = value  # new support set of given membership function

        else:
            raise Exception('Support Set must be 2-dim tuple (a, b) with real a, b parameters, a < b!')

    @property
    def defuzValue(self):
        self._defuzValue = self._Defuz()
        return self._defuzValue

    def _Defuz(self):
        """
        Defuzzyfication function returns real value in support set of given fuzzy set using "center of gravity method".
        Integrals in this method calculated from left to right border of support set of membership function.
        Integrals are approximately calculated by Newton-Leibniz formula.
        """
        left = self._supportSet[0]
        right = self._supportSet[1]
        step = (right - left) / self._mFunction.accuracy

        numeratorIntegral = 0
        denominatorIntegral = 0

        for iteration in range(self._mFunction.accuracy):
            x = left + (iteration + 1) * step
            mjuValue = self._mFunction.mju(x)

            numeratorIntegral += x * mjuValue
            denominatorIntegral += mjuValue

        return numeratorIntegral / denominatorIntegral

    def Defuz(self):
        """
        This function now used for backward compatibility.
        """
        return self.defuzValue


class FuzzyScale():
    """
    Routines for work with fuzzy scales. Fuzzy scale is an ordered set of linguistic variables.
    Fuzzy scale contains named levels and its MF. This object looks like this:
    S = [{'name': 'name_1', 'fSet': fuzzySet_1},
         {'name': 'name_2', 'fSet': fuzzySet_2}, ...]
        where name-key is a linguistic name of fuzzy set,
        fSet-key is a user define fuzzy set, an instance of FuzzySet class.
    """

    def __init__(self):
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
        # return view of fuzzy scale - name = {**levels} and levels interpreter. Example:
        # DefaultScale = {Min, Med, High}
        #     Minimum = <Hyperbolic(x, {"a": 7, "b": 4, "c": 0}), [0.0, 1.0]>
        #     Medium = <Bell(x, {"a": 0.35, "b": 0.5, "c": 0.6}), [0.0, 1.0]>
        #     High = <Triangle(x, {"a": 0.7, "b": 1, "c": 1}), [0.0, 1.0]>
        allLevelsName = self._levels[0]['name']
        allLevels = '\n    {}'.format(self._levels[0]['fSet'].__str__())

        for level in self._levels[1:]:
            allLevelsName += ', {}'.format(level['name'])
            allLevels += '\n    {}'.format(str(level['fSet']))

        scaleView = '{} = {{{}}}{}'.format(self._name, allLevelsName, allLevels)

        return scaleView

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value

        else:
            raise Exception("Name of Fuzzy Scale must be a string value!")

    @property
    def levels(self):
        return self._levels

    @levels.setter
    def levels(self, value):
        if value:
            for level in value:
                if isinstance(level, dict) and (len(level) == 2) and ('name' and 'fSet' in level.keys()):
                    if not isinstance(level['name'], str):
                        raise Exception("Level name - 'name' parameter - must be a string value!")

                    if not isinstance(level['fSet'], FuzzySet):
                        raise Exception("Fuzzy set - 'fSet' parameter - must be an instance of FuzzySet class!")

                    nameCount = 0  # check for unique name:
                    for otherLevel in value:
                        if otherLevel['name'] == level['name']:
                            nameCount += 1

                    if nameCount > 1:
                        raise Exception("The scale contains no unique levels! Warning for: {}".format(level['name']))

                else:
                    raise Exception("Level of fuzzy scale must be 2-dim dictionary looks like {'name': 'level_name', 'fSet': FuzzySet_instance}!")

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
        """
        Fuzzyfication function returns one of levels on fuzzy scale for given real value who MF(value) are highest.
        """
        fuzzyLevel = self._levels[0]
        fuzzyMembership = fuzzyLevel['fSet'].mFunction.mju(realValue)

        for level in self._levels[1:]:
            levelMembership = level['fSet'].mFunction.mju(realValue)

            if fuzzyMembership <= levelMembership:
                fuzzyLevel = level
                fuzzyMembership = levelMembership

        return fuzzyLevel

    def GetLevelByName(self, levelName, exactMatching=True):
        """
        Function return fuzzy level as dictionary level = {'name': 'level_name', 'fSet': fuzzySet}
        exactMatching is a flag for exact matching search,
            if True then levelName must be equal to level['name'],
            otherwise - level['name'] in uppercase must contains levelName in uppercase.
        """
        if exactMatching:
            return self._levelsNames.get(levelName)

        else:
            return self._levelsNamesUpper.get(levelName.upper())


class UniversalFuzzyScale(FuzzyScale):
    """
    Iniversal fuzzy scale S_f = {Min, Low, Med, High, Max}. Example view:
    FuzzyScale = {Min, Low, Med, High, Max}
        Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
        Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
        Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
        High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
        Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>
    """

    def __init__(self):
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
        return self._levels  # only readable levels and it's fuzzy set for Universal Fuzzy Scale

    @property
    def levelsNames(self):
        return self._levelsNames  # only levels' names of Universal Fuzzy Scale

    @property
    def levelsNamesUpper(self):
        return self._levelsNamesUpper  # only levels' names of Universal Fuzzy Scale in upper cases


if __name__ == "__main__":
    pass
