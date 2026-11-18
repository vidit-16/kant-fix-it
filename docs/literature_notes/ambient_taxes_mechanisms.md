# Ambient taxes, team moral hazard and Pigouvian instruments with learning agents; incentive instruments vs agent-level norms in multi-agent learning (novelty check)

Search date: 2026-11-18. Status labels: "read in full" means the full text was read; "abstract only" means only an abstract, index page or search snippet was seen. **No source in this file was read in full.** Every claim below rests on abstracts, RePEc/IDEAS pages, publisher listings or search-engine snippets, so the exact theorem statements still need checking against the full texts.

Search log (query / source / hits screened / included):
1. "ambient tax nonpoint pollution experiment heterogeneous agents collusion Vossler Poe Schulze Segerson" / WebSearch / 10 / 4 (Vossler et al. 2006 Economic Inquiry WP; Suter et al. 2008 AJAE; Suter, Vossler & Poe 2009 Ecol Econ; Suter & Vossler AJAE MS)
2. "ambient tax agent-based simulation reinforcement learning nonpoint source" / WebSearch / 10 / 1 (agent-based ML farmer model, MDPI Mathematics 2025: mentioned only, not verified)
3. "homo moralis Pigouvian taxation Kantian moral preferences externalities optimal tax" / WebSearch / 10 / 3
4. "Pigouvian tax multi-agent reinforcement learning social dilemma" / WebSearch / 10 / 1 (LOPT)
5. Fetch IDEAS ces/ceswps/_8749 (Eichner & Pethig) / abstract only / included
6. "ambient tax budget-balancing Holmström team Groves mechanism each firm pays full damage" / WebSearch / 10 / 2 (Horan et al. multiple choices; Herriges et al. budget-balancing)
7. "Daube Ulph moral behaviour environmental taxation Kantian" / WebSearch / 10 / 1
8. "Learning to Incentivize Other Learning Agents LIO" / WebSearch / 10 / 1
9. Fetch Millock & Salanié PDF (PSE extranet) / FAILED: compressed PDF stream with no extractable text, and pypdf is not installed locally. The journal record came from the running header only. Content was later taken from search snippets (query 11).
10. "Xepapadeas 1991 Environmental policy under imperfect information" / WebSearch / 10 / 2 (JEEM 1991; Kritikos 1993 comment)
11. "Cochard Willinger Xepapadeas 2005 efficiency nonpoint" / WebSearch / 10 / 1
12. "Shortle Horan 2013 policy instruments water quality ambient tax review" / WebSearch / 10 / 1
13. "multi-agent RL prosocial reward shaping versus incentive mechanism taxes" / WebSearch / 10 / 3 (Gifting; LOPT; AAMAS 2022/2023 incentive-design papers, titles not verified)
14. "ambient tax equivalent Groves mechanism ... full marginal damage" / WebSearch / 10 / 4 (Hansen 1998; Millock & Salanié snippets; Willinger et al. 2014; Figuières & Willinger 2012)
15. Fetch IDEAS Hansen 1998 / abstract only
16. Fetch IDEAS Figuières & Willinger 2012 / abstract only
17. "Roemer Kantian equilibrium externalities ... Kantian optimization" / WebSearch / 10 / 2
18. "reward hacking proxy incentive multi-agent ... Goodhart mechanism design" / WebSearch / 10 / 0 peer-reviewed. Mostly blogs and 2026 arXiv preprints, which were not verified.
19. "Spraggon 2002 Exogenous targeting instruments" / WebSearch / 10 / 1
20. "Zheng The AI Economist ... Science Advances 2022" / WebSearch / 10 / 1
21. Fetch IDEAS Willinger, Ammar & Ennasri 2014 / abstract only
22. "Hughes 2018 Inequity aversion improves cooperation" / WebSearch / 10 / 1
23. "Alger Weibull homo moralis Econometrica 2013" / WebSearch / 10 / 1
24. "ambient tax learning dynamics repeated play ... adaptive agents" / WebSearch / 10 / 0 ambient-tax hits. One Oxford-hosted pdf on Pigouvian taxes with reinforcement learners in oligopoly pricing turned up, but its author and venue were NOT verified, so it is not included as a citation.

Not searched, a known gap given the tool budget: Google Scholar directly, SSRN, the 2023–2026 arXiv "Pigouvian"/"tax" MARL papers beyond LOPT, Holmström–Milgrom multitask with RL agents, Kotchen/Segerson follow-ups, Horan–Shortle–Abler on risk aversion, Aronsson & Johansson-Stenman on moral taxation.

---

## Q1. Ambient tax literature: core results (heterogeneity, risk, collusion, learning/repeated play) and any ABM/RL simulation

### Takeaway
The theory and laboratory record on ambient taxes is mature. In theory, a Segerson-type ambient instrument reaches the first best when each agent faces the full social marginal damage. In the lab, it works at the group level but not reliably at the individual level. It is fragile to communication and cooperation, and its performance with heterogeneous agents is mixed. I found **no agent-based or reinforcement-learning simulation of an ambient tax in which the agents themselves learn**. The nearest work uses human-subject repeated play and an ML agent-based model of farmer adoption.

### Cited Findings
- Segerson's ambient instrument draws on Holmström's team moral-hazard analysis. The snippet reads: "Segerson ..., drawing on Holmstrom's ... analysis of moral hazard in teams, noted that one method ... is to charge each firm a unit tax based on the aggregate level of pollution". This comes from Millock & Salanié, "Nonpoint Source Pollution and Cooperation", *Topics in Economic Analysis & Policy* 5(1) Art. 12, 2005 (snippet only; full-text fetch failed) — [PSE PDF](https://extranet.parisschoolofeconomics.eu/docs/millock-katrin/millock-salanie.pdf)
- Millock & Salanié: "Efficiency obtains when the tax is computed so that each agent bears the full social marginal [damage]". Large transfers can be corrected by a lump-sum transfer or a nonlinear tax. "The efficiency result for ambient taxes does not extend to the case when polluters might cooperate" (snippets) — [PSE PDF](https://extranet.parisschoolofeconomics.eu/docs/millock-katrin/millock-salanie.pdf)
- Xepapadeas, "Environmental policy under imperfect information: incentives and moral hazard", *JEEM* 20(2):113–126, 1991. A later comment by Kritikos (JEEM 1993) describes it as presenting a budget-balancing mechanism that implements optimal emissions when only aggregate emissions are observable (abstract and snippet only) — [Scilit](https://scilit.net/publications/1777bd22210e74b771f2e1956a228674)
- Hansen, "A Damage Based Tax Mechanism for Regulation of Non-Point Emissions", *ERE* 12(1):99–112, 1998. Segerson's mechanism needs knowledge of cost and emission functions when damages are nonlinear, and it can encourage coalitions that make it inefficient. Hansen's damage-based version removes the need for that knowledge and makes coalitions less likely (abstract only) — [IDEAS](https://ideas.repec.org/a/kap/enreec/v12y1998i1p99-112.html)
- Horan et al., "Ambient taxes when polluters have multiple choices" (JEEM). It studies optimal design and budget-balancing properties when firms have richer choice sets than in Segerson's model (OSTI abstract only) — [OSTI](https://www.osti.gov/scitech/biblio/659030)
- Herriges, Govindasamy & Shogren, "Budget-Balancing Incentive Mechanisms", *JEEM* 27(3):275–285, 1994 (citation page only) — [IDEAS](https://ideas.repec.org/r/eee/jeeman/v27y1994i3p275-285.html)
- Spraggon, "Exogenous targeting instruments as a solution to group moral hazards", *J. Public Econ.* 84(3):427–456, 2002. A lab test of Holmström forcing-contract instruments (multiple equilibria) against Segerson-type instruments (unique equilibria). Some instruments reduce moral hazard at the group level, and the result is robust to uncertainty and experience. "None of the instruments insures compliance at the individual level" (abstract only) — [SUFE abstract page](https://academicnewsletter.sufe.edu.cn/info/284877)
- Cochard, Willinger & Xepapadeas, "Efficiency of Nonpoint Source Pollution Instruments: An Experimental Study", *ERE* 30(4):393–422, 2005. It compares an input tax, an ambient tax/subsidy, an ambient tax and a group fine. The abstract reports that the ambient tax/subsidy lowers welfare relative to the status quo and is very unreliable. The 2002 WP version reports the input tax as almost perfectly efficient. Results differ between versions (abstract only) — [IDEAS/HAL](https://ideas.repec.org/p/hal/journl/hal-02680148.html)
- Willinger, Ammar & Ennasri, "Performance of the Ambient Tax: Does the Nature of the Damage Matter?", *ERE* 59(3):479–502, 2014. Its abstract reconciles Spraggon (external damage) and Cochard et al. (internal damage): "the ambient tax is equally efficient under internal and external damage" (abstract only) — [IDEAS](https://ideas.repec.org/a/kap/enreec/v59y2014i3p479-502.html)
- Vossler, Poe, Schulze & Segerson, lab test of Segerson's mechanisms (marginal tax/subsidy, fixed penalty, combination) with and without cheap talk (WP 2002; *Economic Inquiry*). Without discussion, the tax/subsidy hits the target at group level but not at individual level. Discussion leads to over-compliance under the tax/subsidy (abstract only) — [Cornell eCommons](https://ecommons.cornell.edu/entities/publication/253777f6-4a55-4872-bffb-63ea5cc2b32a); [EconPapers](https://econpapers.repec.org/RePEc:ags:cudawp:127334)
- Suter, Vossler, Poe & Segerson, "Experiments on Damage-Based Ambient Taxes for Nonpoint Source Polluters", *AJAE* 90(1):86–102, 2008. Linear and nonlinear damage-based taxes approximate the optimum without communication. With communication, emissions fall well below the optimum, and rescaling the tax restores efficiency (abstract only) — [Oberlin](https://digitalcommons.oberlin.edu/faculty_schol/1151); [EconPapers](https://econpapers.repec.org/RePEc:oup:ajagec:v:90:y:2008:i:1:p:86-102)
- Suter, Vossler & Poe, "Ambient-Based Pollution Mechanisms: A Comparison of Homogeneous and Heterogeneous Groups of Emitters", *Ecological Economics* 2009. Theory says the mechanisms do not depend on firm characteristics, while policy discussion favours homogeneous groups (abstract only) — [Oberlin](https://digitalcommons.oberlin.edu/faculty_schol/1304)
- Suter & Vossler, AJAE manuscript: an ambient tax with heterogeneous dairy farms and stochastic pollution, with students vs farmers. It reports group-level compliance in both pools (manuscript landing, abstract only) — [UTK PDF](https://volweb.utk.edu/~cvossler/files/AJAE%20MS%2012224.pdf)
- Shortle & Horan, "Policy Instruments for Water Quality Protection", *Annual Review of Resource Economics* 5:111–138, 2013. Practical NPS approaches "will necessarily be second best", and information challenges dominate (abstract only) — [EconPapers](https://econpapers.repec.org/RePEc:anr:reseco:v:5:y:2013:p:111-138)
- Figuières & Willinger, "Regulating ambient pollution when social costs are unknown", LAMETA WP 12-17, 2012. A mechanism that Nash-implements Pareto-optimal ambient pollution without conditioning on individual emissions and without the regulator knowing preferences, given a known number of agents (abstract only) — [IDEAS](https://ideas.repec.org/p/lam/wpaper/12-17.html)

### Inferences
- **Collusion and communication is the best-documented weakness.** Millock & Salanié and Hansen (theory) and Vossler et al. and Suter et al. (lab) all report it. The project's setting has agents that learn independently with no communication channel, so it sits in the regime where the literature finds ambient taxes work. That should be stated as a scope condition.
- **"Ambient tax ≈ Kantian gate with identical agents" is consistent with the lab finding of group-level efficiency.** The project's distinct contribution is that learning agents reach it without human subjects, and that heterogeneous exposure favours the ambient tax over a symmetric Kantian rule. The heterogeneity-in-exposure angle (unequal exposure to harm, as opposed to unequal abatement costs) does not appear in the abstracts seen. Suter, Vossler & Poe (2009) and the Suter & Vossler dairy paper study heterogeneity in emitter characteristics, and their full texts should be checked before claiming novelty.
- **The project's "budget-breaking, each agent charged the full incident loss in all other modules" design is the classic large-transfer Segerson/Holmström form.** The literature already flags its fiscal burden and the lump-sum fixes, so the novelty lies in the comparison and the learning setting, not in the instrument.
- No RL or ABM study of ambient taxes with learning polluters was found in these searches. This is weak evidence of a gap, because Scholar and arXiv were not searched directly.

### Gaps
- Risk aversion results for ambient taxes: not found in this pass. The relevant authors are probably Horan, Shortle & Abler (1998), and they were not searched.
- The full text of Millock & Salanié could not be extracted. Its claims rest on snippets only.
- Verified 2023–2026 ambient-tax ABM or learning studies: none found. An MDPI *Mathematics* (2025) ML agent-based farmer model with ambient subsidies was mentioned by a search engine but not opened or verified.

---

## Q2. Is "ambient tax = each agent internalises total welfare (Groves/VCG-like)" stated in the literature?

### Takeaway
The substance is standard. Efficiency requires each agent to bear the *full* social marginal damage, which is a Holmström (1982) team-style budget-breaker. However, I found **no source that explicitly states the identity "ambient tax at full level equals each agent maximising total welfare, a Groves-like transfer"**, nor the project's specific identity "ambient tax at level 1 equals the unilateral welfare-maximising acceptance rule". It is best presented as a known-in-spirit, easily derived equivalence and attributed to Segerson (1988) and Holmström (1982), not claimed as new.

### Cited Findings
- Each agent must "bear the full social marginal [damage]" for efficiency (Millock & Salanié 2005, snippet) — [PSE PDF](https://extranet.parisschoolofeconomics.eu/docs/millock-katrin/millock-salanie.pdf)
- The Segerson unit ambient tax is explicitly derived from Holmström's teams analysis (same source, snippet) — [PSE PDF](https://extranet.parisschoolofeconomics.eu/docs/millock-katrin/millock-salanie.pdf)
- Groves mechanisms are generally not budget-balanced, since payments flow into or out of the system. This is the analogue of the ambient tax's budget breaking — [arXiv 1203.1809, Undominated Groves Mechanisms](https://arxiv.org/pdf/1203.1809)
- Holmström's (1982) "budget breaker" device is discussed in the dynamic-contribution-games literature (Georgiadis et al., Kellogg WP) — [Kellogg PDF](https://www.kellogg.northwestern.edu/faculty/georgiadis/EfficiencyDCG.pdf)
- Figuières & Willinger (2012) cite Groves & Ledyard (1977) in an ambient-pollution mechanism paper, but the abstract does not draw an explicit ambient-tax/Groves equivalence — [IDEAS](https://ideas.repec.org/p/lam/wpaper/12-17.html)

### Inferences
- The equivalence follows directly from charging agent i the damages in all other modules. Agent i's payoff then becomes own private benefit minus total damage (up to a constant), which is a Groves-form transfer with the "h_i" term set to zero. Reviewers in mechanism design will regard this as known, so the project should frame its identity as a convenient observation linking the learning-rule gate and the tax. It should not be framed as a theorem contribution.

### Gaps
- An explicit textual statement linking ambient taxes to Groves/VCG could not be located. Candidates to check in full text are Herriges, Govindasamy & Shogren (1994), Xepapadeas (1991), Segerson (1988) and Figuières & Willinger (2012).

---

## Q3. Moral or Kantian norms vs Pigouvian or ambient taxes

### Takeaway
There is an active economics line on *optimal taxation in the presence of* Kantian or homo moralis agents: Daube & Ulph 2016, Eichner & Pethig 2020/2022, and Muñoz Sobrado. Roemer shows that Kantian optimisation alone decentralises efficient outcomes in commons games. However, **no source compared a Kantian decision rule head-to-head with an ambient tax under unobservable individual emissions**, and none studied this with learning agents. The result that an ambient tax beats a symmetric Kantian rule under unequal exposure appears new, subject to full-text checks.

### Cited Findings
- Roemer, "Kantian optimization: A microfoundation for cooperation", *J. Public Econ.* 127:45–57, 2015. Additive Kantian equilibria of strictly monotone games (including the tragedy of the commons) are Pareto efficient, so Kantian optimisation decentralises efficient outcomes with externalities (abstract only) — [EconPapers](https://econpapers.repec.org/RePEc:eee:pubeco:v:127:y:2015:i:c:p:45-57)
- Alger & Weibull, "Homo moralis: Preference evolution under incomplete information and assortative matching", *Econometrica* 81(6):2269–2302, 2013. Mixes of selfishness and Kantian morality are evolutionarily stable, and the stable degree of morality equals the assortativity index (abstract only) — [Econometric Society](https://econometricsociety.org/publications/econometrica/browse/2013/11/01/homo-moralis—preference-evolution-under-incomplete-information)
- Daube & Ulph, "Moral Behaviour, Altruism and Environmental Policy", *ERE* 63:505–522, 2016. In their Kantian-style moral model, the optimal environmental tax is the same as the classical Pigouvian one (abstract only) — [Springer](https://link.springer.com/10.1007/s10640-014-9836-2)
- Eichner & Pethig, "Kantians Defy the Economists' Mantra of Uniform Pigovian Emissions Taxes", CESifo WP 8749 (2020); *Ecological Economics* 200 (2022). Materially efficient tax rates are type-specific, lie below the Pigouvian rate, and fall as the propensity to act morally rises (abstract only) — [IDEAS](https://ideas.repec.org/p/ces/ceswps/_8749.html)
- Muñoz Sobrado, "Taxing Moral Agents" (CESifo WP 2022). Homo moralis agents in income-tax design, where taxing low-skilled workers can crowd out the moral motivation of high-skilled workers (search snippet only) — [CESifo](https://www.cesifo.org/en/publications/2022/working-paper/taxing-moral-agents)

### Inferences
- This literature treats morality and taxes as *complements*: what tax is optimal given moral agents. The project instead treats them as *substitute instruments*: a norm gate vs a tax, under non-attributable harm. That framing difference is the defensible novelty claim.
- Eichner & Pethig's type-specific-rate result echoes the project's heterogeneity finding. With heterogeneous agents, a uniform instrument or norm is inefficient. The project's finding (a symmetric Kantian gate underperforms an ambient tax under unequal exposure) should cite them as the closest economic analogue.
- Roemer's efficiency theorem relies on symmetric or monotone game structure. Kantian rules losing efficiency under asymmetry is consistent with his framework (multiplicative vs additive Kantian variants). The full texts should be checked for asymmetric-agent caveats.

### Gaps
- Aronsson & Johansson-Stenman's work on moral or Kantian preferences and taxation was not searched in this pass.
- No paper was found that combines a Kantian norm, an ambient tax and non-observable individual emissions.

---

## Q4. MARL mechanism design: taxes and transfers vs altruistic or social-welfare reward shaping

### Takeaway
MARL work on learned taxes and incentives exists: the AI Economist, LIO, LOPT, and gifting. Separately, there is work on intrinsic social preferences such as inequity aversion. In all incentive work found, the planner or incentive-giver **observes individual actions or attributable externalities**. I found **no paper that compares a tax instrument against an agent-level norm or prosocial reward under non-attributable, concealable harm**. LOPT is the closest: it explicitly casts social dilemmas as externalities and learns a Pigouvian tax.

### Cited Findings
- Zheng, Trott, Srinivasa, Parkes & Socher, "The AI Economist: Taxation policy design via two-level deep multiagent reinforcement learning", *Science Advances* 8(18):eabk2607, 2022. The agents and the planner co-adapt, the method recovers optimal theory in one-step economies, and the learned policies cope with emergent tax-gaming strategies (abstract only) — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9067926)
- Yang, Li, Farajtabar, Sunehag, Hughes & Zha, "Learning to Incentivize Other Learning Agents" (LIO), NeurIPS 2020, arXiv 2006.06051. Agents learn incentive functions that reward others, which yields a division of labour in Escape Room and Cleanup (abstract only) — [arXiv](https://arxiv.org/pdf/2006.06051)
- Hua et al., "LOPT: Learning Optimal Pigovian Tax in Sequential Social Dilemmas", NeurIPS 2025 (earlier arXiv 2305.06227 and AAMAS 2023 extended abstract). A tax agent learns tax and allowance to reshape individual rewards towards social welfare, giving higher welfare than the baselines in Escape Room and Cleanup (abstract only) — [NeurIPS proceedings](https://proceedings.nips.cc/paper_files/paper/2025/hash/34321b2d5c5f5ce3f856df87648b12eb-Abstract-Conference.html); [arXiv](https://arxiv.org/html/2305.06227v2)
- "Emergent Prosociality in Multi-Agent Games Through Gifting" (arXiv 2105.06593). Gifting is offered as a looser alternative to imposed prosocial reward shaping, and it increases convergence to prosocial equilibria in coordination games (abstract only) — [arXiv](https://arxiv.org/pdf/2105.06593)
- Hughes, Leibo et al., "Inequity aversion improves cooperation in intertemporal social dilemmas", NeurIPS 2018. An intrinsic social preference, not a transfer, improves cooperation in Cleanup and Harvest (abstract only) — [NeurIPS proceedings](https://proceedings.neurips.cc/paper/2018/hash/7fea637fd6d02b8f0adf6f7dc36aed93-Abstract.html)

### Inferences
- LOPT's "Pigovian tax reward shaping" makes each agent's reward reflect its effect on social welfare. This is conceptually the same object as the project's ambient tax at level 1 equalling a welfare-maximising rule. LOPT must be cited, and the project should stress the differences: harm is unattributable, carriers can be concealed, and the instrument is a fixed rule rather than a learned planner.
- No direct head-to-head comparison of social-welfare reward shaping (a norm) against a tax under identical conditions surfaced. The search engine also noted this absence. It is weak evidence of a gap.

### Gaps
- 2023–2026 arXiv papers on "Pigouvian"/"tax" MARL other than LOPT were not systematically enumerated.
- The AAMAS 2022/2023 adaptive incentive-design papers (e.g., the meta-gradient incentive designer and IQ-Flow) appeared only as unlabeled PDFs, and their titles and authors were not verified, so they are not cited.

---

## Q5. Multitask gaming of proxy charges by learning agents (Goodhart, reward hacking)

### Takeaway
The economic anchor is Holmström–Milgrom multitask: an incentive on a measurable task diverts effort from the unmeasured task. The AI analogue is reward hacking and Goodhart's law. I found **no peer-reviewed paper in which learning agents game a Pigouvian or ambient charge on an observable by concealment**. The AI Economist reports "tax-gaming strategies" but in a different sense: income timing, not hiding a harm carrier.

### Cited Findings
- The AI Economist's learned policies are robust to "emergent tax-gaming strategies" by learning agents (abstract only) — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9067926)
- Cochard et al. 2005 and Spraggon 2002 report individual-level non-compliance under group instruments. This is behavioural, not concealment-based gaming — [IDEAS](https://ideas.repec.org/p/hal/journl/hal-02680148.html); [SUFE](https://academicnewsletter.sufe.edu.cn/info/284877)

### Inferences
- The project's finding (a charge on visible coupling is gamed into concealment) is a clean multitask or Goodhart demonstration with learning agents in an externality setting. Nothing directly overlapping was found, but the search here was shallow.

### Gaps
- Holmström & Milgrom (1991) and canonical reward-hacking papers (Skalse et al.; Manheim & Garrabrant) were named by a search engine but not verified in this pass. The search results were dominated by blogs and unverified 2026 arXiv preprints, which were excluded.
- A Pigouvian-tax-with-reinforcement-learners paper on oligopoly pricing, hosted on an Oxford personal page, surfaced, but its author and venue were not verified, so it is excluded.
