# EvoRTGS — canonical project document

Single source of truth for decisions, evidence, status and open questions.
Supersedes the handoff of 17 November 2026 where they conflict.
Last updated: 17 November 2026.

Related files: [PREREGISTRATION.md](PREREGISTRATION.md) and
[PREREGISTRATION_E8.md](PREREGISTRATION_E8.md) (frozen protocols),
[REPORT.md](REPORT.md) (paper-style write-up), `runs/` (raw records,
`results.json`, `results_e8.json`).

---

## 1. Where the project stands

| Item | Status |
|---|---|
| Novelty audit | Done at the level of a targeted review, not a systematic one (§3) |
| Research question | Narrowed and frozen (§2) |
| Simulator, evolution loop, evaluator | Built, 40 tests passing |
| Pre-registration | Committed before confirmatory runs (`4d6ebe9`) |
| Confirmatory experiments E1–E6 | Run, 950 runs, analysed (§5) |
| Post hoc ablation E7 | Run, labelled exploratory (§5.7) |
| Rule-level policies, second pre-registration | Committed before E8 runs (`9729748`) |
| Confirmatory experiment E8 (gates against pricing) | Run, 520 runs, analysed (§5.8) |
| Language-model proposers | Not started; needs a model API key and a budget decision (§7) |
| Transfer to a second domain | Not started |
| External replication, peer review | None |

One-sentence state: a working, tested, reproducible testbed and two
pre-registered studies exist; together they show that the acceptance gate is a
consequential design choice but that, in this environment, a delay price beats
every gate tested, with three-parameter and with rule-level policies alike; no
novelty claim is made.

## 2. Direction taken, and why it differs from the handoff

### 2.1 What was dropped

The handoff's H1 had two halves. Both fail as novelty claims:

* *"Independently improving banks can worsen system outcomes."* This is the
  textbook result of the payment-timing literature: Bech and Garratt (2003)
  show the intraday liquidity game is a prisoner's dilemma or stag hunt
  depending on credit policy, and Galbiati and Soramäki (2008/2011) find
  learned equilibrium liquidity below the efficient level over a wide range of
  costs. It can serve as a validity check for a simulator, not as a finding.
* *"An adaptive system-aware coordinator reduces the trade-off."* A planner
  that adapts rules while agents learn is the two-level structure of
  learned-mechanism-design work (for example the AI Economist line), and
  FRAIL (2026) already tests stabilising mechanisms for LLM agent societies in
  financial coordination games. "Adaptive coordinator" was also undefined
  enough to be rescued by any outcome.

The 2 × 2 design (fixed/evolving × fixed/adaptive) was therefore replaced.

### 2.2 What replaced it

Every self-improvement loop — DGM, Hyperagents, CORAL, AIDE², MASS, and the
financial skill-evolution systems — has the same skeleton: propose a change,
evaluate it, accept or reject. The published systems evaluate against a fixed
benchmark. When several such loops run in a shared environment, each
acceptance changes the environment the others are evaluated in, and "verified
improvement" stops being well defined. The **acceptance gate** is then a
design object in its own right.

**Research question.** Holding the proposal mechanism, the search budget and
the environment fixed, how much of the efficiency loss from independent
self-improvement is removed by changing only the acceptance gate, and what
information does each gate need?

Gates are ordered by what they must observe:

1. private gate — own cost, unilateral change (κ = 0);
2. universalization gate — own cost in the counterfactual where every agent
   makes the same shift (κ = 1). This is the acceptance-rule form of Roemer's
   Kantian optimisation and of Alger and Weibull's *homo moralis* with degree
   of morality κ; intermediate κ gives a dose-response test;
3. gates that read everyone's costs — unilateral welfare, joint welfare,
   no-harm;
4. the classical remedy that leaves the gate private and changes the game —
   an operator surcharge on delay.

EvoRTGS stays as the test environment because the payment-timing game has
known theory to validate against and a natural operator who could impose a
gate or a fee.

### 2.3 Honest assessment of the contribution

* The game theory is not new. Universalization as *decision-time prompting*
  for LLM agents exists (GovSim, NeurIPS 2024; an ICML 2026 workshop paper on
  Kantian equilibrium). Universalization as the *selection rule of a
  self-evolution loop*, compared at matched budget against welfare gates and a
  Pigouvian baseline with held-out shocks, was not found in the search. That
  is "not found", not "does not exist".
* The realistic contribution type is **empirical plus testbed**, not a new
  algorithm. The main result below includes a negative: a plain delay
  surcharge with selfish gates does as well as the best gate.
* Nothing here is evidence about recursive self-improvement in the strong
  sense. The agents tune three numbers; the loop itself does not change.

## 3. Novelty audit

### 3.1 Method and limits

Sources: web search (17 Nov 2026) plus direct reads of arXiv abstract pages,
the BIS project page, one GitHub repository and one conference page. Full
texts were read only for FRAIL (partly) and GovSim (partly). Two PDFs
(Galbiati–Soramäki; Castro et al.) could not be text-extracted and are cited
from abstracts and catalogue text only. OpenReview was blocked. This is a
targeted review. Blind spots: SSRN, central-bank working papers not indexed
by the search engine, non-English sources, anything published in the last few
weeks, and the full texts of most 2026 preprints.

### 3.2 Verified facts

| Work | Verified | Relevance |
|---|---|---|
| CORAL, arXiv 2604.01658 (v3 Sep 2026) | exists; multi-agent evolution infrastructure with evaluator separation | evolution loop against fixed graders; no strategic interaction between owners |
| Hyperagents, arXiv 2603.19461 | exists; editable meta-level | single lineage, fixed benchmarks |
| MASS, arXiv 2610.12176 | exists; workflow search + fine-tuning on own trajectories | same |
| AIDE², arXiv 2609.26457 | exists; reports reward hacking falling 55 %→32 % (author-reported) | same; shows gate integrity matters |
| Misevolve, arXiv 2509.26354 (ICLR 2026) | exists | single-agent evolution going wrong; not multi-principal externalities |
| Co-evolution survey, arXiv 2608.10299 | exists; abstract does not mention social dilemmas or multi-principal externalities (body not read) | closest taxonomy |
| Internal vs. External, arXiv 2605.09128 | exists; evolved vs deliberated constitutions in public-goods games | evolution of *shared rules*, not of per-agent acceptance gates |
| Economy of Minds, arXiv 2606.02859 (NeurIPS 2026) | exists; auctions and bankruptcy as selection | economic selection inside one system |
| FRAIL, arXiv 2609.30940 | exists; bank run, debt rollover, crowdfunding; three commitment mechanisms; agents appear to be fixed-policy LLMs; no payment network | closest on "financial coordination failure + stabilisers"; no policy evolution |
| FinEvo-Bench, arXiv 2608.06144 | exists; longitudinal single-agent professional tasks | not interactive |
| BIS Project Agenti | page exists, "ongoing", last updated 14 Oct 2026; describes an RTGS-like agentic simulator that "will be used"; no code, no results | closest institutional overlap; cannot be compared or reused |
| BIS WP 1310 / BoC SWP 2025-35 | exists; single prompted agent, simple settings | not multi-agent |
| GovSim, arXiv 2404.16698 (NeurIPS 2024) | universalization is a sentence injected at decision time | closest on universalization |
| "Kantian Equilibrium in the Age of Multi-Agent Systems" (ICML 2026 workshop poster) | abstract only: Kantian prompting in a commons game | same; prompting, not selection |
| Bech & Garratt 2003; Galbiati & Soramäki 2008/2011; Castro et al. 2021/2025 | abstracts and catalogue text | the phenomenon and learning in payment games are established |
| PSSimPy (MIT, ICIS 2024 paper) | repository exists; queues, credit facility, strategic bank hook; small user base | candidate reference simulator for cross-validation |

Handoff items **not** re-verified here: ADAS, AFlow, AgentSquare, EvoAgentX,
Swarm Skills, Adaptive Orchestration, RSIAgent, RSIBench(-Data), AI4AI-Bench,
SEA-Eval, SEABench, FinSkillOps, FinSkillBench, EvolveTrade, EvoTS-Agent,
SHARP, MARS, MarketSim, the ECB bulletin, the IMF note, the Bundesbank
article, the BoE FSR and the FSB report. None of them bears on the narrowed
question except as background; cite only after checking.

### 3.3 Novelty map

* **Established:** self-modifying agents; workflow search; local optimisation
  harming payment-system efficiency; RL/LLM agents in payment settings;
  mechanisms that stabilise LLM financial games; universalization prompting.
* **Partial overlap:** homo-moralis/Kantian evolutionary theory (analytical,
  about preferences, not about acceptance rules in search loops);
  constitutional evolution for agent groups.
* **Not found:** acceptance gates of co-evolving agents compared as the
  experimental factor, with information requirements, matched budget,
  held-out shocks and a Pigouvian baseline.
* **Unknown:** full texts of the 2026 preprints; anything inside Project
  Agenti.

## 4. System

### 4.1 Architecture

```
scenarios.py   pure function (config, family, split, index) -> Scenario
sim.py         deterministic settlement engine and cost accounting
evolve.py      propose / evaluate / gate loop; sees only a DevSampler
evaluate.py    locked holdout evaluation with invariant checks on
experiments.py experiment definitions, parallel runner, JSONL records
analysis.py    pre-registered statistics, results.json, figures
```

Trust boundaries: a policy is three numbers in [0, 1] validated on every
call; scenarios and results are immutable; `evolve.py` cannot import the
evaluator or construct a holdout scenario (enforced by a test that parses its
source); development and holdout seeds are separated by a split tag in the
seed.

### 4.2 Model

Six banks (ten in a robustness run), 20 ticks, integer money, no intraday
credit, no liquidity-saving mechanism. A bank posts opening liquidity as a
fraction of its expected outflow, keeps a buffer, and may hold ordinary
payments for a number of ticks; time-critical payments go out on arrival.
Costs fall on the sender: liquidity 1, delay `d` per day, deadline miss 2,
unsettled at close 10. Conservation: total balances equal total posted
liquidity after every settlement; no balance is negative.

Holdout families: `base`, `surge`, `outage`, `late_heavy`, `hub`. Evolution
sees `base` development scenarios only.

### 4.3 Stack and what was left out

| Used | Why |
|---|---|
| Python 3.12, uv, lockfile | reproducible environment |
| NumPy, SciPy | arrays, bootstrap, Wilcoxon |
| pytest, Hypothesis | hand-computed cases and property tests of accounting |
| matplotlib | two figures |
| multiprocessing, JSONL, git | parallel runs and an append-only record with commit hash |

| Proposed in handoff | Decision |
|---|---|
| SimPy | not used; a 60-line tick loop is simpler to audit and test |
| Pydantic | not used; frozen dataclasses and one validator cover three floats |
| NetworkX, DuckDB, Parquet, SQLite | not needed at 1 000 runs |
| LangGraph, LangChain, LangSmith/Langfuse | no language model in the loop yet; revisit only if the proposer stage needs resumable long runs |
| Docker | no generated code is executed; revisit at code-level proposals |
| Streamlit/Next.js | no UI until there is a result worth browsing |
| CORAL | relevant when proposals become code edits by coding agents; not for parameter search |
| Jev, Laya | identities still unconfirmed; not needed |
| PSSimPy | not used as engine (speed, control of invariants); planned as an independent cross-check |

## 5. Results

All numbers: holdout system cost per unit of payment value, mean over five
families, 20 paired seeds, 95 % bootstrap intervals. Lower is better. 950
confirmatory runs; every evaluation simulation ran with invariant checks and
none failed.

### 5.1 Gate 2 first failed, then passed

The first scenario generator drew payments independently. Liquidity then
funded net positions, a bank that under-provided hurt only itself, and all
gates coincided (pilot, `pilot` split). After switching to balanced cyclic
flows — the realistic case in which turnover is many times liquidity — a
unilateral cut from the planner's liquidity level became privately profitable
and costly to others (best response to 0.40 is 0.20; symmetric
price-of-anarchy estimates 1.03–1.15). The dilemma is a property of the flow
structure, and the result below is conditional on it.

### 5.2 Arms (E1, homogeneous banks, d = 0.5)

| Arm | Reads | Cost | 95 % CI | Unsettled | Delay (ticks) | Liquidity |
|---|---|---|---|---|---|---|
| private κ=0 | own | 1.125 | 1.093–1.160 | 7.0 % | 5.66 | 0.22 |
| κ=0.25 | own | 1.060 | 1.030–1.089 | 6.4 % | 4.80 | 0.25 |
| κ=0.5 | own | 1.051 | 1.030–1.074 | 6.6 % | 3.80 | 0.26 |
| κ=0.75 | own | 1.014 | 0.993–1.035 | 6.1 % | 3.79 | 0.27 |
| universalization κ=1 | own | 0.997 | 0.973–1.021 | 5.9 % | 3.22 | 0.29 |
| welfare, unilateral | all | 1.051 | 1.010–1.100 | 6.5 % | 3.87 | 0.26 |
| no-harm | all | 0.901 | 0.881–0.921 | 5.1 % | 1.55 | 0.33 |
| welfare, joint | all | 0.864 | 0.851–0.878 | 3.2 % | 1.38 | 0.48 |
| private + surcharge 8 | own | 0.876 | 0.858–0.894 | 5.2 % | 0.96 | 0.29 |
| symmetric planner (reference) | all | 0.874 | 0.839–0.911 | 3.8 % | 3.12 | 0.39 |

### 5.3 Pre-registered hypotheses

| | Claim | Outcome |
|---|---|---|
| H1 | private gate is at least 5 % worse than the planner | **Supported.** +0.251 (0.196–0.308), +29 %, p < 10⁻⁵ |
| H2 | universalization gate closes at least half the gap | **Supported, barely.** 0.51 (0.41–0.63) |
| H2b | cost falls as κ rises | **Supported.** Spearman −0.58 (−0.69 to −0.48); means monotone |
| H3 | heterogeneity erodes the gain | **Refuted.** Closure 0.51 / 0.39 / 0.52 at heterogeneity 0 / 0.75 / 1.5; difference −0.004 (−0.18 to 0.17). No bank rank is worse off under κ=1 at any level |
| H4 | gain transfers to each unseen shock family | **Supported.** All five, Holm p ≤ 4×10⁻⁵; largest in `late_heavy` |
| H5 | one private defector among universalizing banks gains | **Refuted.** Own-cost change +0.002 (−0.004 to +0.008); system cost unchanged |
| H6 | universalization beats unilateral welfare (pilot-suggested) | **Supported.** −0.054 (−0.089 to −0.021) |

### 5.4 What the results say

1. **The gate matters.** With proposals, budget and environment fixed, the
   choice of gate moves system cost by 23 % (1.125 to 0.864).
2. **A gate that reads only the agent's own cost recovers about half the
   loss**, in every cost regime tried (closure 0.45–0.54, E3), with ten banks,
   with sequential updates (E5), and with three times the budget, where its
   margin over the private gate grows from 0.112 to 0.186 on the same seeds
   (E6).
3. **Evaluating joint moves matters more than reading others' costs.**
   Unilateral welfare (full information) is worse than universalization (own
   cost only); joint welfare is the best gate. The bottleneck in this game is
   that useful changes are only visible when several banks move together.
4. **The classical remedy is as good as any gate.** A delay surcharge chosen
   on development data, with every bank keeping a private gate, reaches 0.876
   — statistically indistinguishable from the planner reference (+0.002,
   −0.038 to +0.041) and from no-harm (p = 0.08), and 12 % better than the
   universalization gate. Anyone who can impose a gate can impose a fee, and
   the fee needs no change to the agents.
5. **Two predicted weaknesses did not show up.** Heterogeneity did not erode
   the universalization gate, and a lone defector did not profit. Both are
   absences of evidence at this budget and in a three-parameter policy space;
   the defector result in particular should not be read as "the gate is
   incentive compatible".

### 5.5 Deviations from the pre-registration and weaknesses found

* The symmetric planner is a weak reference: joint welfare beats it, and the
  surcharge and no-harm arms match it. Gap closure is reported as registered
  but understates the gap to the best achievable outcome.
* The planner's delay (3.1 ticks) shows its search had not converged on the
  hold parameter.
* **Acceptance is noise-dominated.** Gates accept whenever the estimated
  change is negative; with four candidates and sixteen scenarios, about five
  of six banks accept something every generation, even at the end. The
  no-harm gate accepts 3.2 of 6 and may owe part of its advantage to being
  conservative. This motivated E7.
* Residual unsettled value is 3–7 %, far above real systems, because there is
  no liquidity-saving mechanism and no end-of-day credit.

### 5.6 Robustness

| Check | Private | Universalization | Unilateral welfare |
|---|---|---|---|
| d = 0.1 | 0.994 | 0.905 | 0.950 |
| d = 2 | 1.074 | 0.949 | 1.014 |
| d = 6 | 1.086 | 1.008 | 1.042 |
| sequential updates | 1.123 | 0.985 | 1.054 |
| ten banks | 1.143 | 0.984 | 1.074 |
| 120 generations (10 seeds) | 1.125 | 0.939 | 1.040 |

### 5.7 E7 — post hoc, not pre-registered

Added after seeing the confirmatory results, to test whether the gate ranking
is an artefact of noisy acceptance. Each gate accepts only if the paired
t-statistic of its score is below −2. Same seeds, budget and regime.

| Arm | Cost | 95 % CI | Accepted per generation (of 6) |
|---|---|---|---|
| private κ=0 | 1.538 | 1.493–1.584 | 1.25 |
| welfare, unilateral | 1.348 | 1.312–1.389 | 0.89 |
| no-harm | 1.290 | 1.222–1.360 | 1.03 |
| universalization κ=1 | 1.249 | 1.224–1.272 | 1.30 |
| private + surcharge 8 | 1.117 | 1.082–1.155 | 1.50 |

* The ordering private > unilateral welfare > universalization > surcharge
  survives (κ=1 vs κ=0: −0.289, −0.338 to −0.240; surcharge vs κ=1: −0.133,
  −0.168 to −0.093).
* The no-harm gate's advantage over universalization does **not** survive
  (+0.041, −0.029 to +0.113). Its E1 ranking should be treated as unreliable.
* Every thresholded arm is far worse than its unthresholded counterpart at
  this budget: strict acceptance starves the search within 40 generations.
  Permissive, noisy acceptance was the better search strategy here. Whether
  that reverses at larger budgets is untested.

### 5.8 E8 — gates against pricing with rule-level policies (pre-registered)

Protocol: [PREREGISTRATION_E8.md](PREREGISTRATION_E8.md), frozen in `9729748`
after a pilot on separate seeds (`runs/pilot2.jsonl`). Policies become eight
numbers: opening liquidity, morning and afternoon buffers, hold time, an
opening tick, a size threshold, a hold time for large payments and a bilateral
net sending limit. The three-parameter space is exactly nested in it (tested).
Budget, environment and seeds are those of E1. A second, coarser price was
added: a two-band tariff charged on value settled in the second half of the
day. Price levels are chosen on development cost and reported on holdout.

| Arm | Three parameters | Eight parameters |
|---|---|---|
| private gate | 1.125 (1.093–1.160) | 1.145 (1.113–1.179) |
| universalization gate | 0.997 (0.973–1.022) | 1.022 (1.008–1.037) |
| welfare gate, unilateral | 1.051 (1.010–1.100) | 1.059 (1.033–1.087) |
| welfare gate, joint | 0.864 (0.851–0.878) | 0.929 (0.911–0.952) |
| private + delay surcharge (level 16) | 0.815 (0.804–0.829) | 0.863 (0.850–0.876) |
| private + band tariff (level 4 / 2) | 0.845 (0.835–0.857) | 0.979 (0.952–1.008) |
| symmetric planner (reference) | 0.874 (0.839–0.910) | 0.934 (0.911–0.958) |

The four gate arms in the three-parameter column reproduce E1 to the last
digit, which confirms the engine extension did not change existing behaviour.

| Hypothesis | Outcome |
|---|---|
| R1 pricing still matches or beats gates | **Supported.** Surcharge vs universalization −0.159 (−0.180 to −0.138); vs joint welfare −0.066 (−0.091 to −0.045) |
| R2 gates degrade with richness more than pricing | **Not supported.** Interaction +0.017 (−0.013 to +0.049). Joint welfare worsens by 0.065, the surcharge by 0.048 |
| R3 gate ordering survives | **Supported.** Universalization vs private −0.123 (−0.148 to −0.099); vs unilateral welfare −0.037 (−0.060 to −0.015) |
| R4 the coarse price is gamed | **Not supported as registered.** The tariff loses far more than the surcharge with rule-level policies (interaction +0.086, +0.050 to +0.123), but the registered mechanism, bunching at the tick before the band, did not occur (tick-9 share lower, −0.008) |
| R5 richness alone | Private +0.021 (−0.013 to +0.052); surcharge +0.048 (+0.031 to +0.065) |

What this says:

* **The question that decided this stage is answered against gates.** Where an
  operator can charge for delay, the price beats every gate, and richer
  policies do not change that. By the registered decision rule, gates are not a
  competitive alternative to pricing in this environment.
* **E1 understated the price.** Its grid stopped at level 8. With levels up to
  32 the surcharge beats the joint-welfare gate already with three parameters
  (−0.049, −0.068 to −0.029). Level 32 is better still on holdout (0.788 and
  0.833) but was not the level chosen on development data, so it is not the
  reported arm.
* **The coarse price is fragile, for an unregistered reason.** Under the
  tariff, rule-level banks delay about three times as long as under the
  surcharge (3.1 against 1.0 value-weighted ticks) and open later (mean
  opening parameter 0.25 against 0.03). The tariff prices only crossing the
  band, so delay inside each band is free; richer policies use that. This is an
  interpretation made after seeing the data. It still beats the private gate
  with no price (−0.167).
* **Every arm is worse with eight parameters,** including the planner. The
  larger space contains the smaller one, so this is a search effect at fixed
  budget, not a property of what rule-level policies can achieve. It limits
  every comparison across the two columns.
* **Why the price is robust here** (stated in the protocol before the runs): a
  charge proportional to settlement tick equals the delay surcharge plus a term
  the bank cannot influence. The surcharge therefore prices the externality
  channel itself and needs no private information. A gate cannot improve on
  that; it can only matter where such a price cannot be levied.

Provenance note: the E8 records carry commit `9729748` with the "dirty" flag
set. The only uncommitted file under `src/` when the runs started was the new
analysis script, written while the runs were starting and before any result
existed; the engine, evolution and experiment code are unchanged between
`9729748` and the following commit (`git diff 9729748 0547687 -- src` shows
only `analysis_e8.py`).

Limits specific to E8: eight bounded parameters are not programs; mutation
search may miss exploits a stronger proposer would find; one cost regime;
homogeneous banks.

## 6. Decision log

| ID | Question | Resolution |
|---|---|---|
| D1 | Is the handoff's mechanism novel? | No as stated. Narrowed to acceptance gates; "not found" in targeted search |
| D2 | Does local/system divergence occur? | Only with balanced flows; then strongly (+29 %) |
| D3 | Does adaptive coordination add value? | Reframed. Gates help; a surcharge helps more (E8) |
| D4 | Transfer to unseen shocks? | Yes for the gate ranking, across five families |
| D5 | Is the toy simulator credible? | As a game with the right qualitative structure, yes; as a payment-system model, no (§5.5) |
| D6 | SimPy or custom loop? | Custom |
| D7 | Evolution algorithm? | Bounded Gaussian mutation; best-of-4; decaying step |
| D8 | Model backend? | Open; nothing uses a model yet |
| D9 | Jev / Laya? | Not needed; identities unconfirmed |
| D10 | LangSmith or Langfuse? | Neither for now |
| D11 | UI? | None |
| D12 | Reuse CORAL? | Later, if proposals become code |
| D13 | Arbitrary code in candidates? | No |
| D14 | Seeds? | 20 paired; adequate for the registered effects (|dz| 0.7–3.3) |
| D15 | External simulator? | Agenti unavailable; BoF-PSS3 access unverified; PSSimPy available |
| D16 | Name available? | Not checked |
| D17 | Planner reference | Weak; replace with joint-welfare search at higher budget in the next study |
| D18 | Noise in acceptance | Open; see E7 |
| D19 | Do gates beat pricing once policies are rule-level? | No (E8, R1). Line "gates as an alternative to pricing" closed for this environment |
| D20 | Is a coarse price robust to richer policies? | No; band tariff loses most of its effect, by within-band delay rather than boundary bunching |
| D21 | Where could gates still matter? | Only where no party can levy a price on the externality; needs a different environment |

## 7. Unresolved questions and next steps

E8 closed the question that was first on this list. The remaining ones, ordered
by how much they would change the conclusions:

1. **Is there a setting where a gate is the only available instrument?** In the
   payment game an operator can price the externality directly, so gates lose.
   Shared resources with no operator and no meter (agents sharing a codebase,
   a context budget or an evaluation harness) are the natural candidates, and
   they are closer to the project's stated ambition than payments are. This
   means a second environment, not more work on this one.
2. **Language-model proposers.** Still not started. E8 lowers its priority in
   the payment environment: a stronger proposer would mainly test whether the
   surcharge can be exploited, which the equivalence argument in §5.8 makes
   unlikely. It becomes the main step in whichever environment item 1 selects.
   Needs an API key, a model choice and a spending cap from the project owner.
3. **Search quality with rule-level policies.** All arms degrade at fixed
   budget. A better optimiser (for example CMA-ES per bank) would show whether
   the cross-space comparisons hold when search is not the bottleneck.
4. **Noise-aware gates** as a registered factor (follow-up to E7).
5. **Model realism**: liquidity-saving mechanism, intraday credit, calibrated
   turnover; cross-check the engine against PSSimPy on shared scenarios.
6. **Heterogeneous banks under a uniform price.** A single price level may fit
   large and small banks differently; E8 used homogeneous banks only.
7. Full-text review of the 2026 preprints before any external claim; venue
   policy on disclosure of development tooling; name and licence checks.

## 8. Reproduce

```bash
uv sync
uv run pytest
uv run python -m evortgs.experiments E1 E2 E3 E4 E5 E6 E7 E8
uv run python -m evortgs.analysis
uv run python -m evortgs.analysis_e8
```

About 90 minutes on eight logical cores. Records carry the commit hash;
results are deterministic given the commit.
