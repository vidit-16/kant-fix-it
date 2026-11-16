import ast
from pathlib import Path

import pytest

from evortgs.evolve import EvoConfig, evolve
from evortgs.scenarios import FAMILIES, DevSampler, WorldConfig, holdout_set, make_scenario
from evortgs.sim import Costs

CFG = WorldConfig(n=4, T=10, payments_per_bank=6)
C = Costs()
SRC = Path(__file__).resolve().parents[1] / "src" / "evortgs"


def test_dev_and_holdout_streams_are_disjoint():
    dev = {make_scenario(CFG, "base", "dev", i).pay for i in range(300)}
    hold = {s.pay for f in FAMILIES for s in holdout_set(CFG, f, 100)}
    assert dev.isdisjoint(hold)


def test_dev_sampler_refuses_holdout():
    with pytest.raises(ValueError):
        DevSampler(CFG, split="holdout")


def test_evolution_module_cannot_reach_holdout_or_evaluator():
    tree = ast.parse((SRC / "evolve.py").read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module != "evaluate" and "evaluate" not in (node.module or "")
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
    assert "holdout_set" not in names and "make_scenario" not in names
    assert "holdout" not in (SRC / "evolve.py").read_text(encoding="utf-8")


def test_evolution_is_reproducible_and_seed_sensitive():
    e = EvoConfig(generations=3, K=2, M=2)
    a = evolve(DevSampler(CFG), C, e, seed=5)
    b = evolve(DevSampler(CFG), C, e, seed=5)
    c = evolve(DevSampler(CFG), C, e, seed=6)
    assert a.profile == b.profile and a.history == b.history
    assert a.profile != c.profile


@pytest.mark.parametrize("gate,kappa", [("kappa", 0.0), ("kappa", 0.5), ("kappa", 1.0),
                                        ("welfare", 0.0), ("noharm", 0.0)])
def test_all_gates_spend_the_same_simulation_budget(gate, kappa):
    e = EvoConfig(generations=3, K=2, M=2, gate=gate, kappa=kappa)
    r = evolve(DevSampler(CFG), C, e, seed=1)
    S = 2 * e.M
    assert r.sims == e.generations * (S + CFG.n * e.K * S)
    for p in r.profile:
        assert all(0.0 <= x <= 1.0 for x in p)


def test_gates_share_initial_profile_and_scenarios_for_a_seed():
    e0 = EvoConfig(generations=1, K=1, M=2, kappa=0.0)
    e1 = EvoConfig(generations=1, K=1, M=2, kappa=1.0)
    a = evolve(DevSampler(CFG), C, e0, seed=3)
    b = evolve(DevSampler(CFG), C, e1, seed=3)
    assert a.history[0]["profile"] == b.history[0]["profile"]
    assert a.history[0]["dev_system_cost"] == b.history[0]["dev_system_cost"]
