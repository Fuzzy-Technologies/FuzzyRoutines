# FuzzyRoutines
Library contains some routines for work with fuzzy logic operators, fuzzy datasets and fuzzy scales.


*Index:*
- [Install](#Chapter_1)
- [Usage examples](#Chapter_2)
    - [Work with membership functions](#Chapter_2_1)
    - [Work with fuzzy set](#Chapter_2_2)
    - [Work with fuzzy scales](#Chapter_2_3)
    - [Work with Universal Fuzzy Scale](#Chapter_2_4)
    - [Work with fuzzy logic operators](#Chapter_2_5)
    - [Working with other methods](#Chapter_2_6)

<a name="Chapter_1"></a>Install
-------------------------------

You can install FuzzyRoutines using pip:

    pip install fuzzyroutines [--upgrade] [--pre]
    
or using setuptools to build local version:

    git clone https://github.com/devopshq/FuzzyRoutines.git
    cd FuzzyRoutines
    python setup.py install

After installing you can check the version of the FuzzyRoutines library:

    pip show fuzzyroutines


<a name="Chapter_2"></a>Usage examples
--------------------------------------

You can see and run Example.py script:

    cd fuzzyroutines
    python Examples.py

Example.py contains some examples of working with fuzzy library. Just copying and run examples below. Do not forget to import FuzzyRoutines module before use:

    from fuzzyroutines.FuzzyRoutines import *


<a name="Chapter_2_1"></a>***Work with membership functions***

Usage of some membership functions:

    mjuPars = {'a': 7, 'b': 4, 'c': 0}  # hyperbolic params example
    funct = MFunction(userFunc='hyperbolic', **mjuPars)  # creating instance of hyperbolic function
    print('Printing Membership function with parameters: ', funct)
    
    mjuPars = {'a': 0, 'b': 0.3, 'c': 0.4}  # bell params example
    funct = MFunction(userFunc='bell', **mjuPars)  # creating instance of bell function
    print('Printing Membership function with parameters: ', funct)
    
    mjuPars = {'a': 0, 'b': 1}  # parabolic params example
    funct = MFunction(userFunc='parabolic', **mjuPars)  # creating instance of parabolic function
    print('Printing Membership function with parameters: ', funct)
    
    mjuPars = {'a': 0.2, 'b': 0.8, 'c': 0.7}  # triangle params example
    funct = MFunction(userFunc='triangle', **mjuPars)  # creating instance of triangle function
    print('Printing Membership function with parameters: ', funct)
    
    mjuPars = {'a': 0.5, 'b': 0.15}  # exponential params example
    funct = MFunction(userFunc='exponential', **mjuPars)  # creating instance of exponential function
    print('Printing Membership function with parameters: ', funct)
    
    mjuPars = {'a': 15, 'b': 0.5}  # sigmoidal params example
    funct = MFunction(userFunc='sigmoidal', **mjuPars)  # creating instance of sigmoidal function
    print('Printing Membership function with parameters: ', funct)
    
    funct = MFunction(userFunc='desirability')  # creating instance of desirability function without parameters
    print('Printing Membership function with parameters: ', funct)
    
    mjuPars = {'a': 0.1, 'b': 1, 'c': 0.5, 'd': 0.8}  # trapezium params example
    funct = MFunction(userFunc='trapezium', **mjuPars)  # creating instance of trapezium function
    print('Printing Membership function with parameters: ', funct)

Output:

    Printing Membership function with parameters:  Hyperbolic(x, {"a": 7, "b": 4, "c": 0})
    Printing Membership function with parameters:  Bell(x, {"a": 0, "b": 0.3, "c": 0.4})
    Printing Membership function with parameters:  Parabolic(x, {"a": 0, "b": 1})
    Printing Membership function with parameters:  Triangle(x, {"a": 0.2, "b": 0.8, "c": 0.7})
    Printing Membership function with parameters:  Exponential(x, {"a": 0.5, "b": 0.15})
    Printing Membership function with parameters:  Sigmoidal(x, {"a": 15, "b": 0.5})
    Printing Membership function with parameters:  Desirability(y)
    Printing Membership function with parameters:  Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8})


Calculating Trapezium function's values in [0, 1]:

    xPar = 0
    for i in range(0, 10, 1):
        xPar = (xPar + i) / 10
        res = funct.mju(xPar)  # calculate one value of MF with given parameters
        print('x = {:.1f}, {} = {:1.4f}'.format(xPar, funct, res))

Output:

    x = 0.0, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.0000
    x = 0.1, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.0000
    x = 0.2, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.2750
    x = 0.3, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.5525
    x = 0.4, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.8302
    x = 0.5, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 1.0000
    x = 0.7, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 1.0000
    x = 0.8, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 1.0000
    x = 0.9, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.6173
    x = 1.0, Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}) = 0.0617


<a name="Chapter_2_2"></a>***Work with fuzzy set***

    fuzzySet = FuzzySet(funct, (0., 1.))  # creating fuzzy set A = <mju_funct, support_set>
    print('Printing fuzzy set after init and before changes:', fuzzySet)
    print('Defuz({}) = {:1.2f}'.format(fuzzySet.name, fuzzySet.Defuz()))
    
    changedMjuPars = copy.deepcopy(mjuPars)  # change parameters of membership function with deepcopy example:
    changedMjuPars['a'] = 0
    changedMjuPars['b'] = 1
    changedSupportSet = (0.5, 1)  # change support set
    fuzzySet.name = 'Changed fuzzy set'
    
    fuzzySet.mFunction.parameters = changedMjuPars
    fuzzySet.supportSet = changedSupportSet
    
    print('New membership function with parameters: ', fuzzySet.mFunction)
    print('New support set: ', fuzzySet.supportSet)
    print('New value of Defuz({}) = {:1.2f}'.format(fuzzySet.name, fuzzySet.Defuz()))
    print('Printing fuzzy set after changes:', fuzzySet)

Output:

    Printing fuzzy set after init and before changes: FuzzySet = <Trapezium(x, {"a": 0.1, "b": 1, "c": 0.5, "d": 0.8}), [0.0, 1.0]>
    Defuz(FuzzySet) = 0.59
    New membership function with parameters:  Trapezium(x, {"a": 0, "b": 1, "c": 0.5, "d": 0.8})
    New support set:  (0.5, 1)
    New value of Defuz(Changed fuzzy set) = 0.59
    Printing fuzzy set after changes: Changed fuzzy set = <Trapezium(x, {"a": 0, "b": 1, "c": 0.5, "d": 0.8}), [0.5, 1]>


<a name="Chapter_2_3"></a>***Work with fuzzy scales***

Fuzzy scale is an ordered set of linguistic variables that looks like this:

S = [{'name': 'name_1', 'fSet': fuzzySet_1}, {'name': 'name_2', 'fSet': fuzzySet_2}, ...]

where name is a linguistic name of fuzzy set, fSet is a user define fuzzy set of FuzzySet type.

    scale = FuzzyScale()  # intialize new fuzzy scale with default levels
    
    print('Printing default fuzzy scale in human-readable:', scale)
    
    print('Defuz() of all default levels:')
    for item in scale.levels:
        print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

Output:

    Printing default fuzzy scale in human-readable: DefaultScale = {Min, Med, High}
        Minimum = <Hyperbolic(x, {"a": 7, "b": 4, "c": 0}), [0.0, 1.0]>
        Medium = <Bell(x, {"a": 0.35, "b": 0.5, "c": 0.6}), [0.0, 1.0]>
        High = <Triangle(x, {"a": 0.7, "b": 1, "c": 1}), [0.0, 1.0]>
    Defuz() of all default levels:
    Defuz(Min) = 0.10
    Defuz(Med) = 0.55
    Defuz(High) = 0.90

Add new fuzzy levels:

    print('Define some new levels:')
    
    minFunct = MFunction('hyperbolic', **{'a': 2, 'b': 20, 'c': 0})
    levelMin = FuzzySet(membershipFunction=minFunct, supportSet=(0., 0.5), linguisticName='min')
    print('Printing Level 1 in human-readable:', levelMin)
    
    medFunct = MFunction('bell', **{'a': 0.4, 'b': 0.55, 'c': 0.7})
    levelMed = FuzzySet(membershipFunction=medFunct, supportSet=(0.25, 0.75), linguisticName='med')
    print('Printing Level 2 in human-readable:', levelMed)
    
    maxFunct = MFunction('triangle', **{'a': 0.65, 'b': 1, 'c': 1})
    levelMax = FuzzySet(membershipFunction=maxFunct, supportSet=(0.7, 1.), linguisticName='max')
    print('Printing Level 3 in human-readable:', levelMax)

Output:

    Define some new levels:
    Printing Level 1 in human-readable: min = <Hyperbolic(x, {"a": 2, "b": 20, "c": 0}), [0.0, 0.5]>
    Printing Level 2 in human-readable: med = <Bell(x, {"a": 0.4, "b": 0.55, "c": 0.7}), [0.25, 0.75]>
    Printing Level 3 in human-readable: max = <Triangle(x, {"a": 0.65, "b": 1, "c": 1}), [0.7, 1.0]>

Change scale levels:

    scale.name = 'New Scale'
    scale.levels = [{'name': levelMin.name, 'fSet': levelMin}, {'name': levelMed.name, 'fSet': levelMed},
                    {'name': levelMax.name, 'fSet': levelMax}]  # add new ordered set of linguistic variables into scale
    
    print('Changed List of levels as objects:', scale.levels)
    print('Printing changed fuzzy scale in human-readable:', scale)
    
    print('Defuz() of all New Scale levels:')
    for item in scale.levels:
        print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

Output:

    Changed List of levels as objects: [{'name': 'min', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB3F17B8>}, {'name': 'med', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB337D68>}, {'name': 'max', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB3F18D0>}]
    Printing changed fuzzy scale in human-readable: New Scale = {min, med, max}
        min = <Hyperbolic(x, {"a": 2, "b": 20, "c": 0}), [0.0, 0.5]>
        med = <Bell(x, {"a": 0.4, "b": 0.55, "c": 0.7}), [0.25, 0.75]>
        max = <Triangle(x, {"a": 0.65, "b": 1, "c": 1}), [0.7, 1.0]>
    Defuz() of all New Scale levels:
    Defuz(min) = 0.24
    Defuz(med) = 0.61
    Defuz(max) = 0.89


<a name="Chapter_2_4"></a>***Work with Universal Fuzzy Scale***

Universal fuzzy scales S_f = {Min, Low, Med, High, Max} pre-defined in UniversalFuzzyScale() class.

    uniFScale = UniversalFuzzyScale()
    print('Levels of Universal Fuzzy Scale:', uniFScale.levels)
    print('Printing scale:', uniFScale)

    print('Defuz() of all Universal Fuzzy Scale levels:')
    for item in uniFScale.levels:
        print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

Output:

    Levels of Universal Fuzzy Scale: [{'name': 'Min', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB34F7B8>}, {'name': 'Low', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB34F198>}, {'name': 'Med', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB34F048>}, {'name': 'High', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB34F0F0>}, {'name': 'Max', 'fSet': <fuzzyroutines.FuzzyRoutines.FuzzySet object at 0x000001AECB34F710>}]
    Printing scale: FuzzyScale = {Min, Low, Med, High, Max}
        Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
        Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
        Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
        High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
        Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>
    Defuz() of all Universal Fuzzy Scale levels:
    Defuz(Min) = 0.06
    Defuz(Low) = 0.29
    Defuz(Med) = 0.50
    Defuz(High) = 0.71
    Defuz(Max) = 0.93

Use Fuzzy() function to looking for level on Fuzzy Scale:

    xPar = 0
    for i in range(0, 10, 1):
        xPar = (xPar + i) / 10
        res = uniFScale.Fuzzy(xPar)  # calculate fuzzy level for some real values
        print('Fuzzy({:1.1f}, {}) = {}, {}'.format(xPar, uniFScale.name, res['name'], res['fSet']))

Output:

    Fuzzy(0.0, FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    Fuzzy(0.1, FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    Fuzzy(0.2, FuzzyScale) = Low, Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
    Fuzzy(0.3, FuzzyScale) = Low, Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
    Fuzzy(0.4, FuzzyScale) = Med, Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
    Fuzzy(0.5, FuzzyScale) = Med, Med = <Bell(x, {"a": 0.34, "b": 0.4, "c": 0.6}), [0.34, 0.66]>
    Fuzzy(0.7, FuzzyScale) = High, High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
    Fuzzy(0.8, FuzzyScale) = High, High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
    Fuzzy(0.9, FuzzyScale) = Max, Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>
    Fuzzy(1.0, FuzzyScale) = Max, Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>

Finding fuzzy level using GetLevelByName() function with exact matching:

    print('Finding level by name with exact matching:')

    res = uniFScale.GetLevelByName('Min')
    print('GetLevelByName(Min, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('High')
    print('GetLevelByName(High, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('max')
    print('GetLevelByName(max, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

Output:

    Finding level by name with exact matching:
    GetLevelByName(Min, FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    GetLevelByName(High, FuzzyScale) = High, High = <Bell(x, {"a": 0.6, "b": 0.66, "c": 0.77}), [0.6, 0.83]>
    GetLevelByName(max, FuzzyScale) = None, None

Finding fuzzy level using GetLevelByName() function without exact matching:

    print('Finding level by name without exact matching:')

    res = uniFScale.GetLevelByName('mIn', exactMatching=False)
    print("GetLevelByName('mIn', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('max', exactMatching=False)
    print("GetLevelByName('max', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('Hig', exactMatching=False)
    print("GetLevelByName('Hig', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('LOw', exactMatching=False)
    print("GetLevelByName('LOw', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('eD', exactMatching=False)
    print("GetLevelByName('eD', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

    res = uniFScale.GetLevelByName('Highest', exactMatching=False)
    print("GetLevelByName('Highest', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None', res['fSet'] if res else 'None'))

Output:

    Finding level by name without exact matching:
    GetLevelByName('mIn', FuzzyScale) = Min, Min = <Hyperbolic(x, {"a": 8, "b": 20, "c": 0}), [0.0, 0.23]>
    GetLevelByName('max', FuzzyScale) = Max, Max = <Parabolic(x, {"a": 0.77, "b": 0.95}), [0.77, 1.0]>
    GetLevelByName('Hig', FuzzyScale) = None, None
    GetLevelByName('LOw', FuzzyScale) = Low, Low = <Bell(x, {"a": 0.17, "b": 0.23, "c": 0.34}), [0.17, 0.4]>
    GetLevelByName('eD', FuzzyScale) = None, None
    GetLevelByName('Highest', FuzzyScale) = None, None


<a name="Chapter_2_5"></a>***Work with fuzzy logic operators***

Checks that number is in [0, 1]:

    print('IsCorrectFuzzyNumberValue(0.5) =', IsCorrectFuzzyNumberValue(0.5))
    print('IsCorrectFuzzyNumberValue(1.1) =', IsCorrectFuzzyNumberValue(1.1))

Output:

    IsCorrectFuzzyNumberValue(0.5) = True
    IsCorrectFuzzyNumberValue(1.1) = False

Calculates result of fuzzy NOT, fuzzy NOT with alpha parameter and parabolic fuzzy NOT operations:

    print('FNOT(0.25) =', FuzzyNOT(0.25))
    print('FNOT(0.25, alpha=0.25) =', FuzzyNOT(0.25, alpha=0.25))
    print('FNOT(0.25, alpha=0.75) =', FuzzyNOT(0.25, alpha=0.75))
    print('FNOT(0.25, alpha=1) =', FuzzyNOT(0.25, alpha=1))

    print('FNOTParabolic(0.25, alpha=0.25) =', FuzzyNOTParabolic(0.25, alpha=0.25))
    print('FNOTParabolic(0.25, alpha=0.75) =', FuzzyNOTParabolic(0.25, alpha=0.75))

Output:

    FNOT(0.25) = 0.75
    FNOT(0.25, alpha=0.25) = 0.25
    FNOT(0.25, alpha=0.75) = 0.9166666666666666
    FNOT(0.25, alpha=1) = 1.0
    FNOTParabolic(0.25, alpha=0.25) = 0.25000000000000017
    FNOTParabolic(0.25, alpha=0.75) = 0.9820000000000008

Calculates result of fuzzy AND/OR operations:

    print('FuzzyAND(0.25, 0.5) =', FuzzyAND(0.25, 0.5))
    print('FuzzyOR(0.25, 0.5) =', FuzzyOR(0.25, 0.5))

Output:

    FuzzyAND(0.25, 0.5) = 0.25
    FuzzyOR(0.25, 0.5) = 0.5

Calculates result of T-Norm operations, where T-Norm is one of conjunctive operators - logic, algebraic, boundary, drastic:

    print("TNorm(0.25, 0.5, 'logic') =", TNorm(0.25, 0.5, normType='logic'))
    print("TNorm(0.25, 0.5, 'algebraic') =", TNorm(0.25, 0.5, normType='algebraic'))
    print("TNorm(0.25, 0.5, 'boundary') =", TNorm(0.25, 0.5, normType='boundary'))
    print("TNorm(0.25, 0.5, 'drastic') =", TNorm(0.25, 0.5, normType='drastic'))

Output:

    TNorm(0.25, 0.5, 'logic') = 0.25
    TNorm(0.25, 0.5, 'algebraic') = 0.125
    TNorm(0.25, 0.5, 'boundary') = 0
    TNorm(0.25, 0.5, 'drastic') = 0

Calculates result of S-coNorm operations, where S-coNorm is one of disjunctive operators - logic, algebraic, boundary, drastic:

    print("SCoNorm(0.25, 0.5, 'logic') =", SCoNorm(0.25, 0.5, normType='logic'))
    print("SCoNorm(0.25, 0.5, 'algebraic') =", SCoNorm(0.25, 0.5, normType='algebraic'))
    print("SCoNorm(0.25, 0.5, 'boundary') =", SCoNorm(0.25, 0.5, normType='boundary'))
    print("SCoNorm(0.25, 0.5, 'drastic') =", SCoNorm(0.25, 0.5, normType='drastic'))

Output:

    SCoNorm(0.25, 0.5, 'logic') = 0.5
    SCoNorm(0.25, 0.5, 'algebraic') = 0.625
    SCoNorm(0.25, 0.5, 'boundary') = 0.75
    SCoNorm(0.25, 0.5, 'drastic') = 1

Calculates result of T-Norm operations for N numbers, N > 2:

    print("TNormCompose(0.25, 0.5, 0.75, 'logic') =", TNormCompose(0.25, 0.5, 0.75, normType='logic'))
    print("TNormCompose(0.25, 0.5, 0.75, 'algebraic') =", TNormCompose(0.25, 0.5, 0.75, normType='algebraic'))
    print("TNormCompose(0.25, 0.5, 0.75, 'boundary') =", TNormCompose(0.25, 0.5, 0.75, normType='boundary'))
    print("TNormCompose(0.25, 0.5, 0.75, 'drastic') =", TNormCompose(0.25, 0.5, 0.75, normType='drastic'))

Output:

    TNormCompose(0.25, 0.5, 0.75, 'logic') = 0.25
    TNormCompose(0.25, 0.5, 0.75, 'algebraic') = 0.09375
    TNormCompose(0.25, 0.5, 0.75, 'boundary') = 0
    TNormCompose(0.25, 0.5, 0.75, 'drastic') = 0

Calculates result of S-coNorm operations for N numbers, N > 2:

    print("SCoNormCompose(0.25, 0.5, 0.75, 'logic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='logic'))
    print("SCoNormCompose(0.25, 0.5, 0.75, 'algebraic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='algebraic'))
    print("SCoNormCompose(0.25, 0.5, 0.75, 'boundary') =", SCoNormCompose(0.25, 0.5, 0.75, normType='boundary'))
    print("SCoNormCompose(0.25, 0.5, 0.75, 'drastic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='drastic'))

Output:

    SCoNormCompose(0.25, 0.5, 0.75, 'logic') = 0.75
    SCoNormCompose(0.25, 0.5, 0.75, 'algebraic') = 0.90625
    SCoNormCompose(0.25, 0.5, 0.75, 'boundary') = 1
    SCoNormCompose(0.25, 0.5, 0.75, 'drastic') = 1


<a name="Chapter_2_6"></a>***Working with other methods***

Converting some strings to range of sorted unique numbers with DiapasonParser():

    print("Converting some strings to range of sorted unique numbers:")
    print('String "1,5" converted to:', DiapasonParser("1,5"))
    print('String "1-5" converted to:', DiapasonParser("1-5"))
    print('String "8-10, 1-5, 6" converted to:', DiapasonParser("8-10, 1-5, 6"))
    print('String "11, 11, 12, 12, 1-5, 3-7" converted to:', DiapasonParser("11, 12, 1-5, 3-7"))

Output:

    Converting some strings to range of sorted unique numbers:
    String "1,5" converted to: [1, 5]
    String "1-5" converted to: [1, 2, 3, 4, 5]
    String "8-10, 1-5, 6" converted to: [1, 2, 3, 4, 5, 6, 8, 9, 10]
    String "11, 11, 12, 12, 1-5, 3-7" converted to: [1, 2, 3, 4, 5, 6, 7, 11, 12]
