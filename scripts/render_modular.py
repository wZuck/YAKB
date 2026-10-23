"""Render B1 from saved STEP/GLB geometry; reuse the established Cycles studio."""
import gzip,json,hashlib,subprocess
from pathlib import Path
import cadquery as cq
from PIL import Image,ImageDraw,ImageFont
from common import ROOT
CACHE=ROOT/'.render-cache';OUT=ROOT/'assets/modular'

def main():
 OUT.mkdir(exist_ok=True);data=[];sources={}
 parts={'fit_coupon':'mechanical/modular/rear_pod_fit_coupon.step','base':'mechanical/modular/case_base_B1.step','lid':'mechanical/modular/pod_lid_B1.step','module':'mechanical/modular/controller_module_envelope.step','flex':'mechanical/modular/shaped_fpc_envelope.step','plug':'mechanical/modular/external_usb_plug_envelope.step','bezel':'mechanical/case_bezel.step','plate':'mechanical/plate_case.step','caps':'mechanical/keycap_envelopes.step','battery':'mechanical/battery_envelope.step'}
 for name,file in parts.items():
  shape=cq.importers.importStep(str(ROOT/file)).val();vs,fs=shape.tessellate(.04,.07);data.append(dict(name=name,vertices=[list(v.toTuple()) for v in vs],faces=fs));sources[file]=hashlib.sha256((ROOT/file).read_bytes()).hexdigest()
 with gzip.open(CACHE/'b1-meshes.json.gz','wt') as f:json.dump(data,f)
 for file in ['mechanical/YAKB-populated.glb','mechanical/modular/YAKB-controller-B1.glb','mechanical/modular/YAKB-interposer-B1.glb','design/modular.json','scripts/render_modular.py','scripts/render_modular_blender.py']:
  sources[file]=hashlib.sha256((ROOT/file).read_bytes()).hexdigest()
 blender='/Users/wzy/.cache/yakb-render-runtime/Blender.app/Contents/MacOS/Blender'
 subprocess.run([blender,'-b','--python',str(ROOT/'scripts/render_modular_blender.py'),'--','--root',str(ROOT),'--width','2600','--samples','72'],check=True)
 font='/System/Library/Fonts/Supplemental/Arial.ttf';images={}
 titles={'B1-fit-coupon':('B1.1 / REAR POD FIT COUPON','Actual cropped base / lid raised 35 mm / qualify the USB shroud, board clip and installed module height'), 'B1-closed':('B1 / DIRECT USB AT REAR-LEFT','Saved CAD / side-entry USB / keycaps and module shown as clearance envelopes'), 'B1-open':('B1 / MODULAR CONTROLLER','Main PCB raised 25 mm for inspection / shaped FPC remains at its installed height'), 'B1-top':('B1 / TRUE TOP VIEW','HHKB: left blocker 1.5u, right blocker 2.5u / rear-left pod adds 28 mm depth')}
 for name,(title,caption) in titles.items():
  raw=Image.open(CACHE/(name+'.png')).convert('RGB');w,h=raw.size;im=Image.new('RGB',(w,h+145),(239,239,232));im.paste(raw,(0,90));dr=ImageDraw.Draw(im);dr.text((64,24),title,font=ImageFont.truetype(font,32),fill=(24,55,49));dr.text((64,h+105),caption,font=ImageFont.truetype(font,23),fill=(55,75,65));path=OUT/(name+'.png');im.save(path,optimize=True);images[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
 assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in sources.items())
 (OUT/'render-manifest.json').write_text(json.dumps(dict(renderer='Blender Cycles 4.5 LTS',samples=72,width=2600,sources=sources,images=images),indent=2)+'\n')
if __name__=='__main__':main()
