# API documentation evaluation

![FuzzyRoutines](assets/brand/fuzzyroutines-horizontal.svg){ .fr-brand-lockup }

This disposable site renders the real
[`ScalarFuzzySet`][fuzzyroutines.fuzzysets.ScalarFuzzySet] API and the directed
difference contract

$$
\mu_{A \setminus B}(x) = T\left(\mu_A(x), N\left(\mu_B(x)\right)\right).
$$

The site is an architecture spike for Task #198. It is not the production API
site and must not be published by the current GitHub Pages workflow.

A scalar fuzzy set is declared over a
[`ContinuousUniverse`][fuzzyroutines.domain.ContinuousUniverse] or a
[`DiscreteUniverse`][fuzzyroutines.domain.DiscreteUniverse]. These qualified
type references deliberately exercise cross-page object resolution.
