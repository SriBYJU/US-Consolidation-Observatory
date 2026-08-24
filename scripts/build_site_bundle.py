from pathlib import Path
import gzip, json, shutil

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SITE = DATA / 'site'

panel = json.loads((DATA / 'panel_2014_2023.json').read_text())
latest = json.loads((DATA / 'latest_2023.json').read_text())
replay = json.loads((DATA / 'replay_2014_2021.json').read_text())
sens = json.loads((DATA / 'score_sensitivity_2023.json').read_text())

states = {r['st']: r['state_name'] for r in panel}
sectors = {r['sector']: r['sector_name'] for r in panel}
panel_keys = [
    'st','sector','year','firms','estabs','emp','estabs_entry_rate','estabs_exit_rate',
    'net_job_creation_rate','reallocation_rate','firms_per_1000_emp','structural_readiness_score'
]
replay_keys = [
    'st','sector','year','structural_readiness_score',
    'srs_percentile_within_sector','future_growth_2y_ann','srs_top_quintile'
]
sens_keys = ['st','sector','base_score','score_p05','score_p95','probability_top_quintile']

def pack(rows, keys):
    return {'k': keys, 'r': [[r.get(k) for k in keys] for r in rows]}

def compact(obj):
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)

research = {
    'metadata': json.loads((DATA / 'metadata.json').read_text()),
    'validation': json.loads((DATA / 'model_validation.json').read_text()),
    'diagnostics': json.loads((DATA / 'research_diagnostics.json').read_text()),
    'repro': json.loads((DATA / 'reproducibility_manifest.json').read_text()),
    'source': json.loads((DATA / 'source_manifest.json').read_text()),
}

bundle = {
    'bundle_version': '0.3',
    'panel': {**pack(panel, panel_keys), 'states': states, 'sectors': sectors},
    'latest': pack(latest, panel_keys),
    'replay': pack(replay, replay_keys),
    'sensitivity': pack(sens, sens_keys),
    **research,
}
raw = compact(bundle).encode('utf-8')
gzip_out = DATA / 'site_data.json.gz'
with gzip_out.open('wb') as raw_file:
    with gzip.GzipFile(filename='', mode='wb', fileobj=raw_file, compresslevel=9, mtime=0) as f:
        f.write(raw)

if SITE.exists():
    shutil.rmtree(SITE)
SITE.mkdir(parents=True)
panel_files=[]
for year in range(2014, 2024):
    name=f'panel_{year}.json'; panel_files.append(name)
    (SITE/name).write_text(compact(pack([r for r in panel if r['year']==year], panel_keys)))
replay_files=[]
for year in range(2014, 2022):
    name=f'replay_{year}.json'; replay_files.append(name)
    (SITE/name).write_text(compact(pack([r for r in replay if r['year']==year], replay_keys)))
(SITE/'sensitivity_2023.json').write_text(compact(pack(sens, sens_keys)))
(SITE/'research.json').write_text(compact(research))
manifest={
    'bundle_version':'0.3','states':states,'sectors':sectors,
    'panel_files':panel_files,'replay_files':replay_files,
    'sensitivity_file':'sensitivity_2023.json','research_file':'research.json'
}
(SITE/'manifest.json').write_text(compact(manifest))
print(f'Wrote {gzip_out} ({len(raw):,} JSON bytes -> {gzip_out.stat().st_size:,} gzip bytes)')
print(f'Wrote {len(list(SITE.iterdir()))} branch-safe browser shards to {SITE}')
