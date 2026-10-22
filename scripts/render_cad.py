"""Tessellate saved STEP solids, then render them with Blender Cycles.

No generative imagery. Native KiCad GLB supplies the actual routed board.
Run after export_geometry.py. Blender path is a CLI argument or BLENDER_BIN.
"""
import argparse, gzip, hashlib, json, os, subprocess
from pathlib import Path
import cadquery as cq
from common import ROOT

CACHE=ROOT/'.render-cache';CACHE.mkdir(exist_ok=True)
PARTS=['case_base','case_bezel','plate_case','plate_tray','keycap_envelopes','battery_envelope','module_envelope','usb_plug_envelope','case_screw_envelopes','case_base_three_bay','battery_pack_envelopes']

def prepare():
    geometry=json.loads((ROOT/'reports/component-geometry.json').read_text())
    assert geometry['pcb_sha256']==hashlib.sha256((ROOT/'hardware/YAKB.kicad_pcb').read_bytes()).hexdigest(), 'Native GLB/STEP exports are stale'
    meshes=[];sources={}
    for name in PARTS:
        path=ROOT/'mechanical'/(name+'.step');shape=cq.importers.importStep(str(path)).val()
        vertices,faces=shape.tessellate(.04,.07)
        meshes.append(dict(name=name,vertices=[list(v.toTuple()) for v in vertices],faces=faces))
        b=shape.BoundingBox();sources[str(path.relative_to(ROOT))]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bounds_mm=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
    with gzip.open(CACHE/'cad-meshes.json.gz','wt') as f:json.dump(meshes,f,separators=(',',':'))
    for name in ['hardware/YAKB.kicad_pcb','mechanical/YAKB-populated.glb','design/yakb.json','scripts/render_cad.py','scripts/render_blender.py']:
        sources[name]=dict(sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest())
    return sources

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--blender',default=os.environ.get('BLENDER_BIN','blender'));p.add_argument('--samples',type=int,default=96);p.add_argument('--width',type=int,default=3200);p.add_argument('--only',default='');args=p.parse_args()
    sources=prepare()
    subprocess.run([args.blender,'-b','--python',str(ROOT/'scripts/render_blender.py'),'--','--root',str(ROOT),'--samples',str(args.samples),'--width',str(args.width),'--only',args.only],check=True)
    from PIL import Image, ImageDraw, ImageFont
    from matplotlib.font_manager import findfont, FontProperties
    fontfile=findfont(FontProperties(family='DejaVu Sans'));boldfile=findfont(FontProperties(family='DejaVu Sans',weight='bold'))
    descriptions={
      'assembly-render':('01 / YAKB','NiZ EC / 60 keys / 6u HHKB','Saved CAD with keycap clearance envelopes; cap shape and finish are illustrative.'),
      'exploded-render':('02 / ASSEMBLY','Base / populated PCB / plate / bezel','Parts separated vertically for inspection; NiZ internals and fasteners omitted.'),
      'case-interior-render':('03 / CASE INTERIOR','R8 corners / hidden bottom screws / relieved PCB bridge','Exact case_base.step geometry, including component reliefs and battery fence.'),
      'case-side-render':('04 / SIDE PROFILE','Rear 25.1 mm / front 21.4 mm / 1.95 degree floor','Dimensions are nominal plane heights; model retains the PCB-top z=0 datum.'),
      'plate-render':('05 / NiZ PLATE','1.6 mm / 14 mm R0.5 / fixed HHKB','Actual plate_case.step. Stabilizer and NiZ fit still require same-process coupons.'),
      'pcb-top':('06 / SENSOR FACE','Native KiCad geometry / 4 copper layers','Orthographic top view. EC copper remains soldermask-covered; no switch models.'),
      'case-bottom-render':('08 / HIDDEN FASTENERS','Bottom-up M2 / 20 mm rear, 18 mm sides, 16 mm front','Saved base and screw envelopes; top bezel surface is uninterrupted.'),
      'battery-study-render':('09 / OPTIONAL BATTERY BAY','Three pouch spaces / factory-built 1S2P or 1S3P pack','Actual three-bay case variant; pouches and shared protection PCB are clearance envelopes.'),
      'pcb-bottom':('07 / POPULATED FACE','Native footprints, routing, holes and component models','Orthographic bottom view, already mirrored. Module remains an explicit CAD envelope.')}
    produced={}
    for name,(title,sub,caption) in descriptions.items():
        if args.only and name not in args.only.split(','):continue
        raw=Image.open(CACHE/(name+'.png')).convert('RGB');w,h=raw.size
        top=int(w*.073);bottom=int(w*.039);canvas=Image.new('RGB',(w,h+top+bottom),(239,239,232));canvas.paste(raw,(0,top))
        draw=ImageDraw.Draw(canvas);pad=int(w*.035)
        draw.text((pad,top*.17),title,font=ImageFont.truetype(boldfile,int(w*.014)),fill=(24,55,49))
        draw.text((pad,top*.58),sub,font=ImageFont.truetype(fontfile,int(w*.0095)),fill=(84,104,92))
        draw.text((w-pad,top*.2),'YET ANOTHER KEYBOARD',anchor='ra',font=ImageFont.truetype(fontfile,int(w*.008)),fill=(84,104,92))
        draw.text((pad,top+h+bottom*.28),caption,font=ImageFont.truetype(fontfile,int(w*.0078)),fill=(84,104,92))
        path=ROOT/'assets'/(name+'.png');canvas.save(path,optimize=True);produced[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    path=ROOT/'assets/render-manifest.json'
    old=json.loads(path.read_text()) if path.exists() else {}
    assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v['sha256'] for k,v in sources.items()), 'Render inputs changed'
    if old.get('sources')!=sources or old.get('samples')!=args.samples or old.get('width')!=args.width:
        old={}
    old.update(renderer='Blender Cycles 4.5 LTS',samples=args.samples,width=args.width,tessellation_mm=.04,sources=sources)
    old.setdefault('images',{}).update(produced);path.write_text(json.dumps(old,indent=2)+'\n')

if __name__=='__main__':main()
