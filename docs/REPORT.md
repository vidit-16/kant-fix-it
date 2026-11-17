# Acceptance gates for co-evolving agents: a pre-registered study in a stylized payment network

Research report, 17 November 2026. Status: single-site, unreviewed,
unreplicated. Full detail, audit trail and decision log are in
[PROJECT.md](PROJECT.md); the frozen protocol is in
[PREREGISTRATION.md](PREREGISTRATION.md).

## Abstract

Self-improving agent systems share a propose–evaluate–accept loop and are
usually evaluated against a fixed benchmark. When several such loops share an
environment, each accepted change alters the conditions under which the others
are evaluated. We isolate the acceptance gate as the experimental factor. Six
bank agents in a stylized real-time gross settlement network repeatedly mutate
a three-parameter liquidity policy; proposals, search budget and environment
are identical across arms and only the gate differs. In a pre-registered study
(20 paired seeds, 950 runs, five held-out shock families) private gates leave
the system 29 % more costly than a symmetric planner. A universalization gate,
which reads only the agent's own cost in the counterfactual where every agent
makes the same change, removes 51 % of that gap (95 % CI 41–63 %), with a
monotone dose response and transfer to every held-out family. Two registered
predictions failed: heterogeneity in bank size did not erode the gain, and a
single private defector did not profit. A unilateral welfare gate with full
cost visibility did worse than universalization, while a joint-move welfare
gate did best, indicating that evaluating coordinated changes matters more
than observing others' costs. A conventional delay surcharge with private
gates matched the best gate. The gate is therefore a consequential design
choice, but in this low-dimensional setting it offers no advantage over
pricing.

## 1. Background

The payment-timing game is a standard example of privately rational behaviour
with collective cost: delaying payments to recycle incoming funds saves
liquidity for one bank and withholds it from others (Bech and Garratt 2003;
Galbiati and Soramäki 2011). Learning agents in such games have been studied
with reinforcement learning (Castro et al. 2021) and, in single-agent form,
with language models (BIS WP 1310). Stabilising mechanisms for societies of
language-model agents in financial coordination games are studied in FRAIL
(arXiv 2609.30940). Universalization has been used as a decision-time prompt
(Piatti et al., NeurIPS 2024). Kantian optimisation (Roemer) and *homo
moralis* preferences (Alger and Weibull 2013) supply the theory for a gate
parameterised by a degree of morality κ. We did not find prior work that
treats the acceptance rule of co-evolving agents as the experimental factor at
matched budget; our search was targeted, not systematic.

## 2. Method

**Environment.** Six banks, 20 ticks, integer money, no intraday credit.
Policy: opening liquidity fraction, buffer fraction, hold time. Sender-borne
costs: liquidity 1, full-day delay 0.5, deadline miss 2, unsettled at close
10. 85 % of payments lie on closed cycles so that liquidity serves timing
rather than net funding.

**Evolution.** 40 generations; each bank proposes four Gaussian mutations per
generation; each candidate is scored on 16 fresh development scenarios; the
best is accepted if the gate's score is negative; all banks update together.
Every gate spends the same number of simulations.

**Gates.** κ ∈ {0, 0.25, 0.5, 0.75, 1} mixes own cost under a unilateral
change (κ = 0, private) with own cost when all banks make the same shift
(κ = 1). Comparators: unilateral welfare, joint welfare, no-harm, private
gates under a delay surcharge chosen on development data, and a symmetric
planner.

**Evaluation.** Final profiles are scored on 100 held-out scenarios in each of
five families, four of them shocks never seen in evolution. Accounting
invariants are checked in every evaluation simulation. Statistics: paired by
seed, percentile bootstrap, Wilcoxon signed-rank, Holm correction where
registered.

**Integrity.** The evolution module cannot import the evaluator or construct
holdout scenarios (tested); the cost regime and budget were chosen on separate
pilot seeds and a separate scenario split; the protocol was committed before
confirmatory runs.

## 3. Results

Holdout system cost per unit of payment value, mean of five families.

| Arm | Cost (95 % CI) |
|---|---|
| private κ=0 | 1.125 (1.093–1.160) |
| κ=0.5 | 1.051 (1.030–1.074) |
| universalization κ=1 | 0.997 (0.973–1.021) |
| welfare, unilateral | 1.051 (1.010–1.100) |
| no-harm | 0.901 (0.881–0.921) |
| welfare, joint | 0.864 (0.851–0.878) |
| private + surcharge | 0.876 (0.858–0.894) |
| symmetric planner | 0.874 (0.839–0.911) |

Registered hypotheses: H1 supported (+29 %); H2 supported at the threshold
(closure 0.51); H2b supported (Spearman −0.58); H3 refuted (closure 0.51,
0.39, 0.52 across heterogeneity levels); H4 supported in all five families;
H5 refuted (defector gain +0.002, CI −0.004 to +0.008); H6 supported
(−0.054 against unilateral welfare).

Robustness: the universalization advantage holds for delay costs 0.1, 2 and 6
(closure 0.45–0.54), with sequential updates, with ten banks, and grows at
three times the budget (−0.186 against private on the same ten seeds).

Post hoc (E7, not registered): requiring a paired t-statistic below −2 for
acceptance preserves the ordering private > unilateral welfare >
universalization > surcharge, removes the no-harm gate's advantage, and makes
every arm much worse at this budget.

![gates](../runs/fig_gates.png)

## 4. Discussion

*Joint moves, not altruism.* The unilateral welfare gate is the textbook
cooperative learner and it underperforms a gate that never sees another
agent's cost. In this game improvements are visible only when several banks
shift together; a unilateral probe of a good joint direction looks bad. The
universalization gate works mainly as a way of evaluating coordinated moves.

*Pricing is enough here.* The surcharge needs no change to the agents and no
counterfactual simulation of others. With three policy parameters one price
aligns incentives. Whether that survives richer policy spaces, where a price
can be gamed, is the question that decides if gates deserve further study.

*Failed predictions.* The absence of a heterogeneity effect and of a defector
gain may reflect the small policy space and noisy search rather than
properties of the gate. They are reported as registered and not interpreted
further.

## 5. Limitations

* Toy model: six banks, three parameters, uncalibrated costs, no
  liquidity-saving mechanism, 3–7 % of value left unsettled.
* The dilemma exists only under balanced flows; with independent flows all
  gates coincided.
* Acceptance is noise-dominated (about five of six proposals accepted per
  generation); the no-harm ranking is not robust to this.
* The symmetric planner is a weak reference; gap closure is understated
  relative to the best arm.
* Mutation-based proposals. No language model is involved, so the connection
  to self-evolving language-model agents is an analogy, not a result.
* One environment. No claim of generality, and no claim about recursive
  self-improvement.
* Prior-art search was targeted; several 2026 preprints were read at abstract
  level only.

## 6. Next

Language-model proposers behind the same gate interface; rule-level policies
to test whether pricing still matches gates; noise-aware gates as a registered
factor; a stronger reference optimum; a second domain.

## References

* Alger, I., Weibull, J. (2013). Homo moralis. *Econometrica* 81(6).
* Bech, M., Garratt, R. (2003). The intraday liquidity management game. *J. Econ. Theory* 109(2).
* Castro, P. S., Desai, A., Du, H., Garratt, R., Rivadeneyra, F. (2021). Estimating policy functions in payments systems using reinforcement learning. Bank of Canada SWP 2021-7.
* Fu, Z., Xu, R., Ren, Q. (2026). Financial fragility in societies of LLM agents. arXiv:2609.30940.
* Galbiati, M., Soramäki, K. (2011). An agent-based model of payment systems. *J. Econ. Dyn. Control* 35(6).
* Piatti, G. et al. (2024). Cooperate or collapse. NeurIPS 2024, arXiv:2404.16698.
* Qu, A. et al. (2026). CORAL. arXiv:2604.01658.
* Roemer, J. (2019). *How We Cooperate*. Yale University Press.
* Srikanth, D. et al. (2026). Recursive self-improvement of AI research agents. arXiv:2609.26457.
* Zhang, J. et al. (2026). Hyperagents. arXiv:2603.19461.
