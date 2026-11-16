import json, sys, collections, numpy as np
R=[json.loads(l) for l in open(sys.argv[1])]
g=collections.defaultdict(list)
for r in R:
    lab=r['gate'] if r['gate']!='kappa' else f"k{r['kappa']}"
    if r.get('fee'): lab+=f"+fee{r['fee']}"
    g[(r['exp'],r['delay_day'],r['n'],r['het'],lab)].append(r)
for key in sorted(g):
    rs=g[key]; b=[r['eval']['base'] for r in rs]
    P=np.array([r['profile'] for r in rs])
    print(key,'n=%d'%len(rs),'sys=%.3f sd=%.3f'%(np.mean([x['system_cost'] for x in b]),np.std([x['system_cost'] for x in b])),
      'liq=%.2f delay=%.2f unset=%.3f'%tuple(np.mean([x[k] for x in b]) for k in ('liquidity','delay_ticks','unsettled')),
      'theta=',P.mean(axis=(0,1)).round(2),'liq spread within run=%.2f'%P[:,:,0].std(axis=1).mean())
