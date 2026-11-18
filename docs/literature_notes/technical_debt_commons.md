# Technical debt as a commons, and multi-agent shared-repository externalities (novelty check)

Search date: 2026-11-18. Tools: one web search engine (results arrive as a summary from a small model, so every claim used below was checked against the primary page or PDF where marked) and a web page fetcher. No Google Scholar, ACM DL, or IEEE Xplore queries ran directly. Venue coverage comes only from what the web search engine indexes.

## Search log

| # | Query | Source | Screened | Included | Notes |
|---|---|---|---|---|---|
| 1 | fetch arXiv 2405.15866 | arxiv.org abstract | 1 | 1 | abstract only |
| 2 | technical debt tragedy of the commons game theory model | web (extended) | 9 | 1 (2405.15866 again) | the rest were generic commons/debt games |
| 3 | multi-agent LLM coding agents shared repository interference merge conflicts technical debt | web (extended) | 9 | 3 (2610.07261, 2608.16630, 2607.04697) | vendor and practitioner blogs excluded as evidence |
| 4 | fetch arXiv 2610.07261 | arxiv abstract | 1 | 1 | abstract only |
| 5 | fetch arXiv 2608.16630 | arxiv abstract | 1 | 1 | abstract only |
| 6 | CooperBench multi-agent coding collaboration benchmark arXiv | web | 10 | 1 (2601.13295) | abstract/listing only |
| 7 | "technical debt" agent-based simulation OR "system dynamics" model software maintenance | web (extended) | 9 | 4 (1609.06868, CISQ simulator, 2610.20394, 2605.27320) | |
| 8 | fetch arXiv 2610.20394 | arxiv abstract | 1 | 1 | abstract only |
| 9 | fetch arXiv 2605.27320 | arxiv abstract | 1 | 1 | abstract only |
| 10 | technical debt principal-agent OR moral hazard OR externality economic model software | web (extended) | 9 | 0 (one Critical AI essay noted) | no formal model found |
| 11 | Baldwin Clark architecture of participation free riding | web | 10 | 1 | listing/abstract only |
| 12 | "game theory" "technical debt" developers refactoring equilibrium | web (extended) | 9 | 3 (Gavidia-Calderon JSS + thesis; Inderscience 2021) | KEY HIT |
| 13 | error budget SRE incentive formal model / internal pricing | web | 10 | 2 (Google SRE pages, practitioner only) | no formal model found |
| 14 | Goodhart's law code quality metrics gaming developers study | web | 10 | 0 peer-reviewed | blogs only |
| 15 | fetch JSS19egt.pdf (UCL staff page) | ucl.ac.uk | 0 | 0 | FAILED: connection refused |
| 16 | fetch UCL thesis PDF 10106595 | discovery.ucl.ac.uk | 1 | 1 | the fetcher returned binary data. Text was extracted locally with pdftotext and chapter 4 was **read in full** |
| 17 | Gavidia-Calderon JSS bibliographic search | web | 10 | 1 | confirmed venue and DOI |
| 18 | LLM agents shared codebase incentive mechanism design externality technical debt | web (extended) | 10 | 0 directly relevant | |
| 19 | fetch arXiv 2607.04697 | arxiv abstract | 1 | 1 | abstract only |
| 20 | MacCormack Sturtevant technical debt coupling / real options | web | 10 | 1 (JSS 2016) | real-options TD papers not surfaced |
| 21 | AI coding agent adoption technical debt empirical (Cursor) | web | 10 | 3 (2511.04427, 2603.28592, 2601.13597) | search summary only |

The tool-call budget left no time for dedicated searches on real-options TD models (Kruchten/Nord/Ozkaya; Sullivan et al.), open-source public-goods economics (e.g., Johnson 2002), DORA/"you build it you run it" formal analyses, or concealment and hidden-coupling Goodhart simulations. These are listed as gaps.

---

## Q1. Game-theoretic, economic or agent-based models of technical debt or shared-code quality as a commons

### Takeaway
The claim that "no agent-based or game-theoretic simulation of technical debt as a commons was found" is **not safe as written**. Gavidia-Calderon, Sarro, Harman and Barr (JSS 2020, and the 2020 UCL thesis) state explicitly that "Technical debt is a tragedy of the commons." They build a discrete-event simulation in which developers choose kludge or fix, kludges degrade shared codebase quality, and they derive an empirical game, solve for Nash equilibrium (kludging dominates), and use mechanism design to pick a code-review intervention. The project's model still differs from that prior work in substantive ways (see Inferences), so novelty should be re-scoped rather than claimed absolutely.

### Cited findings
- **Gavidia-Calderon, Sarro, Harman, Barr, "Game-theoretic analysis of development practices: Challenges and opportunities", Journal of Systems and Software 159:110424 (2020), DOI 10.1016/j.jss.2019.110424, presented as a journal-first paper at ASE 2020.** — [ORO record](https://oro.open.ac.uk/79717); [ASE 2020 listing](https://conf.researchr.org/details/ase-2020/ase-2020-journal-first-papers/3/Game-theoretic-Analysis-of-Development-Practices-Challenges-and-Opportunities); [preprint](https://discovery-pp.ucl.ac.uk/10084762/1/gt-process-improvement.pdf). The JSS paper is abstract/listing only. Its content was read in full through thesis chapter 4, which the thesis says is based on that paper.
- In the thesis (C. Gavidia-Calderon, "A Game-Theoretic Approach to Software Process Improvement", UCL PhD, 2020; **chapter 4 read in full**):
  - It states verbatim that "Technical debt is a tragedy of the commons: the codebase quality, the shared resource or common, progressively degrades as the team pushes kludges." — [UCL Discovery](https://discovery.ucl.ac.uk/id/eprint/10106595/)
  - **Model:** a discrete-event Kanban simulation. Each developer chooses fix or kludge. Kludges are faster (Tk = 0.75T against Tf = 1.1T) and have a higher rework probability. Each kludge raises the average resolution time by Qk = 0.05T, a shared quality degradation. The payoff is features per release. Parameters are calibrated to the Eclipse Platform bug repository. — [thesis](https://discovery.ucl.ac.uk/id/eprint/10106595/)
  - **Players and strategies:** two developers with two heuristic strategies, "fix until a week before release" and "kludge when the backlog exceeds 2". The empirical game has a single Nash equilibrium, kludge-intensive (payoffs 9.06 each, against 9.80 each under mutual fix), which makes it a prisoner's-dilemma structure. — [thesis](https://discovery.ucl.ac.uk/id/eprint/10106595/)
  - **Mechanism design:** adding a part-time code reviewer who detects kludges flips the game. At 10% detection there are three equilibria, one of them still kludge. At 25% detection there is a unique fix-intensive equilibrium. — [thesis](https://discovery.ucl.ac.uk/id/eprint/10106595/)
  - The thesis also sketches a "tragedy of the test suite", in which the test infrastructure is treated as a commons spoiled by unremoved tests, and frames QA engineers competing for developer time as a commons in a bug-prioritisation game. That game led to "assessor-throttling" (TSE 2019, "The Assessor's Dilemma"), a reputation-based mechanism that penalises inflated priorities. — [thesis](https://discovery.ucl.ac.uk/id/eprint/10106595/)
  - The thesis cites Lavallée and Robillard as the empirical origin of "budget-driven technical debt", and it surveys prior game theory in SE, including Stackelberg models of open-source contribution (Hata et al.) and evolutionary games (Wang and Redmiles). — [thesis](https://discovery.ucl.ac.uk/id/eprint/10106595/)
- **Sundelin, Gonzalez-Huerta, Torkar, Wnuk, "Governing the Commons: Code Ownership and Code-Clones in Large-Scale Software Development", arXiv 2405.15866 (v1 May 2024, v3 Nov 2024).** It uses data from 10 teams across 8 components of one large industrial system and fits a multi-level generalized linear (Bayesian) model of clone introduction relative to change size. It finds that team behaviour varies by component, and practitioner interviews found the model visualisations useful as a feedback tool under weak or collective ownership. The commons framing is in the title. This is an empirical statistical study, not a game or simulation. — [arXiv](https://arxiv.org/abs/2405.15866) (abstract only. The abstract does not itself state the "non-owner changes create more clones" result, so the project's paraphrase should be checked against the full text before it is cited.)
- **Baldwin and Clark (2006), "The Architecture of Participation: Does Code Architecture Mitigate Free Riding in the Open Source Development Model?", Management Science 52(7):1116–1127.** This is a game-theoretic model (prisoners' dilemma, public goods) showing that modularity and option value in a codebase raise participation and reduce free riding at equilibrium. It concerns contribution to a public good, not degradation of a shared stock. — [RePEc/IDEAS](https://ideas.repec.org/a/inm/ormnsc/v52y2006i7p1116-1127.html) (abstract only)
- **MacCormack and Sturtevant (2016), "Technical debt and system architecture: The impact of coupling on defect-related activity", JSS 120.** They measure coupling for more than 20,000 components and use it to predict defect-related maintenance effort. This is empirical support for "coupling acts as a debt stock that drives incidents", but it is not a strategic model. — [search listing](https://core.ac.uk/download/154881372.pdf) (listing only, not opened). See also Sturtevant's 2013 MIT dissertation on the cost of architectural complexity ([INCOSE slides](https://incose.org/docs/default-source/enchantment/130612_dansturtevant_techdebtlgsystems.pdf?sfvrsn=2), not opened).
- **System dynamics:** arXiv 1609.06868 builds a 4-stock system dynamics model of TD management under maintenance resource-allocation policies. It has no strategic agents. — [arXiv](https://arxiv.org/abs/1609.06868) (search summary only). The CISQ Technical Debt Simulator is a simple practitioner system dynamics tool. — [CISQ](https://www.it-cisq.org/technical-debt-simulator/)
- **Madhivanan and Godandapani (2021), IJIDS 13(3).** This is a "perturbed software refactor game" in which quality attributes such as coupling, inheritance and TD are the *players*, solved by ε-Nash. It is an optimisation heuristic, not a model of developer incentives. — [Inderscience](https://www.inderscience.com/info/inarticle.php?artid=118052) (abstract only)
- No formal principal-agent or externality model of software TD turned up. Hits were essays, for example a Critical AI piece calling the shipping of LLM TD to users a "moral hazard". — [Duke UP](https://read.dukeupress.edu/critical-ai/article/doi/10.1215/2834703X-11205182/390857/The-Moral-Hazards-of-Technical-Debt-in-Large) (abstract only)

### Inferences
- The prior work closest to the project is Gavidia-Calderon et al. It already covers several of the project's pieces: technical debt as an explicit commons, simulation of agents choosing shortcut or quality, an equilibrium at the shortcut, and an institutional intervention (review/detection) that restores cooperation. The project should cite it and position against it.
- Differences that plausibly remain novel, judged from chapter 4 only. Gavidia-Calderon et al. have 2 players, binary heuristic strategies, a linear quality penalty on resolution time, no incident process, no module ownership, and no concealment. The detection is a review probability, not an operator charge. They have no **continuous shortcut intensity**, no **concealed share of coupling invisible to the operator**, no **hardening action**, no **convex incident hazard in a debt stock**, no **incidents landing in random modules** (cross-module cost-shifting), no **charges or pricing instruments**, and no evolutionary or learning dynamics over many agents. The defensible claim is narrower, along the lines of "no simulation that combines hidden coupling (concealment), convex incident arrival, and operator charging instruments".
- Baldwin and Clark (2006) is the canonical economics reference for modularity as a public-goods mechanism in code and should be cited as framing.

### Gaps
- Real-options models of TD (e.g., Sullivan, Chalasani and Jha on design as real options; Kruchten, Nord and Ozkaya's TD theory work) were not searched within budget, so they are not verified here.
- Open-source public-goods economics (Johnson 2002; Lerner and Tirole) was not verified in this session.
- The full JSS 2020 paper was not opened (the UCL staff PDF fetch failed). The thesis chapter is stated to be based on it, but there may be minor differences.
- The TechDebt conference proceedings were not searched directly. A TechDebt paper on commons or simulation could have been missed.

---

## Q2. Multiple LLM coding agents in a shared repository (2024–2026)

### Takeaway
There is a fast-growing empirical and benchmark literature (2026) on agents interfering in shared repositories: merge conflicts, a coordination penalty, and quality degradation after agent adoption. None of the papers found model **incentives, cost-shifting externalities, or operator charges** among agents. Coordination is treated as a capability or scheduling problem, not an incentive problem.

### Cited findings
- **CooperBench (Khatua et al., arXiv 2601.13295, Jan 2026; ICLR 2026).** It has 652 tasks from 12 open-source libraries. Two agents implement separately assigned features in the same repo, and success is about 30% lower on average than when each task is done alone (the "curse of coordination"). — [arXiv](https://arxiv.org/html/2601.13295); [ICLR](https://iclr.cc/virtual/2026/10018462) (search summary/listing only)
- **Xu, Subramanian, Karthik, "AI Agent Pull Requests on GitHub: Frequency, Structure, and Merge Conflict Rates", arXiv 2607.04697 (Jul 2026).** The dataset is AIDev-pop, with 33,596 agent PRs across 2,807 repos. Exactly concurrent agent PR pairs occur in 40.2% of repos. Replayed merges conflict in 41.7% of cross-agent pairs and 19.8% of intra-agent pairs. 84.4% of conflicted files are source code. — [arXiv](https://arxiv.org/abs/2607.04697) (abstract only)
- **NP-Bench, "Verifying Coordination in Parallel Coding Agents: NP-Bench and a Scheduling Planner", arXiv 2610.07261.** It measures clean integration, conflicts, scope leakage and repeated mistakes, and proposes a scheduling planner. It does not model incentives or costs imposed between agents. — [arXiv](https://arxiv.org/abs/2610.07261) (abstract only)
- **Mohammadi et al., "The Working Set of a Coding Agent: Coherence Debt in Repository-Scale Tasks", arXiv 2608.16630 (Aug 2026).** "Coherence debt" means facts needed for an edit that neither context nor memory covers. It is single-agent and per edit, not a shared stock. — [arXiv](https://arxiv.org/abs/2608.16630) (abstract only)
- **Hydari, Iqbal, Ramasubbu, "Modeling Agentic Technical Debt and Stochastic Tax", arXiv 2605.27320 (May 2026).** It defines Agentic Technical Debt as a *stock* of design/governance liability plus a recurring "stochastic tax" flow, with a spreadsheet simulation of an accounts-payable agent. It is not multi-agent and has no game theory, commons or incentives. The name "agentic technical debt" is taken. — [arXiv](https://arxiv.org/abs/2605.27320) (abstract only)
- **arXiv 2610.20394, "What Should a Software Team Spend on Agents? Simulation-Based Cost Optimization of Mixed AI-Human Teams".** It simulates TD (feature work and bug fixing raise it, a refactoring agent lowers it) and bug injection/detection, and finds escaped bugs are the dominant cost. It covers agent price, but has no inter-agent externalities or internal charges. — [arXiv](https://arxiv.org/abs/2610.20394) (abstract only)
- **Empirical quality degradation after AI tool adoption:**
  - He et al., arXiv 2511.04427 (MSR 2026): Cursor adoption brings a transient velocity gain and a persistent increase of about 30% in static-analysis warnings and about 41% in complexity, and accumulated debt later reduces velocity. — [arXiv](https://arxiv.org/html/2511.04427v2)
  - arXiv 2601.13597: agent adoption is associated with about 18% more warnings and 39% more cognitive complexity. — [arXiv](https://arxiv.org/html/2601.13597)
  - arXiv 2603.28592: 302.6k AI-authored commits across 6,299 repos, tracking whether the debt they introduce persists. — [arXiv](https://arxiv.org/html/2603.28592)
  - (All three are search summary only.)
- Practitioner sources (Augment guides, a Microsoft Tech Community "Swarm Diaries" post, a Codex blog) describe semantic conflicts, duplicated utilities and hotspot files. They are anecdotal and were not used as evidence. — e.g. [Microsoft Tech Community](https://techcommunity.microsoft.com/blog/appsonazureblog/the-swarm-diaries-what-happens-when-you-let-ai-agents-loose-on-a-codebase/4501393)

### Inferences
- These empirical results (cross-agent conflicts roughly double, a coordination penalty of about 30%, persistent debt after adoption) give a 2026 motivation for the project's setting. None frames the harm as an externality one agent imposes on another, or tests pricing or charging instruments. That gap appears real as of this search.

### Gaps
- No search covered the ACM EC 2026 or NeurIPS 2026 workshops on LLM mechanism design, where incentive-design work on coding agents might appear.
- Full texts were not read, so a paper might discuss incentives in its body and not in its abstract.

---

## Q3. Incentive or pricing instruments for software quality inside organisations

### Takeaway
SRE error budgets and "you build it, you run it" are documented only as practitioner policy. No formal economic or game-theoretic analysis of internal incident charges or error budgets turned up. The only formal "instrument" analysis found is the code-review detection mechanism and the assessor-throttling reputation mechanism of Gavidia-Calderon et al.

### Cited findings
- Google's SRE Workbook error-budget policy presents the budget as balancing reliability and feature velocity, and states that it is not a punishment. — [sre.google](https://sre.google/workbook/error-budget-policy/)
- Treynor Sloss's "Tenets of SRE" frames the error budget as resolving the conflict between development and SRE incentives. — [O'Reilly](https://oreilly.com/ideas/tenets-of-sre)
- In GTPI, review detection of 25% of kludges is enough to make "fix" the unique equilibrium. This is a detection-probability instrument, not a price. — [thesis](https://discovery.ucl.ac.uk/id/eprint/10106595/)
- A 2026 token-economics survey frames shared-infrastructure frictions as externalities to be internalised through dynamic pricing. That is the closest pricing-externality framing for LLM agents, but it concerns compute, not code. — [arXiv 2605.09104](https://arxiv.org/html/2605.09104v1) (search summary only)

### Inferences
- The project's operator charges (incident-based or metric-based Pigouvian charges inside a codebase) appear not to have been analysed formally in SE. The closest analogues are general environmental economics (Pigouvian taxes under unobservable emissions) and the review mechanism above.

### Gaps
- Internal transfer pricing and chargeback literature in IS/management (e.g., IT chargeback studies) was not searched.
- DORA or "you build it, you run it" formal analyses were not searched.

---

## Q4. Prior simulation in which hidden coupling or concealment makes a proxy metric gameable (Goodhart in code metrics)

### Takeaway
I found no simulation or formal model of developers or agents concealing coupling or debt from a metric-based operator. Evidence on Goodhart effects in code metrics is anecdotal: coverage gaming and gaming of activity metrics in practitioner writing.

### Cited findings
- Practitioner pieces describe tests that raise coverage without asserting behaviour, and argue AI tools make metric gaming a side effect of normal use. — [dougseven.com](https://dougseven.com/2026/06/05/when-the-agent-games-your-metric/); [roy60e substack](https://roy60e.substack.com/p/ep6-when-metrics-backfire-exploring) (both non-peer-reviewed)
- GTPI's assessor-throttling treats dishonest and incompetent priority assessment as indistinguishable and penalises both through reputation. This is the nearest formal treatment of strategic misreporting to an operator in SE, but it concerns bug priority, not hidden coupling. — [thesis](https://discovery.ucl.ac.uk/id/eprint/10106595/)
- MacCormack's Propagation Cost coupling metric is reported to be sensitive to file count and does not always capture architecture-level variation, so the measurement gaps are documented. — [Drexel ICSE 2016 paper](https://www.cs.drexel.edu/~yc349/papers/2016/icse2016-DL.pdf) (search summary only)

### Inferences
- The "concealed share of coupling invisible to the operator" mechanic looks like the most distinctive part of the project relative to the SE literature. Its natural theory anchors are outside SE: Pigouvian taxation with unobservable emissions, and multitask principal-agent theory (Holmström and Milgrom). Those anchors were not searched here.

### Gaps
- No search covered ML "specification gaming" or "reward hacking" by coding agents on tests (e.g., agents modifying tests to pass), which is the closest LLM analogue of concealment.
- Empirical SE studies of "metric gaming" in MSR/ICSE were not searched directly.
