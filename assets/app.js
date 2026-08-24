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

function renderRanking(){const q=$('#rankSearch').value.toLowerCase().trim();let rows=LATEST.filter(r=>r.structural_readiness_score!=null);if(q)rows=rows.filter(r=>(r.state_name+' '+r.sector_name).toLowerCase().includes(q));rows=rows.slice(0,40);$('#rankBody').innerHTML=rows.map((r,i)=>`<tr><td>${i+1}</td><td><b>${r.state_name}</b></td><td>${r.sector_name}</td><td><span class="score-chip">${r.structural_readiness_score.toFixed(1)}</span></td><td>${fmt(r.firms)}</td><td>${fmt(r.estabs)}</td><td>${pct(r.estabs_entry_rate)}</td><td>${pct(r.net_job_creation_rate)}</td></tr>`).join('')}

function renderCompare(){
 const sector=$('#compareSector').value, year=+$('#compareYear').value, ids=['compareA','compareB','compareC'].map(id=>$('#'+id).value);
 const rows=ids.map(st=>PANEL.find(r=>r.st===st&&r.sector===sector&&r.year===year)).filter(Boolean);
 $('#compareBody').innerHTML=rows.map(r=>`<tr><td><b>${r.state_name}</b><br><small>${r.sector_name}</small></td><td><span class="score-chip">${r.structural_readiness_score==null?'—':r.structural_readiness_score.toFixed(1)}</span></td><td>${fmt(r.firms)}</td><td>${pct(r.estabs_entry_rate)}</td><td>${pct(r.estabs_exit_rate)}</td><td>${pct(r.net_job_creation_rate)}</td><td>${fmt(r.firms_per_1000_emp)}</td></tr>`).join('');
}

function renderScreener(){
 const score=+$(' #screenScore'.trim()).value, entry=+$(' #screenEntry'.trim()).value, jobs=+$(' #screenJobs'.trim()).value, sector=$('#screenSector').value;
 $('#screenScoreValue').textContent=score.toFixed(0); $('#screenEntryValue').textContent=entry.toFixed(1)+'%'; $('#screenJobsValue').textContent=jobs.toFixed(1)+'%';
 let rows=LATEST.filter(r=>{const e=safe(r.estabs_entry_rate),j=safe(r.net_job_creation_rate);return r.structural_readiness_score!=null&&r.structural_readiness_score>=score&&e!=null&&j!=null&&e>=entry&&j>=jobs});
 if(sector!=='all')rows=rows.filter(r=>r.sector===sector); rows=rows.sort((a,b)=>b.structural_readiness_score-a.structural_readiness_score);
 $('#screenCount').textContent=`${rows.length} markets`;
 $('#screenResults').innerHTML=rows.slice(0,8).map(r=>`<button class="screen-result" data-st="${r.st}" data-sector="${r.sector}"><span><b>${r.state_name}</b><small>${r.sector_name}</small></span><strong>${r.structural_readiness_score.toFixed(1)}</strong></button>`).join('')||'<p>No 2023 markets meet all current thresholds.</p>';
 document.querySelectorAll('.screen-result').forEach(btn=>btn.addEventListener('click',()=>{ $('#stateSelect').value=btn.dataset.st;$('#sectorSelect').value=btn.dataset.sector;$('#yearSelect').value='2023';renderAll();document.querySelector('#explorer').scrollIntoView({behavior:'smooth'});}));
}

function renderDiagnostics(){
 const d=DIAG.descriptive_replay.summary, wins=DIAG.rolling_origin.wins_vs_persistence, top=DIAG.feature_diagnostics.permutation_importance[0];
 const friendly=featureName(top.feature);
 $('#findingCards').innerHTML=[
  [`${d.positive_uplift_cohorts}/${d.cohorts}`,'annual cohorts with positive SRS top-quintile future-growth uplift'],
  [`+${d.mean_uplift_ann_log_pct.toFixed(2)}`,'mean annualized log-growth uplift, top quintile vs. remainder'],
  [`${wins.mae}/${DIAG.rolling_origin.window_count}`,'rolling-origin windows where HGB beat persistence on MAE'],
  [friendly,'strongest validation-period permutation signal']
 ].map(([a,b])=>`<article class="finding-card"><b>${a}</b><span>${b}</span></article>`).join('');
 $('#rollingBody').innerHTML=DIAG.rolling_origin.windows.map(r=>`<tr><td>${r.window}</td><td><b>${r.model}</b></td><td>${r.mae_ann_log_pct.toFixed(3)}</td><td>${r.spearman.toFixed(3)}</td><td>${(100*r.top_decile_precision).toFixed(1)}%</td></tr>`).join('');
 const imp=DIAG.feature_diagnostics.permutation_importance, max=Math.max(...imp.map(x=>x.mae_increase_when_permuted));
 $('#featureBars').innerHTML=imp.map(x=>`<div class="bar-row"><span>${featureName(x.feature)}</span><div class="bar-track"><div class="bar-fill" style="width:${100*x.mae_increase_when_permuted/max}%"></div></div><b>${x.mae_increase_when_permuted.toFixed(3)}</b></div>`).join('');
 renderUpliftChart();
}
function featureName(f){return ({firms_per_1000_emp:'Fragmentation',estabs_entry_rate:'Entry rate',estabs_exit_rate:'Exit rate',net_job_creation_rate:'Net job creation',reallocation_rate:'Reallocation',log_firms:'Firm scale',log_emp:'Employment scale',lag_growth_2y_ann:'Lagged growth'})[f]||f}

function renderReplay(){
 const year=+$('#replayYear').value, sector=$('#replaySector').value;
 const rows=REPLAY.filter(r=>r.year===year&&r.sector===sector&&r.structural_readiness_score!=null).sort((a,b)=>b.structural_readiness_score-a.structural_readiness_score).slice(0,8);
 $('#replayBody').innerHTML=rows.map(r=>`<tr><td><b>${r.state_name}</b></td><td>${r.structural_readiness_score.toFixed(1)}</td><td>${(100*r.srs_percentile_within_sector).toFixed(0)}th</td><td class="${r.future_growth_2y_ann>=0?'positive':'negative'}">${r.future_growth_2y_ann>=0?'+':''}${r.future_growth_2y_ann.toFixed(2)}</td><td>${r.srs_top_quintile?'Yes':'No'}</td></tr>`).join('');
}

function renderUpliftChart(){
 const rows=DIAG.descriptive_replay.annual, svg=$('#upliftChart'),W=760,H=330,L=45,R=15,T=22,B=42; const vals=rows.map(r=>r.uplift), max=Math.max(Math.abs(Math.min(...vals)),Math.abs(Math.max(...vals)),1), y=v=>T+(max-v)*(H-T-B)/(2*max), zero=y(0), bw=(W-L-R)/rows.length;
 let html=`<line x1="${L}" y1="${zero}" x2="${W-R}" y2="${zero}" stroke="currentColor" opacity=".35"/>`;
 rows.forEach((r,i)=>{const yy=y(r.uplift), h=Math.abs(zero-yy), x=L+i*bw+.5;html+=`<rect x="${x}" y="${Math.min(zero,yy)}" width="${Math.max(2,bw-1)}" height="${Math.max(1,h)}" rx="1" fill="${r.uplift>=0?'var(--blue)':'var(--orange)'}" opacity=".82"><title>${r.year}: ${r.uplift>=0?'+':''}${r.uplift.toFixed(3)}</title></rect>`;if(i%5===0||i===rows.length-1)html+=`<text x="${x+bw/2}" y="${H-12}" text-anchor="middle" fill="currentColor" opacity=".55" font-size="10">${r.year}</text>`}); svg.innerHTML=html;
}

function renderRepro(){
 $('#sourceFingerprint').innerHTML=`Census source SHA-256: <code>${SOURCE.sha256.slice(0,16)}…</code><br>${SOURCE.rows.toLocaleString()} rows · ${SOURCE.min_year}–${SOURCE.max_year}`;
 const diagHash=REPRO.file_sha256['data/research_diagnostics.json']||''; $('#artifactFingerprint').innerHTML=`Diagnostics SHA-256: <code>${diagHash.slice(0,16)}…</code><br>Python ${REPRO.python} · scikit-learn ${REPRO.packages['scikit-learn']}`;
}

function exportMarketBrief(){
 const r=current(); if(!r)return; const sens=r.year===2023?SENS.find(s=>s.st===r.st&&s.sector===r.sector):null;
 const text=`# U.S. Consolidation Observatory — Evidence Snapshot\n\n**Market:** ${r.state_name} — ${r.sector_name}\n**Year:** ${r.year}\n**Structural Readiness Score:** ${r.structural_readiness_score==null?'N/A':r.structural_readiness_score.toFixed(1)}\n\n## Public-data measures\n\n- Firms: ${fmt(r.firms)}\n- Establishments: ${fmt(r.estabs)}\n- Employment: ${fmt(r.emp)}\n- Establishment entry rate: ${pct(r.estabs_entry_rate)}\n- Establishment exit rate: ${pct(r.estabs_exit_rate)}\n- Net job-creation rate: ${pct(r.net_job_creation_rate)}\n- Firms per 1,000 employees: ${fmt(r.firms_per_1000_emp)}\n${sens?`\n## 2023 score robustness\n\n- 5th–95th percentile score interval under 1,000 weight perturbations: ${sens.score_p05.toFixed(1)}–${sens.score_p95.toFixed(1)}\n- Probability of remaining in sector top quintile: ${(100*sens.probability_top_quintile).toFixed(0)}%\n`:''}\n## Evidence boundary\n\nSRS is an exploratory structural summary. It is not a validated M&A forecast, valuation, investment recommendation, or prediction of returns.\n\n## Source\n\nU.S. Census Bureau, 2023 Business Dynamics Statistics — State by Sector.\n${SOURCE.landing_url}\nSource SHA-256: ${SOURCE.sha256}\n\nGenerated from U.S. Consolidation Observatory v0.2.\n`;
 const blob=new Blob([text],{type:'text/markdown'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`USCO_${r.state_name.replace(/\W+/g,'-')}_${r.sector.replace(/[^0-9-]/g,'')}_${r.year}.md`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function runQuery(){const q=$('#queryInput').value.toLowerCase().trim();if(!q){$('#queryAnswer').textContent='Enter a state, sector, or “top <sector>”.';return}const states=[...new Map(LATEST.map(r=>[r.st,r.state_name]))],sectors=[...new Map(LATEST.map(r=>[r.sector,r.sector_name]))];const sm=states.find(([,n])=>q.includes(n.toLowerCase())),sec=sectors.find(([,n])=>q.includes(n.toLowerCase())||n.toLowerCase().split(/[,&]/)[0].trim().split(' ').some(w=>w.length>7&&q.includes(w)));let rows=LATEST.filter(r=>r.structural_readiness_score!=null);if(sm)rows=rows.filter(r=>r.st===sm[0]);if(sec)rows=rows.filter(r=>r.sector===sec[0]);if(q.startsWith('top')&&sec)rows=LATEST.filter(r=>r.sector===sec[0]&&r.structural_readiness_score!=null).slice(0,5);if(!rows.length){$('#queryAnswer').innerHTML='No confident match. Try an exact state plus a broad sector name such as <b>Virginia construction</b>.';return}const top=rows.slice(0,5);$('#queryAnswer').innerHTML=top.map((r,i)=>`<div><b>${i+1}. ${r.state_name} — ${r.sector_name}</b>: SRS ${r.structural_readiness_score.toFixed(1)}, ${fmt(r.firms)} firms, ${pct(r.estabs_entry_rate)} entry rate, ${pct(r.net_job_creation_rate)} net job creation. <small>Source: Census BDS 2023.</small></div>`).join('<hr>')}

load().catch(e=>{console.error(e);document.body.insertAdjacentHTML('afterbegin','<div style="padding:12px;background:#fee2e2;color:#7f1d1d">Data failed to load. Serve this folder over HTTP (for example, GitHub Pages) rather than opening index.html directly.</div>')});
