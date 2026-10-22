from render_provenance import hashes, record
"""Build the offline Chinese soldering workbench and actual-pad stage images."""
import json,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,FancyBboxPatch
from common import ROOT,SPEC
from circuit import components

OUT=ROOT/'hardware/soldering'
PHASES=[dict(id='P1',code='P1',title='低矮被动件'),dict(id='P2',code='P2',title='模拟前端'),dict(id='P3',code='P3',title='通孔与模块'),dict(id='P4',code='P4',title='通电与装配')]

def step_data():
    groups=[
      ('P1','100Ω 行电阻','0805 / 2012',[f'R{i}' for i in range(1,6)],'焊接5路行激励串联电阻。',['先核对100Ω料袋，按R1至R5依次完成。','先固定一端，摆正后焊另一端。'],'5颗均为100Ω，不是1k或100k。'),
      ('P1','100kΩ 泄放与上拉','0805 / 2012',[f'R{i}' for i in range(10,25)]+['R30','R33','R34','R35'],'同值元件合并完成，分别承担列泄放、反馈与关断上拉。',['R10至R24共15颗；另装R30、R33、R34、R35。','在线测量受并联支路影响，有疑问应先测散件。'],'本组19颗；不要混入1k电阻。'),
      ('P1','1kΩ 放电与反馈电阻','0805 / 2012',['R31','R32','R36'],'完成增益下臂、放电限流和MOS栅极串联。',['逐一对照R31、R32、R36。','R32连接DRAIN到SENSE，重点清洁其周围。'],'三颗都是1kΩ，不能用100Ω替代。'),
      ('P1','100nF 去耦','0805 X7R',['C1','C2','C3'],'先为两个MUX和运放完成近端去耦。',['确认C1、C2、C3为100nF。','贴平焊接，无极性；排除立碑和锡桥。'],'C4不属于本组。'),
      ('P1','220pF 采样电容','0805 C0G / NP0',['C4'],'这颗电容直接影响静电容采样。',['确认220pF，优先C0G/NP0。','焊完清除残留助焊剂，保持SENSE节点干净。'],'不要误装220nF，二者相差1000倍。'),
      ('P1','1µF 电源去耦','0805 X5R / X7R',['C5'],'完成VCC本地去耦。',['确认1µF且额定电压不低于6.3V。','完成后复查所有阻容，不要立即接电池。'],'无极性，焊点应润湿且无桥连。'),
      ('P2','双路列模拟多路器','SOIC-16 · 1.27mm',['U2','U3'],'两个CD74HC4051M96选择15个有效列，共用SENSE。',['核对1脚，先固定对角脚再逐脚焊。','16脚VCC、8脚GND、7脚VEE接地；6脚为INH。','两个INH只能交替有效，不能同时低。'],'必须是SOIC版本，不使用TSSOP焊盘猜适配。'),
      ('P2','静电容运放','OPA350UA · SOIC-8',['U4'],'安装可断电模拟放大器。',['核对1脚方向，固定对角脚后焊其余脚。','7脚电源，4脚地，3脚SENSE，2脚FB，6脚ADC。','1、5、8脚保留NC，不自行接地。'],'不要与其他8脚芯片按外形互换。'),
      ('P2','运放电源MOS','AO3401A · SOT-23',['Q1'],'仅切换运放，MUX在扫描空闲时保持供电。',['核对采购器件脚位：1=G，2=S，3=D。','源极接VCC，漏极接AFE_3V3。','完成后断电检查VCC和AFE对地无明显短路。'],'按厂家引脚图确认，不凭封装猜方向。'),
      ('P3','电池插座','S2B-PH-K horizontal · 2.0mm',['J1'],'仅安装座子，此时仍不接电池。',['确认J1-1=BAT_RAW正极，J1-2=GND。','先固定一个引脚并贴平，再完成另一脚。'],'不同厂商电池插头线序可能相反。'),
      ('P3','实体断电开关线','2.54mm 两孔接线',['SW1'],'这是一组接线孔，外接SPST开关。',['SW1-1接BAT_RAW，SW1-2接BAT_SW。','短绝缘线焊好后固定开关，导线留应力释放。','断电检查OFF隔离、ON导通。'],'不是某个滑动开关的专用封装；关闭时电池不能充电。'),
      ('P3','Reset 接线','2.54mm 两孔接线',['SW2'],'外接常开瞬时按钮，或保留检修短接位置。',['一端RESET，另一端GND。','不要使用常闭按钮；修齐焊脚。'],'模块本身也有UF2 bootloader复位功能。'),
      ('P3','可插拔蓝牙主控','nice!nano v2 · 2×12针',['U1'],'对齐低矮插座后再安装成品主控。',['按PCB正面坐标USB朝左、天线朝右；本背面图已镜像，USB显示在右侧。','用未通电模块作夹具，先焊插座四角。','取下模块检查桥连；模块与插座总下凸≤6.5mm。','BOOST不桥接；无需重焊模块内部晶振、射频或MCU。'],'D19=P0.02/AIN0；D18不是本版ADC。'),
      ('P4','清洗、干燥与断电检查','NO POWER',[],'所有焊接完成后，先排除电气缺陷。',['依助焊剂说明清洗，特别注意C4、U4和MUX输入。','完全干燥后复查短路、型号、1脚、开关和插座方向。','电池、USB和机构仍保持移开。'],'电容充电可导致阻值短暂变化；持续近0Ω需排查。'),
      ('P4','第一次只接 USB','CURRENT LIMIT',['U1','U2','U3','U4','Q1'],'先验证USB供电、VCC和模拟开关时序。',['电池断开，限流USB从100mA起步，先直连模块。','测U1-21标称3.3V；U1-23为GND。','示波器检查Q1栅极、U4-7及两路INH，异常就断电。'],'不要接入电池来尝试修复限流、发热或枚举故障。'),
      ('P4','小组静电容试装与校准','4-KEY BRING-UP',['EC1','EC2','EC3','EC4'],'先验证少量真实NiZ机构，减少故障定位变量。',['装配高度固定在设计值，锥簧自然落在电极中心。','测试mask必须对应实际已装位置。','启用EC校准器，用ec命令补全查设备名，再start/save/load。'],'通过按下、释放、噪声和冷启动检查后才扩展到全部60键。'),
      ('P4','最后接入保护电池','1S LiPo · 1000mAh',[],'确认极性、外包络和充电路径。',['断开USB，实体开关关闭，测插头与J1-1相配的端子为正。','整个电芯包络≤60×35×5.5mm，包含保护板及出线。','打开开关测电流并验证BLE，再接USB检查充电温升。'],'默认约100mA充电；BOOST不桥接，电池不受挤压。'),
      ('P4','装配全键与 HHKB 外壳','FINAL ASSEMBLY',[],'机构最后安装，逐步固定并完成60键校准。',['重新断电，再装全部胶碗、锥簧、轴壳与卫星轴。','6u空格为中心十字、95.25mm卫星轴间距。','先在上框底面安装8颗M2嵌件；底部锁入：后侧3颗M2×20、两侧2颗M2×18、前侧3颗M2×16，勿混用长度。','检查板间距、中央柱、USB线和电池绝缘；可选三仓底壳仅配工厂成组的带保护1S2P/1S3P电池包，单路接J1。','冷启动复核校准、BLE切换、快速首键及大键回弹。'],'文件检查不能替代真实轴体、天线、充电和续航试验。')]
    steps=[]
    for i,(phase,title,subtitle,refs,summary,instructions,checkpoint) in enumerate(groups,1):
        color={'P1':'#256f78','P2':'#c74f1b','P3':'#174b3a','P4':'#8c5e21'}[phase]
        steps.append(dict(id=f'step-{i:02}',code=f'{i:02}',phase=phase,phaseTitle=next(p['title'] for p in PHASES if p['id']==phase),color=color,title=title,subtitle=subtitle,refs=refs,summary=summary,instructions=instructions,checkpoint=checkpoint,count=(f'{len(refs)} 件' if i<=13 else '检查 / 装配'),parts=refs if refs else ['断电操作' if i in [14,18] else '阶段验证'],image=f'step-{i:02}.png',imageNote='ACTUAL PCB PAD POSITIONS · white ring = pad 1'))
    steps[16]['image']='../../assets/case-interior-render.png';steps[16]['imageNote']='GENERATED CAD · battery envelope requires a real cell check'
    steps[17]['image']='../../assets/exploded-render.png';steps[17]['imageNote']='ACTUAL STEP GEOMETRY · hardware and NiZ internals omitted'
    return steps

def image(step,padmap):
    from render_plan import draw_board, PAPER, INK
    selected=set(step['refs']);front=step['code']=='16'
    active=[a for part in padmap if part['ref'] in selected for a in part['pads'] if a['front' if front else 'back']]
    if active and step['code']!='14':
        xmin=min(a['x'] for a in active)-10;xmax=max(a['x'] for a in active)+10
        ymin=min(a['y'] for a in active)-10;ymax=max(a['y'] for a in active)+10
        if (xmax-xmin)/(ymax-ymin)<2.15:
            extra=((ymax-ymin)*2.15-(xmax-xmin))/2;xmin-=extra;xmax+=extra
    else:xmin,xmax,ymin,ymax=-5,290,-5,100
    fig=plt.figure(figsize=(16,8.4),facecolor=PAPER)
    ax=fig.add_axes([.035,.15,.93,.69]);draw_board(ax,front,selected)
    ax.set_xlim((xmin,xmax) if front else (xmax,xmin));ax.set_ylim(ymax,ymin)
    fig.text(.04,.935,'YAKB  /  ASSEMBLY ATLAS',fontsize=19,weight='bold',color=INK)
    fig.text(.96,.935,step['code']+' / 18',ha='right',fontsize=18,color=INK)
    subtitle=step['subtitle'].replace('两孔接线','2-hole harness').replace('针','pin')
    fig.text(.04,.88,subtitle,fontsize=12,color='#61736a')
    fig.text(.04,.09,'SELECTED  '+(', '.join(step['refs']) if step['refs'] else 'FULL BOARD INSPECTION'),fontsize=9,weight='bold',color=INK)
    fig.text(.04,.045,('FRONT VIEW' if front else 'BACK VIEW / ALREADY MIRRORED')+'  |  Native copper polygons, routed traces and drilled outline. White ring = pad 1.',fontsize=9,color='#61736a')
    fig.savefig(OUT/step['image'],dpi=180,facecolor=PAPER);plt.close(fig)

def main():
    sources=hashes(['hardware/YAKB.kicad_pcb','design/pad-map.json','design/pcb-scene.json','design/yakb.json','scripts/circuit.py','scripts/generate_soldering.py','scripts/render_plan.py'])
    OUT.mkdir(exist_ok=True);steps=step_data();cs=components();mapref={r:s for s in steps[:13] for r in s['refs']};inventory=[]
    assert len(mapref)==40 and len({c['ref'] for c in cs if c['kind']!='EC'})==40
    for c in cs:
        s=mapref.get(c['ref']);note='无极性；核对数值'
        if c['kind']=='EC':note='PCB感应铜，不焊锡、不焊弹簧'
        elif c['ref']=='U1':note='正面坐标USB朝左（背面图朝右）；D19=ADC；BOOST不桥接'
        elif c['ref']=='Q1':note='1=G，2=S/VCC，3=D/AFE'
        elif c['ref'] in ['U2','U3','U4']:note='核对1脚和型号'
        elif c['ref']=='J1':note='水平S2B-PH-K；1=电池正极，2=GND；先测线序'
        elif c['ref'].startswith('SW'):note='两孔线位，外接开关 / 常开按钮'
        inventory.append(dict(ref=c['ref'],step=s['code'] if s else '18',phase=s['phase'] if s else 'P4',value=c['value'],footprint=c['footprint'].split(':')[-1],side='顶面免焊' if c['kind']=='EC' else '背面 / 通孔',x=c['x'],y=c['y'],note=note,type='electrode' if c['kind']=='EC' else 'populate',nets=' '.join(n for n in c['pins'].values() if n)))
    (OUT/'data.js').write_text('window.YAKB_GUIDE = '+json.dumps(dict(phases=PHASES,steps=steps,inventory=inventory),ensure_ascii=False,indent=2)+';\n')
    with (OUT/'placement-checklist.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,lineterminator='\n',fieldnames=list(inventory[0]));w.writeheader();w.writerows(inventory)
    pads=json.loads((ROOT/'design/pad-map.json').read_text())
    for s in steps[:16]:image(s,pads)
    record('hardware/soldering/render-manifest.json',sources,['hardware/soldering/'+s['image'] for s in steps[:16]],'Matplotlib native copper polygons and routed PCB')
    print('Generated 18 steps, 16 actual-pad images, 100 inventory entries')

if __name__=='__main__':main()
