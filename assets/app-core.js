const $=s=>document.querySelector(s);
const fmt=n=>n==null?'—':Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(n);
const pct=n=>n==null?'—':`${Number(n).toFixed(1)}%`;
const safe=n=>(n==null||n==='')?null:(Number.isFinite(Number(n))?Number(n):null);
let PANEL=[],LATEST=[],META={},VALID={},SENS=[],DIAG={},REPLAY=[],REPRO={},SOURCE={};

const sources=[
 {name:'Business Dynamics Statistics (BDS)',agency:'U.S. Census Bureau',status:'Primary panel',desc:'Annual firm/establishment dynamics, entry, exit, job creation/destruction and reallocation. 1978–2023 in this release.',url:'https://www.census.gov/programs-surveys/bds.html'},
 {name:'Quarterly Census of Employment and Wages (QCEW)',agency:'U.S. Bureau of Labor Statistics',status:'Context / next integration',desc:'Near-census employment, establishment and wage data by geography and industry; used here for current national context.',url:'https://www.bls.gov/cew/'},
 {name:'County Business Patterns (CBP)',agency:'U.S. Census Bureau',status:'Planned enrichment',desc:'Annual establishment, employment and payroll detail by geography and NAICS; planned for finer-grained target-density measures.',url:'https://www.census.gov/programs-surveys/cbp.html'},
 {name:'GDP by State',agency:'U.S. Bureau of Economic Analysis',status:'Current context',desc:'Official quarterly state GDP statistics; included only as a sourced macro context indicator in this preview.',url:'https://www.bea.gov/data/gdp/gdp-state'},
 {name:'Nonemployer Statistics',agency:'U.S. Census Bureau',status:'Planned enrichment',desc:'Businesses with no paid employees; useful for understanding the long tail of small operators in fragmented service markets.',url:'https://www.census.gov/programs-surveys/nonemployer-statistics.html'},
 {name:'SEC EDGAR',agency:'U.S. Securities and Exchange Commission',status:'Transaction-corpus source',desc:'Public filings and exhibits are a future source for human-verified acquisition-event extraction and benchmarking.',url:'https://www.sec.gov/edgar/search-and-access'}
];

async function load(){
 const paths=['data/panel_2014_2023.json','data/latest_2023.json','data/metadata.json','data/model_validation.json','data/score_sensitivity_2023.json','data/research_diagnostics.json','data/replay_2014_2021.json','data/reproducibility_manifest.json','data/source_manifest.json'];
 [PANEL,LATEST,META,VALID,SENS,DIAG,REPLAY,REPRO,SOURCE]=await Promise.all(paths.map(x=>fetch(x).then(r=>{if(!r.ok)throw new Error(x);return r.json()})));
 renderStatic();initControls();renderAll();renderDiagnostics();renderRepro();
}

function renderStatic(){
 $('#heroMetrics').innerHTML=[['44,574','state-sector-year observations'],['51','states + D.C.'],['19','NAICS sectors'],['1978–2023','official BDS history']].map(x=>`<div class="metric"><b>${x[0]}</b><span>${x[1]}</span></div>`).join('');
 const q=META.qcew_2024;
 $('#contextCards').innerHTML=[[`12.06M`,'2024 QCEW covered establishments',q.source],[`155.0M`,'2024 QCEW average employment',q.source],[`$11.71T`,'2024 QCEW total wages',q.source]].map(x=>`<div class="context-card"><b>${x[0]}</b><span>${x[1]}</span><a href="${x[2]}" target="_blank" rel="noreferrer">Official BLS source ↗</a></div>`).join('');
 $('#sourceGrid').innerHTML=sources.map(s=>`<article class="source-card"><span class="status">${s.status}</span><h3>${s.name}</h3><p><b>${s.agency}</b><br>${s.desc}</p><a href="${s.url}" target="_blank" rel="noreferrer">Open official source ↗</a></article>`).join('');
 const h=VALID.selected_holdout, base=VALID.metrics.find(x=>x.model==='Persistence baseline'&&x.split==='holdout');
 $('#validationCards').innerHTML=[['1990–2016','Training period'],['2017–2019','Model-selection validation'],['2020–2021','Locked holdout feature years'],[`${h.n.toLocaleString()}`,'Holdout observations']].map(x=>`<div class="validation-card"><b>${x[0]}</b><span>${x[1]}</span></div>`).join('');
 $('#validationBody').innerHTML=VALID.metrics.map(r=>`<tr class="${r.model===VALID.selected_model?'selected-row':''}"><td><b>${r.model}</b>${r.model===VALID.selected_model?' <small class="mini-tag">selected on validation</small>':''}</td><td>${r.split}</td><td>${r.n.toLocaleString()}</td><td>${r.mae_ann_log_pct.toFixed(3)}</td><td>${r.spearman.toFixed(3)}</td><td>${(100*r.top_decile_precision).toFixed(1)}%</td></tr>`).join('');
 const errs=VALID.segment_error_top5.map(x=>`${x.sector_name} (${x.mae.toFixed(2)})`).join(' · ');
 $('#errorAnalysis').innerHTML=`<b>Holdout interpretation:</b> selected model MAE ${h.mae_ann_log_pct.toFixed(3)} vs. persistence ${base.mae_ann_log_pct.toFixed(3)}; top-decile precision ${(100*h.top_decile_precision).toFixed(1)}% vs. ${(100*base.top_decile_precision).toFixed(1)}%. Rank correlation is only ${h.spearman.toFixed(2)} and slightly below persistence (${base.spearman.toFixed(2)}), so the signal is useful but far from perfect. Highest-error sectors: ${errs}.`;
}

function options(rows,key,label,selected){return rows.map(([v,n])=>`<option value="${v}" ${v===selected?'selected':''}>${n}</option>`).join('')}
function initControls(){
 const states=[...new Map(PANEL.map(r=>[r.st,r.state_name])).entries()].sort((a,b)=>a[1].localeCompare(b[1]));
 const sectors=[...new Map(PANEL.map(r=>[r.sector,r.sector_name])).entries()];
 const years=[...new Set(PANEL.map(r=>r.year))].sort((a,b)=>b-a);
 $('#stateSelect').innerHTML=options(states,'st','state','51'); $('#sectorSelect').innerHTML=options(sectors,'sector','sector','23'); $('#yearSelect').innerHTML=years.map(y=>`<option ${y===2023?'selected':''}>${y}</option>`).join('');
 ['stateSelect','sectorSelect','yearSelect'].forEach(id=>$('#'+id).addEventListener('change',renderAll));
 $('#rankSearch').addEventListener('input',renderRanking);
 $('#queryButton').addEventListener('click',runQuery); $('#queryInput').addEventListener('keydown',e=>{if(e.key==='Enter')runQuery()});
 $('#exportBrief').addEventListener('click',exportMarketBrief);
 $('#themeToggle').addEventListener('click',()=>{document.body.classList.toggle('dark');localStorage.setItem('usco-theme',document.body.classList.contains('dark')?'dark':'light')}); if(localStorage.getItem('usco-theme')==='dark')document.body.classList.add('dark');

 $('#compareSector').innerHTML=options(sectors,'','','23'); $('#compareYear').innerHTML=years.map(y=>`<option ${y===2023?'selected':''}>${y}</option>`).join('');
 [['compareA','51'],['compareB','37'],['compareC','48']].forEach(([id,sel])=>{$('#'+id).innerHTML=options(states,'','',sel)});
 ['compareSector','compareYear','compareA','compareB','compareC'].forEach(id=>$('#'+id).addEventListener('change',renderCompare));
 $('#screenSector').innerHTML+=[...sectors].map(([v,n])=>`<option value="${v}">${n}</option>`).join('');
 ['screenScore','screenEntry','screenJobs','screenSector'].forEach(id=>$('#'+id).addEventListener('input',renderScreener));
 const replayYears=[...new Set(REPLAY.map(r=>r.year))].sort((a,b)=>b-a); $('#replayYear').innerHTML=replayYears.map(y=>`<option ${y===2021?'selected':''}>${y}</option>`).join(''); $('#replaySector').innerHTML=options(sectors,'','','23');
 ['replayYear','replaySector'].forEach(id=>$('#'+id).addEventListener('change',renderReplay));
 renderCompare(); renderScreener(); renderReplay();
}

function current(){return PANEL.find(r=>r.st===$('#stateSelect').value&&r.sector===$('#sectorSelect').value&&r.year===+$('#yearSelect').value)}
function renderAll(){const r=current();if(!r)return;$('#kpiGrid').innerHTML=[['Structural score',r.structural_readiness_score?.toFixed(1)],['Firms',fmt(r.firms)],['Establishments',fmt(r.estabs)],['Entry rate',pct(r.estabs_entry_rate)],['Exit rate',pct(r.estabs_exit_rate)],['Net job creation',pct(r.net_job_creation_rate)]].map(x=>`<div class="kpi"><span>${x[0]}</span><b>${x[1]??'—'}</b></div>`).join('');renderChart(r);renderScore(r);renderSensitivity(r);renderRanking();}
function renderScore(r){const same=PANEL.filter(x=>x.year===r.year&&x.sector===r.sector);const vals=[['Fragmentation',rank(same,'firms_per_1000_emp',r)],['Entry',rank(same,'estabs_entry_rate',r)],['Momentum',rank(same,'net_job_creation_rate',r)],['Scale',rank(same,'firms',r)],['Stability',100-rank(same,'estabs_exit_rate',r)],['Dynamism',rank(same,'reallocation_rate',r)]];$('#scoreBars').innerHTML=vals.map(([n,v])=>`<div class="bar-row"><span>${n}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(0,Math.min(100,v||0))}%"></div></div><b>${v==null?'—':v.toFixed(0)}</b></div>`).join('')}
function rank(rows,key,r){const good=rows.filter(x=>x[key]!=null).sort((a,b)=>a[key]-b[key]);const i=good.findIndex(x=>x.st===r.st);return i<0?null:100*(i+1)/good.length}

function renderSensitivity(r){
 if(r.year!==2023){$('#sensitivityCard').innerHTML=`<p>Weight-perturbation robustness is frozen for the 2023 cross-section. Switch the explorer to 2023 to inspect this market's 1,000-run stability interval.</p>`;return}
 const x=SENS.find(s=>s.st===r.st&&s.sector===r.sector);
 if(!x){$('#sensitivityCard').innerHTML='<p>Complete score inputs are not available for this market.</p>';return}
 const width=Math.max(2,x.score_p95-x.score_p05);
 $('#sensitivityCard').innerHTML=`<div class="robust-metrics"><div><b>${x.score_p05.toFixed(1)}–${x.score_p95.toFixed(1)}</b><span>5th–95th score interval</span></div><div><b>${(100*x.probability_top_quintile).toFixed(0)}%</b><span>probability of remaining sector top quintile</span></div></div><div class="interval-track"><span style="left:${x.score_p05}%;width:${width}%"></span><i style="left:${x.base_score}%"></i></div><p>1,000 deterministic positive weight perturbations around the declared score design. This tests ranking fragility, not economic causality.</p>`;
}

function renderChart(r){const history=PANEL.filter(x=>x.st===r.st&&x.sector===r.sector).sort((a,b)=>a.year-b.year);$('#chartSubtitle').textContent=`${r.state_name} · ${r.sector_name} · 2014–2023`;const svg=$('#historyChart'),W=760,H=330,L=48,R=18,T=25,B=38;const x=i=>L+i*(W-L-R)/(Math.max(1,history.length-1));const est0=history.find(x=>x.estabs>0)?.estabs||1;const series=[{key:'structural_readiness_score',color:'var(--blue)',map:v=>v??0},{key:'estabs',color:'var(--cyan)',map:v=>100*(v||0)/est0}];const all=series.flatMap(s=>history.map(r=>s.map(r[s.key])).filter(Number.isFinite));const yMax=Math.max(110,...all),y=v=>T+(yMax-v)*(H-T-B)/yMax;let html='';[0,25,50,75,100].forEach(v=>{html+=`<line x1="${L}" y1="${y(v)}" x2="${W-R}" y2="${y(v)}" stroke="currentColor" opacity=".10"/><text x="${L-8}" y="${y(v)+4}" text-anchor="end" fill="currentColor" opacity=".55" font-size="11">${v}</text>`});history.forEach((d,i)=>{html+=`<text x="${x(i)}" y="${H-10}" text-anchor="middle" fill="currentColor" opacity=".55" font-size="10">${String(d.year).slice(2)}</text>`});series.forEach(s=>{const pts=history.map((d,i)=>{const v=s.map(d[s.key]);return Number.isFinite(v)?`${x(i)},${y(v)}`:null}).filter(Boolean).join(' ');html+=`<polyline points="${pts}" fill="none" stroke="${s.color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`});svg.innerHTML=html;}

