"""Save native copper geometry and a compact physical-pin connectivity report."""
import json,hashlib
import pcbnew as p,wx
from common import ROOT,SPEC
from circuit import components

def geometry_hash():
 payload={k:SPEC[k] for k in ['pcb','pitch','rows','mounts']};payload['components']=components()
 payload['antenna_keepout']=SPEC['module']['antenna_keepout']
 return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
def main():
 app=wx.App(False);b=p.LoadBoard(str(ROOT/'hardware/YAKB.kicad_pcb'));tracks=[]
 for t in b.GetTracks():
  r={'net':t.GetNetname(),'locked':t.IsLocked()}
  if isinstance(t,p.PCB_VIA):r.update(via=True,at=[p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)],width=p.ToMM(t.GetWidth(p.F_Cu)),drill=p.ToMM(t.GetDrillValue()))
  else:r.update(layer=b.GetLayerName(t.GetLayer()),a=[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],b=[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)],width=p.ToMM(t.GetWidth()))
  tracks.append(r)
 (ROOT/'design/routing.json').write_text(json.dumps({'geometry_sha256':geometry_hash(),'copper_layers':b.GetCopperLayerCount(),'tracks':tracks},indent=2)+'\n')
 pins={(f.GetReference(),a.GetNumber()):a.GetNetname() for f in b.GetFootprints() for a in f.Pads() if a.GetNumber() and a.GetNetname() and not a.GetNetname().startswith('unconnected-')}
 (ROOT/'reports/pcb-connectivity.json').write_text(json.dumps({'copper_layers':b.GetCopperLayerCount(),'pins':[{'ref':r,'pin':pin,'net':net} for (r,pin),net in sorted(pins.items())],'track_count':sum(not r.get('via') for r in tracks),'via_count':sum(bool(r.get('via')) for r in tracks),'min_width_mm':min(r['width'] for r in tracks if not r.get('via')),'min_via_mm':min(r['width'] for r in tracks if r.get('via')),'min_drill_mm':min(r['drill'] for r in tracks if r.get('via'))},indent=2)+'\n')
 print('Exported',len(tracks),'copper items and',len(pins),'physical pins')
if __name__=='__main__':main()
