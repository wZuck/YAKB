"""Check the delivered CAD/STLs and provide the physical short-FPC envelope."""
import json,hashlib,struct,math
import cadquery as cq
from common import ROOT,normalize_text
from modular_common import D,I,flex_geometry,clip_y
from generate_mechanical import box,case_outer,rounded_rect

def stl_bounds(file):
 data=file.read_bytes();n=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*n
 low=[math.inf]*3;high=[-math.inf]*3
 for i in range(n):
  nums=struct.unpack_from('<12f',data,84+50*i)
  for j in [3,6,9]:
   for k in range(3):low[k]=min(low[k],nums[j+k]);high[k]=max(high[k],nums[j+k])
 return low+high

def main():
 out=ROOT/'mechanical/modular'
 def load(n):return cq.importers.importStep(str(out/(n+'.step'))).mirror('XZ')
 base=load('case_base_B1');crop=load('rear_pod_fit_coupon');expected=base.intersect(box(-7,-35,-25,96,34.4,55));crop_error=expected.cut(crop).val().Volume()+crop.cut(expected).val().Volume();assert crop_error<.01
 flex=load('shaped_fpc_envelope');envelope=case_outer().union(rounded_rect(-7,-35,96,34.4,8,-18,21.5));outside=flex.cut(envelope).val().Volume();assert outside<.01
 bb=flex.val().BoundingBox();a,b=D['flex']['contacts'];assert abs(bb.ymin-(a[1]-1.75))<1e-5 and abs(bb.ymax-(b[1]+1.75))<1e-5
 assert abs(bb.zmin+3.35)<1e-5 and abs(bb.zmax+3.05)<1e-5
 bounds={};solid_counts={}
 for name in ['case_base_B1','case_base_B1_three_bay','pod_lid_B1','rear_pod_fit_coupon']:
  solid_counts[name]=len(load(name).solids().vals());assert solid_counts[name]==1,(name,'Disconnected print bodies')
  bounds[name]=stl_bounds(out/(name+'.stl'));assert bounds[name][2]>=-.001 and abs(bounds[name][2])<.001
 # Native KiCad STEP represents constant board thickness; this adds the actual nominal end stiffeners.
 points,poly=flex_geometry(True);body=cq.Workplane('XY').polyline(poly).close().extrude(.2)
 for j,xy in enumerate([points[0],points[-1]]):
  tip=xy[1]+(-1 if j==0 else 1)*1.75;start=tip if j==0 else tip-5
  clean=[]
  for point in clip_y(poly,start,start+5):
   if not clean or math.dist(point,clean[-1])>1e-8:clean.append(point)
  if math.dist(clean[0],clean[-1])<1e-8:clean.pop()
  body=body.union(cq.Workplane('XY').polyline(clean).close().extrude(.1).translate((0,0,.2)))
 assert body.val().isValid() and len(body.solids().vals())==1;cb=body.val().BoundingBox();assert abs(cb.xlen-26.1)<1e-5 and abs(cb.ylen-25)<1e-5 and abs(cb.zlen-.3)<1e-5;file=out/'fpc_mating_coupon_envelope.step';cq.exporters.export(body.mirror('XZ'),str(file));normalize_text(file)
 inputs=['design/yakb.json','scripts/common.py','design/modular.json','design/fpc-interface.json','scripts/modular_common.py','scripts/verify_interface_samples.py','scripts/generate_mechanical.py','mechanical/modular/case_base_B1.step','mechanical/modular/rear_pod_fit_coupon.step','mechanical/modular/shaped_fpc_envelope.step']+['mechanical/modular/'+n+'.stl' for n in bounds]
 report={'print_solid_counts':solid_counts,'short_fpc_envelope_size_mm':[cb.xlen,cb.ylen,cb.zlen],'coupon_crop_difference_mm3':crop_error,'installed_flex_outside_case_envelope_mm3':outside,'installed_flex_constructed_bounds_mm':[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax],'print_STL_bounds_mm':bounds,'sample_measurements':'NONE - drawings and file geometry only','sources':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in inputs},'outputs':{str(file.relative_to(ROOT)):hashlib.sha256(file.read_bytes()).hexdigest()}}
 (ROOT/'reports/modular/sample-checks.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: coupon equals actual base crop; FPC stays within enclosure; four delivered STLs sit on bed; short FPC stiffened envelope exported.')
if __name__=='__main__':main()
