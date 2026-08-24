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
for anchor in ['public-data','guide','explorer','workbench','validation','replay','methodology','reproducibility','sources','query','about','limitations']:
    check(f'Anchor exists: #{anchor}',anchor in p.ids)
internal=[h for h in p.hrefs if h and not h.startswith(('http://','https://','mailto:','#'))]
check('All internal linked files exist',all((ROOT/h.split('#')[0]).exists() for h in internal),f'{len(internal)} links')
check('Primary script exists',all((ROOT/s).exists() for s in p.scripts),','.join(p.scripts))

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
check('Validation table has multiple models',len(research['validation']['metrics'])>=6,str(len(research['validation']['metrics']))
check('Rolling-origin table has eight model/window rows',len(research['diagnostics']['rolling_origin']['windows'])==8)
check('Feature diagnostics expose eight features',len(research['diagnostics']['feature_diagnostics']['permutation_importance'])==8)

for control in ['stateSelect','sectorSelect','yearSelect','rankSearch','queryButton','queryInput','exportBrief','themeToggle','compareSector','compareYear','compareA','compareB','compareC','screenScore','screenEntry','screenJobs','screenSector','replayYear','replaySector']:
    check(f'Interactive control wired: {control}',f'id="{control}"' in html and control in js)
check('Data-load error degrades gracefully','data-error-banner' in js and 'renderStaticScaffold' in js)
check('About image has an explicit fallback',bool(p.imgs) and 'onerror' in p.imgs[0])
check('No pickleball 4.5 claim appears in viewer HTML','4.5' not in html)

failed=[x for x in results if not x[1]]
print(f'\nEND-TO-END RESULT: {len(results)-len(failed)}/{len(results)} checks passed')
if failed:
    print('FAILED:',', '.join(x[0] for x in failed));sys.exit(1)
