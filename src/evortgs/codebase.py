"""Second environment: agents sharing a codebase, with hidden coupling.

Each of ``n`` agents owns a module and ships output every period (sprint). Its
policy is three numbers in [0, 1]:

``s``  shortcut intensity. Shortcuts (reaching into other modules' internals,
       copying, shared mutable state) raise the agent's own output by up to
       ``boost`` (concave in ``s``) and add coupling to the codebase.
``m``  concealed share of that coupling. Concealed coupling (implicit
       assumptions, undocumented dependencies) is invisible to static analysis,
       costs the author ``conceal_cost`` of the shortcut's gain, and adds
       ``conceal_harm`` more debt than visible coupling.
``q``  hardening (tests, defensive code in the agent's own module). Costs up to
       ``harden_cost`` of capacity and cuts the agent's own incident exposure by
       up to ``harden_effect``. Purely private: no effect on anyone else.

All coupling flows into one shared debt stock ``D`` that decays at ``decay`` per
period. Incidents arrive in *every* module at a rate that rises convexly with
``D`` (scaled by the module's own hardening), and each incident destroys
``incident_loss`` of that module's output for the period. Coupling added in a
period only raises incident rates from the next period on.

Why the harm cannot be attributed: an incident surfaces in a random module, not
in the module whose shortcut caused it, and the debt stock mixes every agent's
past coupling. An operator observes (i) each agent's *visible* coupling (static
analysis), (ii) each agent's shipped output, (iii) where incidents surface and
the total incident loss. It does not observe policies or concealed coupling.
Instruments are defined only on those observables (see ``INSTRUMENTS``).

Costs are lost value against the agent's nominal maximum output, so lower is
better and the social cost is the sum over agents. Instrument charges are
transfers: they enter the private cost a gate reads, never the social cost.

Every scenario is a pure function of (config, family, split, index), with the
split tag mixed into the seed, exactly as in ``scenarios.py``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

FAMILIES = ("base", "crunch", "fragile", "spike", "legacy")
_FAMILY_ID = {f: i for i, f in enumerate(FAMILIES)}
_SPLIT_ID = {"dev": 11, "holdout": 23, "pilot": 37}

# Observable signals on which an operator can levy a charge (all transfers).
INSTRUMENTS = ("proxy", "activity", "surface", "ambient")
# proxy    per unit of the agent's visible coupling
# activity per unit of the agent's shipped output
# surface  per unit of incident loss that surfaces in the agent's own module
# ambient  per unit of incident loss surfacing in *other* agents' modules,
#          charged to every agent in full (Holmstrom/Segerson-style ambient
#          tax; budget-breaking). At level 1 an agent's private cost differs
#          from the social cost only by terms its own policy cannot move, so
#          every social optimum is a Nash equilibrium of the charged game.

KMAX = 12  # Poisson inverse-CDF truncation; P(k > 12) is negligible at calibrated rates


@dataclass(frozen=True)
class CodebaseConfig:
    n: int = 6
    T: int = 20
    boost: float = 0.6
    conceal_cost: float = 0.25   # gamma: share of a shortcut's gain lost when concealed
    conceal_harm: float = 0.5    # eta: extra debt per unit of concealed coupling
    harden_cost: float = 0.15
    harden_effect: float = 0.7
    decay: float = 0.15
    rate: float = 0.12           # incidents per module-period per unit of debt
    convex: float = 0.3          # quadratic term of the incident rate
    incident_loss: float = 0.2
    heterogeneity: float = 0.0   # module size ~ rank ** -heterogeneity, mean 1
    # incident exposure ~ rank ** -exposure_skew, mean 1: central modules absorb
    # most incidents, peripheral ones rarely break; coupling enters the shared
    # debt by size alone, so exposure and contribution come apart
    exposure_skew: float = 0.0


def sizes(cfg: CodebaseConfig) -> np.ndarray:
    w = np.arange(1, cfg.n + 1, dtype=float) ** (-cfg.heterogeneity)
    return w * cfg.n / w.sum()


def exposure(cfg: CodebaseConfig) -> np.ndarray:
    w = np.arange(1, cfg.n + 1, dtype=float) ** (-cfg.exposure_skew)
    return w * cfg.n / w.sum()


@dataclass(frozen=True)
class Batch:
    """A batch of scenarios as arrays; immutable by convention (arrays are read-only)."""

    cap: np.ndarray    # (S, T, n) capacity multiplier
    val: np.ndarray    # (S, T) value of one unit of output
    mult: np.ndarray   # (S, T) incident-rate multiplier
    u: np.ndarray      # (S, T, n) uniforms that realise incident counts
    d0: np.ndarray     # (S,) initial debt

    def __len__(self) -> int:
        return self.cap.shape[0]

    def __getitem__(self, sl: slice) -> "Batch":
        return Batch(self.cap[sl], self.val[sl], self.mult[sl], self.u[sl], self.d0[sl])


def _scenario(cfg: CodebaseConfig, family: str, split: str, index: int):
    rng = np.random.default_rng([_SPLIT_ID[split], _FAMILY_ID[family], index, cfg.n, cfg.T,
                                 int(round(cfg.heterogeneity * 1000)), 4242])
    T, n = cfg.T, cfg.n
    cap = rng.lognormal(-0.02, 0.2, size=(T, n))
    val = np.ones(T)
    mult = np.ones(T)
    d0 = 0.0
    if family == "crunch":      # a block of periods where shipped output is worth double
        a = int(rng.integers(0, T - T // 4))
        val[a:a + T // 4] = 2.0
    elif family == "fragile":   # the whole codebase is more failure-prone
        mult[:] = 1.5
    elif family == "spike":     # a cascade window with triple incident rates
        a = int(rng.integers(T // 4, T - T // 5))
        mult[a:a + T // 5] = 3.0
    elif family == "legacy":    # the day starts with inherited debt
        d0 = float(rng.uniform(2.0, 5.0))
    u = rng.random((T, n))
    return cap, val, mult, u, d0


def make_batch(cfg: CodebaseConfig, family: str, split: str, start: int, count: int) -> Batch:
    parts = [_scenario(cfg, family, split, start + i) for i in range(count)]
    arrs = [np.stack([p[k] for p in parts]) for k in range(4)]
    d0 = np.array([p[4] for p in parts])
    for a in (*arrs, d0):
        a.setflags(write=False)
    return Batch(*arrs, d0)


class DevSampler:
    """The only scenario source the evolution loop is given: base family, dev or pilot split."""

    def __init__(self, cfg: CodebaseConfig, split: str = "dev"):
        if split == "holdout":
            raise ValueError("the evolution loop may not sample holdout scenarios")
        self.cfg = cfg
        self._split = split

    def batch(self, start: int, count: int) -> Batch:
        return make_batch(self.cfg, "base", self._split, start, count)


@dataclass(frozen=True)
class Outcome:
    cost: np.ndarray       # (S, n) real cost: lost value against nominal maximum
    nominal: np.ndarray    # (S,) total nominal value (normaliser)
    charges: np.ndarray    # (S, n, 4) observable bases of INSTRUMENTS, per agent
    debt: np.ndarray       # (S,) mean debt over the day
    incidents: np.ndarray  # (S,) incidents per module-period
    visible: np.ndarray    # (S,) total visible coupling
    hidden: np.ndarray     # (S,) total concealed coupling

    @property
    def system_cost(self) -> np.ndarray:
        return self.cost.sum(axis=1)


def _poisson(u: np.ndarray, lam: np.ndarray) -> np.ndarray:
    """Inverse-CDF Poisson draw, elementwise; monotone in lam for fixed u."""
    p = np.exp(-lam)
    cdf = p.copy()
    k = np.zeros(lam.shape)
    for j in range(1, KMAX + 1):
        k += u > cdf
        p = p * lam / j
        cdf = cdf + p
    return k


def validate(profile) -> np.ndarray:
    P = np.asarray(profile, dtype=float)
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError("a profile is n policies of three numbers")
    if not np.all(np.isfinite(P)) or P.min() < 0.0 or P.max() > 1.0:
        raise ValueError("policy parameters must lie in [0, 1]")
    return P


def simulate(b: Batch, profile, cfg: CodebaseConfig, check: bool = False) -> Outcome:
    P = validate(profile)
    s, m, q = P[:, 0], P[:, 1], P[:, 2]
    if len(s) != cfg.n:
        raise ValueError("profile size does not match the configuration")
    A = sizes(cfg)
    gain = 1.0 + cfg.boost * (2 * s - s * s) * (1.0 - cfg.conceal_cost * m)   # (n,)
    keep = 1.0 - cfg.harden_cost * q
    expo = 1.0 - cfg.harden_effect * q
    if cfg.exposure_skew:
        expo = expo * exposure(cfg)
    load = s * (1.0 + cfg.conceal_harm * m)                                     # debt per unit capacity
    S, T, n = b.cap.shape
    D = b.d0.astype(float).copy()
    cost = np.zeros((S, n))
    nominal = np.zeros(S)
    ch = np.zeros((S, n, 4))
    debt_sum = np.zeros(S)
    inc = np.zeros(S)
    vis = np.zeros(S)
    hid = np.zeros(S)
    for t in range(T):
        capA = b.cap[:, t, :] * A                                    # (S, n)
        v = b.val[:, t][:, None]
        lam = cfg.rate * (D + cfg.convex * D * D)[:, None] * b.mult[:, t][:, None] * expo
        k = _poisson(b.u[:, t, :], lam)
        down = np.minimum(1.0, cfg.incident_loss * k)
        planned = capA * keep * gain
        y = planned * (1.0 - down)
        nom = v * capA * (1.0 + cfg.boost)
        cost += nom - v * y
        nominal += nom.sum(axis=1)
        loss = v * planned * down                                     # incident loss by module
        ch[:, :, 0] += capA * s * (1.0 - m)
        ch[:, :, 1] += y
        ch[:, :, 2] += loss
        ch[:, :, 3] += loss.sum(axis=1)[:, None] - loss
        coup = capA * s
        vis += (coup * (1.0 - m)).sum(axis=1)
        hid += (coup * m).sum(axis=1)
        debt_sum += D
        inc += k.sum(axis=1)
        D = (1.0 - cfg.decay) * D + (capA * load).sum(axis=1) / n
        if check:
            assert np.all(D >= 0.0) and np.all(y >= -1e-12) and np.all(y <= planned + 1e-12)
            assert np.all(cost >= -1e-9)
    return Outcome(cost=cost, nominal=nominal, charges=ch, debt=debt_sum / T,
                   incidents=inc / (T * n), visible=vis, hidden=hid)


def private_cost(o: Outcome, instrument: str | None, level: float) -> np.ndarray:
    """Real cost plus the charge of one instrument at one level (a transfer)."""
    if not instrument or level == 0.0:
        return o.cost
    return o.cost + level * o.charges[:, :, INSTRUMENTS.index(instrument)]
