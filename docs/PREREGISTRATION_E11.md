# Pre-registration — E11: does E10's verdict depend on the units of universalization?

Frozen and committed **before** any E11 run. The commit that adds this file is
the timestamp. This is a robustness check prompted by the literature review
(Sloev and Lianos 2026, arXiv:2610.28180, building on Sher and Roemer). It was
decided after E10's results were known; it is registered so that its own
outcome is not chosen after the fact. Design choices were made from the pilot
records `runs/unitspilot.jsonl` (seeds 1000–1005, `pilot` split) and, for
comparators, `runs/cbpilot3.jsonl`. E11 uses seeds 0–19, the `dev` split for
evolution and the `holdout` split for evaluation, exactly as E10. The analysis
script `src/evortgs/analysis_e11.py` is committed with this file.

## Why

The Kantian gate asks "what would my cost be if every agent made the same
change?". "The same change" needs a scale. E10's gate adds the same shift to
every agent's policy in the policy's own units (0 to 1). The Kantian
counterfactual is known to depend on how actions are represented. If a
different but equally natural scale let the gate beat the ambient tax, E10's
closure of the strong line would be an artefact of units.

## Design

* The environment, budget, seeds, splits, mutation and evaluation are E10's.
  Exposure skew ∈ {0, 0.75, 1.5}.
* **Factor: scale of the universalized counterfactual.** Agent i's candidate
  change x_i → x_i' is applied to every other agent j as
  x_j' = g⁻¹(g(x_j) + g(x_i') − g(x_i)), clipped to [0, 1], coordinate by
  coordinate. Scales:
  * `linear`: g(x) = x, which is E10's gate. Its records are taken from E10
    rather than re-run; the modified code was checked to reproduce E10 runs
    bit for bit.
  * `log`: g(x) = log(x + 0.05), close to Roemer's multiplicative form.
  * `sqrt`: g(x) = √x.
  * `logit`: g(x) = log((x + 0.05) / (1.05 − x)).
* Arms run in E11: κ ∈ {0.5, 1} × the three new scales × three skews × 20
  seeds = 360 runs. Mutation and the unilateral half of the κ = 0.5 score are
  unchanged; only the universalized counterfactual changes.
* Comparators from E10, same seeds and scenarios: the linear gates, the
  private gate (κ = 0), the ambient tax at level 1, and the asymmetric
  optimum.
* **Best own-cost gate over all scales**: chosen on development cost (last
  generation) among k0, k0.5 and k1 under all four scales, i.e. nine
  variants. This gives the gate every chance.

## Statistics

As E10: holdout system cost, equal-weight mean of five families, 100
scenarios each; seeds paired (n = 20); 95 % percentile bootstrap with 10 000
resamples; Wilcoxon signed-rank; margin ±0.002.

## Hypotheses

* **U1 — E10's verdict is robust to scale.** At skew 0.75 and at skew 1.5,
  the ambient tax (level 1) is clearly cheaper than the best own-cost gate
  over all scales. Pilot at skew 1.5: ambient 0.1761 against the best
  rescaled gate, logit κ = 1, at 0.1781.
* **U2 — the gate itself depends on units when agents differ.** At skew 1.5
  the log-scale Kantian gate is clearly costlier than the linear one. Pilot:
  +0.025.
* **U3 — the distortion survives every scale.** At skew 1.5, for every scale
  the spread s(least exposed) − s(most exposed) under the Kantian gate,
  minus the spread at the optimum, is clearly positive.
* **U4 — symmetry makes scale irrelevant.** At skew 0, the Kantian gate under
  each new scale is within ±0.002 of the linear gate. Theory: with identical
  policies every scale gives the same counterfactual. Pilot: about +0.001.
  Random initial profiles are not identical, so this is approximate.

## Decision rule (fixed in advance; mirrors E10)

* **The strong line reopens only if**, at both skew 0.75 and skew 1.5, the
  best own-cost gate over all scales is clearly cheaper than the ambient tax
  and the point estimate of the difference exceeds 0.002.
* **E10's closure is called robust to scale if U1 holds.** If U1 fails
  without the line reopening, the closure stands but is reported as
  scale-dependent at the skew where it fails.

## Known limits, stated in advance

* Three alternative scales, chosen as natural monotone maps of [0, 1]. Other
  scales could behave differently; with enough freedom in choosing g, the
  scale can itself be tuned to the problem. That would be a different
  instrument, not the gate studied here.
* The offset 0.05 in `log` and `logit` keeps the maps finite at the bounds,
  and is a choice.
* As in E10: one heterogeneity, one functional form, risk-neutral agents
  that cannot coordinate.
