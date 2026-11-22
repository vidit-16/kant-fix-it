"""Report figures for the site, drawn as HTML from the stored result files.

Each figure is rows of dots (seed means) with 95 % bootstrap intervals, on an
axis that does not start at zero, so they are dots and intervals rather than
bars. A dashed line marks the optimum (or planner) where the study has one.
The matplotlib figures in runs/ stay the record; these only restyle them.
"""
import json
import math
from html import escape
from pathlib import Path

RUNS = Path(__file__).resolve().parent.parent.parent / "runs"

INK, BLUE, RED, GREY, REF = "#1d1c17", "#2456d6", "#d8361f", "#a9a69d", "#55534b"
CI_NOTE = "Dots are means over 20 seeds; lines are 95% bootstrap intervals. Lower cost is better."
CHOSEN = "* Level chosen on development data before the held-out test."


def load(name):
    return json.loads((RUNS / f"{name}.json").read_text(encoding="utf-8"))


def ticks(lo, hi, n=4):
    step = 10 ** math.floor(math.log10((hi - lo) / n))
    for m in (1, 2, 2.5, 5, 10):
        if (hi - lo) / (step * m) <= n:
            step *= m
            break
    t = math.ceil(lo / step) * step
    out = []
    while t <= hi + 1e-12:
        out.append(round(t, 10))
        t += step
    return out


def fmt(v, d):
    return f"{v:.{d}f}"


def panel(rows, title="", ref=None, xlabel="", digits=3, legend=None):
    """rows: [(label, [(mean, lo, hi, colour), ...])]; lo/hi may be None."""
    vals = [x for _, ser in rows for m, lo, hi, _ in ser for x in (m, lo, hi) if x is not None]
    if ref is not None:
        vals.append(ref)
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.08 or 0.01
    lo, hi = lo - pad, hi + pad
    pos = lambda v: (v - lo) / (hi - lo) * 100
    out = [f'<div class="panel">']
    if title:
        out.append(f"<h4>{title}</h4>")
    for label, ser in rows:
        k = len(ser)
        marks = []
        for j, (m, a, b, c) in enumerate(ser):
            y = 50 if k == 1 else 28 + 44 * j / (k - 1)
            if a is not None:
                marks.append(f'<i class="ci" style="left:{pos(a):.2f}%;width:{pos(b) - pos(a):.2f}%;top:{y:.0f}%;background:{c}"></i>')
            marks.append(f'<i class="pt" style="left:{pos(m):.2f}%;top:{y:.0f}%;background:{c}"></i>')
        refline = f'<i class="ref" style="left:{pos(ref):.2f}%"></i>' if ref is not None else ""
        vals_txt = "<br>".join(f'<span style="color:{c if c not in (GREY,) else REF}">{fmt(m, digits)}</span>' for m, _, _, c in ser)
        aria = "; ".join(f"{fmt(m, digits)}" + (f" ({fmt(a, digits)} to {fmt(b, digits)})" if a is not None else "") for m, a, b, _ in ser)
        out.append(f'<div class="drow" role="img" aria-label="{escape(label)}: {aria}"><span class="dl">{label}</span>'
                   f'<div class="dt">{refline}{"".join(marks)}</div><span class="dv">{vals_txt}</span></div>')
    tk = "".join(f'<i style="left:{pos(t):.2f}%">{t:g}</i>' for t in ticks(lo, hi))
    out.append(f'<div class="axis" aria-hidden="true"><span></span><div class="ticks">{tk}</div><span></span></div>')
    if xlabel:
        out.append(f'<p class="xlab">{xlabel}</p>')
    out.append("</div>")
    return "".join(out)


def legend(items):
    return '<div class="legend">' + "".join(
        f'<span><i style="background:{c}"></i>{t}</span>' if c else f'<span><i class="dash"></i>{t}</span>' for t, c in items) + "</div>"


def figure(title, body, notes, cls=""):
    return (f'<figure class="dots {cls}"><figcaption><b>{title}</b></figcaption>{body}'
            f'<p class="fnote">{" ".join(notes)}</p></figure>')


def C(arm):
    return tuple(arm["cost"])


# ---- E1: gates in the payment network ---------------------------------------------
def fig_gates():
    A = load("results")["E1_arms"]
    rows = [("private gate (κ = 0)", "k0", GREY), ("κ = 0.25", "k0.25", GREY), ("κ = 0.5", "k0.5", GREY),
            ("κ = 0.75", "k0.75", GREY), ("<b>Kantian gate (κ = 1)</b>", "k1", INK),
            ("welfare, unilateral", "welfare", GREY), ("welfare, joint", "welfare_universal", GREY),
            ("no-harm", "noharm", GREY)]
    rows += [(f"<b>delay surcharge, level {l}</b>", f"k0+fee{l}", BLUE) for l in (1, 2, 4, 8)]
    rows += [("planner", "planner", REF)]
    data = [(lab, [(*C(A[k]), c)]) for lab, k, c in rows]
    body = legend([("Kantian gate", INK), ("price on delay", BLUE), ("planner", None)])
    body += panel(data, ref=A["planner"]["cost"][0], xlabel="Held-out system cost per unit of payment value")
    return figure("Payment network: every acceptance gate against a plain delay surcharge (E1)", body, [CI_NOTE])


# ---- E8: richer policies ----------------------------------------------------------
def fig_e8():
    R = load("results_e8")
    A = R["arms"]
    arms = [("private gate", "k0"), ("<b>Kantian gate</b>", "k1"), ("welfare, unilateral", "welfare"),
            ("welfare, joint", "welfare_universal"), ("<b>delay surcharge*</b>", "fee*"), ("band tariff*", "tar*"),
            ("planner", "planner")]
    data = [(lab, [(*C(A[f"simple/{k}"]), INK), (*C(A[f"rich/{k}"]), BLUE)]) for lab, k in arms]
    body = legend([("three-parameter policies", INK), ("eight-parameter policies", BLUE)])
    body += panel(data, xlabel="Held-out system cost per unit of payment value")
    return figure("Payment network with richer, rule-level policies (E8)", body, [CI_NOTE, CHOSEN])


# ---- E9: the shared codebase -------------------------------------------------------
def fig_e9():
    R9 = load("results_e9")["regimes"]
    panels = []
    for gamma, name in ((0.25, "Concealment is cheap (γ = 0.25)"), (1.0, "Concealment is costly (γ = 1)")):
        R = R9[f"gamma={gamma:g},n=6"]
        ch = R["choice"]
        rows = [("private gate", "k0", GREY), ("<b>Kantian gate</b>", "k1", INK), ("welfare gate", "welfare", GREY),
                ("<b>proxy charge*</b>", f"proxy{ch['proxy']['chosen']:g}", RED),
                ("surface charge*", f"surface{ch['surface']['chosen']:g}", GREY),
                ("<b>ambient tax*</b>", f"ambient{ch['ambient']['chosen']:g}", BLUE), ("optimum", "planner", REF)]
        data = [(lab, [(*C(R["arms"][k]), c)]) for lab, k, c in rows]
        panels.append(panel(data, title=name, ref=R["arms"]["planner"]["cost"][0], digits=3,
                            xlabel="Held-out system cost"))
    body = legend([("Kantian gate", INK), ("tax on the damage", BLUE), ("charge on visible coupling", RED), ("optimum", None)])
    body += '<div class="panels">' + "".join(panels) + "</div>"
    return figure("Shared codebase, six agents (E9)", body, [CI_NOTE, CHOSEN])


# ---- E10: unequal exposure ---------------------------------------------------------
SKEWS = ("0", "0.75", "1.5")
SKEW_NAME = {"0": "Equal exposure (skew 0)", "0.75": "Some take more (skew 0.75)", "1.5": "One takes most (skew 1.5)"}


def fig_e10():
    S = load("results_e10")["skews"]
    panels = []
    for sk in SKEWS:
        R = S[sk]
        ch = R["choice"]
        rows = [("private gate", "k0", GREY), ("<b>Kantian gate</b>", "k1", INK),
                ("<b>ambient tax*</b>", f"ambient{ch['ambient']['chosen']:g}", BLUE),
                ("best budget-balanced*", ch["best_balanced"], RED), ("optimum", "planner_asym", REF)]
        data = [(lab, [(*C(R["arms"][k]), c)]) for lab, k, c in rows]
        panels.append(panel(data, title=SKEW_NAME[sk], ref=R["arms"]["planner_asym"]["cost"][0], xlabel="Held-out system cost"))
    R = S["1.5"]
    amb = f"ambient{R['choice']['ambient']['chosen']:g}"
    srows = []
    for i in range(6):
        srows.append((f"agent {i + 1}" + (" (most exposed)" if i == 0 else " (least exposed)" if i == 5 else ""),
                      [(R["arms"]["planner_asym"]["s_by_agent"][i], None, None, GREY),
                       (R["arms"]["k1"]["s_by_agent"][i], None, None, INK),
                       (R["arms"][amb]["s_by_agent"][i], None, None, BLUE)]))
    shortcut = (legend([("optimum", GREY), ("Kantian gate", INK), ("ambient tax*", BLUE)])
                + panel(srows, title="Who cuts corners, one takes most (skew 1.5)", digits=2,
                        xlabel="Shortcut intensity s (seed mean)"))
    body = legend([("Kantian gate", INK), ("ambient tax", BLUE), ("best budget-balanced charge", RED), ("optimum", None)])
    body += '<div class="panels three">' + "".join(panels) + "</div>"
    body += f'<div class="sub">{shortcut}</div>'
    return figure("Unequal exposure: cost by skew, and who restrains at the highest skew (E10)", body,
                  [CI_NOTE, CHOSEN, "The shortcut panel shows seed means only."])


# ---- E11: units of universalization ------------------------------------------------
def fig_e11():
    S = load("results_e11")["skews"]
    panels = []
    for sk in SKEWS:
        A = S[sk]["arms"]
        rows = [("Kantian, linear", "k1@linear", INK), ("Kantian, logit", "k1@logit", INK),
                ("Kantian, square root (faulty, §4.5)", "k1@sqrt", GREY), ("Kantian, log", "k1@log", RED),
                ("<b>ambient tax</b>", "ambient1", BLUE), ("optimum", "optimum", REF)]
        data = [(lab, [(*C(A[k]), c)]) for lab, k, c in rows]
        panels.append(panel(data, title=SKEW_NAME[sk], ref=A["optimum"]["cost"][0], xlabel="Held-out system cost"))
    body = legend([("Kantian gate, four scales", INK), ("log scale", RED), ("ambient tax", BLUE), ("optimum", None)])
    body += '<div class="panels three">' + "".join(panels) + "</div>"
    return figure("The Kantian gate on four scales of “the same change” (E11)", body, [CI_NOTE, "The square-root variant was implemented incorrectly (found by an independent review) and is shown in grey for the record only."])


FIGURES = {"gates": fig_gates, "e8": fig_e8, "e9": fig_e9, "e10": fig_e10, "e11": fig_e11}
