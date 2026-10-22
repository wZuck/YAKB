"""Verify delivered renders, reports, firmware and manufacturing ZIP are current."""
import hashlib
import json
import zipfile
from common import ROOT


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    pcb=digest('hardware/YAKB.kicad_pcb')
    for path in ['design/pcb-scene.json','reports/design-checks.json','reports/hardware-checks.json','reports/component-geometry.json','reports/electrical-analysis.json']:
        assert json.loads((ROOT/path).read_text())['pcb_sha256']==pcb,path
    battery=json.loads((ROOT/'reports/battery-study.json').read_text())
    for name,value in battery['sources'].items():assert digest(name)==value,name
    component=json.loads((ROOT/'reports/component-geometry.json').read_text())
    assert component['components_sha256']==digest('mechanical/components.step')
    manifests={'assets/render-manifest.json':9,'assets/plan-render-manifest.json':2,'hardware/soldering/render-manifest.json':16}
    for path,count in manifests.items():
        data=json.loads((ROOT/path).read_text());assert len(data['images'])==count,path
        for name,value in data['sources'].items():assert digest(name)==(value['sha256'] if isinstance(value,dict) else value),name
        for name,value in data['images'].items():assert digest(name)==value,name
    with zipfile.ZipFile(ROOT/'fabrication/YAKB-A0-gerbers.zip') as archive:
        expected={p.name for p in (ROOT/'fabrication/gerbers').iterdir() if p.is_file()}
        assert set(archive.namelist())==expected
        for name in expected:assert archive.read(name)==(ROOT/'fabrication/gerbers'/name).read_bytes(),name
    for line in (ROOT/'firmware/prebuilt/SHA256SUMS').read_text().splitlines():
        sha,name=line.split();assert digest('firmware/prebuilt/'+name)==sha,name
    manifest=json.loads((ROOT/'firmware/prebuilt/build-manifest.json').read_text())
    for path,value in manifest['inputs'].items():assert digest(path)==value,path
    for label,name in [('normal','yakb-a0.uf2'),('calibrator','yakb-a0-calibrator.uf2')]:assert digest('firmware/prebuilt/'+name)==manifest['builds'][label]['uf2_sha256']
    patch=json.loads((ROOT/'firmware/patches/manifest.json').read_text())
    assert digest('firmware/patches/0001-ec-wake-on-raw-transition.patch')==patch['patch_sha256']
    build=json.loads((ROOT/'reports/firmware.json').read_text());test=json.loads((ROOT/'reports/firmware-regression.json').read_text())
    assert build['driver_sha256']==test['driver_sha256']==patch['after_sha256']
    assert build['patch_sha256']==patch['patch_sha256']
    print('PASS: 27 rendered outputs match current sources; PCB reports, Gerber ZIP and firmware hashes agree.')


if __name__=='__main__':main()
