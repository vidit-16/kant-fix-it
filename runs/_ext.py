import numpy as np
from evortgs.scenarios import WorldConfig, make_scenario
from evortgs.sim import Costs, simulate
w=WorldConfig(); S=[make_scenario(w,"base","pilot",5000+i) for i in range(150)]
def ev(prof,c):
    R=np.array([simulate(s,prof,c).cost for s in S])/np.mean([sum(p[2] for p in s.pay) for s in S])
    return R.mean(axis=0)
for d,cE in ((0.5,10.0),(2.0,10.0),(6.0,10.0)):
    c=Costs(cL=1.0,cD=d/20,cX=2.0 if cE>5 else 0.5,cE=cE)
    # symmetric optimum over liq with buf=0,hold=0
    best=min(((sum(ev(tuple((l,0.0,0.0) for _ in range(6)),c)),l) for l in np.arange(0.0,1.01,0.05)))
    l0=best[1]; base=ev(tuple((l0,0.0,0.0) for _ in range(6)),c)
    print(f"d={d} cE={cE}: symmetric optimum liq={l0:.2f} sys={best[0]:.4f} own={base[0]:.4f}")
    for l in (l0-0.2,l0-0.1,l0-0.05,l0+0.05,l0+0.1):
        if l<0: continue
        for hold in (0.0,0.15):
            x=ev(((l,0.0,hold),)+tuple((l0,0.0,0.0) for _ in range(5)),c)
            print(f"   dev liq={l:.2f} hold={hold}: d_own={x[0]-base[0]:+.4f} d_others={x[1:].sum()-base[1:].sum():+.4f} d_sys={x.sum()-base.sum():+.4f}")
