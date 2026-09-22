# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Demonstrate the broad historical FuzzyRoutines compatibility API.

Execution prints human-readable membership, set, scale, operator, negation,
and parser observations to stdout. The module creates no files and performs no
network access. New integrations should prefer the focused modern API and the
smaller migration examples under `examples/migration`.
"""

from fuzzyroutines.FuzzyRoutines import *

# --- Usage of some membership functions (uncomment one of them):

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

# --- Calculating some function's values in [0, 1]:

xPar = 0
for i in range(0, 10, 1):
    xPar = (xPar + i) / 10
    res = funct.mju(xPar)  # calculate one value of MF with given parameters
    print('x = {:.1f}, {} = {:1.4f}'.format(xPar, funct, res))

# --- Work with fuzzy set:

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

# --- Work with fuzzy scales:
# Fuzzy scale is an ordered set of linguistic variables that looks like this:
# S = [{'name': 'name_1', 'fSet': fuzzySet_1}, {'name': 'name_2', 'fSet': fuzzySet_2}, ...],
#     where name is a linguistic name of fuzzy set,
#     fSet is a user define fuzzy set of FuzzySet type.
scale = FuzzyScale()  # intialize new fuzzy scale with default levels

print('Printing default fuzzy scale in human-readable:', scale)

print('Defuz() of all default levels:')
for item in scale.levels:
    print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

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

scale.name = 'New Scale'
scale.levels = [{'name': levelMin.name, 'fSet': levelMin}, {'name': levelMed.name, 'fSet': levelMed},
                {'name': levelMax.name, 'fSet': levelMax}]  # add new ordered set of linguistic variables into scale

print('Changed List of levels as objects:', scale.levels)
print('Printing changed fuzzy scale in human-readable:', scale)

print('Defuz() of all New Scale levels:')
for item in scale.levels:
    print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

# --- Work with Universal Fuzzy Scale:
# Universal fuzzy scales S_f = {Min, Low, Med, High, Max} pre-defined in UniversalFuzzyScale() class.

uniFScale = UniversalFuzzyScale()
print('Levels of Universal Fuzzy Scale:', uniFScale.levels)
print('Printing scale:', uniFScale)

print('Defuz() of all Universal Fuzzy Scale levels:')
for item in uniFScale.levels:
    print('Defuz({}) = {:1.2f}'.format(item['name'], item['fSet'].Defuz()))

# Use Fuzzy() function to looking for level on Fuzzy Scale:

xPar = 0
for i in range(0, 10, 1):
    xPar = (xPar + i) / 10
    res = uniFScale.Fuzzy(xPar)  # calculate fuzzy level for some real values
    print('Fuzzy({:1.1f}, {}) = {}, {}'.format(xPar, uniFScale.name, res['name'], res['fSet']))

# Finding fuzzy level using GetLevelByName() function:

print('Finding level by name with exact matching:')

res = uniFScale.GetLevelByName('Min')
print('GetLevelByName(Min, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None',
                                                res['fSet'] if res else 'None'))

res = uniFScale.GetLevelByName('High')
print('GetLevelByName(High, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None',
                                                 res['fSet'] if res else 'None'))

res = uniFScale.GetLevelByName('max')
print('GetLevelByName(max, {}) = {}, {}'.format(uniFScale.name, res['name'] if res else 'None',
                                                res['fSet'] if res else 'None'))

print('Finding level by name without exact matching:')

res = uniFScale.GetLevelByName('mIn', exactMatching=False)
print("GetLevelByName('mIn', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None',
                                                  res['fSet'] if res else 'None'))

res = uniFScale.GetLevelByName('max', exactMatching=False)
print("GetLevelByName('max', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None',
                                                  res['fSet'] if res else 'None'))

res = uniFScale.GetLevelByName('Hig', exactMatching=False)
print("GetLevelByName('Hig', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None',
                                                  res['fSet'] if res else 'None'))

res = uniFScale.GetLevelByName('LOw', exactMatching=False)
print("GetLevelByName('LOw', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None',
                                                  res['fSet'] if res else 'None'))

res = uniFScale.GetLevelByName('eD', exactMatching=False)
print("GetLevelByName('eD', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None',
                                                 res['fSet'] if res else 'None'))

res = uniFScale.GetLevelByName('Highest', exactMatching=False)
print("GetLevelByName('Highest', {}) = {}, {}".format(uniFScale.name, res['name'] if res else 'None',
                                                      res['fSet'] if res else 'None'))

# --- Work with fuzzy logic operators:

# Checks that number is in [0, 1]:

print('IsCorrectFuzzyNumberValue(0.5) =', IsCorrectFuzzyNumberValue(0.5))
print('IsCorrectFuzzyNumberValue(1.1) =', IsCorrectFuzzyNumberValue(1.1))

# Calculates result of fuzzy NOT, fuzzy NOT with alpha parameter and parabolic fuzzy NOT operations:

print('FNOT(0.25) =', FuzzyNOT(0.25))
print('FNOT(0.25, alpha=0.25) =', FuzzyNOT(0.25, alpha=0.25))
print('FNOT(0.25, alpha=0.75) =', FuzzyNOT(0.25, alpha=0.75))
print('FNOT(0.25, alpha=0.9) =', FuzzyNOT(0.25, alpha=0.9))

print('FNOTParabolic(0.25, alpha=0.25) =', FuzzyNOTParabolic(0.25, alpha=0.25))
print('FNOTParabolic(0.25, alpha=0.75) =', FuzzyNOTParabolic(0.25, alpha=0.75))

# Calculates result of fuzzy AND/OR operations:

print('FuzzyAND(0.25, 0.5) =', FuzzyAND(0.25, 0.5))
print('FuzzyOR(0.25, 0.5) =', FuzzyOR(0.25, 0.5))

# Calculates result of T-Norm operations, where T-Norm is one of conjunctive operators - logic, algebraic, boundary, drastic:

print("TNorm(0.25, 0.5, 'logic') =", TNorm(0.25, 0.5, normType='logic'))
print("TNorm(0.25, 0.5, 'algebraic') =", TNorm(0.25, 0.5, normType='algebraic'))
print("TNorm(0.25, 0.5, 'boundary') =", TNorm(0.25, 0.5, normType='boundary'))
print("TNorm(0.25, 0.5, 'drastic') =", TNorm(0.25, 0.5, normType='drastic'))

# Calculates result of S-coNorm operations, where S-coNorm is one of disjunctive operators - logic, algebraic, boundary, drastic:

print("SCoNorm(0.25, 0.5, 'logic') =", SCoNorm(0.25, 0.5, normType='logic'))
print("SCoNorm(0.25, 0.5, 'algebraic') =", SCoNorm(0.25, 0.5, normType='algebraic'))
print("SCoNorm(0.25, 0.5, 'boundary') =", SCoNorm(0.25, 0.5, normType='boundary'))
print("SCoNorm(0.25, 0.5, 'drastic') =", SCoNorm(0.25, 0.5, normType='drastic'))

# Calculates result of T-Norm operations for N numbers, N > 2:

print("TNormCompose(0.25, 0.5, 0.75, 'logic') =", TNormCompose(0.25, 0.5, 0.75, normType='logic'))
print("TNormCompose(0.25, 0.5, 0.75, 'algebraic') =", TNormCompose(0.25, 0.5, 0.75, normType='algebraic'))
print("TNormCompose(0.25, 0.5, 0.75, 'boundary') =", TNormCompose(0.25, 0.5, 0.75, normType='boundary'))
print("TNormCompose(0.25, 0.5, 0.75, 'drastic') =", TNormCompose(0.25, 0.5, 0.75, normType='drastic'))

# Calculates result of S-coNorm operations for N numbers, N > 2:

print("SCoNormCompose(0.25, 0.5, 0.75, 'logic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='logic'))
print("SCoNormCompose(0.25, 0.5, 0.75, 'algebraic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='algebraic'))
print("SCoNormCompose(0.25, 0.5, 0.75, 'boundary') =", SCoNormCompose(0.25, 0.5, 0.75, normType='boundary'))
print("SCoNormCompose(0.25, 0.5, 0.75, 'drastic') =", SCoNormCompose(0.25, 0.5, 0.75, normType='drastic'))

# --- Working with other methods:

# Converting some strings to range of sorted unique numbers with DiapasonParser():

print("Converting some strings to range of sorted unique numbers:")
print('String "1,5" converted to:', DiapasonParser("1,5"))
print('String "1-5" converted to:', DiapasonParser("1-5"))
print('String "8-10, 1-5, 6" converted to:', DiapasonParser("8-10, 1-5, 6"))
print('String "11, 11, 12, 12, 1-5, 3-7" converted to:', DiapasonParser("11, 12, 1-5, 3-7"))
