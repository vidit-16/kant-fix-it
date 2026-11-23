# Pre-registration — E13: the Kantian gate against budget-balanced transfers when effort is off the ledger

Frozen and committed **before** any E13 calibration, selection or confirmatory run. The commit that adds this file is the timestamp. The code (`src/evortgs/e13.py`), the analysis (`src/evortgs/analysis_e13.py`) and the tests (`tests/test_e13.py`) are committed with it.

The run happens in three stages, each frozen before the next:

1. **Calibration** (dev seeds 2000–2019) fixes the direct-charge scale and the contract anchor.
2. **Selection** (dev seeds 2100–2119) chooses one strict-budget comparator and one ambient comparator per cell. The result is written to `runs/e13_lock.json` and committed before any confirmatory run.
3. **Confirmation** (seeds 3000–3019) runs on a fresh holdout block.

## Origin, and what was seen before this freeze

- **Why this study exists.** An independent review (PROJECT.md §5.12) showed that equal output sharing, which is budget-balanced, makes the same decisions as the level-1 ambient tax in E9–E12's model. The equivalence rests on agents having no cost outside the output ledger. E13 adds such a cost and asks whether the gate then beats the strongest budget-balanced transfer. The design was drafted outside the repository and checked against this source before freezing.
- **An exploratory pilot shaped some choices.** It ran 168 runs on seeds 1000–1005, on the `pilot` split, with 8 generations, 2 candidates and 6 scenarios per score. It used a scratch adapter outside the repository. Its raw rows are not in the repository; its table is reproduced in the appendix below. It informed four things:
  - the effort rate ρ = 0.15;
  - dropping mechanisms the pilot could not validate;
  - pricing full coupling load (s and m) and tuning the direct charge, instead of the pilot's untuned charge on shortcut intensity alone;
  - the directional predictions D1–D2 below, which are therefore **post-pilot**.
- **Two checks touched only pilot-split scenarios** and selected or tuned nothing:
  - A pipeline test runs every stage with 2 generations.
  - A theory check computed the full six-agent mixed difference of total ledger cost. It used 64 `base` pilot scenarios at index 5,000,000, both skews and three random profile pairs. The difference was nonzero in every scenario, with mean |difference| 1.0–1.4 against a total of about 55. Its mean over scenarios was small, between −0.08 and +0.39. So the simulator has a **pointwise** full-order interaction among all agents. A **mean** interaction is not established.
- **Not seen:** no confirmatory seed (3000–3019), no calibration or validation seed, no development evaluation block, and no holdout scenario from the new block.

## Setting and question

- **The setting.** Independent owners, such as teams or peer agents from different organisations, must settle any transfers among themselves. No party may keep a surplus or fund a deficit. A firm with a treasury has a wider choice, which we compare separately.
- **The question.** When avoiding shortcuts costs effort that never appears in shipped output, does the Kantian (κ = 1) acceptance gate lower realized welfare cost by more than 0.002 compared with the strongest tested budget-balanced transfer? Separately, how does it compare with the ambient tax, which needs a treasury?
- **Scope.** A simulator, finite noisy policy search, verified current policies, mandatory assignment. Nothing here measures voluntary adoption or real teams.

## Model

- **Fixed settings.** The shared-codebase environment of E9–E12 with n = 6, T = 20, γ = 0.25 (concealment cost), heterogeneity 0, and all other constants pinned.
- **Factors.** Effort ρ ∈ {0, 0.15} crossed with exposure skew ∈ {0, 1.5}.
- **The effort cost.** Each period an agent pays ρ · capA · (1 − s)² in real cost:
  - capA = `b.cap` × module size is policy-invariant, pre-downtime capacity, and is not scaled by output value;
  - it is not shipped output, so no output-based charge sees it;
  - with ρ = 0 the simulator is unchanged (tested).
  - For scale: at s = 0 a shortcut's marginal own-output gain is 2·boost = 1.2 per unit capacity, against an effort saving of 2ρ = 0.3.
- **Channels between agents.** Peers' costs depend on an agent's policy only through shared debt and hence incidents (tested). So the level-1 ambient charge gives an agent the exact unilateral welfare contrast, with effort on or off (tested).
- **What equal sharing does with effort on.** With unit output value, level-1 pooling gives n·Δprivate = ΔW + (n − 1)·ΔK_i (tested). Each agent overweights its own effort saving, which pushes it towards shortcuts.

## Arms

Every arm runs the same pinned search loop:
- 40 synchronous generations, 4 candidates per agent per generation;
- 16 paired development scenarios per score;
- mutation scale 0.15 falling to 0.03, min_t = 0;
- the same initial profiles and mutation draws per seed.

That is 16,000 agent-search scenarios per run, asserted by the analysis. Arms differ only in the private cost the gate reads. Transfers t_i are debits, enter the private cost only, and never enter the reported welfare cost W = Σ(ledger + effort).

| Arm | Gate reads | Transfer | Budget |
|---|---|---|---|
| private | κ = 0, own unilateral change | none | — |
| kantian | κ = 1, own cost when every agent makes the proposer's **realized** clipped change (`linear_realized`); peers clipped | none | — |
| pool_λ | κ = 0 | λ(Y_i − Ȳ), shipped output | exactly balanced |
| direct_λ / directrole_λ | κ = 0 | τ_i h_i − (1/(n−1)) Σ_{j≠i} τ_j h_j, with h = s(1 + 0.5m) the verified load; τ_i = λ·c (common) or λ·c·n(1 − e_i/Σe)/(n−1) (role); c is the calibrated scale | exactly balanced; own rebate fixed |
| contract | κ = 0 | E_i − mean(E), with E_i = Σ_{j≠i}[L_j(P) − L_j(p_i⁰, P_{−i})] (peers' ledger change when i resets to the anchor p⁰), computed by exact simulator resets on the same scenarios | exactly balanced |
| ambient_λ | κ = 0 | λ · (incident loss in other modules) | budget-breaking (treasury) |

- **Change from E1–E12.** κ = 1 now broadcasts the realized change (`linear_realized`, E12's corrected convention), not the raw proposed change.
- **Not included:** an estimated hidden-action regime, flexible output schedules, higher-order or order-2 subset contracts, joint packages, opt-in, veto and escrow. Any claim is limited to this menu.
- **Compute.** The contract needs n reset simulations per scored profile. The operator's reset simulations are counted and reported separately (`total_sims`) as part of that mechanism's cost; the agent search budget is equal across arms.

## Stage 1: calibration (dev seeds 2000–2019)

- **Direct-charge scale c, per skew.** Take a uniform random profile per seed and 32 `base` dev scenarios starting at 990,000,000 + 32·(seed mod 1000). Move each agent's s by ±0.05, clipped, with peers fixed. c is the mean over seeds and agents of Δ(peers' ledger cost) / Δ(load) (`e13.marginal_damage`).
- **Contract anchor.** For each anchor, (0, 0, 0) and (0.5, 0, 0.5), run the private learner under the contract in both effort-on cells. Evaluate on dev block 900,000,000 (100 scenarios per family). Keep the anchor with the lower mean over both cells; ties go to (0, 0, 0).

## Stage 2: selection (dev seeds 2100–2119, effort-on cells only)

- **Arms run in each effort-on cell:**
  - private and kantian;
  - pool_λ, ambient_λ and direct_λ for λ ∈ {0.25, 0.5, 1, 1.5, 2, 4};
  - directrole_λ at skew 1.5 only (at skew 0 it equals direct);
  - the contract with the locked anchor.
- **Evaluation.** Dev block 950,000,000, 100 scenarios per family.
- **Choosing the comparators.** In each cell, the strict comparator is the arm with the lowest mean normalized cost among pool, direct, directrole and contract. The ambient comparator is the lowest among the ambient arms. Ties go by manifest order (`e13.experiments("select")`).
- **Edges.** A choice at a grid edge is reported as such. The grid is not expanded.
- **Recorded in the lock before confirmation:**
  - the expected simultaneous half-width t₁₉(1 − 0.0125/2)·sd/√20, from the validation differences against the gate;
  - the compute-matched M for sensitivity 3: the largest integer with 40·2M·25 ≤ the contract's median total simulations.

## Stage 3: confirmation (seeds 3000–3019)

- **Arms.**
  - In every cell: private, kantian, pool_1.0 and ambient_1.0.
  - In the effort-on cells, also the locked strict and ambient comparators, unless they coincide with a level-1 arm.
- **Evaluation.** A fresh holdout block: indices 1,000,000–1,000,099 in each of the five families. E1–E12 used indices 0–99. Every seed and arm sees the same block.
- **Score.** Normalized welfare cost: per-scenario W / nominal, averaged within each family, then equally across the five families. Seed-paired uncertainty is conditional on this fixed block.

## Primary analysis (confirmatory)

- **Contrasts.** Δ = cost(comparator) − cost(kantian), paired by seed (n = 20). Positive favours the gate. There are four contrasts: {strict, ambient} × {skew 0, skew 1.5}, all with effort on.
- **Intervals.** Bonferroni familywise 95 %: t intervals with t₁₉ at 1 − 0.0125/2. Margin ±0.002.

| Simultaneous interval | Verdict |
|---|---|
| lower > +0.002 | practically meaningful gate advantage in that cell |
| upper < −0.002 | practically meaningful comparator advantage |
| within [−0.002, +0.002] | practical equivalence |
| otherwise | inconclusive |

**Kill criterion.** If the strict comparator's simultaneous upper bound is ≤ +0.002 in **both** effort-on cells, the gate-advantage line closes for budget-balanced settings too, and the report says so. A gate advantage in one cell is reported for that cell only. A gate loss to the ambient tax limits any gate edge to the setting without a treasury.

## Secondary tests (Holm over three, one-sided, α = 0.05)

- **S1.** Effort widens the pool_1.0 − ambient_1.0 gap. Per seed, (gap with effort on − gap with effort off), averaged over the skews, > 0.
- **S2.** With effort on, unequal exposure widens the kantian − ambient_1.0 gap. Per seed, gap(skew 1.5) − gap(skew 0) > 0.
- **S3.** The tuned direct charge **and** the contract have smaller marginal-incentive error than pool_1.0. This uses held-back dev seeds 2200–2219 and 16 `base` dev scenarios from 980,000,000 + 16·(seed mod 1000), at a uniform random profile with 4 random unilateral moves (SD 0.1) per agent.
  - Error is |c·Δown − ΔW|, where ΔW is the exact unilateral welfare contrast; c = n for pool_1.0 and c = 1 otherwise.
  - The tuned direct charge is the direct or directrole arm with the lowest validation mean.
  - Per seed, the error difference is averaged over the effort-on skews. The test's p is the larger of the two one-sided p values (direct, contract).
  - ambient_1.0's error is reported as an identity check; it should be 0.

## Directional predictions (post-pilot; reported held/failed by the sign of the paired mean and whether its 95 % interval excludes 0)

- **D1.** The gate beats pool_1.0 in both effort-on cells. Pilot: 0.2773 vs 0.2955 and 0.2659 vs 0.2727.
- **D2.** The ambient comparator beats the gate in both effort-on cells. Pilot: 0.2755 vs 0.2773 and 0.2518 vs 0.2659.
- **D3.** S1–S3 hold in the stated direction.
- **No prediction** is made for the primary strict comparison. The untuned pilot contract trailed the gate at skew 0 (0.2811 vs 0.2773) and led it at skew 1.5 (0.2534 vs 0.2659).

## Invariants (a failure stops the analysis before any interpretation)

- With effort off, pool_1.0 and ambient_1.0 produce identical final profiles for every seed at both skews.
- Every strict transfer sums to zero in every holdout scenario (|Σt| < 1e-6).
- Every confirmatory run spent exactly 16,000 agent-search scenarios.
- No run read a holdout scenario during search (enforced by `DevSampler`).
- Seed and scenario namespaces are disjoint (tested).

## Descriptive reporting

For every arm and cell, report:
- cost, effort cost, and mean policy (s, m, q) by agent and exposure role;
- the share of agents whose holdout cost including settlement exceeds their cost under the private arm on the same seed;
- the mean 95th-percentile and maximum absolute settlement as a share of the module's nominal value;
- search and total simulations, and run time.

## Sensitivities (labelled; outside selection and inference)

Each is reported as comparator − gate with the same intervals.

1. **Peer noise.** The gate, and the selected strict arm if it is direct or contract, score against peers' policies plus N(0, 0.1²) noise, clipped. The noise is drawn once per (seed, generation, peer) from a stream common to all arms. The focal policy is exact; deployment and settlement use true policies.
2. **Cap.** The selected strict arm with each scenario's settlement vector scaled by a common factor, so that |t_i| ≤ 10 % of the module's ex ante nominal value. This keeps the vector balanced.
3. **Compute-matched gate.** κ = 1 with the locked larger M, against the selected strict arm.

## Failure policy

- A run that fails for a recoverable reason is retried once with the identical seed and configuration.
- A primary contrast with incomplete pairs is reported as inconclusive, with complete-pair values given descriptively.
- Failed attempts are logged.
- No new seeds, levels, scales, arms or outcome measures are added after this freeze.

## Commands

```
EVO_WORKERS=4 OPENBLAS_NUM_THREADS=1 uv run python -m evortgs.e13 calib lock
EVO_WORKERS=4 OPENBLAS_NUM_THREADS=1 uv run python -m evortgs.e13 select lock
# commit runs/e13_lock.json and the calibration/selection records before continuing
EVO_WORKERS=4 OPENBLAS_NUM_THREADS=1 uv run python -m evortgs.e13 E13 E13sens
uv run python -m evortgs.analysis_e13
```

## Appendix: exploratory pilot (outside the repository, not reproducible from it)

Normalized holdout-style cost on 20 pilot scenarios per family per seed. Six seeds, 8 generations. Lower is better.

| ρ | skew | private | kantian | pool | ambient | direct (untuned, s only) | contract (anchor 0) |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 0.3000 | 0.2617 | 0.2589 | 0.2589 | 0.2986 | 0.2609 |
| 0 | 1.5 | 0.2648 | 0.2512 | 0.2415 | 0.2415 | 0.2621 | 0.2393 |
| 0.15 | 0 | 0.3114 | 0.2773 | 0.2955 | 0.2755 | 0.3101 | 0.2811 |
| 0.15 | 1.5 | 0.2781 | 0.2659 | 0.2727 | 0.2518 | 0.2781 | 0.2534 |

Pool and ambient profiles matched in 6/6 runs with effort off and 0/6 with effort on, at both skews.
