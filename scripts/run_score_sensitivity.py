from pathlib import Path
import json, numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data/latest_2023.json').read_text())
df=pd.DataFrame(rows)
# Reconstruct component percentiles directly from 2023 panel, sector by sector.
components=['firms_per_1000_emp','estabs_entry_rate','net_job_creation_rate','firms','estabs_exit_rate','reallocation_rate']
for c in components: df[c]=pd.to_numeric(df[c],errors='coerce')
for c in ['firms_per_1000_emp','estabs_entry_rate','net_job_creation_rate','firms','reallocation_rate']:
    df[c+'_p']=df.groupby('sector')[c].rank(pct=True)*100
df['stability_p']=100-df.groupby('sector')['estabs_exit_rate'].rank(pct=True)*100
cols=['firms_per_1000_emp_p','estabs_entry_rate_p','net_job_creation_rate_p','firms_p','stability_p','reallocation_rate_p']
base=np.array([.25,.20,.20,.15,.10,.10])
rng=np.random.default_rng(42)
valid=df[cols].notna().all(axis=1)
X=df.loc[valid,cols].to_numpy(float)
keys=df.loc[valid,['st','state_name','sector','sector_name','structural_readiness_score']].reset_index(drop=True)
# 1,000 plausible weight perturbations around the declared design; weights remain positive and sum to one.
draws=[]
for _ in range(1000):
    jitter=rng.lognormal(mean=0,sigma=.22,size=len(base)); w=base*jitter; w=w/w.sum(); draws.append(w)
W=np.array(draws)
S=X@W.T
out=[]
for i,row in keys.iterrows():
    vals=S[i]
    # probability of being in top quintile within its sector for each draw
    sector_mask=(keys.sector==row.sector).to_numpy()
    sector_scores=S[sector_mask]
    ranks=(sector_scores<=vals).mean(axis=0)
    out.append({'st':row.st,'state_name':row.state_name,'sector':row.sector,'sector_name':row.sector_name,'base_score':round(float(row.structural_readiness_score),3),'score_p05':round(float(np.quantile(vals,.05)),3),'score_median':round(float(np.median(vals)),3),'score_p95':round(float(np.quantile(vals,.95)),3),'probability_top_quintile':round(float(np.mean(ranks>=.8)),3)})
(ROOT/'data/score_sensitivity_2023.json').write_text(json.dumps(out,indent=2))
print('sensitivity rows',len(out),'draws',len(W))
