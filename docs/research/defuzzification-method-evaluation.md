# Evaluation of additional defuzzification methods

## Status

This research note evaluates candidate methods before public API expansion. It does not approve or implement a method. The existing centroid strategy remains the only supported legacy behavior until the domain, zero-area, and precision contracts are implemented.

## Preconditions for any implementation

Every candidate needs an explicit ordered finite universe or integration domain, a deterministic representation rule for continuous versus sampled membership, and the zero-area policy from Task #80. Let mu(x) be the aggregated membership function on [a, b], let h be its maximum, and let M be the set of locations where mu(x) = h.

If h = 0 or the domain is empty, all methods below are undefined and must raise the documented numerical-domain error. They must not choose a midpoint or a cached prior value.

## Candidate methods

| Method | Mathematical rule | Deterministic edge cases | Appropriate evaluation use |
| --- | --- | --- | --- |
| Bisector of area | choose c such that integral from a to c of mu(x) dx equals one half of integral from a to b of mu(x) dx | Requires finite positive area. A zero-membership gap can yield more than one bisecting location, so an implementation must declare its selection rule. | Candidate when the desired output should split aggregate area rather than balance first moment. |
| Mean of maxima (MOM) | for continuous connected M, (min(M) + max(M)) / 2; for a sampled domain, arithmetic mean of all sampled maximizers | A unique maximizer gives that maximizer. Disconnected or discretized maxima require an explicit representation convention. | Candidate neutral choice when a plateau represents equally preferred values. |
| Smallest of maxima (SOM) | min(M) | A unique maximizer gives that maximizer. Ties intentionally select the lowest maximizer. | Candidate when the output policy must choose the most conservative feasible maximum. |
| Largest of maxima (LOM) | max(M) | A unique maximizer gives that maximizer. Ties intentionally select the highest maximizer. | Candidate when the output policy must choose the most permissive feasible maximum. |

With a unique maximum, MOM, SOM, and LOM necessarily return the same location. Their difference is therefore a deliberate tie policy, not a numerical improvement.

## Evidence and external references

- MathWorks documents centroid, bisector, MOM, SOM, and LOM together and illustrates that the three maxima-based methods diverge on a maximum plateau: https://www.mathworks.com/help/fuzzy/defuzzification-methods.html
- The open peer-reviewed survey context lists centroid, bisector, LOM, SOM, and MOM as established alternatives: https://www.mdpi.com/2076-3417/15/4/1934

## Recommendation

Do not add these methods to the public API yet. First merge the explicit fuzzy-set domain decision, implement the modern centroid and zero-area contracts, and define whether FuzzyRoutines operates on analytical functions, samples, or both. After that, a separate approval Task can select methods and their exact continuous/discrete conventions; tests must include unique maxima, plateaus, disconnected maximizer sets, zero area, and finite-domain boundaries.
