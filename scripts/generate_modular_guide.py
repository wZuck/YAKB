"""B1 variant of the existing offline workbench; native PCB drawings only."""
import json,csv,copy,hashlib,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Polygon,FancyBboxPatch
from matplotlib.transforms import Affine2D
from common import ROOT
from modular_common import flex_geometry,I,clip_y
OUT=ROOT/'hardware/soldering/b1';ASSETS=ROOT/'assets/modular'

def drawings():
 data=json.loads((ROOT/'.render-cache/modular-native-geometry.json').read_text())
 for key,d in data.items():
  fig,ax=plt.subplots(figsize=(8,8) if key=='FPC-coupon' else (15,5 if key!='shaped-FPC' else 8),facecolor='#eeeee7');ax.set_facecolor('#eeeee7')
  if key in ['shaped-FPC','FPC-coupon']:_,poly=flex_geometry(key=='FPC-coupon');shape=Polygon(poly,facecolor='#665022',edgecolor='#183c32',lw=1)
  else:shape=Rectangle((0,0),82 if key=='controller' else 40,24 if key=='controller' else 19,facecolor='#174c42',edgecolor='#0b2924',lw=2)
  ax.add_patch(shape)
  if key in ['shaped-FPC','FPC-coupon']:
   pts,poly=flex_geometry(key=='FPC-coupon')
   for j,xy in enumerate([pts[0],pts[-1]]):
    tip=xy[1]+(-1 if j==0 else 1)*1.75;start=tip if j==0 else tip-5
    ax.add_patch(Polygon(clip_y(poly,start,start+5),facecolor='none',edgecolor='#39c6c0',lw=1,linestyle='--',zorder=6))
  for t in d['tracks']:
   x,y=t['x1'],t['y1'];ex,ey=t['x2'],t['y2'];r=t['width']/2;length=math.hypot(ex-x,ey-y);color='#d7b367' if t['layer']=='F.Cu' else '#74aaa1'
   if length:
    dx=-(ey-y)/length*r;dy=(ex-x)/length*r;ax.add_patch(Polygon([(x+dx,y+dy),(ex+dx,ey+dy),(ex-dx,ey-dy),(x-dx,y-dy)],facecolor=color,edgecolor='none',zorder=2))
   for xx,yy in [(x,y),(ex,ey)]:ax.add_patch(Circle((xx,yy),r,facecolor=color,edgecolor='none',zorder=2))
   if t.get('drill'):ax.add_patch(Circle((x,y),t['drill']/2,facecolor='#eeeee7',edgecolor='none',zorder=4))
  for pad in d['pads']:
   x,y,w,h=pad['x'],pad['y'],pad['w'],pad['h']
   if pad['circle']:patch=Circle((x,y),w/2)
   else:patch=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0,rounding_size='+str(pad['radius']));patch.set_transform(Affine2D().rotate_deg_around(x,y,-pad['angle'])+ax.transData)
   patch.set_facecolor('#f1d79b');patch.set_edgecolor('none');patch.set_zorder(3);ax.add_patch(patch)
   if pad['drill']:ax.add_patch(Circle((x,y),pad['drill']/2,facecolor='#eeeee7',edgecolor='none',zorder=4))
   if pad['number']=='1':ax.add_patch(Circle((x,y),min(max(w,h)*.7,max(min(w,h)*.8,.6)),facecolor='none',edgecolor='white',lw=1,zorder=5))
  if key not in ['shaped-FPC','FPC-coupon']:
   refs={a['ref'] for a in d['pads']}
   for ref in refs:
    pts=[a for a in d['pads'] if a['ref']==ref];x=sum(a['x'] for a in pts)/len(pts);y=sum(a['y'] for a in pts)/len(pts);ax.text(x,y,ref,fontsize=11,weight='bold',ha='center',va='center',color='white',bbox=dict(facecolor='#173c32',edgecolor='none',alpha=.8,pad=2),zorder=6)
  ax.set_aspect('equal');ax.autoscale_view();ax.invert_yaxis();ax.axis('off');fig.suptitle(('YAKB B1.1 / FPC MATING COUPON' if key=='FPC-coupon' else 'YAKB B1.1 / '+key.upper()+' / NATIVE PCB TOP VIEW'),x=.07,ha='left',color='#183c32',fontsize=17,weight='bold');fig.text(.07,.035,('Single B.Cu / dashed cyan = opposite-face stiffener / tabs25mm, fingers0.7x3.5mm / white ring=pin1' if key in ['shaped-FPC','FPC-coupon'] else 'Native pads, drill centres and both copper layers. White ring = pin 1. X right / Y toward typist.'),color='#405e50',fontsize=10)
  fig.savefig(ASSETS/('B1-'+key+'-plan.png'),dpi=170,bbox_inches='tight',facecolor=fig.get_facecolor());plt.close(fig)

def main():
 OUT.mkdir(exist_ok=True);drawings();raw=(ROOT/'hardware/soldering/data.js').read_text();d=json.loads(raw[raw.index('{'):raw.rfind(';')]);d['storageKey']='yakb-b1-1-soldering-v1';old=copy.deepcopy(d['steps'])
 steps=old[:12]
 for s in steps:s['image']='../'+s['image']
 def extra(title,subtitle,refs,instructions,checkpoint,image):
  s=copy.deepcopy(old[12]);s.update(title=title,subtitle=subtitle,refs=refs,parts=refs,count=str(len(refs))+' 类 / 位置',summary=instructions[0],instructions=instructions,checkpoint=checkpoint,image='../../../assets/modular/'+image,imageNote='B1 NATIVE PCB / actual saved pad and route geometry');return s
 steps.append(extra('主板转接板，原 U1 不装主控','INTERPOSER / 47Ω + 24 pins',['I.R1','I.JF1','I.JMAIN'],['先在转接板焊 47Ω，再对照1脚焊 JF1；1mm脚距需放大检查锡桥。','原主板 U1 只接转接板，不能同时安装 nice!nano。','用绝缘夹具保持主板底面到转接板顶面2.6mm净距，焊24根直针后剪齐。','转接板JF1与47Ω朝主板，按原生孔位安装，不翻转焊盘顺序。'],'未取得连接器插接图或小样实配前，停止软板采购。','B1-interposer-plan.png'))
 steps.append(extra('独立载板的两颗电容','CARRIER / 0805',['C.C1','C.C2'],['C1=1nF C0G，ADC_FLEX对GND；C2=100nF X7R，VCC对GND。','先完成低矮件并清洁焊盘；不要将1nF误装成1µF。'],'两个网络均不是电池正极。','B1-controller-plan.png'))
 steps.append(extra('载板插座与唯一主控','CARRIER / nice!nano v2',['C.JF1','C.U1'],['载板JF1对准1脚；先固定锚脚，逐针检查24脚与GND锚脚。','nice!nano装载板顶面，USB朝左、天线朝右；用实际模块核对USB口高度。','保持模型的模块/焊接安装总高度≤6.5mm；BOOST不桥接。','先做未通电的USB插头与外壳开口实配；若改变安装高度，重新检查FPC高度和净空。'],'全键盘仅一块MCU；不要在主板U1上再装模块。','B1-controller-plan.png'))
 steps.append(extra('FPC 接触面与逐针检查','NO POWER / A:n → B:25−n',['FPC1'],['先加工YAKB-FPC-coupon-B1短试片，验证两端锁止、接触和线序；再加工整条异形FPC。','电池和USB均断开；用原生逐针CSV逐项测A1→B24至A24→B1。','载板为A，转接板为B；两端底接触，确认露铜面朝触点，再锁止ZIF。','两根BAT_SW及七根GND在刚性板并联，软板自身各导体独立；检查正极未接地。','FPC平面曲线为定制外形，不用通用直排线强折；装入实际CAD通道，不压在螺丝帽和电池上。','禁止带电插拔，禁止按商品同面/反面名称猜线序。'],'端部25mm、铜指0.7×3.5mm、定位耳、0.30±0.05mm成品厚度按厂家图；先用短FPC试片验配。','B1-shaped-FPC-plan.png'))
 for s in old[13:]:
  if s['image'].startswith('step-'):s['image']='../'+s['image']
  else:s['image']='../../../assets/modular/B1-open.png'
  steps.append(s)
 steps[17]['instructions']=['电池断开，先只接载板USB；从100mA限流开始。','测载板VCC、主板U1-21、U2-16、U3-16标称3.3V；U1-23和J1-2为GND。','主板U1现在是转接针位；ADC到载板间有47Ω，载板ADC对地有1nF。','测试USB枚举及Fn+5 USB输出，再测模拟电源时序和噪声。']
 steps[-2]['instructions'].append('分别记录充电、纯USB、纯电池时ADC空载和按下分布；FPC地线压降可能使基线偏移。')
 steps[-1]['instructions']=['先将载板USB端前板边插入塑料卡唇，再落下载板；断电安装4颗载板M2×4和4颗3mm长M2嵌件；螺丝头≤Ø3.8×1.8mm。','后舱盖用底部2颗M2×16和2颗3mm嵌件锁入，螺丝头≤Ø3.8×2mm。','保留A0上框8颗底部隐藏螺丝：后3颗M2×20、两侧2颗M2×18、前3颗M2×16。','主板转接处必须绝缘定高，FPC不受拉、不压电池，不侵入载板天线禁布区。','只使用工厂成组并带单保护板的1S2P/1S3P包；单路接J1。','左挡块1.5u、右挡块2.5u；最后安装全部NiZ机构并校准60键。','先用rear_pod_fit_coupon.stl和现有后舱盖验证：插头塑料包络≤12×8mm，壳孔14×10mm；量实物USB口中心和凹入深度，不能只看模型。','USB从后左角左侧直接接入主控；闭壳检查插拔、充电温升和BLE输入。']
 steps[-1]['checkpoint']='原生检查不代替连接器配合、轴体、充电温升、无线和续航实测。'
 for i,s in enumerate(steps,1):s['id']='b1-step-%02d'%i;s['code']='%02d'%i
 d['steps']=steps
 for row in d['inventory']:
  if row['ref']=='U1':row.update(value='DNP — install interposer only',note='B1不装主控；此处接I.JMAIN',step='13')
  elif int(row['step'])>=14:row['step']='%02d'%(int(row['step'])+3)
 for prefix,board,stage in [('C.','controller','15'),('I.','interposer','13')]:
  geometry=json.loads((ROOT/'.render-cache/modular-native-geometry.json').read_text())[board]
  for ref in sorted({a['ref'] for a in geometry['pads'] if not a['ref'].startswith('H')}):
   pts=[a for a in geometry['pads'] if a['ref']==ref];d['inventory'].append(dict(ref=prefix+ref,step='14' if prefix=='C.' and ref.startswith('C') else stage,phase='P3',value={'C.C1':'1nF C0G','C.C2':'100nF','I.R1':'47Ω','C.U1':'nice!nano v2','I.JMAIN':'24 pins / main U1 DNP'}.get(prefix+ref,'Molex 200528-0240'),footprint='native B1 PCB',side=board+' TOP',x=sum(a['x'] for a in pts)/len(pts),y=sum(a['y'] for a in pts)/len(pts),note='坐标为该小板本地坐标；核对1脚',type='populate',nets=' '.join(sorted({a['net'] for a in pts}))))
 (OUT/'data.js').write_text('window.YAKB_GUIDE = '+json.dumps(d,ensure_ascii=False,indent=2)+';\n')
 with (OUT/'placement-checklist.csv').open('w',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(d['inventory'][0]),lineterminator='\n');w.writeheader();w.writerows(d['inventory'])
 s=(ROOT/'hardware/soldering/index.html').read_text();s=s.replace('../../','../../../').replace('href="styles.css"','href="../styles.css"').replace('src="app.js"','src="../app.js"').replace('A0','B1.1').replace('18步','21步').replace('>18<','>21<').replace('0 / 18','0 / 21').replace('>40<','>46<').replace('40 个实装位置','46 个实装位置（另列原U1不装主控）').replace('>13<','>16<').replace('2026-10-22','2026-10-23')
 s=s.replace('正常后再接内部延长线。','B1直接接后左主控，无内部USB延长线。').replace('先试片，再备料。','先确认插接，再备料。').replace('确认 NiZ 卡扣、板厚、胶碗、锥簧和卫星轴；','B1原主板U1不装主控；先确认FPC插深、端子厚度与USB口实配。确认NiZ卡扣、板厚、胶碗、锥簧和卫星轴；')
 s=s.replace('../../../docs/soldering-guide.zh-CN.md','../../../docs/modular/README.zh-CN.md').replace('../../../mechanical/assembly.step','../../../mechanical/modular/assembly_B1.step').replace('href="../BOM.csv"','href="../../modular/BOM-B1.csv"').replace('href="../YAKB.kicad_sch"','href="../../modular/YAKB-controller-B1.kicad_sch"').replace('href="../YAKB.kicad_pcb"','href="../../modular/YAKB-controller-B1.kicad_pcb"')
 s=s.replace('U4-6 接 ADC，U1-18 为 D19 / P0.02 / AIN0。','主板U4-6接主板U1-18，经转接板47Ω到载板U1-18（D19 / P0.02 / AIN0）。')
 # B1 is generated before adding the A0 banner, or strips it on subsequent runs.
 import re
 s=re.sub(r'<aside class="b1-banner".*?</aside>','',s,flags=re.S)
 (OUT/'index.html').write_text(s)
 files=['hardware/modular/YAKB-'+n+'-B1.kicad_pcb' for n in ['controller','interposer','shaped-FPC','FPC-coupon']]+['design/fpc-interface.json','design/modular.json','scripts/generate_modular_guide.py','scripts/modular_common.py','hardware/soldering/data.js','hardware/soldering/index.html','hardware/soldering/app.js','hardware/soldering/styles.css','scripts/verify_modular.py']
 inputs={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files};outputs={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [OUT/'index.html',OUT/'data.js',OUT/'placement-checklist.csv',*ASSETS.glob('*-plan.png')]}
 (OUT/'render-manifest.json').write_text(json.dumps(dict(renderer='Matplotlib native KiCad pad and route extraction',sources=inputs,images=outputs),indent=2)+'\n');print('Generated B1 workbench: %d steps, %d inventory records.'%(len(steps),len(d['inventory'])))
if __name__=='__main__':main()
