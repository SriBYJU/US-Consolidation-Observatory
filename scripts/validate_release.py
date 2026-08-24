from pathlib import Path
from html.parser import HTMLParser
import csv, gzip, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, cond, detail=''):
    ok=bool(cond); checks.append((name,ok,detail)); print(('PASS' if ok else 'FAIL'),'-',name,(f'— {detail}' if detail else '')); return ok

required=[
'index.html','assets/styles.css','assets/app.js','README.md','LICENSE','requirements.txt','MASTER_CHECKLIST.md','RESEARCH_MILESTONES.md',
'data/bds_state_sector_panel.csv.gz','data/panel_2014_2023.json','data/latest_2023.json','data/metadata.json','data/model_validation.json','data/source_manifest.json','data/score_sensitivity_2023.json','data/research_diagnostics.json','data/replay_2014_2021.json','data/reproducibility_manifest.json','data/forecast_ledger.json','data/transaction_events_template.csv','data/ai_extraction_benchmark_template.csv',
'research/methodology.md','research/data-dictionary.md','research/limitations.md','research/forecast-protocol.md','research/transaction-schema.md','research/ai-benchmark-protocol.md','research/reviewer-response-log.md','research/model-card.md','research/hypothesis-registry.md','research/reproducibility.md','research/technical-paper.md','research/practitioner-report.md','scripts/build_advanced_diagnostics.py','.github/workflows/validate.yml'
]
check('All required release files exist', all((ROOT/p).exists() for p in required), f'{sum((ROOT/p).exists() for p in required)}/{len(required)}')

# Full derived panel checks
with gzip.open(ROOT/'data/bds_state_sector_panel.csv.gz','rt',newline='') as f:
    rows=list(csv.DictReader(f))
check('Panel row count matches official State × Sector release',len(rows)==44574,str(len(rows)))
keys=[(r['year'],r['st'],r['sector']) for r in rows]
check('Panel key is unique',len(keys)==len(set(keys)))
years={int(r['year']) for r in rows}; states={r['st'] for r in rows}; sectors={r['sector'] for r in rows}
check('Panel covers 1978–2023',min(years)==1978 and max(years)==2023 and len(years)==46,f'{min(years)}–{max(years)}')
check('Panel covers 50 states + District of Columbia',len(states)==51,str(len(states)))
check('Panel contains 19 broad NAICS sectors',len(sectors)==19,str(len(sectors)))

# Score bounds / missing behavior
scores=[]
for r in rows:
    if r['structural_readiness_score'] not in ('','None'):
        try:scores.append(float(r['structural_readiness_score']))
        except:pass
check('Exploratory scores stay within 0–100',scores and min(scores)>=0 and max(scores)<=100,f'{min(scores):.2f}–{max(scores):.2f}')

manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
check('Source manifest records official Census URL',manifest['source_url'].startswith('https://www2.census.gov/'))
check('Source manifest records SHA-256',bool(re.fullmatch(r'[0-9a-f]{64}',manifest['sha256'])),manifest['sha256'][:12]+'…')
check('Manifest coverage agrees with panel',manifest['rows']==44574 and manifest['states_and_dc']==51 and manifest['sectors']==19)
check('Manifest records suppression policy','missing' in manifest['suppression_note'].lower() and 'zero' in manifest['suppression_note'].lower())

browser=json.loads((ROOT/'data/panel_2014_2023.json').read_text())
check('Browser panel covers 2014–2023',min(r['year'] for r in browser)==2014 and max(r['year'] for r in browser)==2023,f'{len(browser)} rows')
latest=json.loads((ROOT/'data/latest_2023.json').read_text())
check('Latest cross-section is 2023 only',len(latest)==969 and all(r['year']==2023 for r in latest),f'{len(latest)} rows')

val=json.loads((ROOT/'data/model_validation.json').read_text())
check('Point-in-time train/validation/holdout split is explicit',val['train_years']=='1990–2016' and val['validation_years']=='2017–2019' and '2020–2021' in val['holdout_feature_years'])
check('Persistence baseline is included',any(r['model']=='Persistence baseline' for r in val['metrics']))
check('At least two fitted model classes are compared',len({r['model'] for r in val['metrics'] if r['model']!='Persistence baseline'})>=2)
hold=[r for r in val['metrics'] if r['split']=='holdout']; selected=val['selected_holdout']; baseline=next(r for r in hold if r['model']=='Persistence baseline')
check('Selected model is chosen by validation rule',val['model_selection_rule'].lower().startswith('lowest validation mae'))
check('Holdout has >1,500 observations',selected['n']>1500,str(selected['n']))
check('Selected model beats persistence on holdout MAE',selected['mae_ann_log_pct']<baseline['mae_ann_log_pct'],f"{selected['mae_ann_log_pct']} < {baseline['mae_ann_log_pct']}")
check('Validation artifact explicitly says target is not M&A activity','not M&A' in val['target'] or 'not M&A' in val['warning'])
check('Sector failure analysis is present',len(val['segment_error_top5'])==5)

sens=json.loads((ROOT/'data/score_sensitivity_2023.json').read_text())
check('2023 score sensitivity covers >900 markets',len(sens)>900,str(len(sens)))
check('Sensitivity output includes uncertainty interval and top-quintile stability',all(k in sens[0] for k in ['score_p05','score_median','score_p95','probability_top_quintile']))

# v0.2 historical replay, rolling-origin and diagnostic checks
diag=json.loads((ROOT/'data/research_diagnostics.json').read_text())
replay_summary=diag['descriptive_replay']['summary']
check('Historical replay spans 44 annual cohorts',replay_summary['cohorts']==44 and replay_summary['cohort_years']=='1978–2021',str(replay_summary['cohorts']))
check('Exploratory top-quintile uplift is positive in 43/44 cohorts',replay_summary['positive_uplift_cohorts']==43,f"{replay_summary['positive_uplift_cohorts']}/44")
check('Historical replay is explicitly labeled post-hoc','post-hoc' in replay_summary['interpretation'].lower())
rolling=diag['rolling_origin']
check('Rolling-origin robustness has four windows',rolling['window_count']==4 and len(rolling['windows'])==8)
check('Fixed HGB beats persistence on MAE in all rolling windows',rolling['wins_vs_persistence']['mae']==4,'4/4')
check('Fixed HGB beats persistence on Spearman in all rolling windows',rolling['wins_vs_persistence']['spearman']==4,'4/4')
check('Fixed HGB beats persistence on top-decile precision in all rolling windows',rolling['wins_vs_persistence']['top_decile_precision']==4,'4/4')
feat=diag['feature_diagnostics']
check('Feature diagnostics cover all eight declared model inputs',len(feat['permutation_importance'])==8 and len(feat['leave_one_feature_out'])==8)
check('Feature diagnostics are explicitly post-selection','post-selection' in feat['warning'].lower())
replay=json.loads((ROOT/'data/replay_2014_2021.json').read_text())
check('Interactive replay covers 2014–2021',min(r['year'] for r in replay)==2014 and max(r['year'] for r in replay)==2021,f"{len(replay)} rows")
check('Interactive replay stores realized future growth',all('future_growth_2y_ann' in r for r in replay[:10]))
repro=json.loads((ROOT/'data/reproducibility_manifest.json').read_text())
check('Reproducibility manifest records environment versions',bool(repro.get('python')) and all(k in repro.get('packages',{}) for k in ['pandas','numpy','scikit-learn','scipy']))
check('Reproducibility manifest fingerprints core source and diagnostic artifacts',bool(re.fullmatch(r'[0-9a-f]{64}',repro['source_sha256'])) and 'data/research_diagnostics.json' in repro['file_sha256'])

ledger=json.loads((ROOT/'data/forecast_ledger.json').read_text())
check('Forecast ledger is intentionally empty before transaction validation',ledger['status']=='no-forecast-issued' and ledger['entries']==[])

# Claim-boundary and source-link checks on public site
html=(ROOT/'index.html').read_text(); js=(ROOT/'assets/app.js').read_text(); readme=(ROOT/'README.md').read_text(); methodology=(ROOT/'research/methodology.md').read_text(); limits=(ROOT/'research/limitations.md').read_text(); milestones=(ROOT/'RESEARCH_MILESTONES.md').read_text(); checklist=(ROOT/'MASTER_CHECKLIST.md').read_text()
for term in ['does <b>not</b> yet claim validated prediction of M&amp;A','Not investment advice','Fragmentation is a proxy','No M&amp;A forecast has been issued yet']:
    check(f'Public claim boundary present: {re.sub("<[^>]+>","",term)}',term in html)
check('Official source links include Census, BLS, BEA, SEC',all(x in js for x in ['census.gov','bls.gov','bea.gov','sec.gov']))
check('Methodology distinguishes SRS from validated M&A forecast','not a validated M&A forecast' in methodology)
check('Limitations explicitly cover transaction-data gap','BDS is not an M&A database' in limits)
check('Future external/adoption milestones are kept unchecked', '- [ ]' in milestones and 'External validation' in milestones)
check('Release checklist itself has no unchecked release gates','- [ ]' not in checklist)

# Static asset references & basic accessibility
for ref in ['assets/styles.css','assets/app.js','data/panel_2014_2023.json','data/latest_2023.json','data/metadata.json','data/model_validation.json']:
    check(f'Referenced asset exists: {ref}',(ROOT/ref).exists())
check('HTML has viewport meta and skip link','name="viewport"' in html and 'class="skip"' in html)
check('Interactive controls have accessible labels','aria-label="Search rankings"' in html and 'aria-live="polite"' in html and '<label>State' in html)
check('Responsive CSS breakpoints are present','@media(max-width:900px)' in (ROOT/'assets/styles.css').read_text() and '@media(max-width:560px)' in (ROOT/'assets/styles.css').read_text())
check('Public UI exposes comparator, screener, replay and reproducibility sections',all(x in html for x in ['id="workbench"','id="compareBody"','id="screenResults"','id="replay"','id="reproducibility"']))
check('Public UI exposes score robustness and evidence export',all(x in html for x in ['id="sensitivityCard"','id="exportBrief"']))
check('Public UI exposes rolling-origin and feature diagnostics',all(x in html for x in ['id="rollingBody"','id="featureBars"','id="upliftChart"']))
check('Model card and hypothesis registry exist with explicit claim boundaries','M&A prediction model' in (ROOT/'research/model-card.md').read_text() and '**not**' in (ROOT/'research/model-card.md').read_text() and 'not a claim of external preregistration' in (ROOT/'research/hypothesis-registry.md').read_text())
check('CI rebuilds advanced diagnostics before validation','build_advanced_diagnostics.py' in (ROOT/'.github/workflows/validate.yml').read_text())

# No obvious placeholders/marketing overclaims in public release files
public_text='\n'.join([html,js,readme,methodology,limits]).lower()
check('No TODO/TBD/lorem placeholders in public release',not any(t in public_text for t in ['todo','tbd','lorem ipsum']))
check('No claim of guaranteed returns/admission or proven acquisition forecasting',not any(t in public_text for t in ['guaranteed return','guaranteed admission','we have a validated m&a forecast','proven acquisition forecast','accurately predicts acquisitions']))

failed=[x for x in checks if not x[1]]
print(f'\nRESULT: {len(checks)-len(failed)}/{len(checks)} checks passed')
if failed:
    print('FAILED:',', '.join(x[0] for x in failed)); sys.exit(1)
