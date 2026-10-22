"""Blender-side deterministic studio lighting for actual CAD and KiCad meshes."""
import argparse, gzip, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--samples',type=int,default=96);p.add_argument('--width',type=int,default=3200);p.add_argument('--only',default='');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);ROOT=args.root;CACHE=ROOT/'.render-cache'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True;scene.cycles.seed=17;scene.cycles.max_bounces=8
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='METAL'
    if any(d.type=='METAL' for d in prefs.devices):scene.cycles.device='GPU'
except Exception:pass
scene.render.resolution_x=args.width;scene.render.resolution_y=int(args.width*.48);scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.6
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.79,.82,.76,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25

def material(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
shell=material('Illustrative satin polymer',(.19,.265,.22),0,.37)
plate=material('Illustrative satin stainless',(.56,.59,.57),.85,.32)
cap=material('Keycap clearance envelope / ivory',(.81,.80,.72),0,.31)
cell=material('Battery clearance envelope',(.34,.40,.38),.35,.4)
module=material('Module clearance envelope',(.11,.28,.24),0,.45)
plug=material('USB plug clearance envelope',(.12,.14,.13),0,.42)
materials={'case_base':shell,'case_bezel':shell,'plate_case':plate,'plate_tray':plate,'keycap_envelopes':cap,'battery_envelope':cell,'module_envelope':module,'usb_plug_envelope':plug,'case_screw_envelopes':plate,'case_base_three_bay':shell,'battery_pack_envelopes':cell}
objects={}
with gzip.open(CACHE/'cad-meshes.json.gz','rt') as f:meshes=json.load(f)
for data in meshes:
    mesh=bpy.data.meshes.new(data['name']);mesh.from_pydata([(v[0]/1000,-v[1]/1000,v[2]/1000) for v in data['vertices']],[],data['faces']);mesh.flip_normals();mesh.update()
    ob=bpy.data.objects.new(data['name'],mesh);scene.collection.objects.link(ob);ob.data.materials.append(materials[data['name']]);objects[data['name']]=[ob]
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(28));ob.select_set(False)
# KiCad GLB is in meters, y points away from the typist, and PCB top is +1.6mm.
# CAD uses y toward the typist: reflect its y for the studio view.
# KiCad already exports negative y; translate its z datum only.
before=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'mechanical/YAKB-populated.glb'))
board=[]
for ob in set(scene.objects)-before:
    if ob.type!='MESH':continue
    mesh=ob.data.copy();world=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.data=mesh
    for v in mesh.vertices:
        q=world @ v.co;v.co=(q.x,q.y,q.z-.0016)
    mesh.update();board.append(ob)
objects['pcb']=board
for ob in list(scene.objects):
    if ob.type=='EMPTY':bpy.data.objects.remove(ob,do_unlink=True)
# Matte studio cyclorama; no fake holes, logos or mechanical features.
floor_mat=material('Studio background',(.77,.78,.72),0,.72)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.016));floor=bpy.context.object;floor.name='Studio floor';floor.data.materials.append(floor_mat)

def aim(ob,at):ob.rotation_euler=(Vector(at)-ob.location).to_track_quat('-Z','Y').to_euler()
def light(name,position,power,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=position;aim(o,(.142,-.047,0))
light('Key / large softbox',(.10,.22,.42),2,.36,(1,.93,.81))
light('Fill / broad silk',(.30,-.27,.29),.8,.30,(.83,.90,1))
light('Rim / strip',(-.16,-.13,.24),1.5,.22,(1,1,.94))
camera_data=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.lens=50;camera.data.clip_start=.001;camera.data.clip_end=100

def render(name,visible,position,target=(.1425,-.0473,.005),explode=None,floor_z=-.016):
    bottom=name in ['pcb-bottom','case-bottom-render']
    for light in scene.objects:
        if light.type=='LIGHT':
            light.location.z=abs(light.location.z)*(-1 if bottom else 1)
            aim(light,(.142,-.047,-.003 if bottom else 0))
    for key,group in objects.items():
        for ob in group:ob.hide_render=key not in visible;ob.location.z=0
    if explode:
        for key,z in explode.items():
            for ob in objects[key]:ob.location.z=z
    floor.hide_render=name in ['pcb-top','pcb-bottom','case-bottom-render'];floor.location.z=floor_z
    camera.location=position;aim(camera,target)
    if name=='pcb-bottom':camera.rotation_euler.rotate_axis('Z',math.pi)
    bpy.context.view_layer.update()
    inv=camera.matrix_world.inverted();points=[inv @ (ob.matrix_world @ Vector(v)) for key in visible for ob in objects[key] for v in ob.bound_box]
    width=max(v.x for v in points)-min(v.x for v in points);height=max(v.y for v in points)-min(v.y for v in points)
    camera.data.ortho_scale=max(width,height*scene.render.resolution_x/scene.render.resolution_y)*1.16
    scene.render.filepath=str(CACHE/(name+'.png'));bpy.ops.render.render(write_still=True)

views=[
('assembly-render',['case_base','case_bezel','plate_case','pcb','keycap_envelopes'],(.41,-.33,.28),(.1425,-.0473,.005),None,-.016),
('exploded-render',['case_base','case_bezel','plate_case','pcb','module_envelope','battery_envelope','usb_plug_envelope'],(.41,-.32,.31),(.1425,-.0473,.035),{'pcb':.026,'module_envelope':.026,'usb_plug_envelope':.026,'plate_case':.055,'case_bezel':.077},-.016),
('case-interior-render',['case_base'],(.36,-.28,.34),(.1425,-.0473,-.005),None,-.016),
('case-side-render',['case_base','case_bezel','plate_case'],(.52,-.0473,.002),(.1425,-.0473,-.002),None,-.016),
('plate-render',['plate_case'],(.36,-.28,.39),(.1425,-.0473,.006),None,.004),
('pcb-top',['pcb'],(.1425,-.0473,.5),(.1425,-.0473,0),None,-.016),
('pcb-bottom',['pcb','module_envelope'],(.1425,-.0473,-.5),(.1425,-.0473,0),None,-.016),
('case-bottom-render',['case_base','case_screw_envelopes'],(.36,-.28,-.34),(.1425,-.0473,-.005),None,-.016),
('battery-study-render',['case_base_three_bay','battery_pack_envelopes'],(.36,-.28,.34),(.1425,-.0473,-.005),None,-.016)]
for values in views:
    if not args.only or values[0] in args.only.split(','):render(*values)
