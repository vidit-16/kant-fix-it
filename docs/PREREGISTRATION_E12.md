# Pre-registration — E12: E11 corrected

Frozen and committed **before** any E12 run. The commit that adds this file is
the timestamp. E12 was prompted by an independent review of the published
repository (23 November 2026; PROJECT.md §5.12), which found two faults in
E11. It was decided after E11's results and the review's findings were known;
it is registered so that its own outcome is not chosen after the fact. A pilot
of 16 runs (`runs/e12pilot.jsonl`, seeds 1000–1001, `pilot` split) checked
only that the new code runs and how long it takes; its costs were not
inspected and nothing below was chosen from it. E12 uses seeds 0–19, the `dev`
split for evolution and the `holdout` split for evaluation, exactly as E10 and
E11. The analysis script `src/evortgs/analysis_e12.py` is committed with this
file.

## Why

E11 asked whether E10's verdict depends on the scale on which the Kantian gate
measures "the same change". The review found:

1. **The square-root variant was wrong.** Its inverse squares g(x_j) + step
   even when that is negative, so a step that should take a peer below zero
   moves it the other way. In a replay at skew 1.5, seed 0, κ = 1, 323 of 960
   proposals moved at least one peer against the proposer's change.
2. **The scales used different conventions.** `linear` (E10's registered rule)
   broadcasts the raw proposed change d; `log`, `sqrt` and `logit` broadcast
   the proposer's realized change after clipping to [0, 1]. E11's comparison
   of scales against linear (U2) therefore mixed scale with convention.
3. A verdict flag in `analysis_e11.py` had a sign error. It changed no
   outcome and is corrected in code; E11's results file is unchanged.

`log` and `logit` are valid as run (their inverses are monotone on the reals
and they use the realized change), so their E11 records are reused.

## Design

* The environment, budget, seeds, splits, mutation and evaluation are E10's.
  Exposure skew ∈ {0, 0.75, 1.5}.
* **New arms (run in E12):** κ ∈ {0.5, 1} × two corrected variants × three
  skews × 20 seeds = 240 runs.
  * `sqrt_fixed`: g(x) = √x with inverse max(y, 0)², so a step can take a peer
    down to zero but never reverse it.
  * `linear_realized`: g(x) = x, broadcasting the proposer's realized change
    instead of the raw d, the convention of the other scales.
* **Reused, same seeds and scenarios:** from E10, the linear gates (κ = 0, 0.5,
  1), the ambient tax at level 1 and the asymmetric optimum; from E11, the
  `log` and `logit` gates (κ = 0.5, 1). E11's `sqrt` records are excluded from
  every test below and used only to describe the fault's effect.
* **Best own-cost gate over all valid variants:** chosen on development cost
  (last generation) among k0 and k0.5 and k1 under `linear`,
  `linear_realized`, `log`, `sqrt_fixed` and `logit`, i.e. eleven variants.
  This gives the gate every chance.

## Statistics

As E10 and E11: holdout system cost, equal-weight mean of five families, 100
scenarios each; seeds paired (n = 20); 95 % percentile bootstrap with 10 000
resamples; Wilcoxon signed-rank; margin ±0.002. Differences are written
ambient − gate, so negative means the ambient tax is cheaper.

## Hypotheses

* **V1 — the closure holds over the corrected variants (primary).** At skew 0.75
  and at skew 1.5 the ambient tax (level 1) is clearly cheaper than the best
  own-cost gate over all eleven valid variants (upper bound of the 95 %
  interval below zero). Expectation from E11, where logit was best: −0.0016
  and −0.0018.
* **V2 — units matter at matched convention.** At skew 1.5 the log-scale
  Kantian gate (κ = 1) is clearly costlier than `linear_realized` (κ = 1).
  E11's comparison with the raw-convention linear gave +0.020.
* **V3 — the distortion survives every valid scale.** At skew 1.5, for
  `linear_realized`, `sqrt_fixed`, `log` and `logit` (κ = 1), the spread
  s(least exposed) − s(most exposed) minus the optimum's spread is clearly
  positive.
* **V4 — symmetry makes scale irrelevant.** At skew 0, `sqrt_fixed` and
  `linear_realized` (κ = 1) are each within ±0.002 of `linear`.

Reported without a prediction:

* the convention effect, `linear_realized` − `linear` (κ = 1), at each skew;
* the fault's effect, `sqrt_fixed` − E11's `sqrt` (κ = 1), at each skew.

## Decision rule (fixed in advance; mirrors E10 and E11, sign corrected)

* **The strong line reopens only if**, at both skew 0.75 and skew 1.5, the best
  own-cost gate over all valid variants is clearly cheaper than the ambient
  tax (lower bound of ambient − gate above zero) and the point estimate of
  ambient − gate exceeds +0.002.
* **The closure is called robust to the corrected variants if V1 holds.** If V1
  fails without the line reopening, the closure stands but is reported as
  scale-dependent at the skew where it fails.
* E11's reported results stay in the record unchanged; E12's are reported
  beside them, not in their place.

## Known limits, stated in advance

* As E11: a handful of natural monotone scales, offsets of 0.05 in `log` and
  `logit`, one heterogeneity, one functional form, risk-neutral agents that
  cannot coordinate.
* The pooling result (PROJECT.md §5.12, D34) already removes the gate's role
  against budget-balanced rules in this model. E12 only tests whether the
  unit dependence and the closure against the ambient tax survive the
  corrections; it cannot restore that role.
