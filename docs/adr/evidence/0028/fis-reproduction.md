<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# FIS fixture reproduction

The [weighted response fixture](weighted-response.fis) was authored for
[ADR-0028](../../0028-external-model-interchange-profile.md). Its terms,
ranges and rules were constructed from the numerical witness in the ADR.
The fixture contains no copied vendor sample or implementation. Its SHA-256
is `2895a62fede3f98923a6d17c95cd13b71b45cd3494d8199267ceb46bcf1f6770`.

An independent CLI read the original bytes with its FIS importer and
evaluated five inputs. The evaluator was FuzzyLite 6.0, tag `v6.0`,
commit `a49a6e22adf3fa69351d5732f8d42b2d1e08c43a`. The scratch build used
Linux x86-64 and GNU C++ 13.3.0 in C++11 mode, compiling the upstream CLI
and source files with default double precision and no source changes.
FuzzyLite was a separate evidence tool. It is absent from the package
and its dependencies. [FuzzyLite v6.0 release](https://github.com/fuzzylite/fuzzylite/releases/tag/v6.0)

From the repository root, with the FuzzyLite 6.0 executable on the PATH:

```sh
printf '0\n1\n2\n3\n4\n' > /tmp/fuzzyroutines-adr0028-input.fld
fuzzylite -i docs/adr/evidence/0028/weighted-response.fis -if fis -of fld \
  -d /tmp/fuzzyroutines-adr0028-input.fld
```

Observed output:

```text
load response
0.000 nan
1.000 2.000
2.000 4.000
3.000 8.000
4.000 nan
```

The FuzzyRoutines scalar engine was evaluated on the same five inputs with
a separately constructed model using `Triangle`, `TermCondition` and
`ConstantConsequent`. It returned 2, 4 and 8 on the three interior inputs
and raised `UndefinedResultError` on both endpoints. The exact arithmetic
reference at input 2 is $(0.5 \cdot 2 + 0.25 \cdot 8) / (0.5 + 0.25) = 4$.
The output log is limited to the precision displayed by the independent
CLI. The scratch run did not expose its membership or firing traces.
