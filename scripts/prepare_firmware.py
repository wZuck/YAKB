"""Apply the exact reviewed EC patch and copy YAKB configuration after west update."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def prepare(workspace):
    metadata=json.loads((ROOT/'firmware/patches/manifest.json').read_text())
    module=workspace/'ec-support-zmk-module'
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=module,text=True).strip()
    assert revision==metadata['revision'],'EC revision differs from reviewed pin'
    target=module/metadata['path'];patch=ROOT/'firmware/patches/0001-ec-wake-on-raw-transition.patch'
    assert hashlib.sha256(patch.read_bytes()).hexdigest()==metadata['patch_sha256'],'Patch differs from manifest'
    current=hashlib.sha256(target.read_bytes()).hexdigest()
    if current==metadata['before_sha256']:
        subprocess.run(['git','apply','--check',str(patch)],cwd=module,check=True)
        subprocess.run(['git','apply',str(patch)],cwd=module,check=True)
    else:assert current==metadata['after_sha256'],'Unexpected EC source edits; refusing a fuzzy patch'
    assert hashlib.sha256(target.read_bytes()).hexdigest()==metadata['after_sha256']
    shutil.copytree(ROOT/'firmware/config/boards',workspace/'config/boards',dirs_exist_ok=True)
    return metadata

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',required=True,type=Path)
    print(json.dumps(prepare(p.parse_args().workspace.resolve()),indent=2))
