# Prior work on learning, evolving and AI agents in payment systems (RTGS liquidity / payment-timing games)

Scope: novelty check for a stylized six-bank RTGS simulation in which banks evolve liquidity policies and acceptance rules (private, Kantian/universalization, welfare) are compared against a delay surcharge. Research date: 18 Nov 2026.

## Key work on the intraday liquidity / payment-timing game and learning agents

### Takeaway
The liquidity-delay dilemma (Bech & Garratt 2003), learning agents in RTGS (Galbiati & Soramäki fictitious play; Castro et al. reinforcement learning) and policy levers (throughput guidelines, LSMs, time-varying tariffs) are all established. Two citation corrections matter. Bank of Canada SWP 2025-35 is the same paper as BIS WP 1310 (Aldasoro & Desai), not a Castro et al. follow-up. The "Castro et al. 2025" cited in that paper is the journal version of the 2021 SWP in ACM Transactions on Economics and Computation 13(1).

### Cited Findings
**Game theory foundations**
- Bech & Garratt (2003), "The intraday liquidity management game", *Journal of Economic Theory* 109(2):198–219. It models the liquidity-delay trade-off as a two-player game in which multiple equilibria arise depending on liquidity versus delay costs. Verified via the reference list and footnote 3 of Aldasoro & Desai. — [BoC SWP 2025-35 PDF](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf) (read in full)
- Bech & Garratt, "Illiquidity in the Interbank Payment System following Wide-Scale Disruptions", FRBNY Staff Report 239 (March 2006), published in *JMCB* 44(5):903–929 (2012). It is an n-player game that uses a potential function for equilibrium selection after disruptions. Coordination can break down after large or key-participant disruptions, the paper studies network topology, and the 2012 version adds Lehman-era behaviour. — [FRBNY SR239](https://www.newyorkfed.org/research/staff_reports/sr239.html); [EconPapers](https://econpapers.repec.org/RePEc:wly:jmoncb:v:44:y:2012:i:5:p:903-929) (abstract only)
- Buckle & Campbell (2003), BoE Working Paper 209, "Settlement bank behaviour and throughput rules in an RTGS payment system". In a two-bank RTGS model, banks delay payments to each other, and aggregate throughput rules may be inadequate with more than two settlement banks. — [BoE WP 209](https://www.bankofengland.co.uk/working-paper/2003/settlement-bank-behaviour-and-throughput-rules) (abstract only, via search summary)

**Agent-based models and learning**
- Galbiati & Soramäki, "An agent-based model of payment systems", BoE WP 352 (2008); *JEDC* 35(6):859–875 (2011).
  - Multi-agent, multi-period RTGS. Banks choose costly opening liquidity and then process random payment orders, and delayed payments carry a cost.
  - Agents learn by fictitious play. The resulting liquidity demand function rises with the delay/liquidity cost ratio and is S-shaped.
  - Policy experiments include an operational incident and a throughput guideline. With a guideline at low delay costs, banks increase their liquidity.
  - Sources: [BoE WP](https://www.bankofengland.co.uk/working-paper/2008/an-agent-based-model-of-payment-systems); [EconPapers JEDC](https://econpapers.repec.org/RePEc:eee:dyncon:v:35:y:2011:i:6:p:859-875) (abstract and summary only)
- Arciero et al. (2009), "Exploring Agent-Based Methods for the Analysis of Payment Systems", *JASSS* 12(1):2 (authorship not checked on page). — [JASSS](https://jasss.soc.surrey.ac.uk/12/1/2.html) (search hit only, not read)
- Essex Discussion Paper 700, "Designing large value payment systems: ...". It applies Erev-Roth reinforcement learning to banks' liquidity posting in a payment game. — [Essex DP700](https://repository.essex.ac.uk/3714/1/dp700.pdf) (search snippet only; authors and full title not verified)
- Castro, Desai, Du, Garratt & Rivadeneyra, "Estimating Policy Functions in Payment Systems Using Reinforcement Learning", BoC SWP 2021-7 (Feb 2021).
  - Reinforcement learning approximates banks' policy rules for start-of-day liquidity.
  - In a simplified two-agent setting, agents converge to the cost-minimizing optimal policy. In more complex settings, agents still learn to cut liquidity costs.
  - The authors frame reinforcement learning as a way to estimate best responses in strategic games.
  - Sources: [EconPapers 21-7](https://econpapers.repec.org/paper/bcabocawp/21-7.htm) (abstract); [BoC PDF](https://www.bankofcanada.ca/wp-content/uploads/2021/02/swp2021-7.pdf)
- Published version: Castro et al. (2025), *ACM Transactions on Economics and Computation* 13(1):1–31. Verified only via Aldasoro & Desai's reference list; a direct search did not surface the ACM page. — [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)
- Related: "Discrete Payments Optimization Using Reinforcement Learning" (same five authors). It treats indivisible payments, which turn the problem into integer optimization. — [AEA 2022 preliminary programme](https://aeaweb.org/conference/2022/preliminary/paper/TD7eH7By) (listing only)
- Also cited by Aldasoro & Desai on liquidity coordination:
  - Rivadeneyra & Zhang (2022), "Payment coordination and liquidity efficiency in the new Canadian wholesale payments system", BoC Staff Discussion Paper 2022-3.
  - Craig, Salakhova & Saldias (2018), "Payments delay: propagation and punishment", Banque de France WP 671.
  - Alexandrova-Kabadjova et al. (2023), "Intraday liquidity around the world", BIS WP 1089.
  - Source: [BoC SWP 2025-35 references](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf) (verified from the reference list, not read)

**Liquidity-saving mechanisms**
- Martin & McAndrews (2008), "Liquidity-saving mechanisms", *Journal of Monetary Economics* 55(3):554–567, doi:10.1016/j.jmoneco.2007.12.011. LSM design affects welfare, and whether an LSM helps depends on parameters. A companion FRBNY *Economic Policy Review* piece (2008) also covers LSMs. — [EconPapers](https://econpapers.repec.org/RePEc:eee:moneco:v:55:y:2008:i:3:p:554-567); [FRBNY EPR summary](https://www.newyorkfed.org/research/epr/08v14n2/exesummary/exesum_mcan.html) (abstract only)
- BIS Project Titus with BIS WP 1318, "Auction-based liquidity saving mechanisms" (16 Dec 2025, revised Jan 2026).
  - It runs an auction-based LSM with side-payments, and partners include the SNB, SARB and BCRP.
  - On RTGS data it reports 2.6–12.2% liquidity savings, with side-payments coordinating incentives and a trade-off between liquidity efficiency and delay.
  - Sources: [BIS Titus](https://www.bis.org/about/bisih/topics/fmis/titus.htm); [BIS WP 1318](https://www.bis.org/publ/work1318.htm) (summary via search; not read in full)

**Simulators**
- Bank of Finland BoF-PSS2 is built for liquidity and risk analysis and supports agent-based modelling and gridlock-resolution/LSM analysis.
  - A TARGET2 variant was delivered with the 3CB (Banca d'Italia, Bundesbank, Banque de France) by ECB Governing Council decision and was used until T2 replaced TARGET2 in March 2023.
  - A successor, BoF-PSS3, is referenced in 2021.
  - Sources: [BoF-PSS2 product page](https://suomenpankki.fi/en/financial-stability/bof-pss-simulator/product); [RePEc BoF DP 23/2003](https://ideas.repec.org/p/zbw/bofrdp/rdp2003_023.html) (search summary only)
- No De Nederlandsche Bank agent-based RTGS paper surfaced in my searches. This is a gap, not a finding of absence.

### Inferences
- The project's claim that "the payment-timing dilemma and learning in payment games are established" is well supported, with a lineage from Bech-Garratt 2003 through Galbiati-Soramäki to Castro et al. 2021/2025.
- Existing learning work uses fictitious play, Erev-Roth or deep reinforcement learning, usually with 2 to n banks optimizing private cost. None found uses evolutionary search over multi-parameter rule-level policies with alternative acceptance criteria.

### Gaps
- I did not read the full texts of Galbiati-Soramäki, Castro et al., Martin-McAndrews, Bech-Garratt 2006 or BIS WP 1318.
- I did not confirm the ACM TEAC page directly.
- I found no specific DNB or ECB working paper on learning agents in RTGS, and did not search Bundesbank discussion papers or the ECB WP series directly.

## BIS WP 1310 (read in full) and BIS Project Agenti

### Takeaway
BIS WP 1310 tests a single commercial LLM agent on three hand-written prompt scenarios. It has no multi-agent interaction, no learning, and no comparison of incentive designs, and it explicitly names multi-agent simulation as future work. Project Agenti is building that multi-agent "Agentic AI Payment Simulator". As of 14 Oct 2026 its BIS page lists no published results or code.

### Cited Findings
**BIS WP 1310 / BoC SWP 2025-35 (read in full via the BoC PDF)**
- Identity: "AI agents for cash management in payment systems", Iñaki Aldasoro (BIS) and Ajit Desai (Bank of Canada), 26 Nov 2025. It is the same paper as BoC SWP 2025-35 (DOI 10.34989/swp-2025-35). — [BIS WP 1310](https://www.bis.org/publ/work1310.htm); [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)
- Method: prompt-based experiments with one commercial reasoning model in its web interface at default settings; key scenarios re-checked with a newer model, plus an interactive form test in an agent mode. — [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)
- Three scenarios:
  1. Precautionary decision: $10 limit, two $1 payments, a possible urgent $10 payment. The agent delays both small payments.
  2. Navigating priorities: $1 and $2 queued, 90% chance of a $2 inflow, 50% chance of an urgent $10. The agent sends only the $1, which the authors call "not fully optimal".
  3. Liquidity-delay trade-off: 1.5% liquidity cost, 1% and 1.5% delay costs, a 99% inflow probability and a penalty borrowing rate. The agent allocates $5.
  - Consistency over 10 repeat runs was 10/10, 9/10 and 8/10. Results held up when probability, wording and scale were varied.
  - Source: [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)
- Scope: the paper analyses one participant only. It notes that efficiency depends on liquidity coordination across participants and calls multi-agent dynamics "further work". The conclusion proposes embedding agents in "a full-fledged multi-agent payment-system simulator" to study gridlock, network effects and stress resilience. — [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)
- Comparison with Castro et al.: the paper contrasts its approach with Castro et al.'s reinforcement learning, where costs are encoded in the reward and extensive training is needed. — [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)
- Risks listed: synchronized behaviour from reliance on similar automated systems, opacity, skills atrophy, and third-party concentration. — [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)
- Absent from the paper: fees, delay surcharges, throughput rules, and any collective, Kantian or welfare decision rule. — [BoC SWP 2025-35](https://www.bankofcanada.ca/wp-content/uploads/2025/11/swp2025-35.pdf)

**Project Agenti (BIS page only, last updated 14 Oct 2026)**
- Partners: BIS Innovation Hub Swiss and Toronto Centres, Bank of Canada, Swiss National Bank. — [BIS Project Agenti](https://www.bis.org/node/87745)
- Design: an "Agentic AI Payment Simulator" models an RTGS-like environment, with AI agents representing banks that each have their own objectives, constraints and strategies. — [BIS Project Agenti](https://www.bis.org/node/87745)
- Planned tests: whether agents reproduce real participant behaviour, and how behaviours and degrees of autonomy affect liquidity demand, delays, gridlock and resilience. — [BIS Project Agenti](https://www.bis.org/node/87745)
- Status: ongoing. No start date, phases, results, report or code are listed. — [BIS Project Agenti](https://www.bis.org/node/87745)
- Context: an IMF note (Apr 2026), "How agentic AI will reshape payments", flags correlated agent behaviour as a risk. — [IMF note](https://www.imf.org/en/Publications/imf-notes/Issues/2026/04/22/how-agentic-ai-will-reshape-payments-575560) (search summary only)

### Inferences
- Project Agenti is the closest active competitor. It is a multi-agent RTGS simulator with heterogeneous AI bank agents and policy evaluation in scope, but nothing published so far shows it comparing acceptance rules or norm-based agents against pricing.
- The project should cite WP 1310 as single-agent evidence and Agenti as ongoing multi-agent work. It should also re-check Agenti before any publication.

### Gaps
- No Agenti publications or code were found. I did not search BIS speeches or the BISIH annual report for Agenti results, and the IFC Bulletin 67 hit ([ifcb67_30.pdf](https://www.bis.org/2026-07/ifcb67_30.pdf)) was not opened. It may be a 2026 conference version of WP 1310 or an Agenti update.

## FRAIL — "Financial Fragility in Societies of LLM Agents" (arXiv:2609.30940, read in full)

### Takeaway
FRAIL is a multi-LLM-agent study of coordination failure in bank runs, debt rollover and crowdfunding. It compares three commitment/communication mechanisms and contains no payment network or RTGS, no fees or delay pricing, and no Kantian or welfare agent rules. It is relevant as a precedent for "individually protective decisions produce collective failure" among AI agents, and it compares mechanisms, not acceptance rules.

### Cited Findings
- Paper details: Zhenhao Fu, Ruipeng Xu (SAIF, Shanghai Jiao Tong) and Qibing Ren (SJTU), arXiv v1 [cs.AI], 25 Sep 2026. — [arXiv PDF](https://arxiv.org/pdf/2609.30940)
- Environments: bank run (15 depositors, 12 rounds), debt rollover (1 borrower, 8 creditors, 7 rounds, four maturity waves) and reward crowdfunding (threshold financing). Agents' choices reshape the state others face. — [arXiv PDF](https://arxiv.org/pdf/2609.30940)
- Models and baseline: seven models from six commercial and open-weight families were tested, five episodes per cell. Under the M0 baseline, 77% of bank-run and 83% of debt-rollover episodes fail. — [arXiv PDF](https://arxiv.org/pdf/2609.30940)
- Mechanisms (implemented as environment-side state machines, not prompt-level instructions):
  - M1, compensated commitments: the central player pays for binding no-exit promises.
  - M2, centralized commitment agreements.
  - M3, participant-led coalitions with voted disclosure.
  - Source: [arXiv PDF](https://arxiv.org/pdf/2609.30940)
- Results:
  - All three mechanisms improve welfare and success. In bank runs, M3 raises welfare realization from 0.215 to 0.737 and success from 23% to 74%.
  - Rankings flip by environment: M3 is best in bank runs and crowdfunding, M2 in debt rollover. Paid commitments (M1) are never best ("communication trumps compensation").
  - Successful stabilization requires broad commitment forming early.
  - Source: [arXiv PDF](https://arxiv.org/pdf/2609.30940)
- Code: an anonymized repo is listed. — [arXiv PDF](https://arxiv.org/pdf/2609.30940)
- Related work cited: LLM cooperation in games, including Welfare Diplomacy (Mukobi et al. 2023) and Phelps & Russell (2025); Diamond-Dybvig (1983). — [arXiv PDF](https://arxiv.org/pdf/2609.30940)

### Inferences
- FRAIL is the nearest analogue to the project's "rules versus incentives" framing among LLM-agent societies. Its result that the transfer-based mechanism (M1) loses to communication/commitment designs contrasts with a "surcharge beats coordination" claim, but in different games. Treat it as a contrasting data point, not a contradiction.
- FRAIL agents are not evolved or learned. They are prompted LLMs with five episodes per cell.

### Gaps
- The appendix with mechanism formalization was skimmed, not studied line by line.

## PSSimPy simulator

### Takeaway
PSSimPy is an MIT-licensed Python LVPS simulator (ICIS 2024) with queues, pluggable bank strategies, credit facilities and time-varying fees. No built-in delay cost or learning agents are documented.

### Cited Findings
- Paper and repository: Kenneth See, Hanzholah Shobri and Nicholas Garcia, ICIS 2024. The paper takes a design-science approach emphasizing modularity, accessibility and data privacy. — [AIS eLibrary](https://aisel.aisnet.org/icis2024/blockchain/blockchain/10); [GitHub](https://github.com/kennethsee/pssimpy)
- Features: `pip install PSSimPy`; `BasicSim` and `ABMSim`; `DirectQueue`, `FIFOQueue` and `PriorityQueue`; operating hours and processing windows; end-of-day clear or force settlement. — [GitHub README](https://github.com/kennethsee/pssimpy)
- Extensibility: `Bank.strategy()` can be overridden, `AbstractCreditFacility` takes a `SimplePriced` default, and `FixedTransactionFee` can vary rates by time of day. — [GitHub README](https://github.com/kennethsee/pssimpy)
- Transaction generation: arrival probability, amount range and priority range. — [GitHub README](https://github.com/kennethsee/pssimpy)
- Not mentioned: LSM or offsetting, delay costs, and learning agents. — [GitHub README](https://github.com/kennethsee/pssimpy)
- Activity: about 185 commits, 5 stars, no tagged releases. — [GitHub README](https://github.com/kennethsee/pssimpy)

### Inferences
- Time-varying fees make PSSimPy a plausible platform for delay-pricing experiments. The evolutionary or learning layer and the acceptance rules would have to be added.

### Gaps
- I did not inspect the source code or PyPI version history.

## LLM or self-improving agents managing bank liquidity (2024–2026), and incentive designs versus agent-level rules

### Takeaway
The only payment-specific LLM work found is BIS WP 1310 (single agent) and Project Agenti (ongoing, unpublished). I found no paper, in payments or elsewhere in banking, that compares Kantian, universalization or welfare acceptance rules with fee or surcharge designs. Kantian optimization (Roemer) has no payment-system application in my searches.

### Cited Findings
- No arXiv or central-bank paper combining multi-agent LLM agents with RTGS timing surfaced. The closest hits are consumer-payment agent systems (HMASP, arXiv 2602.24068; AgenticPay, arXiv 2602.06008), not interbank settlement. — [HMASP](https://www.alphaxiv.org/abs/2602.24068); [AgenticPay](https://arxiv.org/abs/2602.06008) (titles and abstracts only)
- A SUERF brief on WP 1310 urges multi-agent simulations to capture recycling, queuing externalities and gridlock before deployment. — [SUERF brief](https://www.suerf.org/publications/suerf-policy-notes-and-briefs/from-prompts-to-payments-ai-agents-for-cash-management-in-wholesale-payment/) (search snippet only)
- Roemer's Kantian optimization (evaluate a common deviation by all players) gives Pareto-efficient equilibria in strictly monotone games. A search combining it with payment systems, banks or liquidity returned no payment application. — [Roemer, J. Pub. Econ. 2015](https://cpb-us-w2.wpmucdn.com/campuspress.yale.edu/dist/6/414/files/2017/04/Kant.JPubEc.2015-10z624x.pdf)
- FRAIL compares institutional mechanisms (paid commitment, agreement, coalition) among LLM agents. It does not compare pricing versus agent-level moral rules and has no payment network. — [arXiv 2609.30940](https://arxiv.org/pdf/2609.30940)

### Inferences
- The project's specific contribution appears novel within everything searched: evolved bank policies in an RTGS game, with private, Kantian and welfare acceptance rules compared against a delay surcharge. Search coverage was limited (SSRN not queried directly, Google Scholar not used), so state this as "not found in a targeted search", not "does not exist".

### Gaps
- SSRN and Google Scholar were not searched directly. Results came from a general web search engine.
- Bundesbank, DNB and ECB WP series were not browsed.
- Arxiv q-fin was not browsed by listing.

## Do papers on delay fees / intraday credit pricing already establish "delay surcharge beats coordination"?

### Takeaway
Partly. A strand of the literature compares pricing with quantity or coordination rules. Ota (BoE WP 428, 2011) finds a linear time-rising tariff beats CHAPS-style throughput guidelines in most cases. Jurgilas & Martin show fee- versus collateral-based regimes change LSM welfare, and Becher, Galbiati & Tudela find throughput guidelines act as a centralized coordination device. None compares a delay surcharge with agent-level ethical or universalization acceptance rules. The "surcharge beats central rule" direction has precedent; "surcharge beats agents' own cooperative norms" does not.

### Cited Findings
- Ota (May 2011), "Intraday two-part tariff in payment systems", BoE WP 428. Throughput guidelines do not penalize delay before the deadline. A linear time-varying tariff outperforms them in most cases, removing inefficient delay while keeping socially efficient delay, and some delay can be socially efficient. — [BoE WP 428](https://www.bankofengland.co.uk/working-paper/2011/intraday-two-part-tariff-in-payment-systems) (abstract and summary only)
- Jurgilas & Martin, FRBNY Staff Report 438.
  - In fee-based systems, banks weigh central-bank borrowing cost against delay cost.
  - An LSM can lower welfare under fees but always raises it under collateral.
  - Source: [FRBNY SR438](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr438.html) (search summary only)
- Becher, Galbiati & Tudela (FRBNY EPR 14(2), 2008). They find CHAPS throughput guidelines act as a centralized coordination mechanism that limits delay tendencies. — [FRBNY EPR](https://www.newyorkfed.org/medialibrary/media/research/epr/08v14n2/0809becher.html) (search summary only)
- Bech (FRBNY EPR 2008) explains that intraday credit costs (explicit fee or collateral opportunity cost) drive payment timing. — [FRBNY EPR Bech](https://www.newyorkfed.org/medialibrary/media/research/epr/08v14n2/0809bech.html) (search summary only)
- Galbiati & Soramäki test a throughput guideline in their learning ABM. — [BoE WP 352](https://www.bankofengland.co.uk/working-paper/2008/an-agent-based-model-of-payment-systems) (abstract only)
- Buckle & Campbell (2003) question the adequacy of throughput rules with more than two banks. — [BoE WP 209](https://www.bankofengland.co.uk/working-paper/2003/settlement-bank-behaviour-and-throughput-rules) (abstract only)
- Titus/WP 1318: market-based side-payments coordinate incentives in an auction LSM. — [BIS WP 1318](https://www.bis.org/publ/work1318.htm) (summary only)

### Inferences
- The project should cite Ota (2011) as the closest precedent for pricing versus rule results, and Galbiati-Soramäki for policy experiments with learning agents. Its novelty claim should be scoped to comparing a surcharge with agent-level acceptance rules (Kantian, welfare) under evolved policies.

### Gaps
- Full texts of Ota, Jurgilas-Martin and Becher et al. were not read.
- The Fed daylight-overdraft fee literature (for example any Martin paper on optimal intraday credit pricing) was not specifically verified.

---

## Search log

| # | Query | Source/tool | Hits screened | Included |
|---|---|---|---|---|
| 1 | BIS working paper 1310 LLM agents payments liquidity | WebSearch | 10 | BIS WP 1310 page, SUERF, IFC Bull. hit (not opened) |
| 2 | Castro Desai Du Garratt Rivadeneyra reinforcement learning payment system liquidity | WebSearch | 10 | BoC SWP 2021-7, AEA 2022, SWP 2025-35 |
| 3 | arXiv 2609.30940 financial fragility societies of LLM agents FRAIL | WebSearch | 10 | arXiv PDF, EconPapers listing |
| 4 | BIS Project Agenti agentic AI payments | WebSearch | 10 | BIS node 87745, IMF note |
| 5 | Fetch bis.org/publ/work1310.pdf | WebFetch | 1 | Landing summary only (fetch tool lacked detail) |
| 6 | Fetch BoC swp2025-35.pdf | WebFetch, then local pdftotext | 1 | **Read in full** (identical paper to BIS WP 1310) |
| 7 | Fetch arxiv.org/pdf/2609.30940 | WebFetch, then local pdftotext | 1 | **Read in full** (body and key appendix) |
| 8 | Fetch BIS Project Agenti page | WebFetch | 1 | Read in full (short page) |
| 9 | PSSimPy payment system simulator Python | WebSearch | 10 | ICIS 2024, GitHub |
| 10 | Galbiati Soramäki agent-based model fictitious play | WebSearch | 10 | BoE WP 352, JEDC 2011 |
| 11 | delay pricing intraday liquidity throughput guidelines | WebSearch | 10 | Ota WP 428, Buckle-Campbell WP 209, Becher et al. EPR |
| 12 | multi-agent LLM agents RTGS payment timing simulation 2026 | WebSearch (extended) | 10 | None relevant (HMASP and AgenticPay noted as non-RTGS) |
| 13 | multi-agent reinforcement learning interbank payment system | WebSearch (extended) | 10 | Essex DP700, Castro et al. |
| 14 | Martin McAndrews liquidity-saving mechanisms JME 2008 | WebSearch | 10 | JME 55(3) |
| 15 | Bech Garratt 2006 illiquidity wide-scale disruptions | WebSearch | 10 | FRBNY SR239 / JMCB 2012 |
| 16 | BIS Project Titus RTGS liquidity efficiency | WebSearch | 17 | Titus page, WP 1318 |
| 17 | Kantian optimization / universalization payment system liquidity banks | WebSearch (extended) | 9 | Roemer only; no payment application |
| 18 | optimal pricing intraday liquidity delay fee daylight overdraft | WebSearch | 10 | Jurgilas-Martin SR438, Ota, Bech EPR |
| 19 | BoF-PSS2 agent-based TARGET2 ECB Bundesbank DNB | WebSearch | 10 | BoF-PSS2 page, TARGET2 simulator |
| 20 | Castro et al. ACM TEAC 2025 | WebSearch | 10 | None (venue confirmed only via WP 1310 reference list) |
| 21 | Fetch github.com/kennethsee/pssimpy | WebFetch | 1 | README read in full |
| 22 | Fetch EconPapers BoC 21-7 | WebFetch | 1 | Abstract |
| 23 | LLM agents intraday liquidity bank treasury arXiv 2025 2026 gridlock | WebSearch (extended) | 10 | Confirms no multi-agent LLM RTGS paper found |

**Failures and limitations**
- The WebFetch summarizer could not read the raw PDFs for the BoC SWP 2025-35 and arXiv 2609.30940 links. Both were recovered by extracting the saved PDFs locally with pdftotext.
- The BIS WP 1310 fetch returned only landing-page content.
- SSRN, Google Scholar and the IDEAS search UI were not queried directly. All discovery went through a general web search engine, so SSRN-only preprints may be missed.
- The ACM TEAC listing for Castro et al. 2025 was not reached directly.
- No De Nederlandsche Bank source surfaced.
