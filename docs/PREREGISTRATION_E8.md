# Pre-registration — E8: gates against pricing with rule-level policies

Frozen and committed **before** any E8 run. The commit that adds this file is
the timestamp. Choices below were made from `runs/pilot2.jsonl` only (seeds
1000–1005, `pilot` scenario split). E8 uses seeds 0–19, the `dev` split for
evolution and the `holdout` split for evaluation, as in E1–E6.

## Question

E1 found that a delay surcharge with private gates matches the best acceptance
gate when a policy is three numbers. Does that survive when policies are
rule-level, so that a bank can time, size-sort and counterparty-limit its
payments? And does a coarser, more realistic price get gamed?

## What changes and what does not

* **Policy space (the factor).** `simple`: the three numbers of E1. `rich`:
  eight numbers — opening liquidity, separate morning and afternoon buffers,
  hold time, an opening tick before which nothing ordinary is sent, a size
  threshold, a separate hold time for large payments, and a bilateral net
  sending limit (`src/evortgs/sim.py`). The simple space is exactly nested in
  the rich one (tested).
* **Unchanged.** Environment, costs (`d = 0.5`), six homogeneous banks, 40
  generations, 4 candidates per bank, 16 simulations per candidate, mutation
  scale per coordinate, holdout families. Same budget in both spaces. The pilot
  showed no gain from 80 generations in either space.

## Arms (each in both spaces)

| Label | Mechanism |
|---|---|
| `k0` | private gate |
| `k1` | universalization gate |
| `welfare` | system cost, unilateral change |
| `welfare_universal` | system cost, joint shift |
| `k0+fee` | private gate, linear delay surcharge ∈ {4, 8, 16, 32} |
| `k0+tar` | private gate, two-band tariff ∈ {0.5, 1, 2, 4} per unit of value settled from tick 10 on or left unsettled |
| `planner` | symmetric random-search reference (reported, not used in tests) |

The grids were widened after the pilot (fee 16 beat fee 4; tariff 1 beat 0.25).
For each instrument and each space, the level is chosen by last-generation
**development** cost averaged over seeds and then reported on holdout
(`fee*`, `tar*`). Both instruments are transfers and are excluded from the
reported cost.

Analytical note recorded in advance: a charge proportional to settlement tick
equals the linear delay surcharge plus a term the bank cannot influence, so the
linear surcharge needs no knowledge of when a payment reached the bank. The
two-band tariff is the coarse version of the same instrument and is the one a
richer policy could exploit by releasing just before the band boundary.

## Outcome

As in E1: holdout system cost per unit of payment value, equal-weight mean of
five families, 100 scenarios each. Seeds are the unit (n = 20, paired). 95 %
percentile bootstrap (10 000 resamples), two-sided Wilcoxon signed-rank.
"Clearly" below means the interval of the paired difference excludes 0.

## Hypotheses and decision rules

* **R1 — pricing still matches or beats gates with rule-level policies.**
  In the rich space, `fee*` is clearly cheaper than `k1`, and not clearly more
  expensive than `welfare_universal`.
  *Refuted* if either gate is clearly cheaper than `fee*`.
* **R2 — gates degrade with policy richness more than pricing does**
  (suggested by the pilot, so weaker evidence). The interaction
  `(wu_rich − wu_simple) − (fee*_rich − fee*_simple)` is clearly positive.
  Reported separately for `k1` in place of `welfare_universal`.
* **R3 — the gate ordering survives.** In the rich space `k1` is clearly
  cheaper than `k0`, and `k1` is cheaper than `welfare`.
* **R4 — the coarse price is gamed by rule-level policies.**
  `(tar*_rich − fee*_rich) − (tar*_simple − fee*_simple)` is clearly positive,
  **and** the share of value settled at tick 9 under `tar*` in the rich space
  clearly exceeds that under `fee*` in the rich space. The pilot showed no
  bunching at tick 9, so the expectation is that R4 fails; it is registered
  because it was the stated reason for running this study.
* **R5 — richness alone.** `k0_rich − k0_simple` and `fee*_rich − fee*_simple`
  are reported with intervals; no directional prediction.

## What the outcome decides

* R1 supported: in this environment acceptance gates are not a competitive
  alternative to a price where an operator can levy one. Further work on gates
  is then justified only for settings without such an operator, and that claim
  would need its own environment.
* R1 refuted: gates gain standing against pricing as policies get richer, and
  the language-model proposer stage is the natural next step.
* R4 supported: realistic coarse prices are fragile to richer agents even when
  the ideal price is not.

## Known limits, stated in advance

Rule-level here means eight bounded parameters, not programs; mutation search
may simply fail to find exploits that a stronger proposer would. A null on R4
is therefore evidence about this search process, not proof that the tariff
cannot be gamed. Acceptance remains noise-dominated as documented for E1.
