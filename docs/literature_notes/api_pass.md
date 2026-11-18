# Second pass: searches through open scholarly APIs (18 November 2026)

Purpose: close the gaps of the first pass, which used one general web search
engine and did not query scholarly indexes directly. Scripts were run locally
against public APIs with a generic client name; only topical search terms were
sent. Raw outputs were kept outside the repository.

## Sources and outcome

| Source | What was done | Outcome |
|---|---|---|
| arXiv API | Looked up 40 IDs: the 26 marked unverified in the review, plus 14 cited ones | **All 40 exist** with the titles and authors cited |
| Crossref | 15 bibliographic lookups for venues, DOIs and pages | 13 resolved. Economy of Minds: no venue found. Castro et al.: journal DOI found later through OpenAlex (10.1145/3691326) |
| OpenAlex, keyword search | 32 query strings (18 in the first run; 13 failed with HTTP 429 and were re-run slowly with one added; 14 in the second run) | All 32 completed; top 12–15 results by relevance screened by title for each |
| OpenAlex, citation tracing | Works citing 11 seed papers: Roemer 2015, Gavidia-Calderon 2020, Kordonis 2020, Alger and Weibull 2013, Segerson 1988, Galbiati and Soramäki 2011, Spraggon 2002, Suter et al. 2008, LOPT 2025, GovSim 2024, Bech and Garratt 2003 | 9 traced; 3 of those partially (second results page refused with HTTP 401: Alger and Weibull 200 of 458 citers, GovSim 200 of 244, LOPT 2 of 4). Segerson 1988 not found by DOI in OpenAlex. Citers screened by title, 2015 onward |
| Semantic Scholar API | 9 keyword searches | **All failed** (shared rate limit without an API key) |
| Google Scholar | Not accessible to automated clients | Left to the owner; see the query list in LITERATURE_REVIEW.md |

Screening: one reviewer, by title, then by abstract (arXiv API and OpenAlex
abstracts) for about 20 candidates. No full texts were read in this pass.

## Corrections found

* Millock and Salanié (2005): the title is "Nonpoint source pollution when
  polluters might cooperate", *Topics in Economic Analysis & Policy* 5(1),
  DOI 10.2202/1538-0653.1233.
* Castro et al.: journal version confirmed, *ACM Trans. Econ. Comput.*,
  DOI 10.1145/3691326.
* GovSim: NeurIPS 2024 confirmed (DOI 10.52202/079017-3548). LOPT: NeurIPS 2025
  confirmed (DOI 10.52202/085713-1229); an earlier extended abstract appeared
  at AAMAS 2023.
* Suter et al. (2008): *Am. J. Agric. Econ.* 90(1):86–102 confirmed.
  Agogino and Tumer: GECCO 2005, 591–598 confirmed. Holmström and Milgrom
  (1991): *J. Law Econ. Organ.* 7 (special issue):24–52 confirmed.
* Economy of Minds: no venue found in Crossref or OpenAlex; keep "venue not
  confirmed".

## New relevant work (abstract level unless stated)

Gate studies, single agent:

* **Masked Erosion** (arXiv:2610.38392, 2026): ten gate rules across 411
  improvement loops; a paired significance test blocks chance deletions of
  safeguards but not ones that raise task success. Single agent; safety
  redundancy, not externalities. Related to the project's post hoc E7.
* **SEA** (arXiv:2607.00871, 2026), anytime-valid admission gate;
  **Kinetic theory of the gated self-evolving agent** (arXiv:2610.03243,
  2026). Single agent.

Selection on learning rules:

* **McAvoy, Kates-Harbeck, Chatterjee et al. (2022)**, "Evolutionary
  instability of selfish learning in repeated games", *PNAS Nexus*
  pgac141. When learning rules evolve, selfish learning is unstable in most
  two-player repeated games and selection favours rules with other-regarding
  preferences. Theory companion to comparing gates; two players, no prices.

Kantian theory:

* **Kordonis (2020)**, "A model for partial Kantian cooperation", Annals of
  the ISDG, 319–348 (arXiv:1609.01921). Defines an r-Kant-Nash
  equilibrium in which players partly follow the categorical imperative, and
  relates it to Nash, Harsanyi, Rawls and Roemer solutions. Equilibrium
  theory for the κ-mixture.
* **Istrate (2020/2021)**, "Game-theoretic models of moral and
  other-regarding agents" (arXiv:2012.09759): problems with Kantian equilibria
  in normal-form games and a family interpolating between self-regarding and
  Kantian behaviour.
* **Laslier (2022)**, "Universalization and altruism", *Soc. Choice Welf.*
  (no abstract available).
* **Sloev and Lianos (2026)**, "The scale of universalization in
  multiplicative Kantian equilibrium" (arXiv:2610.28180), building on the
  Sher–Roemer discussion of strategic non-invariance: the Kantian
  counterfactual depends on the scale in which actions are represented. The
  same applies to the project's additive gate, whose shift is defined in its
  own policy units.

Prices among learning agents:

* **Danassis, Filos-Ratsikas, Chen et al. (2026)**, "Rectifying market
  externalities via AI policymaking", *JAAMAS*: a deep-RL policymaker sets
  market prices against common-pool externalities among learning agents.

Ambient taxes with heterogeneity and agent-based models:

* **Wu (2017)**, "Essays on experiments and agent-based modeling", PhD
  dissertation, University of Delaware. Ch. 1 (lab, n = 192): size and
  location heterogeneity reduce the effectiveness of an ambient tax/subsidy
  unless peer information is given. Ch. 2: an agent-based model calibrated
  from those experiments, scaling ambient policies to a watershed. So an
  agent-based simulation of ambient policies exists; the earlier note "no
  agent-based or RL simulation of ambient taxes" must be narrowed to learning
  agents compared with a moral rule.
* **Zia, Ding, Messer et al. (2020)**, *J. Water Resour. Plan. Manag.*:
  spatial ambient-water-quality game in the lab; incentives, sensor placement
  and location change behaviour.

Payments:

* **Nellen (2019)**, "Intraday liquidity facilities, late settlement fee and
  coordination", *J. Bank. Finance* (no abstract available). Further
  precedent for pricing delay in payment coordination.

Technical debt and software teams:

* **Stevens, Soundy, Chan (2021)**, ICSE-NIER: game theory of
  self-organising task assignment, with price of anarchy and stability.
  Adjacent; not a shared-stock model.
* No further game-theoretic or agent-based model of technical debt as a
  shared stock was found among the 25 works citing Gavidia-Calderon et al.

## Screened out (examples)

Coalition-aware skill selection (arXiv:2608.22610; skills, not agents);
"Infinite technical debt" (JSS 2022; not a game model); "Payment system
externalities" (J. Finance 2022; lending, not timing); broad LLM multi-agent
surveys among GovSim citers.
