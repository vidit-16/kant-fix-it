import ast
import math
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from evortgs import codebase as cb
from evortgs.cb_experiments import make_costs, planner
from evortgs.evolve import EvoConfig, evolve
from evortgs.gates import evolve_env
from evortgs.scenarios import DevSampler as RtgsSampler
from evortgs.scenarios import WorldConfig
from evortgs.sim import Costs

SRC = Path(__file__).resolve().parents[1] / "src" / "evortgs"
CFG = cb.CodebaseConfig(n=4, T=8)
B = cb.make_batch(CFG, "base", "dev", 0, 6)

policy = st.tuples(*[st.floats(0.0, 1.0)] * 3)
profiles = st.lists(policy, min_size=4, max_size=4)


def reference_simulate(b, i, profile, cfg):
    """Slow, scalar re-implementation of one scenario, written from the docstring."""
    A = cb.sizes(cfg)
    W = cb.exposure(cfg)
    D = float(b.d0[i])
    cost = [0.0] * cfg.n
    for t in range(cfg.T):
        newD = (1 - cfg.decay) * D
        for a, (s, m, q) in enumerate(profile):
            capA = b.cap[i, t, a] * A[a]
            lam = cfg.rate * (D + cfg.convex * D * D) * b.mult[i, t] * (1 - cfg.harden_effect * q) * W[a]
            u, k, p, c = b.u[i, t, a], 0, math.exp(-lam), math.exp(-lam)
            while u > c and k < cb.KMAX:
                k += 1
                p *= lam / k
                c += p
            planned = capA * (1 - cfg.harden_cost * q) * (
                1 + cfg.boost * (2 * s - s * s) * (1 - cfg.conceal_cost * m))
            y = planned * (1 - min(1.0, cfg.incident_loss * k))
            cost[a] += b.val[i, t] * (capA * (1 + cfg.boost) - y)
            newD += capA * s * (1 + cfg.conceal_harm * m) / cfg.n
        D = newD
    return cost


@settings(max_examples=25, deadline=None)
@given(profiles)
def test_vectorised_simulation_matches_scalar_reference(prof):
    o = cb.simulate(B, prof, CFG, check=True)
    for i in range(len(B)):
        assert np.allclose(o.cost[i], reference_simulate(B, i, prof, CFG), rtol=1e-9, atol=1e-9)


@settings(max_examples=25, deadline=None)
@given(profiles)
def test_costs_bounded_and_debt_nonnegative(prof):
    o = cb.simulate(B, prof, CFG, check=True)
    assert np.all(o.cost >= -1e-9)
    assert np.all(o.system_cost <= o.nominal + 1e-9)
    assert np.all(o.debt >= 0) and np.all(o.incidents >= 0)


def test_no_shortcuts_means_no_debt_and_no_incidents():
    o = cb.simulate(B, [(0.0, 0.7, 0.3)] * 4, CFG)
    assert np.all(o.debt == 0) and np.all(o.incidents == 0)
    assert np.all(o.charges[:, :, [0, 2, 3]] == 0)


def test_concealment_hides_coupling_from_proxy_only():
    vis = cb.simulate(B, [(0.8, 0.0, 0.0)] * 4, CFG)
    hid = cb.simulate(B, [(0.8, 1.0, 0.0)] * 4, CFG)
    assert np.all(hid.charges[:, :, 0] == 0) and np.all(vis.charges[:, :, 0] > 0)
    assert np.all(hid.debt >= vis.debt)  # concealed coupling is at least as harmful


@settings(max_examples=20, deadline=None)
@given(profiles, st.sampled_from(cb.INSTRUMENTS), st.floats(0.0, 10.0))
def test_instruments_are_transfers(prof, inst, level):
    o = cb.simulate(B, prof, CFG)
    pc = cb.private_cost(o, inst, level)
    assert np.all(pc >= o.cost - 1e-12)
    # the social cost never contains a charge
    assert np.allclose(o.system_cost, o.cost.sum(axis=1))


def test_ambient_charge_is_incident_loss_elsewhere():
    o = cb.simulate(B, [(0.9, 0.0, 0.0), (0.2, 0.0, 1.0), (0.5, 0.0, 0.5), (1.0, 0.0, 0.0)], CFG)
    surf, amb = o.charges[:, :, 2], o.charges[:, :, 3]
    assert np.allclose(amb, surf.sum(axis=1, keepdims=True) - surf)


def test_ambient_at_one_aligns_unilateral_incentives_with_social_cost():
    # private cost minus social cost must not depend on the agent's own policy
    base = [(0.5, 0.0, 0.5)] * 4
    gaps = []
    for p in [(0.0, 0.0, 0.0), (0.9, 0.3, 0.1), (0.4, 1.0, 1.0)]:
        prof = [p] + base[1:]
        o = cb.simulate(B, prof, CFG)
        gaps.append(cb.private_cost(o, "ambient", 1.0)[:, 0] - o.system_cost)
    for g in gaps[1:]:
        assert np.allclose(g, gaps[0])


def test_profile_validation():
    with pytest.raises(ValueError):
        cb.simulate(B, [(0.5, 0.5, 1.2)] * 4, CFG)
    with pytest.raises(ValueError):
        cb.simulate(B, [(0.5, 0.5, 0.5)] * 3, CFG)


def test_scenarios_deterministic_and_splits_disjoint():
    a = cb.make_batch(CFG, "base", "dev", 3, 4)
    b = cb.make_batch(CFG, "base", "dev", 3, 4)
    assert np.array_equal(a.u, b.u) and np.array_equal(a.cap, b.cap)
    dev = {cb.make_batch(CFG, "base", "dev", i, 1).u.tobytes() for i in range(200)}
    hold = {cb.make_batch(CFG, f, "holdout", i, 1).u.tobytes()
            for f in cb.FAMILIES for i in range(50)}
    pil = {cb.make_batch(CFG, "base", "pilot", i, 1).u.tobytes() for i in range(200)}
    assert dev.isdisjoint(hold) and dev.isdisjoint(pil) and pil.isdisjoint(hold)


def test_batches_are_read_only():
    with pytest.raises(ValueError):
        B.u[0, 0, 0] = 0.5


def test_dev_sampler_refuses_holdout():
    with pytest.raises(ValueError):
        cb.DevSampler(CFG, split="holdout")


@pytest.mark.parametrize("mod", ["gates.py", "codebase.py"])
def test_evolution_code_cannot_reach_evaluator(mod):
    text = (SRC / mod).read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert "evaluate" not in (node.module or "")
    if mod == "gates.py":
        assert "holdout" not in text and "make_batch" not in text


def test_generic_loop_reproduces_payment_loop_exactly():
    world = WorldConfig(n=4, T=10, payments_per_bank=6)
    C = Costs()
    from evortgs.evolve import _costs
    for gate, kappa, fee in [("kappa", 0.0, 0.0), ("kappa", 1.0, 0.0), ("kappa", 0.5, 0.0),
                             ("welfare", 0.0, 0.0), ("welfare_universal", 0.0, 0.0),
                             ("noharm", 0.0, 0.0), ("kappa", 0.0, 4.0)]:
        e = EvoConfig(generations=3, K=2, M=2, gate=gate, kappa=kappa, fee=fee)
        s = RtgsSampler(world)
        a = evolve(s, C, e, seed=2)
        b = evolve_env(lambda st, ct: s.batch(st, ct),
                       lambda scns, prof: _costs(scns, prof, C, fee), world.n, 3, e, seed=2)
        assert a.profile == b.profile and a.history == b.history and a.sims == b.sims


@pytest.mark.parametrize("gate,kappa,inst,lev", [
    ("kappa", 0.0, None, 0.0), ("kappa", 1.0, None, 0.0), ("welfare", 0.0, None, 0.0),
    ("welfare_universal", 0.0, None, 0.0), ("kappa", 0.0, "proxy", 0.4),
    ("kappa", 0.0, "ambient", 1.0), ("kappa", 0.0, "activity", 0.5), ("kappa", 0.0, "surface", 2.0)])
def test_every_arm_spends_the_same_budget(gate, kappa, inst, lev):
    e = EvoConfig(generations=3, K=2, M=2, gate=gate, kappa=kappa)
    s = cb.DevSampler(CFG)
    r = evolve_env(s.batch, make_costs(CFG, inst, lev), CFG.n, 3, e, seed=1)
    S = 2 * e.M
    assert r.sims == e.generations * (S + CFG.n * e.K * S)
    for p in r.profile:
        assert all(0.0 <= x <= 1.0 for x in p)


def test_arms_share_initial_profile_and_scenarios():
    s = cb.DevSampler(CFG)
    e = EvoConfig(generations=1, K=1, M=2)
    a = evolve_env(s.batch, make_costs(CFG, None, 0.0), CFG.n, 3, e, seed=4)
    b = evolve_env(s.batch, make_costs(CFG, "ambient", 1.0), CFG.n, 3, e, seed=4)
    assert a.history[0]["profile"] == b.history[0]["profile"]
    assert a.history[0]["dev_system_cost"] == b.history[0]["dev_system_cost"]


def test_planner_is_symmetric_and_beats_corners():
    s = cb.DevSampler(CFG)
    p = planner(s, seed=0, batch=8)
    assert len(set(p)) == 1
    b = s.batch(50_000_000, 8)
    f = lambda x: cb.simulate(b, [x] * CFG.n, CFG).system_cost.mean()
    for corner in [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0.5, 0, 0.5)]:
        assert f(p[0]) <= f(corner) + 1e-9


def test_asymmetric_planner_never_worse_than_symmetric():
    from evortgs.cb_experiments import planner_asym
    cfg = cb.CodebaseConfig(n=4, T=8, heterogeneity=1.5)
    s = cb.DevSampler(cfg)
    sym = planner(s, seed=0, batch=8)
    asym, sims = planner_asym(s, seed=0, batch=8, sweeps=1)
    b = s.batch(50_000_000, 8)
    f = lambda P: (cb.simulate(b, P, cfg).system_cost / cb.simulate(b, P, cfg).nominal).mean()
    assert f(asym) <= f(sym) + 1e-12 and sims > 0


@pytest.mark.parametrize("het", [0.75, 1.5])
def test_ambient_alignment_holds_with_unequal_agents(het):
    cfg = cb.CodebaseConfig(n=4, T=8, heterogeneity=het)
    b = cb.make_batch(cfg, "base", "dev", 0, 6)
    base = [(0.5, 0.0, 0.5)] * 4
    for i in (0, 3):
        gaps = []
        for p in [(0.0, 0.0, 0.0), (0.9, 0.3, 0.1), (0.4, 1.0, 1.0)]:
            o = cb.simulate(b, base[:i] + [p] + base[i + 1:], cfg)
            gaps.append(cb.private_cost(o, "ambient", 1.0)[:, i] - o.system_cost)
        for g in gaps[1:]:
            assert np.allclose(g, gaps[0])


def test_e9_specification_unchanged():
    from evortgs.cb_experiments import experiments
    S = experiments("E9")
    assert len(S) == 1280 and all("het" not in s for s in S)


@settings(max_examples=15, deadline=None)
@given(profiles)
def test_vectorised_matches_reference_with_skewed_exposure(prof):
    cfg = cb.CodebaseConfig(n=4, T=8, exposure_skew=1.5, heterogeneity=0.75)
    b = cb.make_batch(cfg, "base", "dev", 0, 4)
    o = cb.simulate(b, prof, cfg, check=True)
    for i in range(len(b)):
        assert np.allclose(o.cost[i], reference_simulate(b, i, prof, cfg), rtol=1e-9, atol=1e-9)


def test_exposure_skew_moves_incidents_not_debt():
    flat = cb.CodebaseConfig(n=4, T=8)
    skew = cb.CodebaseConfig(n=4, T=8, exposure_skew=1.5)
    assert np.isclose(cb.exposure(skew).mean(), 1.0) and cb.exposure(skew)[0] > cb.exposure(skew)[-1]
    P = [(0.8, 0.0, 0.0)] * 4
    a, c = cb.simulate(B, P, flat), cb.simulate(B, P, skew)
    assert np.array_equal(a.debt, c.debt)
    assert c.charges[:, 0, 2].sum() >= a.charges[:, 0, 2].sum()


def test_ambient_alignment_holds_with_skewed_exposure():
    cfg = cb.CodebaseConfig(n=4, T=8, exposure_skew=1.5)
    b = cb.make_batch(cfg, "base", "dev", 0, 6)
    base = [(0.5, 0.0, 0.5)] * 4
    for i in (0, 3):
        gaps = []
        for p in [(0.0, 0.0, 0.0), (0.9, 0.3, 0.1), (0.4, 1.0, 1.0)]:
            o = cb.simulate(b, base[:i] + [p] + base[i + 1:], cfg)
            gaps.append(cb.private_cost(o, "ambient", 1.0)[:, i] - o.system_cost)
        for g in gaps[1:]:
            assert np.allclose(g, gaps[0])


# --- E11: scale of the universalized counterfactual -------------------------

from evortgs.gates import SCALES, _universal  # noqa: E402


@pytest.mark.parametrize("scale", [s for s in SCALES if s != "linear"])
def test_scale_maps_invert_on_policy_range(scale):
    g, ginv = SCALES[scale]
    x = np.linspace(0.0, 1.0, 101)
    assert np.allclose(ginv(g(x)), x, atol=1e-12)


@settings(max_examples=30, deadline=None)
@given(st.lists(st.floats(0.0, 1.0), min_size=3, max_size=3),
       st.lists(st.floats(-0.3, 0.3), min_size=3, max_size=3),
       st.sampled_from(sorted(SCALES)))
def test_universal_keeps_own_candidate_and_bounds(x, d, scale):
    from evortgs.evolve import _clip
    cur = (tuple(x), (0.2, 0.5, 0.9), (0.0, 1.0, 0.4))
    cand = tuple(_clip(x[a] + d[a]) for a in range(3))
    allp = _universal(cur, 0, cand, d, 3, 3, scale)
    assert allp[0] == cand
    assert all(0.0 <= v <= 1.0 for p in allp for v in p)


@pytest.mark.parametrize("scale", sorted(SCALES))
def test_scales_agree_when_agents_are_identical(scale):
    cur = ((0.4, 0.3, 0.6),) * 4
    d = (0.05, -0.1, 0.02)
    cand = tuple(cur[0][a] + d[a] for a in range(3))
    lin = _universal(cur, 1, cand, d, 4, 3, "linear")
    other = _universal(cur, 1, cand, d, 4, 3, scale)
    assert np.allclose(np.array(lin), np.array(other), atol=1e-12)


def test_linear_scale_is_the_default_loop():
    s = cb.DevSampler(CFG)
    e = EvoConfig(generations=3, K=2, M=2, gate="kappa", kappa=1.0)
    a = evolve_env(s.batch, make_costs(CFG, None, 0.0), CFG.n, 3, e, seed=3)
    b = evolve_env(s.batch, make_costs(CFG, None, 0.0), CFG.n, 3, e, seed=3, scale="linear")
    assert a.profile == b.profile and a.history == b.history


def test_scale_changes_kantian_gate_only():
    s = cb.DevSampler(CFG)
    for gate, kappa in (("welfare", 0.0), ("kappa", 0.0)):
        e = EvoConfig(generations=2, K=2, M=2, gate=gate, kappa=kappa)
        a = evolve_env(s.batch, make_costs(CFG, None, 0.0), CFG.n, 3, e, seed=5)
        b = evolve_env(s.batch, make_costs(CFG, None, 0.0), CFG.n, 3, e, seed=5, scale="logit")
        assert a.profile == b.profile


def test_e10_specification_unchanged_by_e11():
    from evortgs.cb_experiments import experiments
    S = experiments("E10")
    assert len(S) == 1080 and all("scale" not in s for s in S)
    E = experiments("E11")
    assert len(E) == 360 and {s["scale"] for s in E} == {"log", "sqrt", "logit"}
