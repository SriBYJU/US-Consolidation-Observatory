from __future__ import annotations
import hashlib, json, math, os, shutil
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('BDS_SOURCE', '/mnt/data/bds2023_st_sec.csv'))
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)

STATES = {
'01':'Alabama','02':'Alaska','04':'Arizona','05':'Arkansas','06':'California','08':'Colorado','09':'Connecticut','10':'Delaware','11':'District of Columbia','12':'Florida','13':'Georgia','15':'Hawaii','16':'Idaho','17':'Illinois','18':'Indiana','19':'Iowa','20':'Kansas','21':'Kentucky','22':'Louisiana','23':'Maine','24':'Maryland','25':'Massachusetts','26':'Michigan','27':'Minnesota','28':'Mississippi','29':'Missouri','30':'Montana','31':'Nebraska','32':'Nevada','33':'New Hampshire','34':'New Jersey','35':'New Mexico','36':'New York','37':'North Carolina','38':'North Dakota','39':'Ohio','40':'Oklahoma','41':'Oregon','42':'Pennsylvania','44':'Rhode Island','45':'South Carolina','46':'South Dakota','47':'Tennessee','48':'Texas','49':'Utah','50':'Vermont','51':'Virginia','53':'Washington','54':'West Virginia','55':'Wisconsin','56':'Wyoming'}
SECTORS = {
'11':'Agriculture, forestry, fishing & hunting','21':'Mining, quarrying, oil & gas extraction','22':'Utilities','23':'Construction','31-33':'Manufacturing','42':'Wholesale trade','44-45':'Retail trade','48-49':'Transportation & warehousing','51':'Information','52':'Finance & insurance','53':'Real estate, rental & leasing','54':'Professional, scientific & technical services','55':'Management of companies & enterprises','56':'Administrative, support, waste management & remediation','61':'Educational services','62':'Health care & social assistance','71':'Arts, entertainment & recreation','72':'Accommodation & food services','81':'Other services (except public administration)'}
NUMERIC = ['firms','estabs','emp','denom','estabs_entry','estabs_entry_rate','estabs_exit','estabs_exit_rate','job_creation','job_creation_births','job_creation_continuers','job_creation_rate_births','job_creation_rate','job_destruction','job_destruction_deaths','job_destruction_continuers','job_destruction_rate_deaths','job_destruction_rate','net_job_creation','net_job_creation_rate','reallocation_rate','firmdeath_firms','firmdeath_estabs','firmdeath_emp']

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def pct_rank(s: pd.Series) -> pd.Series:
    return s.rank(pct=True, method='average') * 100

def clean():
    df = pd.read_csv(RAW, dtype={'st':str,'sector':str})
    df['st'] = df['st'].str.zfill(2)
    df['year'] = pd.to_numeric(df['year'], errors='raise').astype(int)
    for c in NUMERIC:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['state_name'] = df['st'].map(STATES)
    df['sector_name'] = df['sector'].map(SECTORS)
    if df['state_name'].isna().any() or df['sector_name'].isna().any():
        raise ValueError('Unmapped state or sector code detected')
    if df.duplicated(['year','st','sector']).any():
        raise ValueError('Duplicate year-state-sector key')

    df['firms_per_1000_emp'] = np.where(df.emp > 0, 1000*df.firms/df.emp, np.nan)
    df['employees_per_firm'] = np.where(df.firms > 0, df.emp/df.firms, np.nan)
    df['estabs_per_firm'] = np.where(df.firms > 0, df.estabs/df.firms, np.nan)
    df['log_firms'] = np.log1p(df['firms'])
    df['log_emp'] = np.log1p(df['emp'])
    df['log_estabs'] = np.log1p(df['estabs'])

    # Transparent exploratory structural score. Percentiles are computed only within the same year+sector.
    g = df.groupby(['year','sector'], group_keys=False)
    df['fragmentation_pct'] = g['firms_per_1000_emp'].transform(pct_rank)
    df['entry_pct'] = g['estabs_entry_rate'].transform(pct_rank)
    df['momentum_pct'] = g['net_job_creation_rate'].transform(pct_rank)
    df['scale_pct'] = g['log_firms'].transform(pct_rank)
    df['exit_pct'] = g['estabs_exit_rate'].transform(pct_rank)
    df['dynamism_pct'] = g['reallocation_rate'].transform(pct_rank)
    df['stability_pct'] = 100 - df['exit_pct']
    score_cols = ['fragmentation_pct','entry_pct','momentum_pct','scale_pct','stability_pct','dynamism_pct']
    weights = {'fragmentation_pct':.25,'entry_pct':.20,'momentum_pct':.20,'scale_pct':.15,'stability_pct':.10,'dynamism_pct':.10}
    weighted = sum(df[c]*w for c,w in weights.items())
    df['structural_readiness_score'] = weighted
    df['score_data_completeness'] = df[score_cols].notna().mean(axis=1)*100
    df.loc[df['score_data_completeness'] < 100, 'structural_readiness_score'] = np.nan
    return df

def validate_future_growth(df):
    base = df[['year','st','sector','estabs','firms','emp','estabs_entry_rate','estabs_exit_rate','net_job_creation_rate','reallocation_rate','firms_per_1000_emp','log_firms','log_emp']].copy()
    # Lagged 2-year establishment growth is a simple persistence baseline.
    past = df[['year','st','sector','estabs']].copy(); past['year'] += 2; past = past.rename(columns={'estabs':'estabs_t_minus_2'})
    future = df[['year','st','sector','estabs']].copy(); future['year'] -= 2; future = future.rename(columns={'estabs':'estabs_t_plus_2'})
    m = base.merge(past,on=['year','st','sector'],how='left').merge(future,on=['year','st','sector'],how='left')
    m = m[(m.estabs>0)&(m.estabs_t_minus_2>0)&(m.estabs_t_plus_2>0)].copy()
    m['lag_growth_2y_ann'] = 50*np.log(m.estabs/m.estabs_t_minus_2)
    m['future_growth_2y_ann'] = 50*np.log(m.estabs_t_plus_2/m.estabs)
    features=['firms_per_1000_emp','estabs_entry_rate','estabs_exit_rate','net_job_creation_rate','reallocation_rate','log_firms','log_emp','lag_growth_2y_ann']
    m = m.dropna(subset=['future_growth_2y_ann'])
    train=m[(m.year>=1990)&(m.year<=2016)].copy()
    valid=m[(m.year>=2017)&(m.year<=2019)].copy()
    test=m[(m.year>=2020)&(m.year<=2021)].copy()
    Xtr, ytr=train[features], train.future_growth_2y_ann
    models={
      'Ridge': Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler()),('model',Ridge(alpha=5.0))]),
      'Histogram Gradient Boosting': Pipeline([('imp',SimpleImputer(strategy='median')),('model',HistGradientBoostingRegressor(max_depth=4,learning_rate=.055,max_iter=180,l2_regularization=1.0,random_state=42))])
    }
    rows=[]
    def metrics(name, frame, pred, split):
        actual=frame.future_growth_2y_ann.to_numpy()
        mae=float(mean_absolute_error(actual,pred))
        spr=float(spearmanr(actual,pred,nan_policy='omit').statistic)
        q_pred=np.nanquantile(pred,.90); q_actual=np.nanquantile(actual,.90)
        top=pred>=q_pred
        precision=float(np.mean(actual[top]>=q_actual)) if top.any() else float('nan')
        return {'model':name,'split':split,'n':int(len(frame)),'mae_ann_log_pct':round(mae,3),'spearman':round(spr,3),'top_decile_precision':round(precision,3)}
    for split,frame in [('validation',valid),('holdout',test)]:
        pred=frame.lag_growth_2y_ann.to_numpy()
        rows.append(metrics('Persistence baseline',frame,pred,split))
    best=None
    for name,pipe in models.items():
        pipe.fit(Xtr,ytr)
        for split,frame in [('validation',valid),('holdout',test)]:
            pred=pipe.predict(frame[features])
            rows.append(metrics(name,frame,pred,split))
        v=[r for r in rows if r['model']==name and r['split']=='validation'][0]
        if best is None or v['mae_ann_log_pct']<best[0]: best=(v['mae_ann_log_pct'],name,pipe)
    # Model choice is made on validation only, then report holdout once.
    chosen=best[1]
    hold=[r for r in rows if r['model']==chosen and r['split']=='holdout'][0]
    # Segment error analysis for chosen model on holdout.
    pred=best[2].predict(test[features]); t=test[['sector','future_growth_2y_ann']].copy(); t['pred']=pred; t['abs_err']=abs(t.future_growth_2y_ann-t.pred)
    seg=t.groupby('sector').agg(n=('abs_err','size'),mae=('abs_err','mean')).reset_index()
    seg['sector_name']=seg.sector.map(SECTORS); seg=seg.sort_values('mae',ascending=False)
    out={
      'target':'Two-year-ahead annualized log establishment growth (not M&A activity)',
      'train_years':'1990–2016','validation_years':'2017–2019','holdout_feature_years':'2020–2021 (targets fall in 2022–2023)',
      'features':features,'model_selection_rule':'Lowest validation MAE; holdout not used for selection',
      'metrics':rows,'selected_model':chosen,'selected_holdout':hold,
      'segment_error_top5':[{**r,'mae':round(r['mae'],3)} for r in seg.head(5).to_dict('records')],
      'warning':'This validates the point-in-time modeling pipeline against future establishment growth only. It does not validate acquisition or investment-return forecasting.'
    }
    return out

def main():
    df=clean()
    validation=validate_future_growth(df)
    cols=['year','st','state_name','sector','sector_name','firms','estabs','emp','estabs_entry_rate','estabs_exit_rate','net_job_creation_rate','reallocation_rate','firms_per_1000_emp','employees_per_firm','structural_readiness_score','score_data_completeness']
    full=df[cols].copy()
    full.to_csv(DATA/'bds_state_sector_panel.csv.gz',index=False,compression='gzip')
    browser=full[full.year>=2014].copy().round(3)
    browser=browser.where(pd.notna(browser),None)
    (DATA/'panel_2014_2023.json').write_text(json.dumps(browser.to_dict('records'),separators=(',',':')),encoding='utf-8')
    latest=full[full.year==2023].copy().sort_values('structural_readiness_score',ascending=False).round(3)
    latest=latest.where(pd.notna(latest),None)
    (DATA/'latest_2023.json').write_text(json.dumps(latest.to_dict('records'),separators=(',',':')),encoding='utf-8')
    (DATA/'model_validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    source={
      'dataset':'U.S. Census Bureau 2023 Business Dynamics Statistics — State by Sector',
      'source_url':'https://www2.census.gov/programs-surveys/bds/tables/time-series/2023/bds2023_st_sec.csv',
      'landing_url':'https://www.census.gov/data/datasets/time-series/econ/bds/bds-datasets.html',
      'sha256':sha256(RAW),'raw_bytes':RAW.stat().st_size,'rows':int(len(df)),'min_year':int(df.year.min()),'max_year':int(df.year.max()),
      'states_and_dc':int(df.st.nunique()),'sectors':int(df.sector.nunique()),'duplicate_key_rows':int(df.duplicated(['year','st','sector']).sum()),
      'suppression_note':'Census suppression/non-numeric codes are converted to missing values, never to zero.'
    }
    (DATA/'source_manifest.json').write_text(json.dumps(source,indent=2),encoding='utf-8')
    meta={
      'project':'U.S. Consolidation Observatory','build_data_release':'BDS 2023','panel_rows':len(df),'jurisdictions':df.st.nunique(),'sectors':df.sector.nunique(),'years':f'{df.year.min()}–{df.year.max()}',
      'latest_year':2023,
      'qcew_2024':{'establishments':12057371,'employment':154990441,'wages':11714940541109,'source':'https://www.bls.gov/cew/publications/employment-and-wages-annual-averages/2024/chart-data.htm'},
      'bea_q1_2026':{'states_plus_dc_growth':47,'highest':'Washington +4.5%','lowest':'South Dakota −1.6%','release':'June 25, 2026','source':'https://www.bea.gov/data/gdp/gdp-state'},
      'score_name':'Structural Readiness Score (exploratory)','score_weights':{'Fragmentation proxy':25,'Establishment entry':20,'Net job creation momentum':20,'Firm scale':15,'Establishment stability':10,'Labor reallocation/dynamism':10},
      'score_disclaimer':'Exploratory structural summary only. It is not a validated M&A forecast, company valuation, investment recommendation, or prediction of returns.'
    }
    (DATA/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps({'rows':len(df),'browser_rows':len(browser),'source_sha256':source['sha256'],'validation':validation['selected_holdout']},indent=2))
if __name__=='__main__': main()
