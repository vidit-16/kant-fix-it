"""E13: off-ledger effort, budget-balanced transfers and the search loop used to compare them."""

import numpy as np
import pytest

from evortgs import e13
from evortgs.cb_evaluate import _holdout, evaluate
from evortgs.codebase import CodebaseConfig, DevSampler, make_batch, private_cost, simulate, sizes
from evortgs.evolve import EvoConfig
from evortgs.gates import evolve_env

RNG = np.random.default_rng(5)
P0 = RNG.random((6, 3))


def cfgs(skew=0.0):
    return e13.config(0.0, skew), e13.config(e13.EFFORT, skew)


def batch(cfg, n=8, start=7_000_000):
    return make_batch(cfg, "base", "pilot", start, n)


def test_effort_adds_exactly_its_term_and_nothing_else():
    off, on = cfgs(1.5)
    b0, b1 = batch(off), batch(on)
    assert all(np.array_equal(getattr(b0, k), getattr(b1, k)) for k in ("cap", "val", "mult", "u", "d0"))
    o0, o1 = simulate(b0, P0, off), simulate(b1, P0, on)
    capA = (b0.cap * sizes(off)).sum(axis=1)                       # (S, n), summed over periods
    K = e13.EFFORT * capA * (1 - P0[:, 0]) ** 2
    assert np.allclose(o1.cost - o0.cost, K, atol=1e-12)
    assert np.allclose(o1.effort, K, atol=1e-12) and not o0.effort.any()
    for k in ("charges", "nominal", "debt", "incidents", "visible", "hidden"):
        assert np.array_equal(getattr(o0, k), getattr(o1, k))


def test_effort_off_matches_the_pinned_simulator():
    pinned = CodebaseConfig(conceal_cost=0.25, exposure_skew=1.5)
    b = batch(pinned)
    a, c = simulate(b, P0, pinned), simulate(b, P0, e13.config(0.0, 1.5))
    assert np.array_equal(a.cost, c.cost)


def test_evaluator_default_block_unchanged_and_new_block_disjoint():
    cfg = e13.config(0.0, 0.0)
    old, new = _holdout(cfg, "base"), _holdout(cfg, "base", "holdout", e13.HOLDOUT_START)
    assert np.array_equal(old.u, make_batch(cfg, "base", "holdout", 0, 100).u)
    assert not np.array_equal(old.u, new.u)
    assert e13.HOLDOUT_START > 100
    ev = evaluate(e13.config(e13.EFFORT, 0.0), P0, start=e13.HOLDOUT_START)
    assert "effort_cost" in ev["base"] and "effort_cost" not in evaluate(cfg, P0)["base"]


def _mech(cfg, kind, **kw):
    return e13.Mechanism(cfg, kind, **kw)


@pytest.mark.parametrize("kind,kw", [("pool", {}), ("pool", {"level": 2.0}),
                                     ("direct", {"level": 1.0, "scale": 3.0}),
                                     ("direct", {"level": 1.0, "scale": 3.0, "role": True}),
                                     ("contract", {"anchor": "zero"}), ("contract", {"anchor": "mid"}),
                                     ("pool", {"capped": True}), ("contract", {"capped": True})])
def test_strict_transfers_balance_in_every_scenario(kind, kw):
    for skew in (0.0, 1.5):
        cfg = e13.config(e13.EFFORT, skew)
        b = batch(cfg)
        c = _mech(cfg, kind, **kw)(b, P0)
        t = c[:, :, 1] - c[:, :, 0]
        assert np.abs(t.sum(axis=1)).max() < 1e-9


def test_cap_bounds_every_settlement_and_keeps_balance():
    cfg = e13.config(e13.EFFORT, 1.5)
    t = np.array([[40.0, -10.0, -10.0, -10.0, -5.0, -5.0], [1.0, -1.0, 0, 0, 0, 0]])
    tc = e13.cap(t, cfg)
    bound = e13.CAP_SHARE * cfg.T * (1 + cfg.boost)
    assert np.abs(tc).max() <= bound + 1e-12 and np.allclose(tc.sum(axis=1), 0)
    assert np.array_equal(tc[1], t[1])   # untouched when inside the bound


def test_direct_charge_own_slope_and_fixed_rebate():
    cfg = e13.config(e13.EFFORT, 1.5)
    for role in (False, True):
        tau = e13.direct_rates(cfg, 2.0, role)
        P1 = P0.copy()
        P1[2, 0] = min(1.0, P0[2, 0] + 0.1)
        t0, t1 = (e13.direct_transfer(cfg, P, 2.0, role) for P in (P0, P1))
        dh = e13.load(P1)[2] - e13.load(P0)[2]
        assert np.isclose(t1[2] - t0[2], tau[2] * dh)
    assert np.allclose(e13.direct_rates(e13.config(0.0, 0.0), 2.0, True), 2.0)


def _unilateral(cfg, kind, i=1, d=(0.08, -0.05, 0.04), **kw):
    b = batch(cfg, 16)
    P1 = P0.copy()
    P1[i] = np.clip(P0[i] + d, 0, 1)
    m = _mech(cfg, kind, **kw)
    c0, c1 = m(b, P0), m(b, P1)
    dW = c1[:, :, 0].sum(axis=1) - c0[:, :, 0].sum(axis=1)
    dpriv = c1[:, i, 1] - c0[:, i, 1]
    dK = simulate(b, P1, cfg).effort[:, i] - simulate(b, P0, cfg).effort[:, i]
    return dW, dpriv, dK


@pytest.mark.parametrize("skew", (0.0, 1.5))
def test_ambient_level1_is_exact_welfare_contrast_with_effort(skew):
    dW, dpriv, _ = _unilateral(e13.config(e13.EFFORT, skew), "ambient")
    assert np.allclose(dpriv, dW, atol=1e-9)


@pytest.mark.parametrize("skew", (0.0, 1.5))
def test_pool_level1_overweights_own_effort(skew):
    cfg = e13.config(e13.EFFORT, skew)
    dW, dpriv, dK = _unilateral(cfg, "pool")
    assert np.allclose(cfg.n * dpriv, dW + (cfg.n - 1) * dK, atol=1e-9)
    assert np.abs(dK).max() > 0


def test_contract_reuses_proposer_reset_and_counts_every_simulation():
    cfg = e13.config(e13.EFFORT, 0.0)
    b = batch(cfg)
    m = _mech(cfg, "contract")
    m(b, P0)
    assert m.sims == len(b) * (1 + cfg.n)
    P1 = P0.copy()
    P1[3, 0] = 0.2
    m(b, P1)   # the reset of agent 3 is the baseline's; five new resets plus the profile
    assert m.sims == len(b) * (1 + cfg.n + 1 + cfg.n - 1)


def test_loop_without_noise_is_the_pinned_loop():
    for effort in (0.0, e13.EFFORT):
        cfg = e13.config(effort, 1.5)
        s = DevSampler(cfg, split="pilot")
        for kappa in (0.0, 1.0):
            ec = EvoConfig(generations=3, K=2, M=2, gate="kappa", kappa=kappa)
            mk = lambda: e13.Mechanism(cfg, "pool")
            a = e13.evolve(s.batch, mk(), cfg.n, ec, 11, kappa)
            costs = lambda b, P: mk()(b, P)
            ref = evolve_env(s.batch, costs, cfg.n, 3, ec, 11, scale="linear_realized")
            assert a.profile == ref.profile and a.history == ref.history and a.sims == ref.sims


def test_peer_noise_is_common_deterministic_and_deploys_true_policies():
    cfg = e13.config(e13.EFFORT, 1.5)
    s = DevSampler(cfg, split="pilot")
    ec = EvoConfig(generations=3, K=2, M=2, gate="kappa", kappa=1.0)
    run = lambda nz: e13.evolve(s.batch, e13.Mechanism(cfg), cfg.n, ec, 4, 1.0, nz)
    a, b, c = run(0.1), run(0.1), run(0.0)
    assert a.profile == b.profile and a.history == b.history
    assert a.sims == c.sims + ec.generations * cfg.n * 2 * ec.M
    # an accepted policy is the agent's exact policy plus its own mutation, never a noisy peer view
    for g in range(len(a.history) - 1):
        for i, (p, q) in enumerate(zip(a.history[g]["profile"], a.history[g + 1]["profile"])):
            assert p == q or max(abs(x - y) for x, y in zip(p, q)) < 0.75


def test_pool_and_ambient_trajectories_coincide_without_effort():
    for skew in (0.0, 1.5):
        cfg = e13.config(0.0, skew)
        s = DevSampler(cfg, split="pilot")
        ec = EvoConfig(generations=4, K=2, M=2, gate="kappa", kappa=0.0)
        a = e13.evolve(s.batch, e13.Mechanism(cfg, "pool"), cfg.n, ec, 3, 0.0)
        b = e13.evolve(s.batch, e13.Mechanism(cfg, "ambient"), cfg.n, ec, 3, 0.0)
        assert a.profile == b.profile


def test_mechanism_matches_pinned_private_cost():
    cfg = e13.config(0.0, 0.0)
    b = batch(cfg)
    o = simulate(b, P0, cfg)
    for kind, inst in (("pool", "pool"), ("ambient", "ambient")):
        c = e13.Mechanism(cfg, kind, 1.5)(b, P0)
        assert np.allclose(c[:, :, 1], private_cost(o, inst, 1.5))


def test_seed_and_scenario_namespaces_are_disjoint():
    groups = [set(e13.CALIB_SEEDS), set(e13.VALID_SEEDS), set(e13.ORACLE_SEEDS),
              set(e13.CONFIRM_SEEDS), set(range(0, 20)), set(range(1000, 1006))]
    assert sum(len(g) for g in groups) == len(set().union(*groups))
    # training indices seed*100000 + g*S stay below every dev evaluation block
    assert max(e13.CONFIRM_SEEDS) * 100_000 + 40 * 2 * 64 < e13.CALIB_EVAL_START
    blocks = [e13.CALIB_EVAL_START, e13.VALID_EVAL_START, e13.ORACLE_START, e13.SCALE_START]
    assert sorted(blocks) == blocks and all(b2 - b1 >= 500 * 100 for b1, b2 in zip(blocks, blocks[1:]))


def test_calibration_and_selection_specs():
    cal = e13.experiments("calib")
    assert {s["seed"] for s in cal} == set(e13.CALIB_SEEDS)
    assert all(s["effort"] == e13.EFFORT and s["kind"] == "contract" for s in cal)
    assert len(cal) == 20 * 2 * 2
    assert e13.marginal_damage(2000, 1.5, batch=4) > 0


def test_whole_pipeline_dry_run(tmp_path, monkeypatch):
    """calib -> lock -> select -> lock -> E13 -> E13sens -> analysis, on pilot scenarios only."""
    import json
    from pathlib import Path
    from evortgs import analysis_e13
    monkeypatch.chdir(tmp_path)
    Path("runs").mkdir()
    for k, v in dict(DEV_SPLIT="pilot", CONFIRM_SPLIT="pilot", GENERATIONS=2,
                     CALIB_SEEDS=range(1000, 1002), VALID_SEEDS=range(1002, 1004),
                     CONFIRM_SEEDS=range(1004, 1007), ORACLE_SEEDS=range(1000, 1003)).items():
        monkeypatch.setattr(e13, k, v)

    def stage(name, fn):
        Path(fn).write_text("\n".join(json.dumps(e13._run(sp)) for sp in e13.experiments(name)))

    stage("calib", "runs/e13_calib.jsonl")
    assert e13.lock()["anchor"] in e13.ANCHORS
    stage("select", "runs/e13_select.jsonl")
    lk = e13.lock()
    assert set(lk["selected"]) == {"0.0", "1.5"} and lk["big_M"] >= 8
    stage("E13", "runs/E13.jsonl")
    stage("E13sens", "runs/E13sens.jsonl")
    analysis_e13.main()
    r = json.loads(Path("runs/results_e13.json").read_text())
    assert len(r["primary"]) == 4 and "met" in r["kill_criterion"]
    assert r["invariants"]["max_abs_strict_balance_residual"] < 1e-9
    for sk in ("0.0", "1.5"):
        assert r["secondary"]["marginal_errors"][sk]["ambient"] < 1e-9
