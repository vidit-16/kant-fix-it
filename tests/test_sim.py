import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from evortgs.scenarios import WorldConfig, make_scenario
from evortgs.sim import Costs, Scenario, simulate, validate_policy

C = Costs(cL=1.0, cD=0.1, cX=0.5, cE=2.0)


def scn(n, T, exp_out, pay, outage=()):
    pay = tuple(sorted(pay, key=lambda p: p[3]))
    arr = [[] for _ in range(T)]
    for k, p in enumerate(pay):
        arr[p[3]].append(k)
    return Scenario(n=n, T=T, exp_out=tuple(exp_out), pay=pay,
                    arrivals=tuple(tuple(a) for a in arr), outage=tuple(outage))


# two banks, each owes the other 100 at tick 0, two ticks in the day
TWO = scn(2, 2, (100, 100), [(0, 1, 100, 0, -1), (1, 0, 100, 0, -1)])
EARLY = (1.0, 0.0, 0.0)
FREE = (0.0, 0.0, 1.0)  # post nothing, wait for incoming funds


def test_both_early_pay_only_liquidity():
    r = simulate(TWO, (EARLY, EARLY), C, check=True)
    assert r.cost == (100.0, 100.0)
    assert r.settle_tick == (0, 0)
    assert r.balances == (100, 100)


def test_free_rider_recycles_incoming_funds():
    r = simulate(TWO, (EARLY, FREE), C, check=True)
    # bank 0 funds its payment; bank 1 reuses that money one tick later
    assert r.settle_tick == (0, 1)
    assert r.cost[0] == pytest.approx(100.0)
    assert r.cost[1] == pytest.approx(0.1 * 100 * 1)
    assert r.balances == (100, 0)


def test_mutual_free_riding_gridlocks():
    r = simulate(TWO, (FREE, FREE), C, check=True)
    assert r.settle_tick == (-1, -1)
    assert r.unsettled_value == 200
    # each: two ticks of delay plus the end-of-day charge
    assert r.cost == pytest.approx((0.1 * 100 * 2 + 2.0 * 100,) * 2)


def test_free_riding_is_a_private_gain_but_mutual_free_riding_is_worst():
    """The 2x2 game the engine induces: deviating from (early, early) pays
    privately when cD < cL, yet (free, free) is worse for both than (early, early)."""
    ee = simulate(TWO, (EARLY, EARLY), C).cost[1]
    ef = simulate(TWO, (EARLY, FREE), C).cost[1]
    ff = simulate(TWO, (FREE, FREE), C).cost[1]
    assert ef < ee < ff


def test_buffer_blocks_release_until_last_tick():
    s = scn(2, 3, (100, 100), [(0, 1, 60, 0, -1)])
    r = simulate(s, ((1.0, 0.5, 0.0), EARLY), C, check=True)
    assert r.settle_tick == (2,)  # 100-60 < 50 so it waits for the final tick


def test_urgent_payment_bypasses_hold_and_buffer_and_miss_is_charged():
    s = scn(2, 4, (100, 100), [(0, 1, 60, 0, 1)])
    r = simulate(s, ((1.0, 1.0, 1.0), EARLY), C, check=True)
    assert r.settle_tick == (0,)
    r2 = simulate(s, ((0.0, 0.0, 0.0), EARLY), C, check=True)
    assert r2.settle_tick == (-1,) and r2.missed_value == 60
    assert r2.cost[0] == pytest.approx(60 * (0.1 * 4 + 0.5 + 2.0))


def test_outage_bank_receives_but_does_not_send():
    s = scn(2, 4, (100, 100), [(0, 1, 50, 0, -1), (1, 0, 50, 0, -1)], outage=[(1, 0, 2)])
    r = simulate(s, (EARLY, EARLY), C, check=True)
    assert r.settle_tick == (0, 2)


def test_intratick_cascade():
    # 0 -> 1 -> 2 chain funded only by bank 0 settles within one tick
    s = scn(3, 2, (100, 100, 100), [(0, 1, 100, 0, -1), (1, 2, 100, 0, -1)])
    r = simulate(s, (EARLY, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), C, check=True)
    assert r.settle_tick == (0, 0)
    assert r.balances == (0, 0, 100)


@pytest.mark.parametrize("bad", [(1.1, 0, 0), (-0.01, 0, 0), (0.5, float("nan"), 0), (0.5, 0.5)])
def test_out_of_bounds_policy_rejected(bad):
    with pytest.raises(ValueError):
        validate_policy(bad)
    with pytest.raises(ValueError):
        simulate(TWO, (bad, EARLY), C)


unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
policy = st.tuples(unit, unit, unit)


@settings(max_examples=150, deadline=None)
@given(
    n=st.integers(2, 7),
    het=st.sampled_from([0.0, 0.75, 1.5]),
    fam=st.sampled_from(["base", "surge", "outage", "late_heavy", "hub"]),
    idx=st.integers(0, 10_000),
    data=st.data(),
)
def test_invariants_hold_for_arbitrary_policies(n, het, fam, idx, data):
    cfg = WorldConfig(n=n, T=12, payments_per_bank=8, heterogeneity=het)
    s = make_scenario(cfg, fam, "dev", idx)
    prof = tuple(data.draw(policy) for _ in range(n))
    r = simulate(s, prof, C, check=True)  # raises on any accounting violation
    assert sum(r.balances) == sum(r.liquidity)
    assert min(r.balances) >= 0
    settled = sum(p[2] for p, t in zip(s.pay, r.settle_tick) if t >= 0)
    assert settled + r.unsettled_value == r.total_value
    assert simulate(s, prof, C) == simulate(s, prof, C)  # deterministic replay


def test_scenario_and_result_are_immutable():
    r = simulate(TWO, (EARLY, EARLY), C)
    with pytest.raises(Exception):
        TWO.pay = ()
    with pytest.raises(Exception):
        r.cost = (0.0, 0.0)
