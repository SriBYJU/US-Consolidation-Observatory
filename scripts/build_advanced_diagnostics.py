from __future__ import annotations
import hashlib, json, platform, sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
PANEL=DATA/'bds_state_sector_panel.csv.gz'
FEATURES=['firms_per_1000_emp','estabs_entry_rate','estabs_exit_rate','net_job_creation_rate','reallocation_rate','log_firms','log_emp','lag_growth_2y_ann']

def sha256(path: Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def model():
    return Pipeline([
        ('imp',SimpleImputer(strategy='median')),
        ('model',HistGradientBoostingRegressor(max_depth=4,learning_rate=.055,max_iter=180,l2_regularization=1.0,random_state=42))
    ])

def frame():
    p=pd.read_csv(PANEL,dtype={'st':str,'sector':str})
    p['st']=p.st.str.zfill(2)
    base=p[['year','st','state_name','sector','sector_name','estabs','firms','emp','estabs_entry_rate','estabs_exit_rate','net_job_creation_rate','reallocation_rate','firms_per_1000_emp','structural_readiness_score']].copy()
    base['log_firms']=np.log1p(base.firms)
    base['log_emp']=np.log1p(base.emp)
    past=p[['year','st','sector','estabs']].copy(); past['year']+=2; past=past.rename(columns={'estabs':'estabs_t_minus_2'})
    future=p[['year','st','sector','estabs']].copy(); future['year']-=2; future=future.rename(columns={'estabs':'estabs_t_plus_2'})
    m=base.merge(past,on=['year','st','sector'],how='left').merge(future,on=['year','st','sector'],how='left')
    m=m[(m.estabs>0)&(m.estabs_t_minus_2>0)&(m.estabs_t_plus_2>0)].copy()
    m['lag_growth_2y_ann']=50*np.log(m.estabs/m.estabs_t_minus_2)
    m['future_growth_2y_ann']=50*np.log(m.estabs_t_plus_2/m.estabs)
    return m

def rank_metrics(actual,pred):
    actual=np.asarray(actual,float); pred=np.asarray(pred,float)
    q_pred=np.nanquantile(pred,.90); q_actual=np.nanquantile(actual,.90)
    top=pred>=q_pred
    return {
        'n':int(len(actual)),
        'mae_ann_log_pct':round(float(mean_absolute_error(actual,pred)),3),
        'spearman':round(float(spearmanr(actual,pred,nan_policy='omit').statistic),3),
        'top_decile_precision':round(float(np.mean(actual[top]>=q_actual)),3)
    }

def build_replay(m):
    # Replay needs only information at t and the realized t+2 establishment count; it does not require a t-2 lag.
    p=pd.read_csv(PANEL,dtype={'st':str,'sector':str}); p['st']=p.st.str.zfill(2)
    future=p[['year','st','sector','estabs']].copy(); future['year']-=2; future=future.rename(columns={'estabs':'estabs_t_plus_2'})
    x=p.merge(future,on=['year','st','sector'],how='left')
    x=x[(x.estabs>0)&(x.estabs_t_plus_2>0)&x.structural_readiness_score.notna()].copy()
    x['future_growth_2y_ann']=50*np.log(x.estabs_t_plus_2/x.estabs)
    x['srs_percentile_within_sector']=x.groupby(['year','sector'])['structural_readiness_score'].rank(pct=True)
    x['srs_top_quintile']=x.srs_percentile_within_sector>=.8
    annual=[]
    for y,g in x[x.year<=2021].groupby('year'):
        top=g[g.srs_top_quintile].future_growth_2y_ann
        rest=g[~g.srs_top_quintile].future_growth_2y_ann
        annual.append({
            'year':int(y),'n':int(len(g)),
            'top_quintile_mean_growth':round(float(top.mean()),3),
            'rest_mean_growth':round(float(rest.mean()),3),
            'uplift':round(float(top.mean()-rest.mean()),3),
            'spearman_srs_future_growth':round(float(spearmanr(g.structural_readiness_score,g.future_growth_2y_ann).statistic),3)
        })
    uplift=np.array([r['uplift'] for r in annual],float)
    summary={
        'cohort_years':f"{annual[0]['year']}–{annual[-1]['year']}",
        'cohorts':len(annual),
        'positive_uplift_cohorts':int(np.sum(uplift>0)),
        'mean_uplift_ann_log_pct':round(float(uplift.mean()),3),
        'median_uplift_ann_log_pct':round(float(np.median(uplift)),3),
        'interpretation':'Exploratory, post-hoc descriptive replay. SRS was not optimized against this outcome and this does not validate M&A forecasting.'
    }
    replay=x[(x.year>=2014)&(x.year<=2021)][['year','st','state_name','sector','sector_name','structural_readiness_score','future_growth_2y_ann','srs_percentile_within_sector','srs_top_quintile']].copy().round(3)
    replay=replay.where(pd.notna(replay),None)
    (DATA/'replay_2014_2021.json').write_text(json.dumps(replay.to_dict('records'),separators=(',',':')),encoding='utf-8')
    return summary,annual

def build_rolling(m):
    windows=[(2010,2012),(2013,2015),(2016,2018),(2019,2021)]
    rows=[]
    for start,end in windows:
        tr=m[(m.year>=1990)&(m.year<start)].copy()
        te=m[(m.year>=start)&(m.year<=end)].copy()
        pipe=model(); pipe.fit(tr[FEATURES],tr.future_growth_2y_ann)
        pred=pipe.predict(te[FEATURES]); base=te.lag_growth_2y_ann.to_numpy(); actual=te.future_growth_2y_ann.to_numpy()
        rows.append({'window':f'{start}–{end}','training':f'1990–{start-1}','model':'Histogram Gradient Boosting',**rank_metrics(actual,pred)})
        rows.append({'window':f'{start}–{end}','training':f'1990–{start-1}','model':'Persistence baseline',**rank_metrics(actual,base)})
    wins={'mae':0,'spearman':0,'top_decile_precision':0}
    for start,end in windows:
        w=f'{start}–{end}'; mm=next(r for r in rows if r['window']==w and r['model'].startswith('Histogram')); bb=next(r for r in rows if r['window']==w and r['model'].startswith('Persistence'))
        wins['mae']+=int(mm['mae_ann_log_pct']<bb['mae_ann_log_pct'])
        wins['spearman']+=int(mm['spearman']>bb['spearman'])
        wins['top_decile_precision']+=int(mm['top_decile_precision']>bb['top_decile_precision'])
    return {
        'protocol':'Post-hoc rolling-origin robustness check using the already-fixed v0.1 HGB hyperparameters. Each window trains only on prior years; this analysis is not used to rewrite the original locked holdout result.',
        'windows':rows,
        'wins_vs_persistence':wins,
        'window_count':len(windows)
    }

def build_feature_diagnostics(m):
    tr=m[(m.year>=1990)&(m.year<=2016)].copy(); va=m[(m.year>=2017)&(m.year<=2019)].copy()
    full=model(); full.fit(tr[FEATURES],tr.future_growth_2y_ann)
    base_mae=mean_absolute_error(va.future_growth_2y_ann,full.predict(va[FEATURES]))
    perm=permutation_importance(full,va[FEATURES],va.future_growth_2y_ann,n_repeats=20,random_state=42,scoring='neg_mean_absolute_error')
    importance=[]
    for f,mean,std in zip(FEATURES,perm.importances_mean,perm.importances_std):
        importance.append({'feature':f,'mae_increase_when_permuted':round(float(mean),4),'std':round(float(std),4)})
    importance.sort(key=lambda r:r['mae_increase_when_permuted'],reverse=True)
    ablations=[]
    for f in FEATURES:
        fs=[x for x in FEATURES if x!=f]; pipe=model(); pipe.fit(tr[fs],tr.future_growth_2y_ann)
        mae=mean_absolute_error(va.future_growth_2y_ann,pipe.predict(va[fs]))
        ablations.append({'removed_feature':f,'validation_mae':round(float(mae),4),'delta_vs_full':round(float(mae-base_mae),4)})
    ablations.sort(key=lambda r:r['delta_vs_full'],reverse=True)
    return {
        'split':'2017–2019 validation only',
        'full_model_validation_mae':round(float(base_mae),4),
        'permutation_importance':importance,
        'leave_one_feature_out':ablations,
        'warning':'Post-selection diagnostics only. They are not used to change the frozen v0.1 model after holdout inspection.'
    }

def build_repro_manifest():
    files=['scripts/build_research_assets.py','scripts/run_score_sensitivity.py','scripts/build_advanced_diagnostics.py','scripts/validate_release.py','index.html','assets/app-core.js','assets/app.js','assets/styles.css','research/model-card.md','research/hypothesis-registry.md','data/bds_state_sector_panel.csv.gz','data/model_validation.json','data/score_sensitivity_2023.json','data/research_diagnostics.json']
    hashes={p:sha256(ROOT/p) for p in files if (ROOT/p).exists()}
    packages={}
    for name in ['pandas','numpy','scikit-learn','scipy']:
        try: packages[name]=version(name)
        except PackageNotFoundError: packages[name]='unknown'
    source=json.loads((DATA/'source_manifest.json').read_text())
    out={
        'project':'U.S. Consolidation Observatory','release':'v0.2 technical platform','python':sys.version.split()[0],
        'platform':platform.platform(),'packages':packages,'source_sha256':source['sha256'],'file_sha256':hashes,
        'build_commands':['python scripts/build_research_assets.py','python scripts/run_score_sensitivity.py','python scripts/build_advanced_diagnostics.py','python scripts/validate_release.py'],
        'note':'Hashes fingerprint the exact scripts and derived artifacts used by this release. Git commit SHA should be added to immutable future forecasts once the repository exists.'
    }
    (DATA/'reproducibility_manifest.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

def main():
    m=frame()
    replay_summary,annual=build_replay(m)
    diagnostics={
        'version':'v0.2','target':'Two-year-ahead annualized log establishment growth (not M&A activity)',
        'descriptive_replay':{'summary':replay_summary,'annual':annual},
        'rolling_origin':build_rolling(m),
        'feature_diagnostics':build_feature_diagnostics(m)
    }
    (DATA/'research_diagnostics.json').write_text(json.dumps(diagnostics,indent=2),encoding='utf-8')
    build_repro_manifest()
    print(json.dumps({
        'replay':replay_summary,
        'rolling_wins':diagnostics['rolling_origin']['wins_vs_persistence'],
        'top_features':diagnostics['feature_diagnostics']['permutation_importance'][:3]
    },indent=2))

if __name__=='__main__': main()
