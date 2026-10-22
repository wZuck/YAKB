"""B1 rear pod, rigid board envelopes and flat shaped FPC; native CAD frame."""
import json,math,hashlib
import cadquery as cq
from common import ROOT,normalize_text
from modular_common import flex_geometry
from generate_mechanical import box,rounded_rect,floor_z,ANGLE,FLOOR_INTERCEPT
D=json.loads((ROOT/'design/modular.json').read_text());OUT=ROOT/'mechanical/modular'

def plane_halfspace(above=True,inside=False,height=0):
 # B1 extends beyond A0's -30 mm helper domain; cover the complete pod.
 y1,y2=-60,160;a,b=floor_z(y1,inside)+height,floor_z(y2,inside)+height
 points=[(y1,a),(y2,b),(y2,30),(y1,30)] if above else [(y1,-30),(y2,-30),(y2,b),(y1,a)]
 return cq.Workplane('YZ').polyline(points).close().extrude(350).translate((-30,0,0))

def load(name):return cq.importers.importStep(str(ROOT/'mechanical'/(name+'.step'))).mirror('XZ')
def bez(t):
 p=D['flex']['controls'];u=1-t
 return (u*u*u*p[0][0]+3*u*u*t*p[1][0]+3*u*t*t*p[2][0]+t*t*t*p[3][0],u*u*u*p[0][1]+3*u*u*t*p[1][1]+3*u*t*t*p[2][1]+t*t*t*p[3][1])

def main():
 OUT.mkdir(exist_ok=True);base=load('case_base')
 # Open the old rear-left wall into the new pod, including the obsolete USB hole.
 base=base.cut(box(-.6,-8,-12.5,83.2,8,16))
 outer=rounded_rect(-7,-35,96,34.4,8,-18,21.5)
 cavity=rounded_rect(-4.5,-32.5,91,29.4,5.5,-18,22)
 pod=outer.cut(cavity.intersect(plane_halfspace(inside=True))).cut(plane_halfspace(False))
 base=base.union(pod)
 # Module USB plugs straight through the left side of the rear pod.
 base=base.cut(box(-10,-21.5,-4.95,11,12,8))
 for x,y in D['carrier']['mounts']:
  y-=28
  post=cq.Workplane('XY').center(x,y).circle(3).extrude(14).translate((0,0,-18)).intersect(plane_halfspace()).intersect(box(x-4,y-4,-18,8,8,12.8))
  base=base.union(post).cut(cq.Workplane('XY').center(x,y).circle(1.5).extrude(3).translate((0,0,-8.2)))
 # Support the USB end: a 48 mm unsupported FR4 cantilever is unsuitable for plug loads.
 for y,depth in [(-28,3),(-6,3)]:base=base.union(box(1,y,-18,4,depth,12.8).intersect(plane_halfspace()))
 # Front lip captures the edge with 0.30 mm nominal vertical play; rear is captured by the lid.
 base=base.union(box(1,-3.8,-18,4,.8,15).intersect(plane_halfspace())).union(box(1,-4.6,-3.9,4,1.6,.9))
 lid=rounded_rect(-7,-35,96,27.7,8,3.5,2.4)
 lid=lid.union(cq.Workplane('XY').center(3,-26.5).circle(1.5).extrude(7.4).translate((0,0,-3.9)))
 for x,y in D['pod']['lid_screws']:
  # A raised collar leaves 2.5 mm of bearing material above the recessed head seat.
  base=base.union(cq.Workplane('XY').center(x,y).circle(3.5).extrude(7.5).translate((0,0,-18)).intersect(plane_halfspace()))
  # M2x16 from below; insert bore is blind to the lid top.
  base=base.cut(cq.Workplane('XY').center(x,y).circle(1.15).extrude(25).translate((0,0,-18)))
  base=base.cut(cq.Workplane('XY').center(x,y).circle(2.1).extrude(5).translate((0,0,-18)))
  base=base.cut(cq.Workplane('XY').center(x,y).circle(2.5).extrude(5).translate((0,0,.3)))
  lid=lid.union(cq.Workplane('XY').center(x,y).circle(2.25).extrude(3).translate((0,0,.5)))
  lid=lid.cut(cq.Workplane('XY').center(x,y).circle(1.5).extrude(3).translate((0,0,.5)))
 cb=D['carrier'];ib=D['interposer']
 carrier=box(*cb['world_origin'],*cb['size'],1)
 for x,y in cb['mounts']:carrier=carrier.cut(cq.Workplane('XY').center(x,y-28).circle(1.15).extrude(3).translate((0,0,-6.2)))
 interposer=box(*ib['world_origin'],*ib['size'],1)
 # Native exports include actual connector/resistor/capacitor library solids.
 populated={}
 for key,stem,origin in [('controller_populated','YAKB-controller-B1',cb['world_origin']),('interposer_populated','YAKB-interposer-B1',ib['world_origin'])]:
  populated[key]=cq.importers.importStep(str(OUT/(stem+'-native.step'))).mirror('XZ').translate(origin)
 screws=cq.Workplane('XY')
 pieces=[]
 for x,y in cb['mounts']:
  y-=28
  pieces.extend([cq.Workplane('XY').center(x,y).circle(1).extrude(4).translate((0,0,-8.2)).val(),cq.Workplane('XY').center(x,y).circle(1.9).extrude(1.8).translate((0,0,-4.2)).val()])
 for x,y in D['pod']['lid_screws']:
  pieces.extend([cq.Workplane('XY').center(x,y).circle(1).extrude(16).translate((0,0,-13)).val(),cq.Workplane('XY').center(x,y).circle(1.9).extrude(2).translate((0,0,-15)).val()])
 screws=cq.Workplane(obj=cq.Compound.makeCompound(pieces))
 module=box(.25,-24.5,-4.2,33.5,18,6.5)
 plug=box(*D['usb']['insertion_envelope_origin'],*D['usb']['insertion_envelope_size'])
 points,poly=flex_geometry()
 flex=cq.Workplane('XY').polyline(poly).close().extrude(.2).translate((0,0,D['flex']['world_z']-.1))
 base=base.cut(cq.Workplane('XY').polyline(poly).close().extrude(1).translate((0,0,-3.8)))
 parts={'case_base_B1':base,'pod_lid_B1':lid,'controller_pcb':carrier,'interposer_pcb':interposer,'controller_module_envelope':module,'external_usb_plug_envelope':plug,'shaped_fpc_envelope':flex,'pod_screw_envelopes':screws,**populated}
 three_bay=base.union(load('case_base_three_bay').cut(load('case_base')))
 parts['case_base_B1_three_bay']=three_bay
 assembly=cq.Assembly(name='YAKB_B1_MODULAR')
 for name,part in parts.items():
  assert part.val().isValid(),name
  actual=part.mirror('XZ');cq.exporters.export(actual,str(OUT/(name+'.step')));normalize_text(OUT/(name+'.step'))
  if name in ['case_base_B1','pod_lid_B1','case_base_B1_three_bay']:
   printable=part
   if name=='pod_lid_B1':printable=part.rotate((0,0,0),(1,0,0),180).translate((0,0,5.9))
   if name.startswith('case_base_B1'):printable=part.rotate((0,0,0),(1,0,0),-ANGLE).translate((0,0,-FLOOR_INTERCEPT*math.cos(math.radians(ANGLE))))
   assert printable.val().BoundingBox().zmin>=-.001,(name,'print floor protrusion',printable.val().BoundingBox().zmin)
   cq.exporters.export(printable.mirror('XZ'),str(OUT/(name+'.stl')),tolerance=.05,angularTolerance=.15)
  if name not in ['controller_pcb','interposer_pcb','case_base_B1_three_bay']:
   assembly.add(actual,name=name,color=cq.Color(*((.2,.3,.24) if 'case' in name or 'lid' in name else (.68,.48,.19) if 'fpc' in name else (.15,.4,.3))))
 for name in ['pcb_envelope','components','plate_case','case_bezel','keycap_envelopes','battery_envelope']:
  assembly.add(load(name).mirror('XZ'),name=name,color=cq.Color(*((.8,.8,.72) if name=='keycap_envelopes' else (.2,.35,.26))))
 assembly.export(str(OUT/'assembly_B1.step'));normalize_text(OUT/'assembly_B1.step')
 checks={}
 for name,a,b in [('carrier_base',carrier,base),('module_base',module,base),('module_lid',module,lid),('interposer_base',interposer,base),('flex_base',flex,base),('plug_base',plug,base),('base_lid',base,lid),('carrier_main',carrier,load('pcb_envelope')),('module_main',module,load('pcb_envelope')),('flex_main',flex,load('pcb_envelope')),('flex_battery',flex,load('battery_envelope')),('flex_components',flex,load('components')),('carrier_main_screws',carrier,load('case_screw_envelopes')),
 ('controller_populated_base',populated['controller_populated'],base),('controller_populated_lid',populated['controller_populated'],lid),('interposer_populated_base',populated['interposer_populated'],base),('interposer_populated_main',populated['interposer_populated'],load('pcb_envelope')),('interposer_populated_components',populated['interposer_populated'],load('components')),('flex_all_batteries',flex,load('battery_pack_envelopes')),('flex_pod_screws',flex,screws),('screws_module',screws,module),('screws_main',screws,load('pcb_envelope')),('screws_base',screws,base),('screws_lid',screws,lid),('flex_three_bay_base',flex,three_bay)]:
  v=a.intersect(b).val().Volume();checks[name]=round(v,6)
 seat_checks={}
 for i,(x,y) in enumerate(D['pod']['lid_screws']):
  ring=cq.Workplane('XY').center(x,y).circle(1.9).circle(1.15).extrude(2).translate((0,0,-12.9))
  seat_checks[str(i+1)]=round(ring.cut(base).val().Volume(),6)
 assert all(v<.01 for v in seat_checks.values()),seat_checks
 report={'lid_head_seat_missing_material_mm3':seat_checks,'lid_head_seat_bearing_thickness_mm':2.5,'intersections_mm3':checks,'usb_direction':'left side, rear pod; direct module connection; no USB extension','outer_plan_bounds_mm':[-7,-35,292,101.6],'mainboard_population':'U1 omitted; interposer takes its place','pin_map':'A:n -> B:25-n','fpc_centerline_length_mm':sum(math.dist(a,b) for a,b in zip(points,points[1:])),'limitations':['Connector contact height, insertion depth and terminal stiffener require samples/vendor drawing qualification.','nice!nano is a clearance envelope; USB socket face and module standoff height must be measured before fabrication.','Flex-to-connector mating and header engagement are intentional interfaces, not covered by zero-intersection assertions.']}
 files=['design/modular.json','design/yakb.json','scripts/generate_modular_mechanical.py','scripts/modular_common.py','scripts/generate_mechanical.py']+['mechanical/'+n+'.step' for n in ['case_base','case_base_three_bay','pcb_envelope','components','plate_case','case_bezel','keycap_envelopes','battery_envelope','battery_pack_envelopes','case_screw_envelopes']]+['mechanical/modular/'+n+'-native.step' for n in ['YAKB-controller-B1','YAKB-interposer-B1']]
 report['sources']={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
 report['outputs']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [OUT/(name+'.step') for name in parts]+[OUT/'assembly_B1.step']+[OUT/(name+'.stl') for name in ['case_base_B1','case_base_B1_three_bay','pod_lid_B1']]}
 (ROOT/'reports/modular-mechanical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert all(v<.01 for v in checks.values()),checks

if __name__=='__main__':main()
