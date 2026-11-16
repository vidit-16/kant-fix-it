"""Symmetric Nash vs planner on the liquidity dimension (buf=0, hold=0)."""
import sys, numpy as np, multiprocessing as mp
from evortgs.scenarios import WorldConfig, make_scenario
from evortgs.sim import Costs, simulate
GRID=np.round(np.arange(0.0,1.001,0.05),2)
def job(a):
    d,cE,ppb,n=a
    w=WorldConfig(n=n,payments_per_bank=ppb); S=[make_scenario(w,"base","pilot",7000+i) for i in range(120)]
    V=np.mean([sum(p[2] for p in s.pay) for s in S]); c=Costs(1.0,d/20,2.0,cE)
    def ev(prof): return (np.array([simulate(s,prof,c).cost for s in S])/V).mean(axis=0)
    sym={x:ev(tuple((x,0.,0.) for _ in range(n))) for x in GRID}
    opt=min(GRID,key=lambda x:sym[x].sum())
    x=opt; path=[x]
    for _ in range(8):
        br=min(GRID,key=lambda l:ev(((l,0.,0.),)+tuple((x,0.,0.) for _ in range(n-1)))[0])
        if br==x: break
        x=br; path.append(x)
    return a,opt,sym[opt].sum(),x,sym[x].sum(),path
if __name__=="__main__":
    jobs=[(d,cE,ppb,6) for d in (0.1,0.5,2.0) for cE in (3.0,10.0) for ppb in (20,60)]
    with mp.Pool() as p:
        for a,opt,so,x,sx,path in p.map(job,jobs):
            print(f"d={a[0]} cE={a[1]} ppb={a[2]}: planner liq={opt} sys={so:.4f} | BR path {path} -> sys={sx:.4f}  PoA={sx/so:.3f}")
