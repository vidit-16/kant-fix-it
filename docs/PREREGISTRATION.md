# Pre-registration — confirmatory experiments E1–E6

Frozen and committed **before** any confirmatory run. The commit that adds this
file is the timestamp. Nothing below was chosen with knowledge of holdout
results: the pilot used seeds 1000–1005 and the separate `pilot` scenario split;
confirmatory runs use seeds 0–19, the `dev` split for evolution and the
`holdout` split for evaluation.

## Question

When several agents sharing an environment each improve their own policy by a
propose–evaluate–accept loop, the acceptance gate decides which changes
survive. Holding the proposal mechanism, the search budget and the environment
fixed, how much of the efficiency loss from independent self-improvement can be
removed by changing only the gate, and what does each gate need to know?

## Environment and what the pilot fixed

Stylized RTGS network (`src/evortgs/sim.py`): 6 banks, 20 ticks, about 20
payments per bank, 85 % of payments in closed cycles, no intraday credit.
Costs: liquidity 1, deadline miss 2, end-of-day unsettled 10, and a full-day
delay cost `d` (in units of the liquidity cost).

Choices made from the pilot and from diagnostics on the `pilot` split:

* Flows are balanced (cyclic). With unbalanced random flows, liquidity funded
  net positions, deviations had no measurable effect on other banks, and all
  gates coincided. That first model is recorded as a null in `PROJECT.md`.
* Primary regime `d = 0.5` (delay cheaper than liquidity). Selection rule: the
  symmetric planner settles at least 98 % of value and a unilateral cut in
  liquidity from the planner level is privately profitable.
* Search budget: 40 generations, 4 candidates per bank, 16 simulations per
  candidate, identical for every gate.

## Arms

| Label | Gate | Reads |
|---|---|---|
| `k0` | own cost, unilateral change (private) | own cost |
| `k.25`, `k.5`, `k.75` | mixture, degree of morality κ | own cost |
| `k1` | own cost if every bank made the same shift (universalization) | own cost |
| `welfare` | system cost, unilateral change | all costs |
| `welfare_universal` | system cost, joint shift | all costs |
| `noharm` | private gain that does not raise others' summed cost | all costs |
| `k0+fee` | private gate under an operator delay surcharge ∈ {1,2,4,8} | own cost |
| `planner` | best single policy imposed on all banks (reference) | all costs |

## Primary outcome

Holdout system cost per unit of payment value, averaged with equal weight over
the five holdout families (`base`, `surge`, `outage`, `late_heavy`, `hub`), 100
scenarios each. Evolution sees only `base` development scenarios.

Gap closure of arm *g*: `GC(g) = (C_k0 − C_g) / (C_k0 − C_planner)`, computed
from seed-paired means.

## Hypotheses and decision rules

Seeds are the unit of analysis (n = 20, paired across arms). Intervals are 95 %
percentile bootstrap over seeds (10 000 resamples). Tests are two-sided Wilcoxon
signed-rank; the five H4 tests are Holm-corrected.

* **H1 — independent self-improvement is inefficient.** `C_k0 > C_planner`,
  interval excludes 0, and the mean excess is at least 5 %.
  *Refuted* if the interval includes 0 or the excess is below 5 %.
* **H2 — the universalization gate recovers most of the loss.** `GC(k1) ≥ 0.5`
  with interval lower bound above 0, homogeneous banks (E1).
  *Refuted* if the interval includes 0; *partially supported* if the interval
  excludes 0 but the point estimate is below 0.5.
* **H2b — dose response.** Spearman correlation between κ and holdout cost over
  the five κ levels is negative with interval excluding 0.
* **H3 — heterogeneity erodes it.** `GC(k1)` at heterogeneity 0 exceeds
  `GC(k1)` at 1.5, interval of the difference excludes 0 (E1 vs E2). Secondary:
  number of banks whose own holdout cost is higher under `k1` than under `k0`.
* **H4 — transfer to unseen shocks.** `C_k1 < C_k0` in each of the five holdout
  families, Holm-corrected p < 0.05.
* **H5 — the universalization gate is exploitable.** With one `k0` bank among
  five `k1` banks (E4), the defector's own holdout cost is lower than the same
  bank's cost in the all-`k1` run, interval excludes 0; system cost is reported.
* **H6 — suggested by the pilot, so weaker evidence.** `C_k1 < C_welfare`.
  `welfare_universal` is included to separate joint moves from whose cost is
  read; no directional prediction for `k1` vs `welfare_universal`.

## Secondary and robustness (reported whatever the outcome)

* E3: `d ∈ {0.1, 2, 6}` for `k0`, `k1`, `welfare`, `planner`.
* Fee baseline: the surcharge is chosen by last-generation **development**
  cost averaged over seeds, then reported on holdout.
* E5: sequential updates; 10 banks.
* E6: three times the generations (10 seeds) to check whether gaps are a
  finite-budget artefact.
* Settlement rate, delay, liquidity posted, per-bank cost changes, and every
  accounting invariant on every evaluation simulation.

## What would count against the whole line of work

* H1 refuted: no inefficiency to remove in this environment.
* `k1` no better than `k0` on holdout, or better only on the `base` family.
* Gaps that vanish in E6 (pure search-budget artefact).
* Any invariant violation in evaluation.

## Known limits, stated in advance

Six banks, three policy parameters, a toy cost calibration, no liquidity-saving
mechanism, no intraday credit, mutation-based proposals rather than
language-model proposals. Results are about gates in this stylized game, not
about any real payment system.
