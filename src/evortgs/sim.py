"""Deterministic stylized RTGS settlement engine.

This module is the accounting source of truth. Policies only supply bounded
numbers per bank (three, or eight for the rule-level form); they never touch
balances, payments or costs.

Model
-----
* ``n`` banks, one currency, integer money, ``T`` ticks in a day.
* Bank ``i`` opens the day with posted liquidity ``L_i = round(liq_i * E_i)``
  where ``E_i`` is its expected gross daily outflow. No intraday credit: a
  payment settles only if the sender's balance covers it in full.
* Payments are (sender, receiver, amount, arrival, deadline). ``deadline < 0``
  marks an ordinary payment; otherwise it is time-critical.
* Release rule. Time-critical payments are released on arrival. An ordinary
  payment is released once it has been held ``round(hold_i * (T-1))`` ticks and
  settling it leaves at least ``buf_i * L_i`` on the account. In the last tick
  every queued payment is released and the buffer is waived.
* Within a tick, banks are visited in a rotating order and passes repeat until
  no payment settles, so incoming funds can be recycled inside the tick.
* A bank inside an outage window receives funds but sends nothing.

Rule-level policy (eight numbers in [0, 1]); the three-number policy
``(liq, buf, hold)`` is the special case ``(liq, buf, buf, hold, 0, ., hold, 1)``:

  0 ``liq``       opening liquidity fraction
  1 ``buf_am``    buffer fraction before tick ``T // 2``
  2 ``buf_pm``    buffer fraction from tick ``T // 2``
  3 ``hold``      hold time for ordinary payments up to the size threshold
  4 ``open``      no ordinary payment is released before tick ``round(open*(T-1))``
  5 ``big``       size threshold ``250 * 40**big``; amounts above it are "large"
  6 ``hold_big``  hold time for large ordinary payments
  7 ``bilat``     bilateral limit: an ordinary payment to ``j`` is released only
                  if (sent to j - received from j) stays within
                  ``bilat/(1-bilat) * E_i/(n-1)``; 1 means no limit

Time-critical payments ignore all of these, and the last tick waives them.

Costs charged to the sender (all proportional to value)
* liquidity: ``cL * L_i``
* delay: ``cD * amount * ticks_waited`` (a payment unsettled at close waited
  until ``T``)
* deadline miss: ``cX * amount`` for a time-critical payment late or unsettled
* end of day: ``cE * amount`` for every payment unsettled at close

Conservation: with no credit, fees or injections, ``sum(balances) == sum(L)``
after every settlement, and no balance is ever negative.
"""

from __future__ import annotations

from dataclasses import dataclass

Policy = tuple[float, ...]  # 3 numbers (liq, buf, hold) or 8 (rule-level), each in [0, 1]
RICH_DIM = 8
BIG_BASE, BIG_RANGE = 250.0, 40.0
Profile = tuple[Policy, ...]


@dataclass(frozen=True)
class Costs:
    cL: float = 1.0   # per unit of opening liquidity, per day
    cD: float = 0.05  # per unit of value, per tick of delay
    cX: float = 2.0   # per unit of time-critical value that misses its deadline
    cE: float = 10.0  # per unit of value unsettled at close


@dataclass(frozen=True)
class Scenario:
    n: int
    T: int
    exp_out: tuple[int, ...]
    # (sender, receiver, amount, arrival, deadline); deadline -1 = ordinary
    pay: tuple[tuple[int, int, int, int, int], ...]
    arrivals: tuple[tuple[int, ...], ...]  # payment indices arriving at each tick
    outage: tuple[tuple[int, int, int], ...] = ()  # (bank, first_tick, end_tick)


@dataclass(frozen=True)
class Result:
    cost: tuple[float, ...]        # real cost per bank
    delay_cost: tuple[float, ...]  # the delay component of ``cost``
    liquidity: tuple[int, ...]
    balances: tuple[int, ...]
    settle_tick: tuple[int, ...]   # -1 if unsettled at close
    total_value: int
    unsettled_value: int
    delay_value_ticks: int
    missed_value: int
    # per bank: value settled at or after tick T // 2, or not settled at all
    late_value: tuple[int, ...] = ()

    @property
    def system_cost(self) -> float:
        return sum(self.cost)


class InvariantViolation(AssertionError):
    pass


def validate_policy(p: Policy) -> None:
    if len(p) not in (3, RICH_DIM):
        raise ValueError("policy must have three or eight parameters")
    for x in p:
        if not isinstance(x, (int, float)) or x != x or not (0.0 <= x <= 1.0):
            raise ValueError(f"policy parameter out of bounds: {x!r}")


def simulate(scn: Scenario, profile: Profile, costs: Costs, check: bool = False) -> Result:
    n, T, pay = scn.n, scn.T, scn.pay
    if len(profile) != n:
        raise ValueError("profile length must equal number of banks")
    for p in profile:
        validate_policy(p)

    L = [int(round(profile[i][0] * scn.exp_out[i])) for i in range(n)]
    half = T // 2
    inf = float("inf")
    buf_am, buf_pm, hold, hold_big, open_t, thr, limit = [], [], [], [], [], [], []
    rich = False
    for i, p in enumerate(profile):
        if len(p) == 3:
            buf_am.append(p[1] * L[i])
            buf_pm.append(p[1] * L[i])
            h = int(round(p[2] * (T - 1)))
            hold.append(h)
            hold_big.append(h)
            open_t.append(0)
            thr.append(inf)
            limit.append(inf)
        else:
            rich = True
            buf_am.append(p[1] * L[i])
            buf_pm.append(p[2] * L[i])
            hold.append(int(round(p[3] * (T - 1))))
            open_t.append(int(round(p[4] * (T - 1))))
            thr.append(BIG_BASE * BIG_RANGE ** p[5])
            hold_big.append(int(round(p[6] * (T - 1))))
            limit.append(inf if p[7] >= 1.0
                         else p[7] / (1.0 - p[7]) * scn.exp_out[i] / max(1, n - 1))
    net = [[0] * n for _ in range(n)] if rich else None  # sent i->j minus received from j
    bal = L[:]
    total_liq = sum(L)
    queues: list[list[int]] = [[] for _ in range(n)]
    settle = [-1] * len(pay)
    out_lo = [0] * n
    out_hi = [0] * n
    for b, lo, hi in scn.outage:
        out_lo[b], out_hi[b] = lo, hi

    def qkey(k: int):
        _, _, _, arr, dl = pay[k]
        return (0, dl, k) if dl >= 0 else (1, arr, k)

    for t in range(T):
        new = scn.arrivals[t]
        if new:
            touched = set()
            for k in new:
                s = pay[k][0]
                queues[s].append(k)
                touched.add(s)
            for s in touched:
                queues[s].sort(key=qkey)
        last = t == T - 1
        progress = True
        while progress:
            progress = False
            for off in range(n):
                i = (t + off) % n
                q = queues[i]
                if not q or out_lo[i] <= t < out_hi[i]:
                    continue
                b = bal[i]
                floor = 0.0 if last else (buf_am[i] if t < half else buf_pm[i])
                h, hb, th = hold[i], hold_big[i], thr[i]
                opened = t >= open_t[i]
                lim = limit[i]
                ni = net[i] if rich else None
                keep = []
                for k in q:
                    _, r, a, arr, dl = pay[k]
                    if dl >= 0 or last:
                        ok = a <= b
                    else:
                        ok = (opened and t >= arr + (hb if a > th else h)
                              and (b - a >= floor) and a <= b
                              and (lim == inf or ni[r] + a <= lim))
                    if ok:
                        b -= a
                        bal[r] += a
                        if rich:
                            ni[r] += a
                            net[r][i] -= a
                        if check and settle[k] != -1:
                            raise InvariantViolation("duplicate settlement")
                        settle[k] = t
                        progress = True
                    else:
                        keep.append(k)
                bal[i] = b
                queues[i] = keep
            if check:
                if sum(bal) != total_liq:
                    raise InvariantViolation("value not conserved")
                if min(bal) < 0:
                    raise InvariantViolation("negative balance")

    cost = [costs.cL * L[i] for i in range(n)]
    dcost = [0.0] * n
    total = unsettled = dvt = missed = 0
    late = [0] * n
    for k, (s, _r, a, arr, dl) in enumerate(pay):
        total += a
        st = settle[k]
        if st < 0:
            unsettled += a
            cost[s] += costs.cE * a
            waited = T - arr
        else:
            waited = st - arr
        if st < 0 or st >= half:
            late[s] += a
        if waited:
            dvt += a * waited
            d = costs.cD * a * waited
            dcost[s] += d
            cost[s] += d
        if dl >= 0 and (st < 0 or st > dl):
            missed += a
            cost[s] += costs.cX * a

    if check:
        queued = sorted(k for q in queues for k in q)
        open_ = [k for k, st in enumerate(settle) if st < 0]
        if queued != open_:
            raise InvariantViolation("queue and ledger disagree on open payments")
        for k, st in enumerate(settle):
            if st >= 0 and st < pay[k][3]:
                raise InvariantViolation("payment settled before arrival")
        # replay the ledger independently from the settlement log
        rb = L[:]
        for s, r, a, _arr, _dl in (pay[k] for k, st in enumerate(settle) if st >= 0):
            rb[s] -= a
            rb[r] += a
        if rb != bal:
            raise InvariantViolation("ledger replay mismatch")

    return Result(
        cost=tuple(cost),
        delay_cost=tuple(dcost),
        liquidity=tuple(L),
        balances=tuple(bal),
        settle_tick=tuple(settle),
        total_value=total,
        unsettled_value=unsettled,
        delay_value_ticks=dvt,
        missed_value=missed,
        late_value=tuple(late),
    )
