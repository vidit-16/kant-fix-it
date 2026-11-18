# Kantian optimisation and universalization: economic theory and use in AI / learning agents (novelty and correctness check)

Checked 18 Nov 2026. Each source is marked **[read in full]**, **[partial: named sections read]** or **[abstract/listing only]**. The search log is at the end of the last section.

## Q1. Exact efficiency results for Kantian equilibrium (simple, additive, multiplicative), and when heterogeneity breaks them

### Takeaway
Claim (a) is well supported. Claim (b) is right in substance but wrong in wording. Roemer's own theorems say that **additive (K+) and multiplicative (K×) Kantian equilibria of strictly monotone games are Pareto efficient even when agents are heterogeneous**. So with unequal exposure the equilibrium is still Pareto efficient. What it fails to match is the **utilitarian (sum-of-costs) planner**. The over-restrain / over-reach pattern follows directly from the K+ / K× first-order conditions (derived below). I found no paper that states this exposure result as a named property. Only *simple* Kantian equilibrium (everyone takes the same action level) is documented as "generally not Pareto efficient with heterogeneous agents".

### Cited Findings
- Roemer (2015), "Kantian optimization: A microfoundation for cooperation", *Journal of Public Economics* 127: 45–57, doi:10.1016/j.jpubeco.2014.03.011 **[read in full]**:
  - **Theorem 1.** Any strictly positive multiplicative (K×) equilibrium under the *proportional* allocation rule is Pareto efficient. Any strictly positive additive (K+) equilibrium under the *equal-division* rule is Pareto efficient. The converse also holds. Preferences u^i may differ across agents (heterogeneous). — [Roemer 2015 PDF](https://cpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/6/414/files/2017/04/Kant.JPubEc.2015-10z624x.pdf)
  - Roemer's comment on Theorem 1: Kantian optimization does not fully remove the externality inefficiencies "except when the allocation rule is the right one". Efficiency depends on matching the Kantian variation to the way output or harm is shared. — same source, §3
  - **Theorem 2.** K+ equilibria under affine tax rules are Pareto efficient for any tax rate t in [0,1]. — same source
  - **Proposition 1 and the text after it.** With identical utilities, the "simple" rule (choose the effort you would like everyone to choose) is efficient. Roemer adds: "the simpler kind of Kantian equilibrium is generally not Pareto efficient with heterogeneous agents." In his framing, K× and K+ are the right generalization to heterogeneous agents. Footnote 6 cites Ostrom and Gardner (1993) on heterogeneous agents solving commons problems. — same source, §4
  - The earlier Roemer (2010) Theorem 3 had an incorrect proof. The 2015 Theorem 3 supersedes it. — same source, fn 7
- Roemer (2019), *How We Cooperate: A Theory of Kantian Optimization* (Yale UP), as summarized by Sher (2020) **[book not read; summary read in full]**:
  - Any simple, multiplicative or additive Kantian equilibrium of a **strictly monotone game** is Pareto efficient (book p.23 Prop 2.1; p.42 Prop 3.1; p.43 Prop 3.2). A strictly monotone game is one where every V^i is strictly decreasing (or strictly increasing) in every other player's strategy.
  - In strictly monotone, quasi-economic games, any interior Nash equilibrium is inefficient (p.44 Prop 3.3).
  - Source: [Sher, "Normative Aspects of Kantian Equilibrium", EJPE 13(2): 43–84, 2020](https://ejpe.org/journal/article/download/514/353/1232)
- Sher (2020) **[read in full]**. Proposition 3: simple, multiplicative and additive Kantian equilibria can all be inefficient. His counterexample is a 2-player game with identical outcome utilities where the players control different variables (V = ln2 + ln(s1 s2) − s1 − 2 s2). This is an *asymmetric-technology* game, not a monotone commons. He also notes:
  - Kantian equilibrium may fail to exist.
  - It is not invariant to relabeling strategies.
  - It "enjoins solidarity among those who can cooperate" but ignores powerless bystanders, i.e. agents who are affected but have no action of their own. — [Sher 2020](https://ejpe.org/journal/article/download/514/353/1232)
- Vallentyne (2020), EJPE 13(2): 85–97 **[partial]**:
  - Restates that simple Kantian equilibria exist for symmetric / common-diagonal games and are Pareto optimal when payoffs are strictly monotone.
  - In strictly monotone symmetric games, Kantian optimization picks the externality level that, imposed on everyone, leaves each player as well off as any other universalized level.
  - Source: [Vallentyne 2020](https://ejpe.org/journal/article/download/502/354/1233)
- Roemer (2010), "Kantian Equilibrium", *Scandinavian Journal of Economics* 112(1): 1–24. This is the origin of the term. **[citation verified via search listing only]** — [search listing](https://ideas.repec.org/h/spr/spschp/978-3-319-29254-0_12.html)
- Sloev & Lianos (20 Jun 2026), "Three Barriers to Kantian Cooperation under Inequality", arXiv:2606.21931 [econ.TH] **[abstract only]**:
  - Setting: a 2-agent public good with unequal endowments and log preferences, comparing Nash with multiplicative Kantian.
  - Moving from Nash to Kantian is not always a Pareto improvement. "under sufficiently high inequality, the poor agent may prefer the Nash outcome."
  - Different parametrizations (contributions vs consumption) have different distributional effects.
  - Agents still face a selection problem on the Pareto frontier.
  - The heterogeneity here is in endowment, not exposure. — [arXiv](https://arxiv.org/abs/2606.21931)
- Eichner & Pethig (2022), "Kantians defy the economists' mantra of uniform Pigovian emissions taxes", *Ecological Economics* 200; CESifo WP 8749 (2020) **[abstract only]**. With consumers who differ in morality and preferences, materially efficient emissions taxes vary by type and lie below the Pigovian rate. The heterogeneity here is in *degree of morality*, not exposure. — [IDEAS](https://ideas.repec.org/p/ces/ceswps/_8749.html)
- Eichner & Pethig (2024), "International environmental agreements when countries behave morally", *JEEM* 125 **[listing only]** — [IDEAS](https://ideas.repec.org/a/eee/jeeman/v125y2024ics0095069624000299.html)
- Grafton, Kompas & Van Long (2017), "A brave new world? Kantian–Nashian interaction and the dynamics of global climate change mitigation", *European Economic Review* 99: 31–42 **[listing only]**:
  - Defines a generalized Kant–Nash equilibrium (a mix of Kantian and Nashian agents) and proves existence and uniqueness in a static mitigation game, plus a differential game.
  - Whether it models heterogeneous damages was **not verified**.
  - Source: [EconPapers](https://econpapers.repec.org/RePEc:eee:eecrev:v:99:y:2017:i:c:p:31-42)
- Ghosh & Van Long (2015), "Kant's rule of behavior and Kant–Nash equilibria in games of contributions to public goods", CESifo conference paper **[cited secondhand only]**.
- Van Long (2016), "Kant-Nash equilibria in a quantity-setting oligopoly", book chapter (Springer, Okuguchi Festschrift) **[listing only]**. Defines exclusive and inclusive Kant–Nash equilibria. — [IDEAS](https://ideas.repec.org/h/spr/spschp/978-3-319-29254-0_12.html)
  - The brief's "Grafton–Kompas–Van Long, *Kantian equilibria in a class of Cournot/common-pool games*" could not be found under that title. The closest real items are the two Van Long / Grafton papers above. **Do not cite the brief's title.**

### Inferences
- **Own derivation, not from a source; check before citing.**
  - Setup: agent i chooses x_i, with cost C_i = −b_i(x_i) + e_i·D(X), where X = Σx_j and e_i > 0 is i's exposure.
  - **Additive Kantian (K+).** Everyone shifts by the same r, so the first-order condition is b_i'(x_i) = n·e_i·D'(X).
  - **Utilitarian optimum.** b_i'(x_i) = (Σ_j e_j)·D'(X) = n·ē·D'(X), where ē is mean exposure.
  - Comparing the two: agents with e_i > ē restrain *more* than the planner wants (over-restrain), and agents with e_i < ē restrain less (over-reach). This is exactly the project's finding (b).
  - **The K+ point is still Pareto efficient.** It satisfies the Pareto first-order condition with welfare weights λ_i ∝ 1/e_i: λ_i·b_i' = (Σ_j λ_j e_j)·D' holds when λ_i = 1/e_i. So the Kantian outcome is the planner optimum *with exposed agents down-weighted*.
  - **Multiplicative Kantian (K×).** The first-order condition is b_i'(x_i) = e_i·D'(X)·X/x_i. This also departs from the utilitarian rule, and is Pareto efficient with weights λ_i ∝ x_i/(e_i·X).
  - This agrees with Roemer's strictly-monotone-game propositions. The heterogeneous-exposure game is strictly monotone (decreasing) when every e_i > 0.
- **Correctness verdict on (b).** "Kantian behaviour is inefficient under heterogeneous exposure" is **not correct if 'inefficient' means Pareto-inefficient** for a true K+ or K× equilibrium. It **is correct as "departs from the utilitarian / aggregate-cost optimum"**.
  - It is also correct if the project's gate behaves like *simple* Kantian (everyone takes the same level). Roemer 2015 explicitly says that version is generally Pareto-inefficient with heterogeneous agents.
  - It is also correct if κ < 1, because a private–Kantian mixture is a Kant–Nash / homo-moralis hybrid and is generally not Pareto efficient.
  - It may be correct if some agents have e_i = 0. Strict monotonicity then fails and Roemer's efficiency propositions no longer apply.
- **Suggested rewording for the write-up.** "Kantian equilibria are Pareto efficient in strictly monotone games (Roemer 2015 Thm 1; Roemer 2019 Props 3.1–3.2), but they select a point on the frontier that is not the utilitarian optimum. With heterogeneous exposure, the K+ conditions imply that agents more exposed than average over-restrain and less exposed agents over-reach relative to the aggregate-cost optimum (our derivation)."
  - Calling this "a known property of Kantian equilibria" is **not supported by any source found**. Cite it as a derivation, with Roemer 2015 §4 (heterogeneity and simple KE), Sher 2020 (efficiency is not equity; bystanders) and Sloev & Lianos 2026 (inequality barriers) as the nearest related statements.
- The exposure-weighted structure (λ_i ∝ 1/e_i) matches Sher's informal point: Kantian equilibrium reflects agents' "powers" and interests, not a symmetric welfare weighting.

### Gaps
- Roemer 2019 (book) was not read directly. The proposition numbers and pages come from Sher's summary, and the exact hypotheses (interiority, differentiability) were not checked.
- No source found that analyzes Kantian equilibrium with heterogeneous *exposure* (damage incidence) specifically. Grafton–Kompas–Van Long (2017) and Nishimura's 2025 Osaka DP on North–South Kantian pollution may contain it, but were not read. Leads: [Osaka DP 2504](https://www2.econ.osaka-u.ac.jp/econ_society/dp/2504.pdf), [Epp & Hillebrand Aug 2026 manuscript](https://uni-freiburg.de/econ-macro/wp-content/uploads/sites/197/Manuscript_Epp_Hillebrand_August_2026.pdf).
- Whether the project's gate converges to K+, K×, simple KE or none of these depends on its implementation. The gate's "same change" must be compared with Roemer's Kantian variations φ(x,r).

## Q2. Homo moralis (Alger & Weibull): evolutionary stability of the degree of morality κ, and selection rules

### Takeaway
In Alger & Weibull, κ is a *preference* parameter selected by evolution. The evolutionarily stable κ equals the index of assortativity of matching. Curry & Roemer instead let evolution select the *optimization protocol* (Kantian vs Nash). Kantians win only if types are observable. Neither uses universalization as the acceptance or update rule within an evolutionary loop. In both, universalization is the trait that gets selected.

### Cited Findings
- Alger & Weibull (2013), "Homo moralis — preference evolution under incomplete information and assortative matching", *Econometrica* 81(6): 2269–2302 **[listing/abstract only]**:
  - Utility is a convex combination of own payoff and the "Kantian" payoff (what if everyone did the same). The weight is the degree of morality κ.
  - The evolutionarily stable κ equals the index of assortativity.
  - Selfishness is unstable under positive assortativity.
  - Source: [UT Capitole PDF](https://publications.ut-capitole.fr/id/eprint/15435/1/homomoralis.pdf); [EconPapers](https://econpapers.repec.org/RePEc:car:carecp:12-01)
- Alger & Weibull (2016), "Evolution and Kantian morality", *Games and Economic Behavior* 98: 56–67 **[abstract only]**:
  - Covers groups of any finite size with possibly assortative matching.
  - Preferences blending self-interest with Kantian morality are evolutionarily stable. Other behaviour is unstable.
  - Corrigendum/addendum in GEB 140: 585–587 (2023): part of Theorem 1's instability claim needed a stronger hypothesis.
  - Source: [TSE](https://www.tse-fr.eu/articles/evolution-and-kantian-morality); [EconPapers](https://econpapers.repec.org/RePEc:eee:gamebe:v:98:y:2016:i:c:p:56-67)
- Curry & Roemer (2012), "Evolutionary stability of Kantian optimization", working paper dated 22 Apr 2012 **[read in full]**:
  - Natural selection acts on the optimization *protocol* in the Prisoner's Dilemma and the Random Dictator game.
  - If players can identify opponents' types, Kantians drive Nash players to extinction. If not, Nash optimizers win: "nature would select for Nash optimizers".
  - Publication venue not verified.
  - Source: [Waterloo PDF](https://uwaterloo.ca/economics/sites/default/files/uploads/documents/evolutionary-stability-of-kantian-optimization.pdf)
- A JEEM paper on the tragedy of the commons and socialization ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0095069618304881)) uses an overlapping-generations shepherds commons with Nash and Kantian shares evolving by socialization **[snippet only; authors not verified]**.
- Roemer (2015) Theorem 11: for n = 2, iterating a Kantian "best-reply" map converges to the K+ equilibrium. This is the only learning-dynamic convergence result for Kantian equilibrium I found. — [Roemer 2015](https://cpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/6/414/files/2017/04/Kant.JPubEc.2015-10z624x.pdf)

### Inferences
- The project's κ (mixing private and Kantian cost) is formally the Alger–Weibull homo moralis utility. It should be cited as such. The difference is that the project applies it as a *gate on proposed changes* rather than as an evolved preference.
- Alger–Weibull κ is a convex combination of payoffs, which is the simple-Kantian counterfactual (everyone plays *my* strategy). That is not Roemer's K+ / K× "same deviation" counterfactual. This matters for which efficiency results transfer (see Q1).

### Gaps
- The Alger & Weibull papers were not read in full. In particular, whether they treat asymmetric or heterogeneous-role games (their later work on "Kantian morality in asymmetric interactions") was not checked.
- The JEEM shepherds paper's authors and results were not verified.

## Q3. Universalization in AI: GovSim, Levine / Kleiman-Weiner, the ICML 2026 workshop paper, and MARL / LLM agents 2023–2026

### Takeaway
In AI, universalization appears in three forms:
- an **inference-time prompt / memory injection** (GovSim);
- an **evaluation protocol** (Melting Pot's universalization scenarios);
- **prompted or fine-tuned "Kantian" LLM agents** (ICML 2026 workshop; Lu et al. 2025/26 SFT).

The cognitive-science root is Levine et al. (PNAS 2020). No paper found uses universalization as a learned or evolutionary acceptance rule.

### Cited Findings
- Levine, Kleiman-Weiner, Schulz, Tenenbaum & Cushman (2020), "The logic of universalization guides moral judgment", *PNAS* 117(42): 26158–26169, doi:10.1073/pnas.2014505117 **[abstract and listing]**:
  - People judge an action's permissibility by asking what would happen if everyone felt free to do it.
  - The process is formalized in a computational model and tested in adults and children.
  - The authors explicitly do not claim universalization is the only or dominant mechanism.
  - Source: [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7584905); [MIT DSpace](https://dspace.mit.edu/handle/1721.1/130261)
- Piatti, Jin, Kleiman-Weiner, Schölkopf, Sachan & Mihalcea, "Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents" (GovSim), arXiv:2404.16698 (v4, 8 Dec 2024) **[read about 75% of the HTML, including the universalization sections; the remainder, including appendix D.3, was not read]**:
  - Universalization is **a statement added to each agent's memory at inference time**, not training or an acceptance rule. Fishery wording: "if everyone fishes more than F tons, the lake population will shrink next month."
  - Reported gains, all p < 0.001: survival time +44 months (the conclusion text says "4 months", an internal inconsistency), total gain +29, efficiency +24%.
  - No learning is involved.
  - Venue: the arXiv page does not state it; widely reported as NeurIPS 2024 but **not verified here**.
  - Source: [arXiv HTML](https://arxiv.org/html/2404.16698)
- Samoylenko, "Kantian Equilibrium in the Age of Multi-Agent Systems", ICML 2026 workshop *New Frontiers in Game-Theoretic Learning* (poster); OpenReview id hizxbjrwxO **[abstract only; PDF not retrieved]**:
  - Compares payoff-maximizing LLM agents with agents **prompted** with Kantian formulations in a tragedy-of-the-commons game over shared local compute.
  - Finds LLMs can reproduce Kantian reasoning "with qualifications". Results depend strongly on how the Kantian agent is specified, and weaker models sometimes did better.
  - Source: [ICML virtual](https://icml.cc/virtual/2026/78744); [OpenReview](https://openreview.net/forum?id=hizxbjrwxO)
- Leibo et al. (2021), "Scalable Evaluation of Multi-Agent RL with Melting Pot", ICML 2021 (PMLR 139). Includes "universalization" test scenarios, in which every player is a copy of the focal policy, as an **evaluation** of whether a policy is acceptable if everyone adopts it. It is not used as a training rule. **[snippet only]** — [PMLR](http://proceedings.mlr.press/v139/leibo21a/leibo21a.pdf)
- Lu, Dhanda, Chen & Hansen, "Aligning LLM Agents with Rational and Moral Preferences: A Supervised Fine-Tuning Approach", arXiv:2507.20796 (v2 Mar 2026) **[abstract only]**:
  - Builds SFT data from optimal strategies under homo economicus and homo moralis (Kantian universalizability) utilities.
  - Kantian reasoning becomes *training data*, not an online acceptance rule.
  - Source: [arXiv](https://arxiv.org/abs/2507.20796)
- Istrate, "Game-theoretic models of moral and other-regarding agents", arXiv:2012.09759 (cs.GT) **[snippet only]**. Studies Kantian equilibria in finite normal-form games and shows that computing mixed Kantian equilibria is NP-hard. — [arXiv](https://arxiv.org/abs/2012.09759v2)
- Tennant et al., "Moral Alignment for LLM Agents", ICLR 2025, arXiv:2410.01639 **[listing only]**. Uses deontological and utilitarian intrinsic rewards for RL fine-tuning in repeated social dilemmas, not universalization. — [arXiv](https://arxiv.org/pdf/2410.01639)

### Inferences
- GovSim and the ICML 2026 workshop paper are the closest AI prior art for "universalization in a commons". Both are prompt-level, use *homogeneous* exposure (one shared lake / compute pool), and have no learning loop.
- Melting Pot's universalization scenario is the closest *RL* use, but only as a test-time metric.
- Lu et al. used homo moralis utilities as a fine-tuning target. That is the nearest example of Kantian utility shaping what is learned, but the mechanism is supervised imitation of precomputed optima.

### Gaps
- Not read: the ICML 2026 workshop PDF, GovSim appendix D.3 (per-model universalization results), and Levine et al.'s follow-ups (e.g. LLM universalization benchmarks such as MoralExceptQA / MoralCoT, Jin et al. NeurIPS 2022). These were known leads but not verified this session.
- GovSim's venue was not verified from a primary page.

## Q4. Any paper using Kantian / universalization reasoning as the acceptance or update rule of learning or evolutionary agents (not as a prompt)

### Takeaway
**None found.** Prior work uses universalization in four other ways:
- as an equilibrium concept (Roemer);
- as an evolved preference or protocol (Alger–Weibull; Curry–Roemer);
- as an iterated best-reply map, which is the only "dynamic", for n = 2 (Roemer 2015 Thm 11);
- as a prompt, evaluation metric or SFT target in AI (GovSim; ICML 2026 workshop; Melting Pot; Lu et al.).

A universalization *gate* that accepts or rejects candidate changes inside a learning or evolutionary loop appears to be novel. This rests on about 20 searches and fetches, so it is a "not found", not a proof of absence.

### Cited Findings
- Roemer's Kantian best-reply iteration converges for n = 2 with quasi-linear preferences under equal division (Theorem 11). — [Roemer 2015](https://cpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/6/414/files/2017/04/Kant.JPubEc.2015-10z624x.pdf)
- Curry & Roemer select *between* Kantian and Nash protocols by fitness. Universalization is the heritable trait, not the filter on mutations. — [Curry & Roemer 2012](https://uwaterloo.ca/economics/sites/default/files/uploads/documents/evolutionary-stability-of-kantian-optimization.pdf)
- Searches for "Kantian reinforcement learning", "universalization MARL reward" and "Kantian learning dynamics" returned nothing combining Kantian or universalization reasoning with an RL or evolutionary update rule. The search tool itself reported that no such paper was found. — searches 9, 10 and 12 in the log below

### Inferences
- The novelty claim should be phrased narrowly: "to our knowledge, universalization has not been used as the acceptance criterion of a learning or evolutionary search loop". Prior uses to acknowledge: Kantian equilibrium as a solution concept (Roemer 2010/2015/2019), homo moralis as an evolved preference (Alger & Weibull 2013/2016), and universalization as an LLM prompt (Piatti et al. 2024; Samoylenko 2026) or an evaluation scenario (Leibo et al. 2021).
- The project's E10 result (unequal exposure defeats the gate) is consistent with, and predicted by, the K+ first-order condition in Q1. It should be presented as an expected consequence, not a surprise.

### Gaps
- Not searched: Semantic Scholar / Google Scholar citation trails of Roemer 2010 and Levine 2020 restricted to cs.LG / cs.MA; evolutionary-computation venues (GECCO, ALIFE). A remaining blind spot.

### Search log
| # | Query | Source | Hits screened | Included |
|---|---|---|---|---|
| 1 | Kantian equilibrium heterogeneous agents inefficient common pool | WebSearch (extended) | 8 | Roemer 2015; Sloev & Lianos 2026; EJPE symposium |
| 2 | "Kantian Equilibrium in the Age of Multi-Agent Systems" | WebSearch | 10 | ICML 2026 workshop (Samoylenko); Istrate |
| 3 | universalization moral reasoning Levine Kleiman-Weiner … PNAS 2020 | WebSearch | 10 | Levine et al. 2020 |
| 4 | Fetch: Roemer 2015 JPubE PDF | WebFetch failed (binary); text extracted locally with pdftotext | — | read in full |
| 5 | Fetch: arXiv 2606.21931 | WebFetch | — | abstract |
| 6 | Fetch: icml.cc/virtual/2026/78744 | WebFetch | — | abstract |
| 7 | Eichner Pethig Kantian emissions heterogeneous | WebSearch | 10 | Eichner & Pethig 2022, 2024 |
| 8 | Grafton Kompas Van Long Kantian Nashian climate | WebSearch | 10 | GKL 2017 (listing) |
| 9 | Alger Weibull homo moralis evolutionary stability | WebSearch | 10 | AW 2013 |
| 10 | Fetch: IDEAS CESifo 8749 | WebFetch | — | abstract |
| 11 | Fetch: GovSim arXiv HTML | WebFetch | — | ~75% read |
| 12 | universalization MARL reward "what if everyone" | WebSearch (extended) | 9 | Melting Pot; nothing else |
| 13 | "Kantian" reinforcement learning agents … commons | WebSearch (extended) | 10 | none relevant |
| 14 | Kantian equilibrium asymmetric players unequal exposure | WebSearch (extended) | 9 | no exposure-specific source |
| 15 | Fetch: Sher 2020 and Vallentyne 2020 EJPE PDFs | WebFetch failed (binary); text extracted locally | — | Sher read in full; Vallentyne partial |
| 16 | LLM agents universalization Kantian commons 2025 | WebSearch (extended) | 10 | Lu et al. 2025; GovSim |
| 17 | Kantian learning dynamics … Curry Roemer shepherds | WebSearch | 10 | Curry & Roemer 2012; JEEM shepherds |
| 18 | Fetch: arXiv 2507.20796; Curry–Roemer PDF | WebFetch; Curry–Roemer extracted locally | — | abstract; read in full |
| 19 | Alger Weibull "Evolution and Kantian morality" GEB 2016 | WebSearch | 10 | AW 2016 and 2023 corrigendum |
| 20 | Ghosh Van Long Kantian Cournot / Roemer 2010 SJE | WebSearch | 10 | Van Long 2016 chapter; Roemer 2010 citation |

Failures:
- WebFetch could not read the PDF text of Roemer 2015, Sher 2020, Vallentyne 2020 or Curry & Roemer 2012. All were recovered with local pdftotext.
- The "Grafton–Kompas–Van Long Kantian equilibria in a class of Cournot/common-pool games" title from the brief was not found.
- The ICML 2026 workshop PDF was not retrieved.
