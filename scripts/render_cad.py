"""Render actual generated STEP geometry with VTK; no image synthesis."""
import cadquery as cq
import vtk
from common import ROOT, keys
from generate_mechanical import box, rounded_rect

def actor(shape,color,offset=0):
    vv,ff=shape.val().tessellate(.12,.15)
    points=vtk.vtkPoints();polys=vtk.vtkCellArray()
    for v in vv:points.InsertNextPoint(v.x,v.y,v.z+offset)
    for f in ff:
        polys.InsertNextCell(3)
        for i in f:polys.InsertCellPoint(i)
    data=vtk.vtkPolyData();data.SetPoints(points);data.SetPolys(polys)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data);normals.SetFeatureAngle(40)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(*color);a.GetProperty().SetInterpolationToPhong();a.GetProperty().SetAmbient(.3);a.GetProperty().SetDiffuse(.7);a.GetProperty().SetSpecular(.18);a.GetProperty().SetSpecularPower(35)
    return a

def render(scene,name,title,caption,camera=None):
    r=vtk.vtkRenderer();r.SetBackground(.945,.94,.915)
    for s,color,dz in scene:r.AddActor(actor(s,color,dz))
    r.GetActiveCamera().SetPosition(*(camera or (460,355,280)));r.GetActiveCamera().SetFocalPoint(142,47,5 if camera else 20);r.GetActiveCamera().SetViewUp(0,0,1);r.GetActiveCamera().ParallelProjectionOn()
    r.ResetCamera();r.GetActiveCamera().Zoom(1.12)
    if camera:r.GetActiveCamera().SetParallelScale(42)
    for msg,position,size,color in [(title,(48,1020),30,(.09,.22,.23)),(caption,(48,35),17,(.3,.36,.35))]:
        text=vtk.vtkTextActor();text.SetInput(msg);text.SetDisplayPosition(*position);text.GetTextProperty().SetFontSize(size);text.GetTextProperty().SetColor(*color);r.AddActor2D(text)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(r);win.SetSize(1900,1100);win.SetMultiSamples(4);win.Render()
    buf=vtk.vtkWindowToImageFilter();buf.SetInput(win);buf.SetInputBufferTypeToRGB();buf.ReadFrontBufferOff();buf.Update()
    png=vtk.vtkPNGWriter();png.SetFileName(str(ROOT/'assets'/name));png.SetInputConnection(buf.GetOutputPort());png.Write();win.Finalize()

def main():
    m=ROOT/'mechanical'
    base=cq.importers.importStep(str(m/'case_base.step'));pcb=cq.importers.importStep(str(m/'pcb_envelope.step'));plate=cq.importers.importStep(str(m/'plate_case.step'));bezel=cq.importers.importStep(str(m/'case_bezel.step'))
    dark=(.56,.63,.6);green=(.17,.37,.27);metal=(.62,.67,.66)
    caps=[]
    for k in keys():
        w=k['width']*19.05-.8
        lower=rounded_rect(k['x']-w/2,k['y']-9.125,w,18.25,1.1,10.8,.01).faces('<Z').wires().val()
        upper=rounded_rect(k['x']-(w-3.2)/2,k['y']-7.25,w-3.2,14.5,1.2,20.5,.01).faces('<Z').wires().val()
        caps.append(cq.Solid.makeLoft([lower,upper],ruled=True))
    capshape=cq.Workplane('XY').newObject([cq.Compound.makeCompound(caps)])
    render([(base,dark,0),(pcb,green,0),(plate,metal,0),(bezel,dark,0),(capshape,(.88,.87,.81),0)],'assembly-render.png','YAKB  /  Yet Another KeyBoard','Generated CAD + simplified keycap envelopes. NiZ internals and keycap fit are not certified.')
    render([(base,dark,0),(plate,metal,0),(bezel,dark,0),(capshape,(.88,.87,.81),0)],'case-side-render.png','YAKB A0  /  Lower front, coved sides','Nominal shell front 21.4 mm / rear 25.1 mm; 1.95 degree floor slope. Keycaps are generic envelopes.',camera=(500,47,5))
    render([(base,dark,0),(pcb,green,24),(plate,metal,44),(bezel,dark,65)],'exploded-render.png','YAKB A0  /  Assembly layers','Actual generated STEP geometry: base / sensor PCB / 1.6 mm plate / HHKB bezel. Fasteners omitted.')
    render([(plate,metal,0)],'plate-render.png','YAKB A0  /  NiZ plate','14 mm R0.5 starting cutouts. Stabilizer latch openings require a real-part coupon.')
    render([(base,dark,0)],'case-interior-render.png','YAKB A0  /  Battery and component clearance','Original printed base, integral battery fence and tray supports. Module/cable fit remains a prototype check.')
    print('Rendered assembly, exploded view, plate and case interior from STEP')

if __name__=='__main__':main()
