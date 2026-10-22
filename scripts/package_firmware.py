"""Verify compiled inputs and ELF/UF2 agreement before packaging actual west outputs."""
import argparse,hashlib,json,re,shutil,struct
from pathlib import Path
from common import ROOT


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def elf_loads(path):
    data=path.read_bytes();assert data[:7]==b'\x7fELF\x01\x01\x01'
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    return data,[p for i in range(header[10]) if (p:=struct.unpack_from('<IIIIIIII',data,header[5]+i*header[9]))[0]==1]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workspace',type=Path,required=True);work=parser.parse_args().workspace.resolve()
    metadata=json.loads((ROOT/'firmware/patches/manifest.json').read_text());driver=work/'ec-support-zmk-module'/metadata['path']
    assert sha(driver)==metadata['after_sha256'],'Workspace EC source is not the reviewed patch'
    assert sha(ROOT/'firmware/patches/0001-ec-wake-on-raw-transition.patch')==metadata['patch_sha256']
    inputs={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'firmware/config/boards').rglob('*') if p.is_file()}
    for name,digest in inputs.items():assert sha(work/name.removeprefix('firmware/'))==digest,name
    inputs.update({str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'firmware/patches').glob('*.patch')})
    report=json.loads((ROOT/'reports/firmware.json').read_text());builds={}
    for name,dest,label in [('yakb','yakb-a0.uf2','normal'),('yakb-calibrator','yakb-a0-calibrator.uf2','calibrator')]:
        folder=work/'build'/name;base=folder/'zephyr';conf=(base/'.config').read_text();dts=(base/'zephyr.dts').read_text()
        value=lambda key:int(re.search(r'^'+key+r'=(-?\d+)$',conf,re.M)[1])
        actual_priority=-(value('CONFIG_NUM_COOP_PRIORITIES')-value('CONFIG_ZMK_KSCAN_EC_MATRIX_THREAD_PRIORITY'))
        assert actual_priority==-1
        for flag in ['CONFIG_ASSERT=y','CONFIG_ZMK_USB=y','CONFIG_ZMK_BLE=y']:assert flag in conf,flag
        waits=[int(re.search(key+r'\s*=\s*<\s*(0x[0-9a-f]+|\d+)',dts)[1],0) for key in ['active-polling-interval-ms','idle-polling-interval-ms','sleep-polling-interval-ms']]
        assert waits==[4,8,12]
        objects=list(base.rglob('zmk_kscan_ec_matrix.c.obj'));assert len(objects)==1
        obj=objects[0];elf=base/'zmk.elf';uf2=base/'zmk.uf2'
        assert driver.stat().st_mtime<=obj.stat().st_mtime<=elf.stat().st_mtime<=uf2.stat().st_mtime,'Stale compiled artifact'
        commands=json.loads((folder/'compile_commands.json').read_text())
        assert any(x['file'].endswith('/ec-support-zmk-module/'+metadata['path']) for x in commands),'No compiled EC translation unit'
        binary,loads=elf_loads(elf);flash=[p for p in loads if 0x26000<=p[3]<0x100000 and p[4]];ram=[p for p in loads if 0x20000000<=p[2]<0x20040000]
        memory={};uf=uf2.read_bytes();assert len(uf)%512==0
        for offset in range(0,len(uf),512):
            block=uf[offset:offset+512];a,b,flags,address,size,index,count,family=struct.unpack_from('<8I',block)
            assert a==0x0A324655 and b==0x9E5D5157 and size<=476
            for i,v in enumerate(block[32:32+size]):memory[address+i]=v
        header=struct.unpack_from('<16sHHIIIIIHHHHHH',binary)
        for i in range(header[12]):
            section=struct.unpack_from('<10I',binary,header[6]+i*header[11])
            if not(section[2]&2) or section[1]==8 or not section[5]:continue
            segment=next((p for p in flash if p[1]<=section[4] and section[4]+section[5]<=p[1]+p[4]),None)
            if segment is None:continue
            address=segment[3]+section[4]-segment[1]
            assert bytes(memory[address+j] for j in range(section[5]))==binary[section[4]:section[4]+section[5]],'UF2 differs from allocated ELF section'
        report[label]=dict(flash_bytes=max(p[3]+p[4] for p in flash)-min(p[3] for p in flash),ram_bytes=max(p[2]+p[5] for p in ram)-0x20000000)
        builds[label]=dict(uf2_sha256=sha(uf2),elf_sha256=sha(elf),ec_object_sha256=sha(obj),config_sha256=sha(base/'.config'),dts_sha256=sha(base/'zephyr.dts'))
        shutil.copyfile(uf2,ROOT/'firmware/prebuilt'/dest)
    report.update(patch_sha256=metadata['patch_sha256'],driver_sha256=sha(driver),assertions_enabled=True,cooperative_priority=actual_priority,polling_wait_intervals_ms=waits,usb_hid=True,ble_hid=True)
    (ROOT/'reports/firmware.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'firmware/prebuilt/build-manifest.json').write_text(json.dumps(dict(inputs=inputs,builds=builds,driver_sha256=sha(driver)),indent=2)+'\n')
    files=sorted((ROOT/'firmware/prebuilt').glob('*.uf2'))
    (ROOT/'firmware/prebuilt/SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in files));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
