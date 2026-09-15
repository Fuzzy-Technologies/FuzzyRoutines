# -*- coding: utf-8 -*-


# FuzzyRoutines library contains some routines for work with fuzzy logic operators, fuzzy datasets and fuzzy scales.
# Copyright (C) 2019, Timur Gilmullin (DevOpsHQ)
# e-mail: tim55667757@gmail.com


import math
import copy


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


def _RequireFiniteReal(value, parameterName):
    """Return a finite real scalar or raise the public numeric-domain error."""

    if not IsNumber(value) or not math.isfinite(value):
        raise ValueError(f"{parameterName} must be a finite real number")

    return value


def _RequireFuzzyDegree(value, parameterName):
    """Return a finite scalar in the closed fuzzy-degree interval."""

    _RequireFiniteReal(value, parameterName)

    if not 0 <= value <= 1:
        raise ValueError(f"{parameterName} must be in the closed interval [0, 1]")

    return value


def FuzzyNOT(fuzzyNumber, alpha=0.5):
    """
    Fuzzy logic NOT operator. y = 1 - Fuzzy if alpha = 0.5
    """
    _RequireFuzzyDegree(fuzzyNumber, 'fuzzyNumber')

    if not IsNumber(alpha) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be a finite real number in the open interval (0, 1)")

    if fuzzyNumber <= alpha:
        return fuzzyNumber * (alpha - 1) / alpha + 1

    return (fuzzyNumber - 1) * alpha / (alpha - 1)


def FuzzyNOTParabolic(fuzzyNumber, alpha=0.5, epsilon=0.001):
    """
    Return the valid branch of 2a - x - y = (2a - 1)(y - x)^2.

    The strong-negation branch exists for alpha in [1/4, 3/4]. The epsilon
    argument is retained for source compatibility but is not part of the
    analytical solution and is deliberately ignored.
    """
    _RequireFuzzyDegree(fuzzyNumber, 'fuzzyNumber')

    if not IsNumber(alpha) or not math.isfinite(alpha) or not 0.25 <= alpha <= 0.75:
        raise ValueError("alpha must be a finite real number in the closed interval [1/4, 3/4]")

    if fuzzyNumber == 0:
        return 1.0

    if fuzzyNumber == 1:
        return 0.0

    if alpha <= 0.5:
        discriminant = (4 * alpha - 1) ** 2 + 8 * (1 - 2 * alpha) * fuzzyNumber

    else:
        discriminant = (4 * alpha - 3) ** 2 + 8 * (2 * alpha - 1) * (1 - fuzzyNumber)

    return fuzzyNumber + 4 * (alpha - fuzzyNumber) / (1 + math.sqrt(discriminant))


def FuzzyAND(aNumber, bNumber):
    """
    Fuzzy AND operator is minimum of two numbers.
    """
    _RequireFuzzyDegree(aNumber, 'aNumber')
    _RequireFuzzyDegree(bNumber, 'bNumber')
    return min(aNumber, bNumber)


def FuzzyOR(aNumber, bNumber):
    """
    Fuzzy OR operator is maximum of two numbers.
    """
    _RequireFuzzyDegree(aNumber, 'aNumber')
    _RequireFuzzyDegree(bNumber, 'bNumber')
    return max(aNumber, bNumber)


def TNorm(aFuzzyNumber, bFuzzyNumber, normType='logic'):
    """
    T-Norm conjunctive operators.
    normType is an operator's name:
        'logic' - result of fuzzy logic AND (min operator),
        'algebraic' - result of algebraic multiplication operation,
        'boundary' - result of boundary multiplication operation,
        'drastic' - result of drastic multiplication operation.
    """
    _RequireFuzzyDegree(aFuzzyNumber, 'aFuzzyNumber')
    _RequireFuzzyDegree(bFuzzyNumber, 'bFuzzyNumber')

    if normType == 'logic':
        return min(aFuzzyNumber, bFuzzyNumber)

    if normType == 'algebraic':
        return aFuzzyNumber * bFuzzyNumber

    if normType == 'boundary':
        return max(aFuzzyNumber + bFuzzyNumber - 1, 0)

    if normType == 'drastic':
        if aFuzzyNumber == 1:
            return bFuzzyNumber

        if bFuzzyNumber == 1:
            return aFuzzyNumber

        return 0

    raise ValueError(f"unknown t-norm family: {normType!r}")


def TNormCompose(*fuzzyNumbers, normType='logic'):
    """
    T-Norm compose of n numbers.
    normType is an operator's name:
        'logic' - result of fuzzy logic AND (min operator),
        'algebraic' - result of algebraic multiplication operation,
        'boundary' - result of boundary multiplication operation,
        'drastic' - result of drastic multiplication operation.
    """
    if normType not in ('logic', 'algebraic', 'boundary', 'drastic'):
        raise ValueError(f"unknown t-norm family: {normType!r}")

    if not fuzzyNumbers:
        raise ValueError("TNormCompose requires at least one fuzzy degree")

    for operandIndex, fuzzyNumber in enumerate(fuzzyNumbers):
        _RequireFuzzyDegree(fuzzyNumber, f'fuzzyNumbers[{operandIndex}]')

    result = fuzzyNumbers[0]

    for fuzzyNumber in fuzzyNumbers[1:]:
        result = TNorm(result, fuzzyNumber, normType)

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
    _RequireFuzzyDegree(aFuzzyNumber, 'aFuzzyNumber')
    _RequireFuzzyDegree(bFuzzyNumber, 'bFuzzyNumber')

    if normType == 'logic':
        return max(aFuzzyNumber, bFuzzyNumber)

    if normType == 'algebraic':
        return aFuzzyNumber + bFuzzyNumber - aFuzzyNumber * bFuzzyNumber

    if normType == 'boundary':
        return min(aFuzzyNumber + bFuzzyNumber, 1)

    if normType == 'drastic':
        if aFuzzyNumber == 0:
            return bFuzzyNumber

        if bFuzzyNumber == 0:
            return aFuzzyNumber

        return 1

    raise ValueError(f"unknown s-norm family: {normType!r}")


def SCoNormCompose(*fuzzyNumbers, normType='logic'):
    """
    S-coNorm compose of n numbers.
    normType is an operator's name:
        'logic' - result of fuzzy logic AND (min operator),
        'algebraic' - result of algebraic multiplication operation,
        'boundary' - result of boundary multiplication operation,
        'drastic' - result of drastic multiplication operation.
    """
    if normType not in ('logic', 'algebraic', 'boundary', 'drastic'):
        raise ValueError(f"unknown s-norm family: {normType!r}")

    if not fuzzyNumbers:
        raise ValueError("SCoNormCompose requires at least one fuzzy degree")

    for operandIndex, fuzzyNumber in enumerate(fuzzyNumbers):
        _RequireFuzzyDegree(fuzzyNumber, f'fuzzyNumbers[{operandIndex}]')

    result = fuzzyNumbers[0]

    for fuzzyNumber in fuzzyNumbers[1:]:
        result = SCoNorm(result, fuzzyNumber, normType)

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

        if userFunc not in self._functions:
            raise ValueError("unknown membership-function identifier: {!r}".format(userFunc))

        self.mju = self._functions[userFunc]  # Calculate result of define membership function
        self._parameters = self._ValidateParameters(membershipFunctionParams)

    def _ValidateParameters(self, parameters):
        """
        Validate and copy the exact parameter mapping for the selected family.

        Triangle keeps the historical ``a, b, c`` argument names: geometrically
        ``a`` is the left foot, ``c`` is the apex, and ``b`` is the right foot.
        """
        functionName = self.mju.__name__
        requiredParameters = {
            'Hyperbolic': ('a', 'b', 'c'),
            'Bell': ('a', 'b', 'c'),
            'Parabolic': ('a', 'b'),
            'Triangle': ('a', 'b', 'c'),
            'Trapezium': ('a', 'b', 'c', 'd'),
            'Exponential': ('a', 'b'),
            'Sigmoidal': ('a', 'b'),
            'Desirability': (),
        }[functionName]

        if not isinstance(parameters, dict) or set(parameters) != set(requiredParameters):
            raise ValueError(
                "{} membership function requires exactly these parameters: {}".format(
                    functionName,
                    ', '.join(requiredParameters) if requiredParameters else 'none',
                )
            )

        for parameterName in requiredParameters:
            parameterValue = parameters[parameterName]

            if not IsNumber(parameterValue) or not math.isfinite(parameterValue):
                raise ValueError(
                    "{} parameter {!r} must be a finite real number".format(
                        functionName,
                        parameterName,
                    )
                )

        if functionName == 'Hyperbolic':
            if parameters['a'] <= 0 or parameters['b'] <= 0:
                raise ValueError("Hyperbolic parameters must satisfy a > 0 and b > 0")

        elif functionName == 'Bell':
            if not parameters['a'] < parameters['b'] <= parameters['c']:
                raise ValueError("Bell parameters must satisfy a < b <= c")

        elif functionName == 'Parabolic':
            if not parameters['a'] < parameters['b']:
                raise ValueError("Parabolic parameters must satisfy a < b")

        elif functionName == 'Triangle':
            if not parameters['a'] < parameters['c'] <= parameters['b']:
                raise ValueError("Triangle parameters must satisfy a < c <= b")

        elif functionName == 'Trapezium':
            if not parameters['a'] < parameters['c'] <= parameters['d'] < parameters['b']:
                raise ValueError("Trapezium parameters must satisfy a < c <= d < b")

        elif functionName == 'Exponential':
            if parameters['b'] <= 0:
                raise ValueError("Exponential parameter b must satisfy b > 0")

        elif functionName == 'Sigmoidal':
            if parameters['a'] == 0:
                raise ValueError("Sigmoidal parameter a must be non-zero")

        return dict(parameters)

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
        self._parameters = self._ValidateParameters(value)

    def Hyperbolic(self, x):
        """
        This is hyperbolic membership function with real inputs x and parameters a, b, c.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']

        if x <= c:
            return 1

        return 1 / (1 + (a * (x - c)) ** b)

    def Bell(self, x):
        """
        This is bell membership function with real inputs x and parameters a, b, c.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']

        if x < b:
            return self.Parabolic(x)

        if x <= c:
            return 1

        rightBoundary = c + b - a
        rightMidpoint = (c + rightBoundary) / 2

        if x <= rightMidpoint:
            return 1 - (2 * (x - c) ** 2) / (rightBoundary - c) ** 2

        if x < rightBoundary:
            return (2 * (x - rightBoundary) ** 2) / (rightBoundary - c) ** 2

        return 0

    def Parabolic(self, x):
        """
        This is parabolic membership function with real inputs x and parameters a, b.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']

        if x <= a:
            return 0

        if x <= (a + b) / 2:
            return (2 * (x - a) ** 2) / (b - a) ** 2

        if x < b:
            return 1 - (2 * (x - b) ** 2) / (b - a) ** 2

        return 1

    def Triangle(self, x):
        """
        This is triangle membership function with real inputs x and parameters a, b, c.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']

        if x <= a:
            return 0

        if x <= c:
            return (x - a) / (c - a)

        if x < b:
            return (b - x) / (b - c)

        return 0

    def Trapezium(self, x):
        """
        This is trapezium membership function with real inputs x and parameters a, b, c, d.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        c = self._parameters['c']
        d = self._parameters['d']

        if x <= a:
            return 0

        if x < c:
            return (x - a) / (c - a)

        if x <= d:
            return 1

        if x <= b:
            return (b - x) / (b - d)

        return 0

    def Exponential(self, x):
        """
        This is exponential membership function with real inputs x and parameters a, b.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        scaledDistance = (x - a) / b
        return math.exp(-0.5 * scaledDistance * scaledDistance)

    def Sigmoidal(self, x):
        """
        This is sigmoidal membership function with real inputs x and parameters a, b.
        """
        _RequireFiniteReal(x, 'x')
        a = self._parameters['a']
        b = self._parameters['b']
        exponent = a * (x - b)

        # Algebraically equivalent branches avoid overflow in exp for large |x|.
        if exponent >= 0:
            return 1 / (1 + math.exp(-exponent))

        exponential = math.exp(exponent)
        return exponential / (1 + exponential)

    def Desirability(self, y):
        """
        This is Harrington's desirability membership function with real input y without any parameters.
        """
        _RequireFiniteReal(y, 'y')

        # Beyond this bound the inner exponential overflows while the
        # representable value of exp(-exp(-y)) is already exactly zero.
        if y < -math.log(float.fromhex('0x1.fffffffffffffp+1023')):
            return 0.0

        return math.exp(-math.exp(-y))


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
