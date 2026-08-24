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
