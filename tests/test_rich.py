"""Rule-level (eight-parameter) policies and the band tariff."""

import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from evortgs.evolve import EvoConfig, evolve
from evortgs.scenarios import FAMILIES, DevSampler, WorldConfig, make_scenario
from evortgs.sim import RICH_DIM, Costs, Scenario, simulate, validate_policy

CFG = WorldConfig(n=4, T=10, payments_per_bank=6)
C = Costs()
unit = st.floats(0.0, 1.0, allow_nan=False)


def embed(p):
    liq, buf, hold = p
    return (liq, buf, buf, hold, 0.0, 0.5, hold, 1.0)


def two_bank(pay, T=4):
    arrivals = [[] for _ in range(T)]
    for k, p in enumerate(pay):
        arrivals[p[3]].append(k)
    return Scenario(n=2, T=T, exp_out=(100, 100), pay=tuple(pay),
                    arrivals=tuple(tuple(a) for a in arrivals))


@settings(max_examples=60, deadline=None)
@given(st.lists(st.tuples(unit, unit, unit), min_size=4, max_size=4),
       st.sampled_from(FAMILIES), st.integers(0, 50))
def test_three_parameter_policy_is_a_special_case(profile, family, index):
    scn = make_scenario(CFG, family, "dev", index)
    a = simulate(scn, tuple(profile), C, check=True)
    b = simulate(scn, tuple(embed(p) for p in profile), C, check=True)
    assert a == b


@settings(max_examples=150, deadline=None)
@given(st.lists(st.tuples(*[unit] * RICH_DIM), min_size=4, max_size=4),
       st.sampled_from(FAMILIES), st.integers(0, 50))
def test_invariants_hold_for_rule_level_policies(profile, family, index):
    scn = make_scenario(CFG, family, "dev", index)
    r = simulate(scn, tuple(profile), C, check=True)
    assert sum(r.balances) == sum(r.liquidity)
    assert sum(r.late_value) <= r.total_value


def test_policy_length_is_checked():
    with pytest.raises(ValueError):
        validate_policy((0.5,) * 5)
    with pytest.raises(ValueError):
        validate_policy((0.5,) * 7 + (1.5,))


def test_opening_tick_delays_ordinary_but_not_urgent_payments():
    scn = two_bank([(0, 1, 10, 0, -1), (0, 1, 10, 0, 0)])
    base = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0)
    late = (1.0, 0.0, 0.0, 0.0, 2 / 3, 1.0, 0.0, 1.0)  # opens at tick 2 of 0..3
    assert simulate(scn, (base, base), C, check=True).settle_tick == (0, 0)
    assert simulate(scn, (late, base), C, check=True).settle_tick == (2, 0)


def test_large_payments_use_their_own_hold():
    scn = two_bank([(0, 1, 20, 0, -1), (0, 1, 60, 0, -1)])
    # threshold 250 * 40**0 = 250 would make nothing large; use tiny amounts via big=0 and scale
    pol = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1 / 3, 1.0)
    big = two_bank([(0, 1, 200, 0, -1), (0, 1, 300, 0, -1)])
    big = Scenario(n=2, T=4, exp_out=(1000, 1000), pay=big.pay, arrivals=big.arrivals)
    r = simulate(big, (pol, pol), C, check=True)
    assert r.settle_tick == (0, 1)  # 300 > 250 waits one tick, 200 does not
    assert simulate(scn, (pol, pol), C, check=True).settle_tick == (0, 0)


def test_bilateral_limit_blocks_until_counterparty_pays_or_day_ends():
    # limit = bilat/(1-bilat) * E/(n-1) = 0.2/0.8 * 100 = 25
    lim = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.2)
    free = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0)
    alone = two_bank([(0, 1, 20, 0, -1), (0, 1, 20, 0, -1)])
    assert simulate(alone, (lim, free), C, check=True).settle_tick == (0, 3)
    paid = two_bank([(0, 1, 20, 0, -1), (0, 1, 20, 0, -1), (1, 0, 20, 1, -1)])
    assert simulate(paid, (lim, free), C, check=True).settle_tick == (0, 1, 1)


def test_late_value_counts_second_half_and_unsettled():
    scn = two_bank([(0, 1, 10, 0, -1), (0, 1, 30, 2, -1), (0, 1, 500, 0, -1)])
    pol = (1.0, 0.0, 0.0)
    r = simulate(scn, (pol, pol), C, check=True)
    assert r.settle_tick == (0, 2, -1)
    assert r.late_value == (530, 0)


def test_tariff_is_a_transfer_that_changes_private_but_not_reported_cost():
    e0 = EvoConfig(generations=1, K=1, M=2, rich=True)
    e1 = EvoConfig(generations=1, K=1, M=2, rich=True, tariff=1.0)
    a = evolve(DevSampler(CFG), C, e0, seed=3)
    b = evolve(DevSampler(CFG), C, e1, seed=3)
    assert a.history[0]["profile"] == b.history[0]["profile"]
    assert a.history[0]["dev_system_cost"] == b.history[0]["dev_system_cost"]
    assert all(len(p) == RICH_DIM and all(0.0 <= x <= 1.0 for x in p) for p in b.profile)


@pytest.mark.parametrize("kw", [dict(), dict(kappa=1.0), dict(gate="welfare"),
                                dict(gate="welfare_universal"), dict(fee=4.0),
                                dict(tariff=1.0)])
def test_budget_is_identical_across_arms_and_policy_spaces(kw):
    for rich in (False, True):
        e = EvoConfig(generations=2, K=2, M=2, rich=rich, **kw)
        r = evolve(DevSampler(CFG), C, e, seed=1)
        assert r.sims == e.generations * (2 * e.M + CFG.n * e.K * 2 * e.M)


def test_stored_confirmatory_run_is_reproduced_by_the_extended_engine():
    path = Path(__file__).resolve().parents[1] / "runs" / "E1.jsonl"
    if not path.exists():
        pytest.skip("no stored runs")
    from evortgs.experiments import costs_for
    rec = next(r for r in map(json.loads, path.open(encoding="utf-8"))
               if r["seed"] == 0 and r["gate"] == "kappa" and r["kappa"] == 1.0 and not r["fee"])
    world = WorldConfig(n=rec["n"], T=20, heterogeneity=rec["het"])
    r = evolve(DevSampler(world), costs_for(rec["delay_day"]),
               EvoConfig(generations=3, kappa=1.0), seed=0)
    # the mutation scale depends on the run length, so a short run coincides
    # with the stored 40-generation run only up to the start of generation 1
    old = rec["history"]
    assert r.history[0]["dev_system_cost"] == old[0]["dev_system_cost"]
    assert r.history[0]["accepted"] == old[0]["accepted"]
    assert r.history[1]["dev_system_cost"] == old[1]["dev_system_cost"]
