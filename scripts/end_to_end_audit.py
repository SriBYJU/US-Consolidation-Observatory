from pathlib import Path
from html.parser import HTMLParser
import json, sys
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'data/site'
results=[]
def check(name,cond,detail=''):
    ok=bool(cond);results.append((name,ok,detail));print(('PASS' if ok else 'FAIL'),'-',name,(f'— {detail}' if detail else ''))

class P(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.hrefs=[]; self.scripts=[]; self.imgs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.hrefs.append(a['href'])
        if tag=='script' and 'src' in a:self.scripts.append(a['src'])
        if tag=='img':self.imgs.append(a)
html=(ROOT/'index.html').read_text(); js=(ROOT/'assets/app.js').read_text(); p=P();p.feed(html)
check('HTML IDs are unique',len(p.ids)==len(set(p.ids)),f'{len(p.ids)} ids')
for anchor in ['public-data','current-context','guide','explorer','workbench','validation','replay','methodology','reproducibility','sources','query','about','limitations']:
    check(f'Anchor exists: #{anchor}',anchor in p.ids)
internal=[h for h in p.hrefs if h and not h.startswith(('http://','https://','mailto:','#'))]
check('All internal linked files exist',all((ROOT/h.split('#')[0]).exists() for h in internal),f'{len(internal)} links')
check('Primary script exists',all((ROOT/s).exists() for s in p.scripts),','.join(p.scripts))

# Current-context freshness / source-governance layer
ctx_path=ROOT/'data/current_context.json'; gov_path=ROOT/'research/source-governance.md'
check('Current-context registry exists',ctx_path.exists(),'data/current_context.json')
check('Source-governance document exists',gov_path.exists(),'research/source-governance.md')
ctx=json.loads(ctx_path.read_text()) if ctx_path.exists() else {'sources':[],'policy':{}}
ctx_sources={x.get('id'):x for x in ctx.get('sources',[])}
check('Current-context registry has six governed sources',len(ctx.get('sources',[]))>=6,str(len(ctx.get('sources',[]))))
check('Context registry is dated for v0.4 audit',ctx.get('as_of')=='2026-08-23',str(ctx.get('as_of')))
check('BDS remains the only current SRS source',sum(1 for x in ctx.get('sources',[]) if x.get('used_in_srs'))==1 and ctx_sources.get('census_bds_2023',{}).get('used_in_srs') is True)
check('BDS vintage remains 2023',ctx_sources.get('census_bds_2023',{}).get('latest_vintage')=='2023')
q=ctx_sources.get('bls_qcew_q4_2025',{}); qm=q.get('headline_metrics',{})
check('QCEW current context is Q4 2025',q.get('latest_vintage')=='Q4 2025' and qm.get('december_2025_employment')==156700000 and qm.get('q4_2025_avg_weekly_wage_usd')==1569)
b=ctx_sources.get('census_bfs_july_2026',{}); bm=b.get('headline_metrics',{})
check('BFS current context is July 2026',b.get('latest_vintage')=='July 2026' and bm.get('seasonally_adjusted_business_applications')==578926 and bm.get('projected_formations_within_4q')==29959)
g=ctx_sources.get('bea_state_gdp_q1_2026',{}); gm=g.get('headline_metrics',{})
check('BEA current context is Q1 2026',g.get('latest_vintage')=='Q1 2026' and gm.get('states_with_real_gdp_increase')==46 and gm.get('highest_annualized_pct')==4.5 and gm.get('lowest_annualized_pct')==-1.6)
check('Current-context sources use official federal domains',all(any(d in x.get('source_url','') for d in ['census.gov','bls.gov','bea.gov','sec.gov']) for x in ctx.get('sources',[])))
check('Current-context policy forbids mixed-vintage SRS blending','not blended into srs' in (ctx.get('policy',{}).get('srs_rule','')).lower())
check('Public UI exposes freshness matrix and context boundary','id="freshnessMatrix"' in html and 'not blended into SRS' in html and 'Freshness layer · through July 2026' in html)
check('Public UI links official BFS, QCEW and BEA sources',all(x in html for x in ['census.gov/econ/bfs/current','bls.gov/news.release/cewqtr.nr0','bea.gov/data/gdp/gdp-state']))

m=json.loads((SITE/'manifest.json').read_text());states=m['states'];sectors=m['sectors']
def unpack(pack): return [dict(zip(pack['k'],r)) for r in pack['r']]
panel=[]
for fn in m['panel_files']:panel+=unpack(json.loads((SITE/fn).read_text()))
for r in panel:r['state_name']=states[r['st']];r['sector_name']=sectors[r['sector']]
latest=sorted([r for r in panel if r['year']==2023 and r.get('structural_readiness_score') is not None],key=lambda x:x['structural_readiness_score'],reverse=True)
replay=[]
for fn in m['replay_files']:replay+=unpack(json.loads((SITE/fn).read_text()))
for r in replay:r['state_name']=states[r['st']];r['sector_name']=sectors[r['sector']]
sens=unpack(json.loads((SITE/m['sensitivity_file']).read_text()))
research=json.loads((SITE/m['research_file']).read_text())

check('Browser panel has expected 9,690 observations',len(panel)==9690,str(len(panel)))
check('Default explorer market exists',any(r['st']=='51' and r['sector']=='23' and r['year']==2023 for r in panel),'Virginia · Construction · 2023')
default=next(r for r in panel if r['st']=='51' and r['sector']=='23' and r['year']==2023)
check('Default market has all six displayed KPI inputs',all(default.get(k) is not None for k in ['structural_readiness_score','firms','estabs','estabs_entry_rate','estabs_exit_rate','net_job_creation_rate']))
compare=[next((r for r in panel if r['st']==st and r['sector']=='23' and r['year']==2023),None) for st in ['51','37','48']]
check('Default 3-state comparator resolves all markets',all(compare),','.join(r['state_name'] for r in compare if r))
screen=[r for r in latest if r['structural_readiness_score']>=65 and r.get('estabs_entry_rate') is not None and r['estabs_entry_rate']>=5 and r.get('net_job_creation_rate') is not None and r['net_job_creation_rate']>=0]
check('Default evidence screener returns results',len(screen)>0,f'{len(screen)} markets')
va=[r for r in latest if 'virginia' in (r['state_name']+' '+r['sector_name']).lower()]
check('Ranking search for Virginia returns sector rows',len(va)>=15,str(len(va)))
construction=[r for r in latest if r['sector']=='23'][:5]
check('“top construction” query can return five sourced rows',len(construction)==5,'; '.join(r['state_name'] for r in construction))
rep=[r for r in replay if r['year']==2021 and r['sector']=='23' and r.get('structural_readiness_score') is not None]
check('Default historical replay resolves 2021 Construction rows',len(rep)>=40,str(len(rep)))
check('Default market has 2023 sensitivity result',any(r['st']=='51' and r['sector']=='23' for r in sens))
check('Validation table has multiple models',len(research['validation']['metrics'])>=6,str(len(research['validation']['metrics'])))
check('Rolling-origin table has eight model/window rows',len(research['diagnostics']['rolling_origin']['windows'])==8)
check('Feature diagnostics expose eight features',len(research['diagnostics']['feature_diagnostics']['permutation_importance'])==8)

for control in ['stateSelect','sectorSelect','yearSelect','rankSearch','queryButton','queryInput','exportBrief','themeToggle','compareSector','compareYear','compareA','compareB','compareC','screenScore','screenEntry','screenJobs','screenSector','replayYear','replaySector']:
    check(f'Interactive control wired: {control}',f'id="{control}"' in html and control in js)
check('Data-load error degrades gracefully','data-error-banner' in js and 'renderStaticScaffold' in js)
check('About image has an explicit fallback',bool(p.imgs) and 'onerror' in p.imgs[0])
html_lower=html.lower()
check('No pickleball 4.5 claim appears in viewer HTML','4.5 singles' not in html_lower and '4.5 pickleball' not in html_lower and 'pickleball experience, including competing at the 4.5' not in html_lower)
check('v0.4 footer/version label is public','Technical platform v0.4' in html and 'Version 0.4' in html)

failed=[x for x in results if not x[1]]
print(f'\nEND-TO-END RESULT: {len(results)-len(failed)}/{len(results)} checks passed')
if failed:
    print('FAILED:',', '.join(x[0] for x in failed));sys.exit(1)
