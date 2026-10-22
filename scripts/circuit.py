"""Electrical design shared by the schematic, PCB and BOM generators.

No routed-board or electrically-tested claim is made by this file.
"""
from common import keys, SPEC

PM_TO_PAD = {1:1,0:2,2:5,3:6,4:7,5:8,6:9,7:10,8:11,9:12,
             10:13,16:14,14:15,15:16,18:17,19:18,20:19,21:20}
PM_TO_NRF = {0:"P0.08",1:"P0.06",2:"P0.17",3:"P0.20",4:"P0.22",
             5:"P0.24",6:"P1.00",7:"P0.11",8:"P1.04",9:"P1.06",
             10:"P0.09",14:"P1.11",15:"P1.13",16:"P0.10",18:"P1.15",
             19:"P0.02/AIN0",20:"P0.29",21:"P0.31"}
ASSIGN = {0:"ROW_DRV0",1:"ROW_DRV1",2:"ROW_DRV2",3:"ROW_DRV3",4:"ROW_DRV4",
          5:"MUX_A",6:"MUX_B",7:"MUX_C",8:"MUX0_INH",9:"MUX1_INH",
          10:"DRAIN",15:"AFE_ON_N",19:"ADC"}

def components():
    c = []
    def add(ref,value,fp,pins,x,y,kind="IC",side="B"):
        c.append(dict(ref=ref,value=value,footprint=fp,pins={str(k):v for k,v in pins.items()},
                      x=x,y=y,kind=kind,side=side))
    p = {i:ASSIGN.get(pm,"") for pm,i in PM_TO_PAD.items()}
    p.update({3:"GND",4:"GND",21:"VCC",22:"RESET",23:"GND",24:"BAT_SW"})
    add("U1","nice!nano_v2","YAKB:nice_nano",p,*SPEC['module']['footprint_center'],"MODULE")
    c[-1]['rotation'] = SPEC['module']['pcb_rotation_deg']
    channel_pin = [13,14,15,12,1,5,2,4]  # X0..X7, TI CD74HC4051M96
    for bank,x in [(0,105),(1,170)]:
        p={3:"SENSE",6:f"MUX{bank}_INH",7:"GND",8:"GND",9:"MUX_C",10:"MUX_B",11:"MUX_A",16:"VCC"}
        p.update({pin:(f"COL{8*bank+i}" if 8*bank+i<15 else "GND") for i,pin in enumerate(channel_pin)})
        add(f"U{bank+2}","CD74HC4051M96","Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",p,x,84)
    add("U4","OPA350UA","Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",{1:"",2:"FB",3:"SENSE",4:"GND",5:"",6:"ADC",7:"AFE_3V3",8:""},217,84)
    add("Q1","AO3401A","Package_TO_SOT_SMD:SOT-23",{1:"AFE_GATE",2:"VCC",3:"AFE_3V3"},207,84)
    rfp="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
    cfp="Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
    for r in range(5):
        add(f"R{r+1}","100",rfp,{1:f"ROW_DRV{r}",2:f"ROW{r}"},40+r*6,78,"R")
    for col in range(15):
        add(f"R{10+col}","100k",rfp,{1:f"COL{col}",2:"GND"},119+(col%5)*7,78+(col//5)*6,"R")
    for ref,v,pins,x,y in [
        ("R30","100k",{1:"ADC",2:"FB"},219,78),
        ("R31","1k",{1:"FB",2:"GND"},219,91),
        ("R32","1k",{1:"DRAIN",2:"SENSE"},232,78),
        ("R33","100k",{1:"MUX0_INH",2:"VCC"},99,78),
        ("R34","100k",{1:"MUX1_INH",2:"VCC"},164,78),
        ("R35","100k",{1:"AFE_GATE",2:"VCC"},200,78),
        ("R36","1k",{1:"AFE_ON_N",2:"AFE_GATE"},207,78)]:
        add(ref,v,rfp,pins,x,y,"R")
    for ref,v,net,x,y in [("C1","100n","VCC",99,91),("C2","100n","VCC",164,91),
                          ("C3","100n","AFE_3V3",220,88),("C4","220p_C0G","SENSE",239,78),
                          ("C5","1u","VCC",193,78)]:
        add(ref,v,cfp,{1:net,2:"GND"},x,y,"C")
    add("J1","JST_S2B-PH-K","YAKB:Battery_PH2",{1:"BAT_RAW",2:"GND"},20,84,"CONN")
    # Two large solder holes for an external SPST switch harness, not a made-up
    # manufacturer's slide-switch footprint. The case has a bottom access hatch.
    add("SW1","Battery_switch_pigtail","YAKB:SPST_PIGTAIL_2.54",{1:"BAT_RAW",2:"BAT_SW"},10,85,"SW")
    add("SW2","Reset_NO","YAKB:RESET_2.54_TH",{1:"RESET",2:"GND"},238,91,"SW")
    for k in keys():
        add(k["ref"],k["label"],"YAKB:ecs_pad_1U_no_ring",{1:f"ROW{k['row']}",2:f"COL{k['col']}",3:"GND"},k["x"],k["y"],"EC","F")
    return c
