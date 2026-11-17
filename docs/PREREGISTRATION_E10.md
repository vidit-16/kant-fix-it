# Pre-registration — E10: gates against the ambient tax with unequally exposed agents

Frozen and committed **before** any E10 run. The commit that adds this file is
the timestamp. Every design choice below was made from pilot records only
(`runs/cbpilot2.jsonl`, `runs/cbpilot3.jsonl`; seeds 1000–1005, `pilot`
split). E10 uses seeds 0–19, the `dev` split for evolution and the `holdout`
split for evaluation. The analysis script `src/evortgs/analysis_e10.py` is
committed with this file and was dry-run on pilot records only.

## Why this study

E9 found the Kantian gate and the ambient tax practically equivalent with
identical agents. In that setting Kantian optimisation is known to be
efficient, so E9 was the easiest possible test for the gate. This study gives
the strong claim ("gates beat the best available instrument") a test it could
fail on theoretical grounds, so that whatever the outcome, the line is closed
or kept on fair evidence.

## Which heterogeneity, and a pilot that changed the plan

The first pilot (`cbpilot2`) varied **module size**. It is reported here as a
null: the asymmetric optimum equalled the symmetric one and the Kantian gate
stayed at it, because size scales an agent's gain, its coupling and its
exposure in the same proportion, which is only a change of units.

The Kantian test reads "my cost if everyone made my change". It equals the
harm an agent imposes only if every agent is equally exposed to that harm. The
study therefore varies **incident exposure**: incident rates are multiplied by
`rank ** -skew`, normalised to mean 1, so central modules absorb most incidents
while peripheral modules contribute equal coupling but rarely break
(`exposure_skew` in `src/evortgs/codebase.py`; default 0 leaves E9 unchanged,
tested and spot-checked). Theory predicts that the Kantian gate makes the
peripheral agents over-shortcut and the central agents under-shortcut, while
the ambient tax at level 1 stays efficient (alignment tested with skewed
exposure).

Pilot (`cbpilot3`, six seeds): with skew 1.5 the asymmetric optimum costs
0.1757 against 0.2093 for the best symmetric policy; the Kantian gate reaches
0.1788 with shortcut intensity rising from 0.51 (most exposed) to 0.89 (least
exposed) against 0.63–0.74 at the optimum; the ambient tax reaches 0.1761.

## Design

* Concealment cost γ = 0.25, six agents, equal sizes.
* **Factor: exposure skew** ∈ {0, 0.75, 1.5}. Skew 0 repeats the E9 primary
  regime on the same seeds; for arms present in both studies its records
  should equal E9's (a reproduction check, reported).
* Arms, all with the E9 budget (40 generations, 4 candidates, 16 simulations):
  `k0`, `k0.5`, `k1`, `welfare` (unilateral), `ambient` ∈ {0.5, 1, 1.5, 2},
  `proxy` ∈ {0.1, 0.2, 0.4, 0.8}, `surface` ∈ {1, 2, 4, 8}.
  The output charge is dropped (exactly neutral in E9, tested identity) and so
  is the joint-shift welfare gate (worst cooperative gate in E9).
* References: `planner_asym` (symmetric grid, then three sweeps of
  per-agent coordinate descent and a fine pass, on 64 development scenarios
  per seed; tested never worse than the symmetric planner) is **the optimum**
  for every gap and closure; the symmetric planner is reported only.
* Selection on development cost, as before: a level per instrument; the best
  instrument over all three; the best budget-balanced instrument over proxy and
  surface; the **best own-cost gate over `k0`, `k0.5`, `k1`**.

## Outcome and statistics

Holdout system cost per unit of nominal value, equal-weight mean of five
families, 100 scenarios each; seeds are the unit (n = 20, paired); 95 %
percentile bootstrap, 10 000 resamples; Wilcoxon signed-rank. "Clearly" means
the interval of the paired difference excludes 0. Margin ±0.002, as in E9.

## Hypotheses

* **D1 — dilemma.** `k0` is clearly costlier than the optimum at every skew.
* **D2 — the ambient tax beats the gate when exposure is unequal.** At skew
  0.75 and at skew 1.5 the best instrument is clearly cheaper than the best
  own-cost gate. Predicted by theory and by the pilot (−0.0026 at skew 1.5).
* **D3 — the gate's closure falls with skew.** Per-seed closure
  `(k0 − k1)/(k0 − optimum)` at skew 1.5 minus at skew 0 is clearly negative.
* **D4 — the predicted Kantian distortion.** At skew 1.5, the spread
  `s(least exposed) − s(most exposed)` under `k1`, minus the same spread at the
  optimum, is clearly positive.
* **D5 — the gate still beats budget-balanced instruments.** At each skew the
  best own-cost gate is clearly cheaper than the best budget-balanced
  instrument.
* **D6 — identity.** `ambient1` and `welfare` produce identical profiles in
  every seed and skew.

## Decision rule for the strong line (stricter than E9, fixed in advance)

E9 showed that "the interval excludes zero" can be met by a difference too
small to matter. Here the strong claim **survives only if, at both skew 0.75
and skew 1.5, the best own-cost gate is clearly cheaper than the best
instrument and the point estimate of the difference exceeds the margin
(0.002).** Otherwise the line "acceptance gates beat the best available
instrument" is **closed**, and the project keeps only the conditional result
about budget-balanced instruments (D5), if D5 holds.

**Expected outcome from the pilot: the strong line is closed** (D2 holds;
the gate loses by more than the margin at skew 1.5).

## What would count against the expected reading

* D2 fails and the gate is clearly cheaper by more than the margin at both
  skews: the strong claim survives a test designed to break it, and the
  reason (search noise, multiple equilibria) must be found before it is
  believed.
* D4 fails: the gate's behaviour does not follow the theoretical mechanism,
  and any cost difference needs another explanation.
* D6 fails or the skew-0 records differ from E9: a bug; stop and investigate.

## Known limits, stated in advance

* One kind of heterogeneity (exposure), one functional form, six agents.
* Risk-neutral agents and no collusion, which favour the ambient tax.
* The ambient tax remains budget-breaking; D5 is the result that does not
  depend on whether an operator can levy it.
* The asymmetric optimum is found by coordinate descent on a grid; it could
  be a local optimum. The pilot ambient tax came within 0.0004 of it.
