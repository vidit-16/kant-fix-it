# Third pass: Google Scholar, run manually by the owner (20 November 2026)

Google Scholar refuses automated clients, so the owner ran 9 keyword searches
and 3 cited-by searches by hand and pasted the first results page of each
(about 110 results in total). The raw paste is kept outside the repository.

Queries:

1. "technical debt" "tragedy of the commons"
2. "technical debt" "game theory" simulation
3. "Kantian equilibrium" heterogeneous efficiency
4. Kantian "ambient tax" OR "Pigouvian tax"
5. "ambient tax" "agent-based" OR "reinforcement learning"
6. Kantian universalization "multi-agent" learning
7. "self-evolving agents" acceptance "multi-agent" externality (2024 onward)
8. "self-improving agents" "social dilemma" (2024 onward)
9. "payment system" liquidity "reinforcement learning" OR "learning agents"

Cited-by searches:

* Roemer (2015), citers filtered by "learning"
* Gavidia-Calderon et al. (2020), citers filtered by "simulation"
* Segerson (1988), citers filtered by "agent"

Screening was by title and snippet, with abstracts fetched through OpenAlex
for eight candidates.

## Result

No result compares acceptance or selection rules among several learning
agents that impose costs on each other, or Kantian rules against prices. The
central gap still holds. Searches 7 and 8 returned surveys, benchmarks and
governance papers, but nothing on multi-agent acceptance.

## New items worth citing (evidence level in brackets)

Payments:

* **Danisman, Desai, Jiang, Rivadeneyra, Azad (2026)**, "Strategic
  interaction among AI agents: evidence from payment systems", seminar paper
  (TSE, September 2026). It is also listed as "Strategic interactions of AI
  agents in payment systems" for the International Conference on Payments and
  Securities Settlement 2026. Prompted language-model agents interact in an
  RTGS intraday-liquidity game, in three treatments that vary prompt design
  and equilibrium structure. These are the closest multi-agent AI agents in
  payments, but they are prompted, not evolved, and gates and prices are not
  compared. [search snippet only; the PDF host refused the browser and the
  author page is a dead link]
* **Markose, Alentorn, Millard, Yang (2011)**, "Designing large value payment
  systems: an agent-based approach" (Essex). An earlier agent-based RTGS
  model. [title]

Kantian theory and moral agents versus taxes:

* **Nishimura (2025)**, "Kantian equilibrium, income inequality, and global
  public goods", SSRN. Heterogeneity in income, not in exposure. [title]
* **Herweg and Schmidt (2022)**, "How to regulate carbon emissions with
  climate-conscious consumers", *Economic Journal*. Also **Schmidt and Herweg
  (2021)**, prices versus quantities with morally concerned consumers;
  **Bierbrauer et al. (2026)**, morals and the political economy of corrective
  taxes; and **Chan (2024)**, Pigouvian policies under behavioral motives.
  This is the "optimal tax given moral agents" line, alongside Eichner and
  Pethig and Daube and Ulph. It asks how taxes should change when agents are
  moral. It does not compare a moral rule with a tax as substitutes. [titles
  and snippets]
* **Tennant, Hailes, Musolesi (2023)**, "Modeling moral choices in social
  dilemmas with multi-agent reinforcement learning", IJCAI. RL agents with
  intrinsic rewards based on moral theories in social dilemmas. Morality
  enters the reward, not an acceptance rule, and there is no price
  comparison. [abstract]
* **Samoylenko (2026)**, NExT-Game workshop: already cited. **Kwon et al.
  (2023)** on universalization in rule-breaking judgments: cognitive
  science. [titles]

Ambient taxes:

* **Miao (2017)**, dissertation, University of Rhode Island: information and
  ambient-based policy, with field and lab methods. [abstract]
* **Malakpour Estalaki and Hu (2022)**, AGU Fall Meeting abstract: an
  agent-based evaluation of ambient-based policies and information nudges.
  [title] Together with Wu (2017), this confirms that agent-based models of
  ambient policies exist. None of them uses learning agents compared with a
  moral rule.
* **Ambec, Garapin, Muller, Reynaud et al. (2014)**, "Comparing regulations to
  protect the commons: an experimental investigation", *ERE*. [title]
* **Fooks, Messer, Suter (2017)**: a machine-learning-based policy for
  non-point pollution (Delaware). [title]

Technical debt and shared code:

* **Sundelin et al.**: now published, *Empirical Software Engineering*
  (2025). Cite the journal version.
* **Baltes, Cheong, Treude (2026)**, "An endless stream of AI slop", *IEEE
  Software*. A qualitative study of 1,154 posts that frames AI-assisted
  development as a tragedy of the commons: individual productivity gains
  push costs onto reviewers and maintainers. This is empirical support for
  the codebase environment's premise. [abstract]
* **Yin, Zhang, Filkov (2023)**, ICSE: Apache incubator self-governance;
  keeping technical debt low resembles a tragedy of the commons. [snippet]
* **Fungprasertkul, Bahsoon, Kazman (2024)**, *ACM TOSEM*, "Technical debt
  monitoring decision making with skin in the game". Asymmetric information
  and payoffs among technical-debt decision-makers, with a monitoring method
  to align them. An incentive framing, not a simulation. [abstract]
* **Skourletopoulos et al. (2017)**: game-theoretic technical-debt management
  in cloud services. **Morrison-Smith et al. (2012)**: competitive source
  control to reduce technical debt. **Prause (2013)**: reputation-based
  gamification against free riding on internal quality. All are adjacent;
  none models a shared debt stock with operator charges. [titles and
  snippets]

## Screened out

Textbooks and general surveys, and climate and investment papers among
Roemer's citers. Also excluded: Segerson citers on fisheries and wildlife,
and the citers of Gavidia-Calderon et al. outside software engineering.
