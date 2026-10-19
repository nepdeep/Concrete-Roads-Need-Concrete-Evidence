"""Package the static study and a self-contained HTML reading copy. Python stdlib only."""
from pathlib import Path
import json, shutil, zipfile

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'road-decisions-nepal'/'dist'
DOWNLOADS=DIST/'downloads'
DOWNLOADS.mkdir(parents=True,exist_ok=True)

def clean(s):
    if isinstance(s,str):
        for a,b in [('Ã—','×'),('â€“','–'),('â€”','—'),('â‰¥','≥'),('Â±','±'),('Â²','²'),('Â³','³')]: s=s.replace(a,b)
    elif isinstance(s,list): s=[clean(x) for x in s]
    elif isinstance(s,dict): s={k:clean(v) for k,v in s.items()}
    return s

results=clean(json.loads((ROOT/'models/results.json').read_text(encoding='utf-8')))
sources=[]
seen=set()
for filename in ['sources-nepal.json','sources-engineering.json']:
    rows=json.loads((ROOT/'research'/filename).read_text(encoding='utf-8'))['sources']
    for row in rows:
        url=row.get('url','')
        title=row['title']
        # Prefer the Nepal record when titles overlap.
        fingerprint=('flexible' if 'flexible pavement' in title.lower() else 'rigid' if 'rigid pavement' in title.lower() else title.lower())
        if fingerprint in seen: continue
        seen.add(fingerprint)
        facts=row.get('supported_facts',[])
        description=' '.join(facts[:2]) if facts else row.get('verified','')
        sources.append(dict(title=title,publisher=row.get('publisher',''),url=url,
            date=row.get('publication_date',row.get('date','Undated')),description=description,
            locator=row.get('locator','; '.join(row.get('locators',[]))),limitation=row.get('limitations',row.get('caution',''))))
data={'results':results,'sources':clean(sources)}
(DIST/'data.js').write_text('window.RESEARCH_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n',encoding='utf-8')
solver=(ROOT/'models/pavement_model.js').read_text(encoding='utf-8').replace('export function evaluatePavements','window.evaluatePavements = function evaluatePavements')
(DIST/'pavement_model.js').write_text(solver,encoding='utf-8')
for folder in ['research','models']:
    for p in (ROOT/folder).iterdir():
        if p.is_file() and p.suffix in ['.md','.json','.csv','.py','.js','.mjs']:
            shutil.copy2(p,DOWNLOADS/p.name)
# Clean packing list includes sources for reproducibility, without private credentials or caches.
with zipfile.ZipFile(DOWNLOADS/'research-package.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in ['research','models']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts: z.write(p,p.relative_to(ROOT))

html=(DIST/'index.html').read_text(encoding='utf-8')
html=html.replace('250 mm example</span></div><div class="layer subbase"','200 mm example</span></div><div class="layer subbase"')
html=html.replace('In each environment compare matched 1 km asphalt and 1 km concrete sections: 6 km total.','In each environment compare three matched pairs, each with 0.5 km asphalt and 0.5 km concrete: 9 km total.')
html=html.replace('<option value="6">Every 6 years — better performance</option>','<option value="5">Every 5 years — tests the reversal</option><option value="6">Every 6 years — better performance</option>') if 'value="5">Every 5 years' not in html else html
html=html.replace('<link rel="stylesheet" href="styles.css">','<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="study.css">') if 'href="study.css"' not in html else html
html=html.replace('<details open><summary>What is inside this calculation?</summary>','<details><summary>What is inside this calculation?</summary>')
html=html.replace('utility relocation and future routine maintenance.','utility relocation and routine maintenance beyond the two-year pilot allowance.')
if 'id="sensitivity-warning"' not in html:
    html=html.replace('<div id="cost-verdict" class="cost-verdict"></div>','<div id="cost-verdict" class="cost-verdict"></div><div class="sensitivity-callout" id="sensitivity-warning"><p><strong>The key reversal:</strong> at baseline rates and 5% discount, changing stressed-asphalt renewal from 4 to 5 years makes uniform asphalt cheaper than the targeted portfolio. Test it in the controls.</p></div>')
if 'downloads/study.html' not in html:
    html=html.replace('<a href="downloads/decision-report.md" download>','<a href="downloads/study.html" download>Save this interactive HTML</a><a href="downloads/decision-report.md" download>')
(DIST/'index.html').write_text(html,encoding='utf-8')
standalone=html
for css in ['styles.css','study.css']:
    standalone=standalone.replace(f'<link rel="stylesheet" href="{css}">','<style>\n'+(DIST/css).read_text(encoding='utf-8')+'\n</style>')
for js in ['data.js','pavement_model.js','app.js']:
    standalone=standalone.replace(f'<script src="{js}" defer></script>','<script>document.addEventListener("DOMContentLoaded",()=>{\n'+(DIST/js).read_text(encoding='utf-8').replace('</script','<\\/script')+'\n});</script>')
# Downloads in the standalone copy link to the hosted matching files; all study interactions remain offline.
origin='https://nepal-road-decisions.nimble-lake-3747.chatgpt.site/'
standalone=standalone.replace('href="downloads/','href="'+origin+'downloads/').replace("url:'downloads/","url:'"+origin+'downloads/')
(ROOT/'study.html').write_text(standalone,encoding='utf-8')
shutil.copy2(ROOT/'study.html',DOWNLOADS/'study.html')
print(json.dumps({'sources':len(sources),'standalone_bytes':(ROOT/'study.html').stat().st_size,'zip_bytes':(DOWNLOADS/'research-package.zip').stat().st_size}))
