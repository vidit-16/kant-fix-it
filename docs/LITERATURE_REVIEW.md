# Literature review: prior work for the EvoRTGS claims

Review dated 18 November 2026, with a second pass through open scholarly APIs the same day and a third, manual Google Scholar pass on 20 November. Working notes with full search logs are in
[literature_notes/](literature_notes/). Changes made to REPORT.md and PROJECT.md
as a result are recorded in PROJECT.md (D30).

The core gap that EvoRTGS claims holds up, but some of its supporting statements do not. This review found **no prior work that compares acceptance gates of several self-improving agents sharing an environment with externalities, at matched search budget, against a price on the externality**. Two 2026 single-agent papers on acceptance gates explicitly name the multi-agent case as open work. Three statements must change. **First, the E10 sentence calling unequal-exposure distortion "a known property of Kantian equilibria" is unsupported.** No source states it. Roemer's theorems make additive and multiplicative Kantian equilibria **Pareto efficient even with heterogeneous agents**. With unequal exposure, the additive Kantian point is the welfare optimum when each agent's welfare weight is proportional to 1/exposure. It departs only from the equal-weight (utilitarian) optimum that the project uses as its reference. **Second, the technical-debt background statement that "no agent-based or game-theoretic simulation was found" is wrong.** Gavidia-Calderon, Sarro, Harman and Barr (JSS 2020) call technical debt "a tragedy of the commons", simulate developers choosing kludge or fix, find a kludge equilibrium and use mechanism design to restore fixing. **Third, the payment citations need repair.** The Castro et al. reinforcement-learning paper has a journal version in *ACM Transactions on Economics and Computation* 13(1). Bank of Canada SWP 2025-35 is the same paper as BIS WP 1310 by Aldasoro and Desai, not a Castro et al. follow-up. Other statements survive but need narrower scope and added precursors: on pricing versus throughput rules in payments (Ota 2011), on ambient-tax and Groves-style budget breaking, on homo moralis, and on LOPT's learned Pigouvian tax in multi-agent reinforcement learning (MARL). This is a broad, structured review of about 118 logged searches and fetches. It is not a formal systematic review, and several key sources were seen only at abstract level.

**Evidence key.** Each citation carries a tag. **[full]** means the full text was read. **[partial]** means part of the full text was read: the main body of an arXiv HTML page truncated at about 100k characters, a named chapter or section, or a document reached only through another paper's reference list. **[abstract]** means only an abstract, a catalogue or listing page, a search snippet or a third-party summary was seen. **[arXiv ID unverified]** flags an arXiv identifier that the notes did not confirm on its own arXiv page; it came from a search result or a mirror site.

## Claim 1: gate studies exist for single agents, while multi-agent gate comparisons were not found

The project treats the acceptance gate of co-evolving agents as the experimental factor (REPORT §1–2). That framing survives, with one change: the gate is no longer an unstudied object. In 2026 it became an explicit research target, but only for single agents. **SAGE** proposes a paired one-sided exact binomial gate with a regression cap. It compares that gate with a "keep if validation score strictly rises" rule, at equal proposals and equal token cost. Its future-work section calls multi-agent acceptance "a natural and harder extension" because one edit's gain "is no longer decidable from local evidence alone" ([SAGE, arXiv:2609.36043](https://arxiv.org/html/2609.36043v1) [full]). **PACE** compares greedy, paired fixed-n, online-FDR and e-process commit gates for one prompt-evolving agent. Its budgets are not strictly matched, and it argues the multi-agent extension without testing it ([PACE, arXiv:2606.08106](https://arxiv.org/html/2606.08106v1) [full]). **"Evolving Together, Failing Apart"** formalises an idealised cooperative acceptance rule and catalogues the gates of existing methods. Its co-evolution, however, runs between one agent's policy and its own skill bank ([arXiv:2610.20845](https://arxiv.org/html/2610.20845v1) [partial]). These three papers position the project better than any other citation, because they name the project's question as open work.

None of the self-improvement systems the project already cites varies an other-regarding gate. **CORAL** runs several agents against one shared evaluator with a common objective. Their interaction is informational only, and there are no per-agent payoffs or externalities ([arXiv:2604.01658](https://arxiv.org/html/2604.01658) [partial]). **Hyperagents** and the **Darwin Gödel Machine** compare archive-based search with a single-successor variant at matched iterations. In effect they vary the acceptance rule for a single lineage on a single objective, so they are the single-agent precursor the project should acknowledge ([Hyperagents, arXiv:2603.19461](https://arxiv.org/html/2603.19461v1) [partial]; [DGM, arXiv:2505.22954](https://arxiv.org/html/2505.22954) [partial]). Three more systems accept a change only if it beats the incumbent, and none varies that rule:

- **MASS** uses a self-evaluator's pairwise preference ([arXiv:2610.12176](https://arxiv.org/html/2610.12176) [partial]).
- **AIDE²** uses a held-out mean grade, with no margin or test ([arXiv:2609.26457](https://arxiv.org/html/2609.26457) [partial]).
- **Misevolve** proposes a tool gate but does not test it ([arXiv:2509.26354](https://arxiv.org/html/2509.26354) [partial]).

The **co-evolution survey** body (which PROJECT.md records as unread) has now been read. It does not discuss externalities, the tragedy of the commons or welfare-based acceptance. Its own limitations state that "safety and governance are not operationalized" ([arXiv:2608.10299](https://arxiv.org/html/2608.10299) [partial]).

Three neighbouring works deserve explicit contrast rather than silence. **"Internal vs External"** compares deliberated with evolved society-wide constitutions in public-goods games, scored on a collective stability score. That is the closest named work on mixed-motive rule adoption, but the factor it varies is who designs the group rule, not per-agent gates ([arXiv:2605.09128](https://arxiv.org/html/2605.09128) [partial]). The **evolved-constitutions** paper from the same group does centralised search with welfare-motivated fitness ([arXiv:2602.00755](https://arxiv.org/html/2602.00755) [full]). **Economy of Minds** puts prices among co-evolving agents through auctions, rent and bankruptcy. Its prices serve cooperative credit assignment, not externality correction, which makes it the nearest relative of the project's price arm ([arXiv:2606.02859](https://arxiv.org/html/2606.02859) [partial]).

Three classical and adjacent lines are also close. The nearest classical analogue is **Agogino and Tumer's local versus global versus difference evaluation** for evolving multiagent policies. It is conceptually private versus joint versus marginal welfare, but in fully cooperative settings and as fitness shaping rather than accept/reject decisions ([GECCO 2005](https://gpbib.cs.ucl.ac.uk/gecco2005/docs/p591.pdf) [abstract]; [AAMAS 2012](https://ifaamas.csc.liv.ac.uk/Proceedings/aamas2012/papers/2C_2.pdf) [abstract]). **Prosocial reward shaping in MARL** varies the objective each agent trains on rather than gating its proposals: SVO reward sharing in McKee et al. and its successors, and the SocialJax benchmarks ([McKee et al., arXiv:2002.02325](https://arxiv.org/pdf/2002.02325.pdf) [abstract] [arXiv ID verified in second pass]; [SocialJax, arXiv:2503.14576](https://arxiv.org/pdf/2503.14576) [abstract] [arXiv ID verified in second pass]). **Red Queen Gödel Machine** co-evolves agents with their evaluators ([arXiv:2606.26294](https://arxiv.org/abs/2606.26294) [abstract] [arXiv ID verified in second pass]).

Two details in PROJECT.md §3.2 are not supported by these notes and should be checked before reuse: the "NeurIPS 2026" venue for Economy of Minds, and AIDE²'s reported fall in reward hacking from 55 % to 32 %. REPORT §1 says such systems "are evaluated one at a time against fixed benchmarks". That is accurate for single lineages, but CORAL runs several agents at once. The sentence should say "single lineages or agents with a common objective".

## Claim 2: Kantian equilibria stay Pareto efficient, so the E10 distortion is a derivation and not a known property

REPORT §2 states that Kantian equilibria are known to be efficient in symmetric common-pool problems, which makes E9's result expected. **This holds, and the literature says more.** Roemer's 2015 Theorem 1 covers heterogeneous preferences. Under it, any strictly positive multiplicative Kantian equilibrium (K×) with proportional allocation, and any strictly positive additive one (K+) with equal division, is Pareto efficient ([Roemer 2015, *J. Public Econ.* 127](https://cpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/6/414/files/2017/04/Kant.JPubEc.2015-10z624x.pdf) [full]). The book version extends this to **all strictly monotone games**: simple, multiplicative and additive Kantian equilibria are all Pareto efficient there, while interior Nash equilibria are not ([Roemer 2019 via Sher 2020](https://ejpe.org/journal/article/download/514/353/1232); book [abstract], summary [full]). What fails with heterogeneity is narrower. Roemer writes that "the simpler kind of Kantian equilibrium is generally not Pareto efficient with heterogeneous agents", where "simpler" means everyone takes the same action level ([Roemer 2015 §4](https://cpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/6/414/files/2017/04/Kant.JPubEc.2015-10z624x.pdf) [full]). REPORT cites the 2019 book as its Kantian source, but that book was not read in this review. The 2015 article, which was read in full, should be added as the primary citation.

**The E10 discussion sentence is wrong as written.** It says that over-restraint by central agents and over-reach by peripheral ones "is a known property of Kantian equilibria". No source found states an unequal-exposure result for Kantian equilibrium. A targeted search on "Kantian equilibrium asymmetric players unequal exposure" returned nothing exposure-specific ([search log, Kantian notes, search 14] [abstract]). The pattern does follow from a short derivation, which the notes flag as their own and which should be checked before citing. Let agent i have private benefit b_i(x_i), exposure e_i > 0 and shared damage D(X) with X = Σx_j. The **additive Kantian condition** is **b_i′(x_i) = n·e_i·D′(X)**. The **utilitarian (equal-weight, sum-of-costs) condition** is **b_i′(x_i) = (Σ_j e_j)·D′(X) = n·ē·D′(X)**, where ē is mean exposure. Comparing the two, agents with above-average exposure restrain more than the utilitarian planner wants and agents with below-average exposure restrain less. That matches E10's shortcut intensities at skew 1.5: 0.45 for the most exposed agent and 0.89 for the least, against 0.64 to 0.73 at the project's optimum. **The K+ point is nonetheless Pareto efficient.** It satisfies the weighted-planner condition λ_i·b_i′ = (Σ_j λ_j e_j)·D′ when **λ_i ∝ 1/e_i**. Put plainly, the Kantian equilibrium is the welfare optimum of a planner who down-weights the exposed agents. The multiplicative variant is likewise efficient, with weights proportional to x_i/(e_i·X). So the E10 "distortion" is a departure from the project's utilitarian reference, not an inefficiency. The project should not call it Pareto inefficiency unless one of these applies:

- its gate behaves like simple Kantian rather than K+;
- κ < 1, which gives a Kant–Nash hybrid;
- some agent has zero exposure, which breaks strict monotonicity.

These cases depend on implementation, because Alger and Weibull's κ-utility uses the "everyone plays my strategy" counterfactual. That is the simple-Kantian form, not Roemer's "everyone makes the same deviation" form ([Alger & Weibull 2013, *Econometrica* 81(6)](https://publications.ut-capitole.fr/id/eprint/15435/1/homomoralis.pdf) [abstract]). The post hoc finding that development data chose κ = 0.5 at skew 1.5 sits in exactly this grey zone.

*Project note, added after the review (checked against `src/evortgs/gates.py`):*
the project's κ = 1 gate builds its counterfactual by adding the same
mutation `d` to every agent's current policy (`cur[j] + d`, clipped to
bounds). That is Roemer's additive form (K+), not the simple form, so the
derivation above applies directly. The gate targets a Pareto-efficient point
that weights agents by 1/exposure, and E10's "distortion" is a departure
from the equal-weight cost optimum, not Pareto inefficiency. The κ = 0.5 gate
is a Kant–Nash hybrid. Clipping at policy bounds and the nonlinear incident
process mean the derivation is an approximation for this model.

The nearest published statements should be cited as context, not as the source of the result:

- **Sher (2020)** shows that all three Kantian equilibrium types can be inefficient in an asymmetric-technology game. He also notes that the concept "enjoins solidarity among those who can cooperate" while ignoring bystanders ([Sher 2020, EJPE 13(2)](https://ejpe.org/journal/article/download/514/353/1232) [full]).
- **Sloev and Lianos (2026)** show that under high endowment inequality the poor agent may prefer Nash to multiplicative Kantian. Their heterogeneity is in endowment, not exposure ([arXiv:2606.21931](https://arxiv.org/abs/2606.21931) [abstract]).
- **Eichner and Pethig (2022)** find type-specific, sub-Pigouvian efficient taxes when agents differ in morality ([IDEAS](https://ideas.repec.org/p/ces/ceswps/_8749.html) [abstract]).
- **Vallentyne (2020)** restates efficiency for symmetric, strictly monotone games ([EJPE](https://ejpe.org/journal/article/download/502/354/1233) [partial]).

One title supplied in the research brief, a "Grafton–Kompas–Van Long" paper on Kantian equilibria in Cournot or common-pool games, could not be found and must not be cited. The real neighbours are Grafton, Kompas and Van Long (2017) on Kant–Nash climate mitigation ([EconPapers](https://econpapers.repec.org/RePEc:eee:eecrev:v:99:y:2017:i:c:p:31-42) [abstract]) and Van Long (2016) on Kant–Nash oligopoly ([IDEAS](https://ideas.repec.org/h/spr/spschp/978-3-319-29254-0_12.html) [abstract]). Neither was checked for heterogeneous damages.

On the κ gate itself, the project's κ mixture is formally Alger and Weibull's homo moralis utility. There the stable degree of morality equals the index of assortativity ([Alger & Weibull 2013](https://econpapers.repec.org/RePEc:car:carecp:12-01) [abstract]; [Alger & Weibull 2016, *GEB* 98, corrigendum 2023](https://www.tse-fr.eu/articles/evolution-and-kantian-morality) [abstract]). The citation should name the 2016 paper and the 2023 corrigendum to its instability claim. Curry and Roemer select between Kantian and Nash protocols by fitness. They find that Kantians win only when types are observable; otherwise "nature would select for Nash optimizers" ([Curry & Roemer 2012](https://uwaterloo.ca/economics/sites/default/files/uploads/documents/evolutionary-stability-of-kantian-optimization.pdf) [full]). The only learning-dynamic convergence result found is Roemer's 2015 Theorem 11, which shows that iterated Kantian best replies converge for n = 2 ([Roemer 2015](https://cpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/6/414/files/2017/04/Kant.JPubEc.2015-10z624x.pdf) [full]).

In AI, universalization appears in four forms, and none of them is a gate:

- **An inference-time memory statement.** GovSim's universalization sentence improved survival, gain and efficiency at p < 0.001 ([Piatti et al., arXiv:2404.16698](https://arxiv.org/html/2404.16698) [partial]). The paper reports survival as +44 months in its results but "4 months" in its conclusion, and its "NeurIPS 2024" venue, which the project's reference list gives, was not verified here.
- **A prompted Kantian agent.** Samoylenko's ICML 2026 workshop paper reports that results depend strongly on how the Kantian agent is specified ([ICML virtual](https://icml.cc/virtual/2026/78744) [abstract]).
- **An evaluation scenario.** Melting Pot's universalization tests copy the focal policy to every player ([Leibo et al. 2021](http://proceedings.mlr.press/v139/leibo21a/leibo21a.pdf) [abstract]).
- **A fine-tuning target.** Lu et al. train on optimal strategies under homo moralis utilities ([arXiv:2507.20796](https://arxiv.org/abs/2507.20796) [abstract]).

The cognitive-science root is Levine et al. in *PNAS* ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7584905) [abstract]). In this review, no paper used universalization as the acceptance criterion of a learning or evolutionary loop.

## Claim 3: the payment-game lineage holds, and two citations need repair

REPORT §2's payment background holds. The liquidity–delay game has two origins. One is Bech and Garratt's two-player game with multiple equilibria (*J. Econ. Theory* 109(2), 2003; verified via the reference list of [Aldasoro & Desai](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf) [partial]). The other is their n-player disruption model ([FRBNY SR239 / JMCB 2012](https://www.newyorkfed.org/research/staff_reports/sr239.html) [abstract]). Learning agents enter with **Galbiati and Soramäki's fictitious-play agent-based model**, which already ran a throughput-guideline policy experiment ([BoE WP 352 / JEDC 35(6)](https://www.bankofengland.co.uk/working-paper/2008/an-agent-based-model-of-payment-systems) [abstract]). They also appear in an Erev–Roth reinforcement-learning paper of unverified authorship ([Essex DP700](https://repository.essex.ac.uk/3714/1/dp700.pdf) [abstract]). **Castro, Desai, Du, Garratt and Rivadeneyra** use reinforcement learning to estimate liquidity policies. In a simple two-agent setting their agents reach the cost-minimising policy, and in richer settings they still reduce liquidity costs ([BoC SWP 2021-7](https://econpapers.repec.org/paper/bcabocawp/21-7.htm) [abstract]).

Two corrections are required. **First, Castro et al. has a journal version:** *ACM Transactions on Economics and Computation* 13(1):1–31 (2025). The notes confirm it only through Aldasoro and Desai's reference list; the publisher page was not reached ([BoC SWP 2025-35 references](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf) [partial]). REPORT's reference list cites only the 2021 working paper. **Second, Bank of Canada SWP 2025-35 is the Bank of Canada edition of BIS WP 1310**, "AI agents for cash management in payment systems" by Aldasoro and Desai (DOI 10.34989/swp-2025-35). It is not a follow-up by Castro et al. ([BIS WP 1310](https://www.bis.org/publ/work1310.htm) [abstract]; [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf) [full]). The paper tests a **single prompted commercial language model on three hand-written scenarios**, with 10/10, 9/10 and 8/10 consistency across repeat runs. It contains no fees, surcharges, throughput rules or collective decision rules, and it names a multi-agent simulator as future work.

The institutional work closest to the project is **BIS Project Agenti**, an "Agentic AI Payment Simulator" of an RTGS-like system with heterogeneous bank agents. As of its 14 October 2026 page update it lists no results, report or code ([BIS Project Agenti](https://www.bis.org/node/87745) [full]). It must be re-checked before any external release.

The delay-surcharge result needs a precedent cited. **Ota (2011) found that a linear time-rising intraday tariff beats CHAPS-style throughput guidelines in most cases**, removing inefficient delay while keeping socially efficient delay ([BoE WP 428](https://www.bankofengland.co.uk/working-paper/2011/intraday-two-part-tariff-in-payment-systems) [abstract]). Other papers compare pricing with coordination rules:

- Jurgilas and Martin show that a liquidity-saving mechanism (LSM) can lower welfare under fee-based regimes but not under collateral-based ones ([FRBNY SR438](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr438.html) [abstract]).
- Becher, Galbiati and Tudela treat throughput guidelines as a centralised coordination device ([FRBNY EPR](https://www.newyorkfed.org/medialibrary/media/research/epr/08v14n2/0809becher.html) [abstract]).
- Buckle and Campbell doubt aggregate throughput rules beyond two banks ([BoE WP 209](https://www.bankofengland.co.uk/working-paper/2003/settlement-bank-behaviour-and-throughput-rules) [abstract]).
- Martin and McAndrews analyse LSM welfare ([JME 55(3)](https://econpapers.repec.org/RePEc:eee:moneco:v:55:y:2008:i:3:p:554-567) [abstract]).
- Project Titus runs an auction LSM with side-payments ([BIS WP 1318](https://www.bis.org/publ/work1318.htm) [abstract]).

So "a price beats a central coordination rule" has precedent. **"A price beats the agents' own Kantian or welfare acceptance rules" was not found in this review.** The project's payment claim should be scoped to that comparison.

The project cites FRAIL as "stabilising mechanisms for language-model agents in financial coordination games". That description holds, but FRAIL's agents are prompted, not evolved, with five episodes per cell. Its paid-commitment mechanism was never the best performer ("communication trumps compensation") ([Fu, Xu & Ren, arXiv:2609.30940](https://arxiv.org/pdf/2609.30940) [full]). The project should present FRAIL as a contrasting data point from different games, not as support. PSSimPy is a plausible cross-validation platform: it supports time-varying fees, but it has no delay cost, LSM or learning agents ([GitHub](https://github.com/kennethsee/pssimpy) [full README]; [ICIS 2024](https://aisel.aisnet.org/icis2024/blockchain/blockchain/10) [abstract]).

## Claim 4: the ambient-tax identity is known in spirit, and the learning comparison was not found

**Every ambient-tax source in the notes was seen at abstract or snippet level only. None was read in full.** Within that limit, the project's theory statements largely hold. The project names Holmström (1982) as the origin of the budget-breaking idea and Segerson (1988) as the ambient instrument. Neither paper was opened in this review. Both are attested through secondary sources: a snippet from Millock and Salanié says Segerson drew "on Holmstrom's ... analysis of moral hazard in teams" and that efficiency needs each agent to "bear the full social marginal [damage]" ([Millock & Salanié 2005, PSE PDF](https://extranet.parisschoolofeconomics.eu/docs/millock-katrin/millock-salanie.pdf) [abstract]). A Kellogg working paper also discusses the budget-breaker device ([Georgiadis et al.](https://www.kellogg.northwestern.edu/faculty/georgiadis/EfficiencyDCG.pdf) [abstract]).

REPORT lists four known objections to the ambient tax. Three are attested:

- **Collusion.** Efficiency "does not extend to the case when polluters might cooperate" ([Millock & Salanié](https://extranet.parisschoolofeconomics.eu/docs/millock-katrin/millock-salanie.pdf) [abstract]). Coalitions can also make Segerson's mechanism inefficient ([Hansen 1998, ERE 12(1)](https://ideas.repec.org/a/kap/enreec/v12y1998i1p99-112.html) [abstract]).
- **Large payments.** Millock and Salanié note large transfers, fixable by lump-sum transfers or nonlinear taxes.
- **Information demands.** Hansen notes that Segerson's mechanism needs the regulator to know cost and emission functions when damages are nonlinear.

**The fourth, risk aversion, was not verified in this review.** The likely source (Horan, Shortle and Abler) was not searched.

The laboratory evidence supports "mixed" and is richer than REPORT's single citation. Cochard, Willinger and Xepapadeas found the ambient tax/subsidy welfare-reducing and unreliable, and the working-paper and journal versions differ ([ERE 30(4)](https://ideas.repec.org/p/hal/journl/hal-02680148.html) [abstract]). Other experiments add the following:

- **Spraggon (2002):** group-level success, but "none of the instruments insures compliance at the individual level" ([J. Public Econ. 84(3)](https://academicnewsletter.sufe.edu.cn/info/284877) [abstract]).
- **Vossler, Poe, Schulze and Segerson:** targets hit at group level, and over-compliance once subjects can talk ([Cornell eCommons](https://ecommons.cornell.edu/entities/publication/253777f6-4a55-4872-bffb-63ea5cc2b32a) [abstract]).
- **Suter, Vossler, Poe and Segerson (2008):** damage-based taxes approximate the optimum without communication ([AJAE 90(1)](https://digitalcommons.oberlin.edu/faculty_schol/1151) [abstract]).
- **Willinger, Ammar and Ennasri (2014)** reconcile the earlier results ([ERE 59(3)](https://ideas.repec.org/a/kap/enreec/v59y2014i3p479-502.html) [abstract]).

PROJECT.md §3.4 cites "Vossler et al. 2008". The notes support either Vossler et al. in *Economic Inquiry* (working paper 2002; journal year not confirmed) or Suter, Vossler, Poe and Segerson 2008 in AJAE. The reference must be fixed to one of these. One nuance bears on the project's own conclusion that collusion could reopen the line. In the laboratory, communication under ambient taxes often produced **over-abatement, not collusion against the tax**.

**The identity "ambient tax at level 1 = unilateral welfare gate" holds but is known in spirit.** Charging each agent the damage in all other modules turns its payoff into private benefit minus total damage. That is a Groves-form transfer, and Groves mechanisms are generally not budget-balanced ([arXiv:1203.1809](https://arxiv.org/pdf/1203.1809) [abstract] [arXiv ID verified in second pass]). No source found states the identity explicitly. The project should present it as an observation attributed to Segerson and Holmström, not as a result. On the MARL side, **LOPT learns a Pigouvian tax that reshapes each agent's reward toward social welfare**, conceptually the same object, and must be cited ([Hua et al., NeurIPS 2025](https://proceedings.nips.cc/paper_files/paper/2025/hash/34321b2d5c5f5ce3f856df87648b12eb-Abstract-Conference.html) [abstract]; [arXiv:2305.06227](https://arxiv.org/html/2305.06227v2) [abstract] [arXiv ID verified in second pass]). The project's differences from LOPT are that harm is unattributable, the harm's carrier can be concealed, and the instrument is a fixed rule rather than a learned planner. Other MARL incentive work follows a similar pattern:

- Zheng et al.'s two-level tax design ([*Science Advances* 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9067926) [abstract]);
- LIO ([arXiv:2006.06051](https://arxiv.org/pdf/2006.06051) [abstract] [arXiv ID verified in second pass]);
- gifting ([arXiv:2105.06593](https://arxiv.org/pdf/2105.06593) [abstract] [arXiv ID verified in second pass]);
- inequity aversion ([Hughes et al., NeurIPS 2018](https://proceedings.neurips.cc/paper/2018/hash/7fea637fd6d02b8f0adf6f7dc36aed93-Abstract.html) [abstract]).

In all of these, the planner observes individual actions or attributable effects.

Three gaps survive, all at abstract-level evidence. **This review found no agent-based or learning simulation of an ambient tax.** It also found **no head-to-head comparison of a Kantian decision rule with an ambient tax** under unobservable individual emissions. And it found **no study in which learning agents game an externality charge by concealment**: the tax-gaming in Zheng et al. is income timing, not hiding a harm carrier. The economics of tax and morality treats the two as complements, asking which tax is optimal given moral agents. Examples are Daube and Ulph, where the optimal tax stays Pigouvian ([ERE 63](https://link.springer.com/10.1007/s10640-014-9836-2) [abstract]); Eichner and Pethig ([IDEAS](https://ideas.repec.org/p/ces/ceswps/_8749.html) [abstract]); and Muñoz Sobrado ([CESifo 2022](https://www.cesifo.org/en/publications/2022/working-paper/taxing-moral-agents) [abstract]). The project's framing of a norm gate and a tax as **substitute** instruments is the distinct angle. Holmström and Milgrom (1991), which the project cites for the concealment result, was named in searches but not verified in this review. Keep the citation, but check it before release.

## Claim 5: technical debt as a commons already has a game-theoretic simulation

PROJECT.md §3.4 says that "no agent-based or game-theoretic simulation of [technical debt as a commons] was found". **That statement is wrong and must be removed.** Gavidia-Calderon, Sarro, Harman and Barr published "Game-theoretic analysis of development practices: Challenges and opportunities" in *Journal of Systems and Software* 159:110424 (2020), DOI 10.1016/j.jss.2019.110424, presented as journal-first at ASE 2020 ([ORO record](https://oro.open.ac.uk/79717) [abstract]; [ASE listing](https://conf.researchr.org/details/ase-2020/ase-2020-journal-first-papers/3/Game-theoretic-Analysis-of-Development-Practices-Challenges-and-Opportunities) [abstract]). The JSS paper itself was not opened, because the fetch was refused. Its content was read through **chapter 4 of Gavidia-Calderon's 2020 UCL thesis**, which states that it is based on the paper ([UCL Discovery](https://discovery.ucl.ac.uk/id/eprint/10106595/) [partial: chapter 4 read in full]). The thesis says verbatim that **"Technical debt is a tragedy of the commons"**. Its model works as follows:

- **Simulation.** A discrete-event Kanban simulation calibrated on Eclipse bug data. Each developer chooses fix or kludge, and each kludge raises shared resolution time by 0.05T.
- **Equilibrium.** The two-player empirical game has a unique kludge equilibrium (9.06 each, against 9.80 each under mutual fixing), which is a prisoner's dilemma.
- **Intervention.** A code reviewer who detects 25 % of kludges makes fixing the unique equilibrium.

The thesis also sketches a "tragedy of the test suite" and the assessor-throttling reputation mechanism.

The project's codebase model still differs in substance, judged from chapter 4 only. Gavidia-Calderon et al. have two players with binary heuristic strategies and a linear quality penalty. They model no incident process, no module ownership and no concealment, and their instrument is a detection probability rather than a charge. Their model also lacks continuous shortcut intensity, a hidden share of coupling, convex incident hazard, cross-module cost-shifting, operator pricing and evolutionary dynamics over many agents. The corrected background sentence should cite them as direct prior work and claim only that combination as "not found in this review".

Supporting citations should be adjusted. Sundelin et al.'s "Governing the Commons" is a Bayesian multilevel model of clone introduction under weak ownership. Its abstract does not state the "non-owner changes create more clones" result that PROJECT.md paraphrases, so that wording needs a full-text check ([arXiv:2405.15866](https://arxiv.org/abs/2405.15866) [abstract]). Further framing citations:

- **Baldwin and Clark (2006):** the canonical game-theoretic model of modularity reducing free riding in open source ([Management Science 52(7)](https://ideas.repec.org/a/inm/ormnsc/v52y2006i7p1116-1127.html) [abstract]).
- **MacCormack and Sturtevant (2016):** coupling predicts defect-related effort across more than 20,000 components ([JSS 120 listing](https://core.ac.uk/download/154881372.pdf) [abstract]).
- **A system-dynamics model of technical-debt management** with no strategic agents ([arXiv:1609.06868](https://arxiv.org/abs/1609.06868) [abstract] [arXiv ID verified in second pass]).

A 2026 empirical literature motivates the multi-agent setting, though none of it treats inter-agent harm as an externality or tests charges:

- **CooperBench:** a coordination penalty of about 30 % for two agents working in one repository ([arXiv:2601.13295](https://arxiv.org/html/2601.13295) [abstract] [arXiv ID verified in second pass]).
- **Agent pull requests:** merge conflicts in 41.7 % of cross-agent pairs against 19.8 % of intra-agent pairs ([arXiv:2607.04697](https://arxiv.org/abs/2607.04697) [abstract]).
- **NP-Bench**, a scheduling planner for parallel coding agents ([arXiv:2610.07261](https://arxiv.org/abs/2610.07261) [abstract]).
- **Coherence debt** in single-agent repository-scale tasks ([arXiv:2608.16630](https://arxiv.org/abs/2608.16630) [abstract]).
- **Cost optimisation of mixed AI-human teams by simulation** ([arXiv:2610.20394](https://arxiv.org/abs/2610.20394) [abstract]).
- **Adoption studies:** after one AI coding tool was adopted, static-analysis warnings rose about 30 % and complexity about 41 % ([arXiv:2511.04427](https://arxiv.org/html/2511.04427v2) [abstract] [arXiv ID verified in second pass]).

One naming hazard: the term **"agentic technical debt" is already taken** by Hydari, Iqbal and Ramasubbu ([arXiv:2605.27320](https://arxiv.org/abs/2605.27320) [abstract]). Formal analysis of internal pricing for software quality is thin. The only sources found are SRE error-budget guidance written for practitioners ([SRE Workbook](https://sre.google/workbook/error-budget-policy/) [abstract]) and the review-detection instrument above.

## Search method and coverage

The review comes from five topic notes, all dated 18 November 2026, with **118 logged search or fetch entries**: 30 on self-improving agents, 20 on Kantian theory, 23 on payment systems, 24 on ambient taxes and incentive design, and 21 on technical debt. The first self-improving-agents entry alone covered eight arXiv abstract pages. Discovery ran through **one general web search engine**, in standard and extended modes. Pages were then fetched from arXiv (abstract and HTML), central-bank and BIS sites, RePEc/IDEAS/EconPapers, publisher and author pages, GitHub, and university repositories. Search results arrived as machine-generated summaries. Claims used here were checked against the primary page where the notes say so, and otherwise carry an [abstract] tag.

**Read in full or largely in full:**

- Roemer 2015, Sher 2020 and Curry and Roemer 2012, with Vallentyne 2020 in part;
- Aldasoro and Desai (BoC SWP 2025-35) and FRAIL;
- the Project Agenti page and the PSSimPy README;
- chapter 4 of the Gavidia-Calderon thesis;
- the arXiv HTML bodies of SAGE, PACE, the Skill–Policy paper, the evolved-constitutions paper, CORAL, Hyperagents v1, MASS, AIDE², Misevolve, the co-evolution survey, Internal vs External, Economy of Minds, DGM and the self-evolving-agent safety survey (arXiv:2610.00093);
- about 75 % of GovSim.

Most of those arXiv pages were cut at about 100k characters, so some late appendices went unseen: DGM App. A.3/C.2 and Hyperagents App. E.5. **Seen at abstract or snippet level only:** every ambient-tax and MARL-incentive source; Alger and Weibull; Roemer 2019 (cited through Sher's summary); Galbiati and Soramäki; Castro et al.; Ota; Martin and McAndrews; the JSS 2020 paper itself; Agogino and Tumer; the ICML 2026 Kantian workshop paper (whose PDF was not retrieved); and all of the 2026 coding-agent empirical papers.

**Fetch failures:**

- Hyperagents latest-version HTML returned 404.
- The SAGE, safety-survey, Roemer, Sher, Vallentyne, Curry–Roemer, BoC and FRAIL PDFs came back as undecoded binary. Most were recovered by fetching the HTML version or by extracting the text locally.
- BIS WP 1310 returned its landing page only.
- The Millock and Salanié PDF could not be text-extracted.
- The UCL staff copy of the JSS paper refused the connection.
- Tumer's publication page returned 404.
- The ACM TEAC page for Castro et al. was never reached.

**Not searched directly:**

- **General academic indexes:** Google Scholar, Semantic Scholar, SSRN, ACM Digital Library, IEEE Xplore, the OpenReview search interface, and GECCO/ALIFE proceedings.
- **Payments:** the Bundesbank, DNB and ECB working-paper series, and arXiv q-fin listings.
- **Software engineering:** TechDebt proceedings, real-options models of technical debt, IT chargeback, and specification gaming by coding agents.
- **Economics and incentives:** Holmström–Milgrom with learning agents; Horan, Shortle and Abler on risk; Aronsson and Johansson-Stenman on moral taxation; and population-based-training interference.

The 26 arXiv IDs first taken from search results or mirrors were all confirmed through the arXiv API in the second pass (§Second pass), with matching titles and authors. Screening was done by one reviewer, with no registered protocol, no formal inclusion criteria and no de-duplicated flow counts. **This is a broad structured review, not a PRISMA systematic review**, and every "not found" below means not found in this review.

## Second pass: open scholarly APIs

The first pass used one general web search engine. A second pass on the same
day queried scholarly indexes directly; the log is in
[literature_notes/api_pass.md](literature_notes/api_pass.md).

**Coverage.**

* arXiv API: 40 identifiers checked, all of them confirmed.
* Crossref: 15 venue and DOI lookups.
* OpenAlex: 32 keyword searches, and citation tracing for nine of eleven
  seed papers (three of the nine only partly).
* Semantic Scholar: all nine searches failed, because its shared rate limit
  is exhausted without an API key.
* Screening was by title, then by abstract. No full texts were read in this
  pass.

**Corrections.**

* The Millock and Salanié title is "Nonpoint source pollution when polluters
  might cooperate".
* Castro et al.'s journal DOI is 10.1145/3691326.
* GovSim (NeurIPS 2024) and LOPT (NeurIPS 2025) venues are confirmed.
* No venue was found for Economy of Minds.

**What the pass adds.** None of it overturns the central gap.

* **Single-agent gate comparisons are now a small literature.** *Masked
  Erosion* (arXiv:2610.38392) compares ten gate rules across 411 improvement
  loops, and SEA (arXiv:2607.00871) uses an anytime-valid admission gate.
  Both concern single agents, so neither involves externalities between
  agents. [abstract]
* **When learning rules themselves are selected, selfish learning is
  unstable and other-regarding rules are favoured.** This is McAvoy et al.
  (2022, *PNAS Nexus*), in two-player repeated games. It is the closest
  theory to comparing gates, without prices. [abstract]
* **Partial Kantian equilibria are defined in the theory literature.**
  Kordonis (2020) gives the r-Kant-Nash equilibrium, and Istrate (2020)
  interpolates between self-regarding and Kantian behaviour. The project's κ
  mixture should cite both. [abstract]
* **The Kantian counterfactual depends on the scale in which actions are
  represented** (Sloev and Lianos 2026, arXiv:2610.28180, building on
  Sher–Roemer). The project's additive gate shifts every agent by the same
  amount in its own policy units. A different but equivalent parameterisation
  could give a different Kantian outcome. This is a limitation that should be
  stated. [abstract]
* **Learned prices among learning agents exist outside the LOPT line.**
  Danassis et al. (2026, *JAAMAS*) is a deep-RL policymaker setting market
  prices against common-pool externalities. [abstract]
* **An agent-based model of ambient policies exists.** Wu (2017, Delaware
  dissertation, ch. 2) calibrates an ABM from lab data. In the lab (ch. 1),
  size and location heterogeneity reduced the effectiveness of an ambient
  tax/subsidy unless peer information was given.
  * The Claim 4 statement that no agent-based simulation of ambient taxes was
    found is therefore narrowed. What was not found is a simulation with
    learning agents that compares an ambient tax with a moral acceptance
    rule.
  * The lab result also qualifies E10: the ambient tax's robustness to
    unequal exposure was shown for risk-neutral learning agents, not for
    human subjects. [abstract]
* **Late-settlement fees appear as a coordination device in payments**
  (Nellen 2019, *J. Bank. Finance*). [title only]
* **The citers of Gavidia-Calderon et al. add nothing new.** None of its 25
  citers models technical debt as a shared stock with strategic agents.

## Full texts read after the second pass (20 November 2026)

Open-access copies were found through OpenAlex and read from free versions:
an author's working paper, arXiv, HAL, or the publisher's open-access PDF. No
library subscription was used. Copies are kept locally in a folder that is not
committed.

| Work | Version read | What it adds |
|---|---|---|
| Spraggon (2002) | McMaster working paper 98-01 (1998) [full, earlier version] | Segerson-type instruments work for the group but not for individuals; individuals can incur large fines even when choosing the optimal action |
| Cochard, Willinger, Xepapadeas (2005) | BETA working paper 2002-20 [full, earlier version] | Polluters bear the damage themselves, as in the codebase model. Under the ambient tax, subjects cooperated to maximise group payoff, over-restrained, and welfare fell *below* no regulation, unreliably. The input tax was almost perfectly efficient. Removing the subsidy part of the ambient tax restored efficiency |
| Kordonis (2020) | arXiv:1609.01921 v2 [full] | The r-Kant-Nash equilibrium: each player imagines a virtual group of co-movers bound to the same strategy that minimises its mean cost. This differs from the project's κ, which mixes two own-cost scores |
| Laslier (2022) | HAL halshs-03227354 (2021) [partial: abstract and introduction] | With roles assigned at random behind a veil of ignorance, any equilibrium of the universalized game is an equilibrium with utilitarian-altruistic players, but not the converse. This is consistent with the E10 derivation, because E10 fixes exposure rather than randomising it |
| Danassis et al. (2026) | Publisher's open-access PDF [partial: abstract, introduction, model] | Both the price-setting policymaker and the harvesters learn, and harvests are observable. This is a learned price on an attributable externality, in the same class as LOPT |

**Not obtained.**

* Gavidia-Calderon et al. (2020): the repository copy is behind a bot check.
  The thesis chapter, read earlier, remains the source.
* Eichner and Pethig (2022): the SSRN copy refused automated download.
* Nellen (2019) and Alger and Weibull (2016): no open copy exists.

The owner may download these through the library; see PROJECT.md §3.5.

**Effect on the project.** Cochard et al. sharpens a stated assumption. The
ambient tax's success in E9 and E10 depends on agents not coordinating
against it, and human subjects in a closely matching setting did coordinate.
The report's limitations now say so.

## Third pass: Google Scholar, run by the owner (20 November 2026)

The owner ran the queries below by hand: 9 keyword searches and 3 cited-by
searches, about 110 results. The screening log is in
[literature_notes/scholar_pass.md](literature_notes/scholar_pass.md).

**No result compares acceptance rules among several learning agents with
mutual externalities, or Kantian rules against prices. The central gap still
holds.**

New items:

* **AI agents in payment systems.** Danisman, Desai, Jiang, Rivadeneyra and
  Azad (2026) put prompted language-model agents into an RTGS
  intraday-liquidity game, in three treatments that vary prompts and
  equilibrium structure. They are the closest multi-agent AI agents in
  payments, but they are prompted, not evolved, and do not compare gates or
  prices. [search snippet only]
* **Moral agents and taxes.** Herweg and Schmidt (2022, *EJ*) and Bierbrauer
  et al. (2026) extend the "optimal tax given moral agents" line, not a
  norm-versus-tax comparison. In multi-agent RL, Tennant et al. (2023,
  IJCAI) put moral theories into rewards, not into acceptance rules.
* **Ambient policies.** Miao (2017) and Malakpour Estalaki and Hu (2022) add
  to Wu (2017): agent-based and experimental work on ambient policies
  exists, but none with learning agents compared with a moral rule.
* **Technical debt.** Sundelin et al. is now in *Empirical Software
  Engineering* (2025).
  * Baltes, Cheong and Treude (2026, *IEEE Software*) frame AI-assisted
    development as a tragedy of the commons, from 1,154 developer posts.
    This is empirical support for the premise of the codebase environment.
  * Fungprasertkul, Bahsoon and Kazman (2024, *TOSEM*) treat technical-debt
    decisions as a problem of asymmetric payoffs.
  * No further simulation of a shared debt stock with operator charges
    turned up.

## Missed by this review, found by an independent audit (23 November 2026)

An independent audit of the repository cited work this review did not find.
Each DOI was checked in Crossref; contents below are from the abstracts only.

* **Willis, Du, Leibo and Luck (2024)**, *Resolving social dilemmas with minimal
  reward transfer*, Auton. Agents Multi-Agent Syst. 38, 49
  (doi:10.1007/s10458-024-09675-4). Redistributes rewards among agents so that
  a social-welfare optimum becomes a dominant strategy, and measures how much
  of its own reward each agent can keep. Directly relevant to the equal
  output-sharing result (REPORT §4.6): budget-balanced transfers, not only
  budget-breaking taxes, can align incentives.
* **Haupt, Christoffersen, Damani and Hadfield-Menell (2024)**, *Formal contracts
  mitigate social dilemmas in multi-agent reinforcement learning*, Auton.
  Agents Multi-Agent Syst. 38, 51 (doi:10.1007/s10458-024-09682-5). Agents agree
  binding reward transfers; with a rich enough contract space all subgame-
  perfect equilibria of fully observable Markov games are socially optimal.
* **Mohanty, Rao and Roy (2024)**, *Kantian imperatives in public goods
  networks*, J. Econ. Behav. Organ. 224, 194–214
  (doi:10.1016/j.jebo.2024.05.018). No abstract in Crossref; not yet read. By
  its title it bears on Kantian behaviour when agents sit in different network
  positions, which is the setting of E10. Read in full before any novelty
  statement about unequal exposure.
* **Couto and Pal (2023)**, *Introspection dynamics in asymmetric multiplayer
  games*, Dyn. Games Appl. 13, 1256–1285 (doi:10.1007/s13235-023-00525-8).
  Players compare their current strategy with an alternative and adopt it more
  often when it pays more, in asymmetric multiplayer games: close to the
  propose–evaluate–accept loop used here.

Consequence: the claim that a gate is useful where only budget-balanced
instruments are feasible was already weak against this literature, and the
audit's counterexample (equal output sharing) removes it in our model.

## Google Scholar queries for the owner

Google Scholar refuses automated clients, so these are for a manual check.
For each, scan the first two pages and note anything that compares
acceptance or selection rules among several learning agents, or Kantian
rules against prices.

1. `"acceptance rule" OR "acceptance gate" multi-agent self-improving externality`
2. `universalization OR Kantian "learning agents" selection rule`
3. `"Kantian equilibrium" heterogeneous agents efficiency`
4. `"Kantian" "Pigouvian" OR "ambient tax" comparison`
5. `"ambient tax" "agent-based" OR "reinforcement learning"`
6. `"technical debt" "tragedy of the commons" OR "public good" model`
7. `"payment system" liquidity "learning agents" OR "reinforcement learning" fee`
8. `"self-evolving agents" "multi-agent" acceptance social dilemma`
9. Cited-by lists of Roemer (2015) "Kantian optimization", Segerson (1988), and Gavidia-Calderon et al. (2020), filtered with the words `learning`, `simulation` or `agent`.

## Conclusion

The review moves EvoRTGS's contribution from "new objects" to "a new comparison". Acceptance gates (SAGE, PACE), Kantian theory (Roemer, Alger–Weibull), payment learning (Galbiati–Soramäki, Castro et al.), ambient taxes (Segerson, Holmström), learned Pigouvian taxes (LOPT) and technical debt as a game (Gavidia-Calderon et al.) all exist. What was not found is the matched-budget comparison of per-agent gates against prices among co-evolving agents. The defensible novelty is the comparison, and the write-up gains credibility by saying so.

The E10 correction changes how the result reads. If the Kantian equilibrium is the optimum for a planner who weights agents by 1/exposure, then "the gate loses under unequal exposure" is a statement about whose welfare the reference optimum counts. A reader who prefers that implicit weighting would score the gate differently. The project's utilitarian optimum is a choice and should be named as one. The derivation also turns E10 from a confirmation of a "known property" into a small checkable result. It should be presented with its first-order conditions, so a reader can verify it rather than search for a source that does not exist.

## Statement-by-statement verdicts

| Project statement (location) | Verdict | Required change | Citation(s) and evidence |
|---|---|---|---|
| "We did not find prior work treating the acceptance rule of co-evolving agents as the experimental factor" (REPORT §2) | Holds | Keep as "not found in this review". Add single-agent gate studies and single-lineage ablations as precursors | SAGE 2609.36043 [full]; PACE 2606.08106 [full]; Skill–Policy 2610.20845 [partial]; DGM 2505.22954 [partial]; Hyperagents 2603.19461 [partial]; Agogino & Tumer [abstract] |
| Self-improving systems "are evaluated one at a time against fixed benchmarks" (REPORT §1) | Reword | Say "single lineages or agents with a common objective", since CORAL runs several agents | CORAL 2604.01658 [partial]; MASS 2610.12176 [partial]; AIDE² 2609.26457 [partial] |
| Co-evolution survey "body not read" (PROJECT §3.2) | Reword | Body now read: no externality, commons or welfare gating | Survey 2608.10299 [partial] |
| Economy of Minds "(NeurIPS 2026)"; AIDE² "reward hacking 55 %→32 %" (PROJECT §3.2) | Reword | Not supported by this review; verify or drop | Economy of Minds 2606.02859 [partial]; AIDE² 2609.26457 [partial] |
| Kantian optimisation (Roemer 2019) and homo moralis (Alger & Weibull 2013) supply the κ-gate theory (REPORT §2) | Reword | Cite Roemer 2015 as primary. Note that κ uses the simple-Kantian counterfactual, not K+/K×. Add Alger & Weibull 2016 and the 2023 corrigendum | Roemer 2015 [full]; Roemer 2019 via Sher [abstract/summary full]; Alger & Weibull 2013, 2016 [abstract] |
| Kantian equilibria are known to be efficient in symmetric common-pool problems; E9 expected (REPORT §2, §6) | Holds | Optionally strengthen: K+ and K× are Pareto efficient with heterogeneous agents in strictly monotone games | Roemer 2015 Thm 1, Prop 1 [full]; Vallentyne 2020 [partial] |
| Unequal-exposure over-restraint and over-reach "is a known property of Kantian equilibria" (REPORT §6) | Wrong | Replace with: Kantian equilibria remain Pareto efficient and are the welfare optimum with weights ∝ 1/exposure. Relative to the equal-weight optimum, the K+ first-order condition implies exposed agents over-restrain and less-exposed agents over-reach (own derivation, shown). Do not call it Pareto inefficiency unless the gate is simple-Kantian or κ < 1 | Roemer 2015 [full]; Sher 2020 [full]; Sloev & Lianos 2606.21931 [abstract]; Eichner & Pethig 2022 [abstract] |
| Universalization used as a decision-time prompt (Piatti et al. 2024, "NeurIPS 2024") (REPORT §2) | Holds; venue reword | Keep. Mark venue unverified. Add the workshop, Melting Pot and SFT uses | GovSim 2404.16698 [partial]; Samoylenko 2026 [abstract]; Leibo et al. 2021 [abstract]; Lu et al. 2507.20796 [abstract]; Levine et al. 2020 [abstract] |
| Payment-timing dilemma and learning agents are established (REPORT §2) | Holds | Add the 2006/2012 n-player model and the Erev–Roth line if desired | Bech & Garratt 2003 [partial, via reference list]; SR239 [abstract]; Galbiati & Soramäki [abstract] |
| Castro et al. 2021 cited only as BoC SWP 2021-7 (REPORT refs) | Reword | Add journal version: *ACM TEAC* 13(1):1–31 (2025) | SWP 2021-7 [abstract]; TEAC via Aldasoro & Desai reference list [partial] |
| BoC SWP 2025-35 attribution (brief / PROJECT §3.2) | Wrong if read as Castro et al. follow-up | Cite as Aldasoro & Desai, BIS WP 1310 = BoC SWP 2025-35; single prompted agent, no fees | BoC SWP 2025-35 [full]; BIS WP 1310 [abstract] |
| Delay surcharge beats every gate (REPORT abstract, §4.2) | Holds; reword scope | Cite pricing-versus-coordination-rule precedent. Claim novelty only for price versus agent-level Kantian/welfare gates | Ota 2011 [abstract]; Jurgilas & Martin [abstract]; Becher et al. [abstract]; Buckle & Campbell [abstract] |
| FRAIL as stabilising mechanisms for LLM agents in financial games (REPORT §2) | Holds | Add that agents are prompted, not evolved, and paid commitments never ranked best (contrast) | Fu, Xu & Ren 2609.30940 [full] |
| BIS Project Agenti as closest institutional overlap (PROJECT §3.2) | Holds | Re-check before any release | BIS Agenti page [full] |
| Holmström 1982 team moral hazard; Segerson 1988 ambient tax (REPORT §2) | Holds | Keep. Primary texts not opened in this review | Millock & Salanié 2005 [abstract]; Georgiadis et al. [abstract] |
| Ambient-tax objections: "noise, risk aversion, collusion, large payments" (REPORT §2) | Reword | Collusion, large transfers and information needs attested. Risk aversion not verified in this review | Millock & Salanié [abstract]; Hansen 1998 [abstract] |
| "Mixed laboratory evidence (Cochard et al. 2005)"; "Vossler et al. 2008" (REPORT §2; PROJECT §3.4) | Reword | Add Spraggon, Vossler et al., Suter et al. 2008, Willinger et al. 2014. Fix "Vossler et al. 2008" to Suter et al. 2008 AJAE or Vossler et al. *Economic Inquiry* | Cochard et al. [abstract]; Spraggon 2002 [abstract]; Vossler et al. [abstract]; Suter et al. 2008 [abstract]; Willinger et al. 2014 [abstract] |
| Identity: ambient tax level 1 = unilateral welfare gate (REPORT §4.4, D6) | Reword | Present as a known-in-spirit Groves/budget-breaker observation, not a result. Cite LOPT | Millock & Salanié [abstract]; arXiv 1203.1809 [abstract, unverified ID]; LOPT NeurIPS 2025 [abstract] |
| Ambient tax beats Kantian gate under unequal exposure; charges gamed into concealment (REPORT §4.3–4.4) | Holds as "not found in this review" | Cite moral-taxation literature as complements framing. Mark Holmström & Milgrom 1991 as unverified | Eichner & Pethig [abstract]; Daube & Ulph [abstract]; Zheng et al. 2022 [abstract]; Holmström & Milgrom (named, not verified) |
| Technical debt as a commons: "No agent-based or game-theoretic simulation of it was found" (PROJECT §3.4) | Wrong | Cite as direct prior work. Re-scope to hidden coupling, convex incidents, cross-module cost-shifting, operator charges and many evolving agents | Gavidia-Calderon et al., JSS 159:110424 (2020) [abstract]; thesis ch. 4 [partial, chapter full] |
| Technical debt "an informal framing in practitioner writing"; non-owner changes create clones (PROJECT §3.4) | Reword | The framing is formal in SE research. Check the Sundelin paraphrase in full text. Add Baldwin & Clark and MacCormack & Sturtevant | Sundelin et al. 2405.15866 [abstract]; Baldwin & Clark 2006 [abstract]; MacCormack & Sturtevant 2016 [abstract] |
