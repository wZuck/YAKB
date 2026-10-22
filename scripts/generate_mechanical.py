"""Original parametric prototype case and NiZ plates; all dimensions in mm.

Run with CadQuery + ezdxf. Assembly retains the PCB-top z=0 datum.
Construction uses KiCad screen coordinates; delivered CAD uses x right / y rear / z up.
"""
import json, math, hashlib
import cadquery as cq
import ezdxf
from common import normalize_text, ROOT, SPEC, keys, case_screws

OUT=ROOT/"mechanical"
W,H=SPEC["pcb"]["width"],SPEC["pcb"]["height"]
M=SPEC['case']['outer_margin']
FASTEN=SPEC['case']['fastening']
SLOPE=(SPEC['case']['floor_front_z']-SPEC['case']['floor_rear_z'])/(H+2*M)
ANGLE=math.degrees(math.atan(SLOPE))
FLOOR_INTERCEPT=SPEC['case']['floor_rear_z']+M*SLOPE

def floor_z(y,inside=False):
    return FLOOR_INTERCEPT+SLOPE*y+(SPEC['case']['floor_thickness'] if inside else 0)

def plane_halfspace(above=True,inside=False,height=0):
    y1,y2=-30,H+30
    a,b=floor_z(y1,inside)+height,floor_z(y2,inside)+height
    points=[(y1,a),(y2,b),(y2,30),(y1,30)] if above else [(y1,-30),(y2,-30),(y2,b),(y1,a)]
    return cq.Workplane('YZ').polyline(points).close().extrude(W+60).translate((-30,0,0))

def case_outer():
    # A recessed lower skirt replaces the original straight box sidewall.
    profiles=[]
    for z,margin,radius in [(-16,FASTEN['minimum_skirt_margin_mm'],5),(-10.5,6.2,6),(-4.0,M,8),(7.6,M,8)]:
        shape=rounded_rect(-margin,-margin,W+2*margin,H+2*margin,radius,z,0.01)
        profiles.append(shape.faces('<Z').wires().val())
    return cq.Workplane('XY').newObject([cq.Solid.makeLoft(profiles,ruled=True)])

def box(x,y,z,dx,dy,dz):
    return cq.Workplane("XY").box(dx,dy,dz,centered=(False,False,False)).translate((x,y,z))

def rounded_rect(x,y,w,h,r,z,t):
    return cq.Workplane("XY").sketch().rect(w,h).vertices().fillet(r).finalize().extrude(t).translate((x+w/2,y+h/2,z))

def mount_cut(m,z,t):
    x,y,w,h=m["x"],m["y"],m["width"],m["height"]
    if m["name"]=="lower_left":return box(x-w/2,y-h/2,z,w,h,t)
    if abs(w-h)<1e-6:return cq.Workplane('XY').center(x,y).circle(w/2).extrude(t).translate((0,0,z))
    return cq.Workplane("XY").slot2D(w,h).extrude(t).translate((x,y,z))

def stabilizers():
    result=[]
    for k in keys():
        if k["width"]>=2:
            offset=47.625 if k["width"]==6 else 11.90625
            result.extend((k["x"]+d,k["y"]) for d in [-offset,offset])
    return result

def plate(border):
    b=rounded_rect(-border,-border,W+2*border,H+2*border,2,6,1.6)
    for k in keys():
        b=b.cut(rounded_rect(k['x']-7,k['y']-7,14,14,.5,5,4))
    # Cherry-style plate stabilizer candidate: main body + rear latch neck.
    # Exact brand/latch dimensions are NOT approved; the separate coupon is mandatory.
    for x,y in stabilizers():
        b=b.cut(box(x-3.375,y-6.15,5,6.75,12.3,4)).cut(box(x-1.65,y+6.15,5,3.3,1.2,4))
    rf=SPEC['plate']['rf_window']
    b=b.cut(rounded_rect(rf['x'],rf['y'],rf['width'],rf['height'],rf['radius'],5,4))
    if border:
        for x,y in case_screws():
            b=b.cut(cq.Workplane('XY').center(x,y).circle(2.6).extrude(4).translate((0,0,5)))
    return b

def write_dxf(border,name):
    # Export the exact CAD face, so open-edge boss reliefs and DXF cannot diverge.
    profile=plate(border).faces('<Z').wires().translate((0,0,-6)).mirror('XZ')
    cq.exporters.export(profile,str(OUT/name))
    d=ezdxf.readfile(OUT/name)
    if 'CUT' not in d.layers:d.layers.new('CUT',dxfattribs={'color':7})
    for e in d.modelspace():e.dxf.layer='CUT'
    d.saveas(OUT/name)


def main():
    pcb=rounded_rect(0,0,W,H,2,-1.6,1.6)
    for m in SPEC['mounts']:pcb=pcb.cut(mount_cut(m,-2,3))
    border=SPEC['plate']['custom_case_border'];p_custom=plate(border);p_tray=plate(0)
    base=case_outer()
    cavity=rounded_rect(-.6,-.6,W+1.2,H+1.2,2,-20,40)
    base=base.cut(cavity.intersect(plane_halfspace(inside=True)))
    # 0.3 mm plate-edge clearance; the rim closes the old exposed plate gap.
    pocket=border+.3
    base=base.cut(rounded_rect(-pocket,-pocket,W+2*pocket,H+2*pocket,2.3,6,8))
    # Plate sits on the z=6 shelf. PCB rests on post tops at z=-1.6.
    # The lower-left large slot receives a bridge under the PCB, not a post in air.
    for m in SPEC['mounts']:
        x,y=m['x'],m['y']
        if m['name']=='lower_left':
            post=box(x-7,y-10,-16,14,20,14.4).cut(mount_cut(m,-17,18))
        else:
            post=cq.Workplane('XY').center(x,y).circle(3.5).extrude(14.4).translate((0,0,-16))
            post=post.cut(cq.Workplane('XY').center(x,y).circle(1.0).extrude(18).translate((0,0,-17)))
            post=post.cut(cq.Workplane('XY').center(x,y).circle(1.65).extrude(4.5).translate((0,0,-6.1)))
        base=base.union(post)
    # Real 0805s R33 and C1 occupy the right leg of the lower-left bridge.
    # Keep its middle support, and relieve both populated ends including solder.
    bridge=next(m for m in SPEC['mounts'] if m['name']=='lower_left')
    for y in [78,91]:
        base=base.cut(box(bridge['x']+3.4,y-2.5,-6,5,5,4.6))
    fasteners=[]
    for x,y in case_screws():
        length=FASTEN['rear_screw_length_mm'] if y<0 else FASTEN['front_screw_length_mm'] if y>H else FASTEN['side_screw_length_mm']
        seat=FASTEN['screw_tip_z']-length
        base=base.cut(cq.Workplane('XY').center(x,y).circle(1.15).extrude(30).translate((0,0,-20)))
        base=base.cut(cq.Workplane('XY').center(x,y).circle(2.1).extrude(seat+20).translate((0,0,-20)))
        base=base.cut(cq.Workplane('XY').center(x,y).circle(2.45).extrude(5).translate((0,0,4.4)))
        shank=cq.Workplane('XY').center(x,y).circle(1).extrude(length).translate((0,0,seat))
        head=cq.Workplane('XY').center(x,y).circle(1.9).extrude(2).translate((0,0,seat-2))
        fasteners.append(shank.union(head))

    cx=SPEC['case']['usb_center_x']
    base=base.cut(box(cx-6,-9,-8.5,12,10,7))
    # Access window: switch is a replaceable harness, not a guessed footprint.
    base=base.cut(box(2,80,-20,11,10,15))
    # Integral battery fence is open topped, separate from the removable cell.
    bx,by,bz=SPEC['battery']['center']; bw,bh,bt=SPEC['battery']['bay']
    fence=box(bx-bw/2-1,by-bh/2-1,-16,bw+2,bh+2,16)
    fence=fence.cut(box(bx-bw/2,by-bh/2,-17,bw,bh,20))
    fence=fence.intersect(plane_halfspace(inside=True)).intersect(plane_halfspace(False,True,6))
    fence=fence.cut(box(bx-bw/2-2,by-3,floor_z(by,True)+2,5,6,10))
    base=base.union(fence)
    base=base.cut(plane_halfspace(False))
    bezel=rounded_rect(-M,-M,W+2*M,H+2*M,8,7.6,3)
    bezel=bezel.cut(box(-.7,-.7,7, W+1.4,H+1.4,5))
    # HHKB asymmetric blockers: bottom row starts at 1.5u and ends at 12.5u.
    bezel=bezel.union(box(-.7,75.9,7.6,28.4,19.4,3))
    bezel=bezel.union(box(238.0,75.9,7.6,47.7,19.4,3))
    bezel=bezel.edges('>Z').fillet(.7)
    for x,y in case_screws():
        boss=cq.Workplane('XY').center(x,y).circle(2.25).extrude(3.05).translate((0,0,4.6))
        bezel=bezel.union(boss)
        bezel=bezel.cut(cq.Workplane('XY').center(x,y).circle(1.5).extrude(3.1).translate((0,0,4.5)))
        bezel=bezel.cut(cq.Workplane('XY').center(x,y).circle(1.15).extrude(4.6).translate((0,0,4.5)))
    screws=cq.Workplane('XY').newObject([cq.Compound.makeCompound([f.val() for f in fasteners])])

    maxb=SPEC['battery']['max_envelope']
    battery=box(bx-maxb[0]/2,by-maxb[1]/2,bz-maxb[2]/2,*maxb).rotate((bx,by,bz),(bx+1,by,bz),ANGLE)
    mx,my=SPEC['module']['center'];mw,mh,mt=SPEC['module']['envelope']
    module=box(mx-mw/2,my-mh/2,-8.1,mw,mh,mt)
    plug=SPEC['module']['usb_plug']
    usbplug=box(*plug['origin'],*plug['size'])
    component_report=json.loads((ROOT/'reports/component-geometry.json').read_text())
    assert component_report['pcb_sha256']==hashlib.sha256((ROOT/'hardware/YAKB.kicad_pcb').read_bytes()).hexdigest(), 'Export current native component geometry first'
    actual_components=cq.importers.importStep(str(OUT/'components.step')).mirror('XZ')
    coupon=box(0,0,0,80,32,1.6)
    for i,sz in enumerate([13.9,14.0,14.1]):
        coupon=coupon.cut(rounded_rect(4+20*i,4,sz,sz,.5,-1,4))
    # One latch opening for a real stabilizer fit check.
    coupon=coupon.cut(box(68,4,-1,6.75,12.3,4)).cut(box(69.725,16.3,-1,3.3,1.2,4))
    parts={'pcb_envelope':pcb,'plate_case':p_custom,'plate_tray':p_tray,'case_base':base,'case_bezel':bezel,'niz_fit_coupon':coupon}
    # Explicit CAD envelopes: renders must never invent a vendor switch or cap.
    caps=[]
    for k in keys():
        width=k['width']*SPEC['pitch']-.8
        lower=rounded_rect(k['x']-width/2,k['y']-9.125,width,18.25,1.1,10.8,.01).faces('<Z').wires().val()
        upper=rounded_rect(k['x']-(width-3.2)/2,k['y']-7.25,width-3.2,14.5,1.2,20.5,.01).faces('<Z').wires().val()
        caps.append(cq.Solid.makeLoft([lower,upper],ruled=True))
    parts.update(case_screw_envelopes=screws,keycap_envelopes=cq.Workplane('XY').newObject([cq.Compound.makeCompound(caps)]),
                 battery_envelope=battery,module_envelope=module,usb_plug_envelope=usbplug)
    reports={}
    for name,part in parts.items():
        assert part.val().isValid(),name
        cq.exporters.export(part.mirror('XZ'),str(OUT/(name+'.step')))
        normalize_text(OUT/(name+'.step'))
        if name in ['case_base','case_bezel','niz_fit_coupon']:
            printable=part
            if name=='case_base':
                printable=part.rotate((0,0,0),(1,0,0),-ANGLE).translate((0,0,-FLOOR_INTERCEPT*math.cos(math.radians(ANGLE))))
            cq.exporters.export(printable.mirror('XZ'),str(OUT/(name+'.stl')),tolerance=.05,angularTolerance=.15)
        bb=part.val().BoundingBox();reports[name]={'bounds':[round(a,4) for a in [bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]],'volume_mm3':round(part.val().Volume(),3),'valid':True}
    a=cq.Assembly(name='YAKB_A0_design')
    for name,s,color in [('base',base,(.18,.22,.25)),('pcb',pcb,(.12,.35,.21)),('plate',p_custom,(.65,.66,.68)),('bezel',bezel,(.18,.22,.25)),('battery_envelope',battery,(.6,.6,.6)),('module_envelope',module,(.2,.3,.5)),('usb_plug_envelope',usbplug,(.1,.1,.1))]:
        a.add(s.mirror('XZ'),name=name,color=cq.Color(*color))
    a.add(screws.mirror('XZ'),name='bottom_screw_envelopes',color=cq.Color(.3,.3,.3))
    a.add(actual_components.mirror('XZ'),name='native_components',color=cq.Color(.3,.3,.28))
    a.export(str(OUT/'assembly.step'))
    normalize_text(OUT/'assembly.step')
    for border,name in [(0,'plate_tray.dxf'),(border,'plate_case.dxf')]:write_dxf(border,name)
    # Positive-volume intersections are a real error for these defined envelopes.
    pairs=[('base_battery',base,battery),('pcb_battery',pcb,battery),('plate_bezel',p_custom,bezel),('pcb_module',pcb,module),('base_module',base,module),('base_usbplug',base,usbplug),
           ('base_populated_components',base,actual_components),('base_pcb',base,pcb),('module_components',module,actual_components),('usbplug_components',usbplug,actual_components),('base_bezel',base,bezel),('screws_base',screws,base),('screws_bezel',screws,bezel),('screws_plate',screws,p_custom),('screws_pcb',screws,pcb),('screws_components',screws,actual_components)]
    checks={name:round(one.intersect(two).val().Volume(),6) if one.intersect(two).vals() else 0 for name,one,two in pairs}
    reports['coordinate_frames']={'construction_reports':'KiCad screen: x right, y toward typist, z above PCB','delivered_STEP_STL_DXF':'right handed: X right, Y rear, Z above PCB; CAD Y = -construction y'}
    reports['hhkb_blockers']={'left_u':1.5,'right_u':2.5,'left_solid_width_mm':28.4,'right_solid_width_mm':47.7}
    reports['envelope_intersections_mm3']=checks
    reports['minimum_clearance_mm']={name:round(one.val().distance(two.val()),4) for name,one,two in pairs if name in ['base_battery','pcb_battery','base_module','base_usbplug']}
    reports['case_profile']={'outer_plan_mm':[W+2*M,H+2*M],'corner_radius_mm':8,'typing_angle_deg':round(ANGLE,3),'front_wall_height_mm':21.4,'rear_wall_height_mm':25.1,'lower_skirt_inset_mm':round(M-FASTEN['minimum_skirt_margin_mm'],2),'floor_thickness_mm':2.4,'base_stl_orientation':'bottom plane on z=0; STEP retains PCB datum'}
    reports['hidden_fasteners']=[dict(x=x,y=y,length_mm=(FASTEN['rear_screw_length_mm'] if y<0 else FASTEN['front_screw_length_mm'] if y>H else FASTEN['side_screw_length_mm']),engagement_mm=3.0,top_skin_mm=1.5,head_recess_mm=round(FASTEN['screw_tip_z']-(FASTEN['rear_screw_length_mm'] if y<0 else FASTEN['front_screw_length_mm'] if y>H else FASTEN['side_screw_length_mm'])-2-floor_z(y),3)) for x,y in case_screws()]
    assert all(f['head_recess_mm']>=0.2 for f in reports['hidden_fasteners'])
    bb=battery.val().BoundingBox();reports['battery_world_bounds']=[round(a,4) for a in [bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]]
    reports['limitations']=['No real NiZ housing, dome, keycap, stabilizer, USB extension or RF model; physical fit remains open.','Plate R0.5/14mm and 6mm stack are reference starting dimensions, not measured vendor tolerances.','Tray plate needs case-specific retention; it is not a universal drop-in assembly.']
    (ROOT/'reports/mechanical.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(json.dumps(checks));assert all(v<.01 for v in checks.values()),'Envelope collision'

if __name__=='__main__':main()
