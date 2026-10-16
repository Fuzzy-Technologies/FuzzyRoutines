<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Can the fuzzy rules learn

The [neural example](neural-integration.md) uses a fixed fuzzy representation around a
neural network. Its input terms do not learn. Here we test a different idea:
put the membership functions and [Sugeno rules](inference.md) inside the
trainable calculation, so prediction error can move their centers and widths.
This is an optional repository experiment, not a public tensor API.

## A small differentiable model

Two normalized inputs, severity and exposure, each have two Gaussian terms.
Their four combinations form four rules. Rule strength multiplies the two
membership grades and a fixed nonnegative rule weight:

$$
\mu_{jk}(x_j)=\exp\!\left[-\frac{(x_j-c_{jk})^2}{2\sigma_{jk}^2}\right],\qquad
\alpha_i=w_i\prod_j\mu_{j,k(i,j)}(x_j).
$$

Here $j$ identifies the input, $k$ its term and $i$ a rule. Centers $c$ stay
ordered through positive normalized gaps; widths $\sigma$ remain between
0.05 and 0.8. These smooth terms are separate from the historical Universal
Fuzzy Scale, whose parameters remain unchanged.

Each rule contributes a constant in the zero-order model, or an affine
function of the inputs in the first-order model:

$$
z_i=b_i+\sum_j a_{ij}x_j,\qquad
\bar\alpha_i=\frac{\alpha_i}{\sum_r\alpha_r},\qquad
\hat y=\sum_i\bar\alpha_i z_i.
$$

Zero order sets every $a_{ij}=0$. Learning minimizes mean squared prediction
error and differentiates through the entire expression. It does not compute
the centroid of an output fuzzy set. All forward arithmetic stays in Torch;
scalar `Defuz()`, NumPy conversion and detached intermediates do not preserve
this gradient path. Scalar conversion is used only for separate parity checks.

![Membership changes, learning curves and held-out comparison](../assets/figures/sugeno-research-learning.svg)

## What the experiment found

The same 600 synthetic observations and 360/120/120 train/validation/test split
as the neural example are used. A simple latent score selects a historical
label; its centroid, computed by the modern API over the original integration
window, is the regression target. Every trainable model
uses 400 full-batch Adam epochs at learning rate 0.01, with checkpoints chosen
only by validation error. The held-out data never tune the model.

| Model                                          | Centroid RMSE | Label accuracy | Invalid outputs |
| ---                                            | ---:          | ---:           | ---:            |
| Fixed rules                                    | 0.093063      | 68.33%         | 0/120           |
| Trainable zero order                           | 0.068779      | 94.17%         | 0/120           |
| Trainable first order                          | 0.067643      | 91.67%         | 2/120           |
| Fixed memberships, learned affine consequences | 0.065600      | 88.33%         | 0/120           |
| Raw-input MLP                                  | 0.069001      | 93.33%         | 0/120           |

The graph learns, but learning memberships did not reduce centroid-target RMSE
relative to the fixed-membership control. The learned zero/first-order models
did classify more labels correctly: the two objectives favor different models.
Two first-order predictions exceeded the decoder's domain;
they are reported as invalid without clipping. One synthetic task and one
initialization cannot establish a general advantage.

![Continuous predictions and explicit output-domain violations](../assets/figures/sugeno-research-predictions.svg)

## Run and inspect

From a checkout containing this experiment, use Python 3.13 or newer. Install
the test tools and optional CPU dependency, then write the complete evidence
to a JSON file:

```bash
python -m pip install -r requirements.txt
python -m pip install --index-url https://download.pytorch.org/whl/cpu -r examples/neural/requirements.txt
python -m research.run_sugeno --output /tmp/sugeno.json --measure-dependencies
python -m pytest -q tests/test_differentiable_sugeno.py tests/test_sugeno_research.py
```

The [runner](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/research/run_sugeno.py)
records seeds, split identities, source/data hashes, losses, predictions,
parameter counts and timing costs. The checked-in JSON is under
`research/results/`. In the recorded one-thread CPU run, training each model
took about 2–3 seconds. Installed Torch files alone occupied about 682 MiB;
the core package does not require Torch.

Frozen models agree with the scalar Sugeno engine within absolute `1e-12`;
finite-difference checks cover input, membership and consequence gradients.
All-zero rule weights raise `UndefinedResultError`. Positive strengths are
normalized in log space, retaining tiny weights whose scalar products could
underflow; scalar parity is claimed where those products are representable.

[ADR-0020](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/adr/0020-differentiable-sugeno-feasibility.md)
records the **no-go decision for public tensor support in 2.1**. This prototype
uses gradient descent, not the hybrid learning algorithm in
[Jang's ANFIS paper](https://doi.org/10.1109/21.256541). Its graph follows the
[PyTorch autograd contract](https://docs.pytorch.org/docs/2.14/notes/autograd.html).
