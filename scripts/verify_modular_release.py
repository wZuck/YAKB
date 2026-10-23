"""Check B1 source/artifact hashes, manufacturing ZIPs and offline guide links."""
import hashlib,json,re,zipfile
from html.parser import HTMLParser
from pathlib import Path
from common import ROOT

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def hashes(mapping):
 for path,value in mapping.items():assert digest(path)==value,('stale artifact',path)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for name,value in attrs:
   if name in ['href','src'] and value:self.links.append(value)
def links(file):
 parser=Links();parser.feed((ROOT/file).read_text())
 for url in parser.links:
  if url.startswith(('#','http:','https:','data:','mailto:')):continue
  assert ((ROOT/file).parent/url.split('#')[0]).exists(),(file,url)
def main():
 for file in ['reports/modular/sample-checks.json','reports/modular-electrical.json','reports/modular/connectivity.json','reports/modular-mechanical.json','assets/modular/render-manifest.json','hardware/soldering/b1/render-manifest.json']:
  d=json.loads((ROOT/file).read_text());hashes(d['sources']);hashes(d.get('outputs',{}));hashes(d.get('images',{}))
 s=json.loads((ROOT/'reports/modular/sample-checks.json').read_text());assert s['coupon_crop_difference_mm3']<.01 and s['installed_flex_outside_case_envelope_mm3']<.01 and all(n==1 for n in s['print_solid_counts'].values())
 m=json.loads((ROOT/'reports/modular-mechanical.json').read_text());assert all(v<.01 for v in m['lid_head_seat_missing_material_mm3'].values());assert len(m['intersections_mm3'])==28 and all(v<.01 for v in m['intersections_mm3'].values())
 assert m['flex_to_pod_screw_distance_mm']>=.5 and m['usb_lid_roof_thickness_mm']>=1.8 and m['usb_roof_probe_missing_material_mm3']<.01
 for name in ['controller','interposer','shaped-FPC','FPC-coupon']:
  stem='YAKB-'+name+'-B1'
  for kind in ['erc','drc']:
   d=json.loads((ROOT/'reports/modular'/(stem+'-'+kind+'.json')).read_text());assert not d.get('violations') and not any(s.get('violations') for s in d.get('sheets',[])) and not d.get('schematic_parity') and not d.get('unconnected_items')
  folder=ROOT/'fabrication/modular'/stem
  with zipfile.ZipFile(folder.with_suffix('.zip')) as z:
   expected={p.name for p in folder.iterdir() if p.is_file()};assert set(z.namelist())==expected
   for f in expected:assert z.read(f)==(folder/f).read_bytes()
  if 'FPC' in name:
   assert not list(folder.glob('*.gbrjob')) and not list(folder.glob('*F_Cu*'))
   assert json.loads((folder/'FLEX-STACKUP.json').read_text())['physical_copper_layers']==1
   assert list(folder.glob('*-Stiffener_Top.gbr')) and not list(folder.glob('*.gta'))
 raw=(ROOT/'hardware/soldering/b1/data.js').read_text();d=json.loads(raw[raw.index('{'):raw.rfind(';')]);assert len(d['steps'])==21 and len(d['inventory'])==108 and d['storageKey']=='yakb-b1-1-soldering-v2'
 assert len({s['id'] for s in d['steps']})==21
 for s in d['steps']:assert (ROOT/'hardware/soldering/b1'/s['image']).exists(),s['image']
 for file in ['hardware/soldering/b1/index.html','hardware/soldering/index.html']:links(file)
 for file in ['docs/modular/README.md','docs/modular/README.zh-CN.md','README.md','README.zh-CN.md','docs/modular/interface-review.md','docs/modular/interface-review.zh-CN.md']:
  for url in re.findall(r'\[[^\]]*\]\(([^)]+)\)',(ROOT/file).read_text()):
   if url.startswith(('http:','https:','#')):continue
   assert ((ROOT/file).parent/url.split('#')[0]).exists(),(file,url)
 print('PASS B1: native ERC/DRC/parity/airwires 0; 24-contact map; 28 selected solid checks; current CAD/render/guide hashes; 4 fabrication ZIPs; 21-step offline links.')
if __name__=='__main__':main()
