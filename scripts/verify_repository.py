"""Repository-wide file integrity and cross-variant consistency audit.

Run after verify_release.py and verify_modular_release.py. This checks saved
files and contracts; it does not turn pending hardware qualification into a pass.
"""
import ast
import csv
import hashlib
import io
import json
import re
import struct
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
from PIL import Image
from common import ROOT

REPORT = 'reports/repository-consistency.json'


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def read_guide(path):
    raw = (ROOT / path).read_text()
    return json.loads(raw[raw.index('{'):raw.rfind(';')])


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(v for k, v in attrs if k in ('href', 'src') and v)


def assert_native_report(data):
    # KiCad ERC puts findings in sheets[].violations, unlike PCB DRC.
    assert not data.get('violations')
    assert not any(s.get('violations') for s in data.get('sheets', []))
    assert not data.get('schematic_parity') and not data.get('unconnected_items')


def native_recheck():
    """Read-only CLI checks: keep provenance, leave manufacturing exports intact."""
    cli = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
    if '--kicad-cli' in sys.argv:
        cli = sys.argv[sys.argv.index('--kicad-cli') + 1]
    boards = ['hardware/YAKB'] + ['hardware/modular/YAKB-' + n + '-B1' for n in ['controller', 'interposer', 'shaped-FPC', 'FPC-coupon']]
    inputs = ['scripts/verify_repository.py', 'hardware/fp-lib-table', 'hardware/sym-lib-table', 'hardware/YAKB.kicad_sym', 'hardware/modular/fp-lib-table', 'hardware/modular/sym-lib-table', 'hardware/modular/YAKB_B1.kicad_sym']
    inputs += [str(p.relative_to(ROOT)) for p in (ROOT / 'hardware/modular').glob('*.kicad_dru')]
    records = []
    with tempfile.TemporaryDirectory(prefix='yakb-native-consistency-') as folder:
        for board in boards:
            inputs += [board + ext for ext in ['.kicad_pcb', '.kicad_sch', '.kicad_pro']]
            checks = {}
            for domain, kind, ext in [('sch', 'erc', '.kicad_sch'), ('pcb', 'drc', '.kicad_pcb')]:
                target = Path(folder) / (Path(board).name + '-' + kind + '.json')
                args = [cli, domain, kind, '--format', 'json', '--exit-code-violations', '-o', str(target)]
                if kind == 'drc':
                    args += ['--schematic-parity']
                run = subprocess.run(args + [str(ROOT / (board + ext))], capture_output=True, text=True)
                assert run.returncode == 0, run.stdout + run.stderr
                data = json.loads(target.read_text()); assert_native_report(data)
                checks[kind] = dict(violations=0, schematic_parity=0, unconnected=0, kicad_version=data['kicad_version'])
            records.append(dict(board=board, checks=checks))
    report = dict(result='PASS', mode='Read-only native ERC and DRC with schematic parity', boards=records, sources={f: digest(f) for f in inputs})
    (ROOT / 'reports/repository-native-checks.json').write_text(json.dumps(report, indent=2) + '\n')


def main():
    if '--native' in sys.argv:
        native_recheck()
    assert (ROOT / 'reports/repository-native-checks.json').exists(), 'First run: verify_repository.py --native'
    files = sorted(set(filter(None, subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT
    ).decode().split('\0'))) - {REPORT})
    assert all((ROOT / f).is_file() for f in files), 'Missing tracked file'
    catalog = []
    links_checked = 0
    for name in files:
        file = ROOT / name
        suffix = file.suffix.lower()
        methods = ['sha256']
        if suffix in ('.json', '.kicad_pro'):
            data = json.loads(file.read_text())
            if isinstance(data, dict):
                for source, value in data.get('sources', {}).items():
                    sha = value.get('sha256') if isinstance(value, dict) else value
                    if isinstance(sha, str) and re.fullmatch('[0-9a-f]{64}', sha):
                        assert digest(source) == sha, (name, 'stale source', source)
            methods.append('JSON parse')
        elif suffix == '.xml':
            ET.parse(file)
            methods.append('XML parse')
        elif suffix == '.dxf':
            import ezdxf
            doc = ezdxf.readfile(file)
            assert not doc.audit().errors, name
            methods.append('DXF parse/audit')
        elif suffix == '.glb':
            raw = file.read_bytes()
            assert struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw)), name
            offset = 12; kinds = []
            while offset < len(raw):
                size, kind = struct.unpack_from('<I4s', raw, offset)
                assert size % 4 == 0 and offset + 8 + size <= len(raw), name
                if kind == b'JSON':
                    json.loads(raw[offset + 8:offset + 8 + size])
                kinds.append(kind); offset += 8 + size
            assert offset == len(raw) and kinds[0] == b'JSON', name
            methods.append('GLB chunks/JSON')
        elif suffix == '.py':
            ast.parse(file.read_text(), filename=name)
            methods.append('Python AST parse')
        elif suffix == '.csv':
            rows = list(csv.reader(io.StringIO(file.read_text(encoding='utf-8-sig'))))
            assert rows and all(len(row) == len(rows[0]) for row in rows), name
            methods.append('CSV column integrity')
        elif suffix == '.zip':
            with zipfile.ZipFile(file) as z:
                assert z.testzip() is None, name
            methods.append('ZIP CRC')
        elif suffix == '.png':
            with Image.open(file) as image:
                image.verify()
            methods.append('PNG decode')
        elif suffix == '.stl':
            raw = file.read_bytes()
            assert len(raw) == 84 + 50 * struct.unpack_from('<I', raw, 80)[0], name
            methods.append('Binary STL record integrity')
        elif suffix == '.step':
            raw = file.read_text()
            assert raw.startswith('ISO-10303-21;') and raw.rstrip().endswith('END-ISO-10303-21;'), name
            methods.append('STEP exchange framing')
        elif suffix == '.pdf':
            raw = file.read_bytes()
            assert raw.startswith(b'%PDF-') and b'%%EOF' in raw[-1024:], name
            methods.append('PDF framing')
        elif suffix == '.uf2':
            raw = file.read_bytes()
            assert len(raw) % 512 == 0, name
            for i in range(0, len(raw), 512):
                assert struct.unpack_from('<II', raw, i) == (0x0A324655, 0x9E5D5157)
                assert struct.unpack_from('<I', raw, i + 508)[0] == 0x0AB16F30
            methods.append('UF2 block framing')
        if suffix in ('.md', '.html'):
            text = file.read_text()
            if suffix == '.html':
                parser = Links(); parser.feed(text); urls = parser.links
            else:
                text = re.sub(r'```.*?```', '', text, flags=re.S)
                urls = re.findall(r'\[[^\]]*\]\(([^)]+)\)', text)
            for url in urls:
                if re.match(r'^(?:[a-zA-Z][\w+.-]*:|#)', url):
                    continue
                target = unquote(url.split('#')[0].split('?')[0]).strip('<>')
                resolved = (file.parent / target).resolve()
                assert not target or resolved.exists() or resolved == ROOT / REPORT, (name, url)
                links_checked += 1
            methods.append('Local links')
        catalog.append(dict(path=name, bytes=file.stat().st_size, sha256=digest(name), checks=methods))

    for path in ['reports/erc.json', 'reports/drc.json'] + [
            'reports/modular/YAKB-' + board + '-B1-' + kind + '.json'
            for board in ['controller', 'interposer', 'shaped-FPC', 'FPC-coupon']
            for kind in ['erc', 'drc']]:
        assert_native_report(json.loads((ROOT / path).read_text()))
    # Exercise the exact format that was previously missed, without modifying files.
    for invalid in [{'sheets': [{'violations': [{'type': 'pin_not_connected'}]}]},
                    {'violations': [{'type': 'clearance'}]}, {'unconnected_items': [1]},
                    {'schematic_parity': [1]}]:
        try:
            assert_native_report(invalid)
        except AssertionError:
            pass
        else:
            raise AssertionError('Native checker failed to reject injected finding')

    guide = read_guide('hardware/soldering/b1/data.js')
    rows = guide['inventory']
    counts = dict(Counter(r['type'] for r in rows))
    assert counts == dict(populate=46, electrode=60, dnp=1, cable=1), counts
    refs = {r['ref']: r for r in rows}
    assert len(refs) == len(rows) == 108
    assert refs['U1']['type'] == 'dnp' and refs['C.U1']['type'] == 'populate'
    assert refs['FPC1']['x'] == refs['FPC1']['y'] == ''
    assert '保持式' in refs['SW1']['note'] and '瞬时' in refs['SW2']['note']
    table = list(csv.DictReader((ROOT / 'hardware/soldering/b1/placement-checklist.csv').open(encoding='utf-8-sig')))
    assert [{k: str(v) for k, v in r.items()} for r in rows] == table
    complete = list(csv.DictReader((ROOT / 'hardware/modular/BOM-B1-complete.csv').open(encoding='utf-8-sig')))
    assert len(complete) == len(rows) and sum(int(r['Quantity']) for r in complete) == 47
    for r, b in zip(rows, complete):
        assert (r['value'], r['footprint'], r['type'], str(r['x']), str(r['y'])) == (b['Value'], b['Footprint'], b['Status'], b['X_mm'], b['Y_mm'])
        assert int(b['Quantity']) == (0 if r['type'] in ('dnp', 'electrode') else 1)
    geometry = json.loads((ROOT / '.render-cache/modular-native-geometry.json').read_text())
    for prefix, board in [('C.', 'controller'), ('I.', 'interposer')]:
        for f in geometry[board]['footprints']:
            if f['ref'].startswith('H'):
                continue
            r = refs[prefix + f['ref']]
            assert (r['value'], r['footprint'], r['x'], r['y']) == (f['value'], f['footprint'], f['x'], f['y'])
    main_bom = {r['Reference']: r for r in csv.DictReader((ROOT / 'hardware/BOM.csv').open())}
    for ref, b in main_bom.items():
        r = refs[ref]
        if ref != 'U1':
            assert r['value'] == b['Value'] and r['footprint'] == b['Footprint'].split(':')[-1]
        assert abs(float(r['x']) - float(b['X_mm'])) < 1e-6 and abs(float(r['y']) - float(b['Y_mm'])) < 1e-6
    stages = {s['code']: s for s in guide['steps']}
    for r in rows:
        assert r['step'] in stages and r['phase'] == stages[r['step']]['phase']
    for s in guide['steps']:
        assert all(r in refs for r in s['refs']), (s['code'], s['refs'])
        if s['image'].startswith('step-'):
            assert s['image'] == 'step-' + s['code'] + '.png'
    pinout = list(csv.DictReader((ROOT / 'hardware/modular/FPC-pinout.csv').open()))
    design = json.loads((ROOT / 'design/modular.json').read_text())
    assert len(pinout) == 24
    for i, row in enumerate(pinout, 1):
        assert int(row['Carrier_JF1_pin']) == i and int(row['Interposer_JF1_pin']) == 25 - i
        assert row['System_net'] == design['fpc_pinout'][i - 1]
    spec = json.loads((ROOT / 'design/yakb.json').read_text())
    power = json.loads((ROOT / 'reports/electrical-analysis.json').read_text())
    model = power['model']
    for label, row in power['scenarios'].items():
        for index, (frame, scan, background) in enumerate(zip(model['scan_frame_ms'], model['active_total_mA'], model['background_mA'])):
            expected = (background * row['wait_ms'] + scan * frame + model['switched_cap_uF'] * 3.3) / (frame + row['wait_ms'])
            assert abs(row['current_mA'][index] - expected) <= .00051
    modular_power = json.loads((ROOT / 'reports/modular-electrical.json').read_text())
    for index in [0, 1]:
        expected = power['scenarios']['active']['nominal_current_mA'] / 1000 + modular_power['assumed_ADC_filter_full_swing_current_A'] + modular_power['assumed_extra_digital_current_A'][index]
        assert abs(modular_power['assumed_activity_current_A'][index] - expected) < 1e-12
    pack = json.loads((ROOT / 'reports/battery-study.json').read_text())
    for row in pack['options']:
        days = 800 / power['mixed_nominal_current_mA'] / 24 * row['pouches']
        assert row['nominal_mixed_runtime_days'] == round(days, 1)
        for suffix in ['.md', '.zh-CN.md']:
            assert str(round(days, 1)) in (ROOT / ('docs/battery-options' + suffix)).read_text()
    mech = json.loads((ROOT / 'reports/mechanical.json').read_text())
    assert abs(spec['case']['bezel_top_z'] - spec['case']['floor_front_z'] - mech['case_profile']['front_wall_height_mm']) < 1e-6
    # Contract guard: no stale front-height / coordinate claims in the baseline docs.
    for file in ['docs/design.md', 'docs/design.zh-CN.md', 'docs/case-design.md', 'docs/case-design.zh-CN.md']:
        text = (ROOT / file).read_text()
        assert '21.0 mm' not in text and '21.0 毫米' not in text
        assert 'CAD and DXF preserve the same coordinates without mirroring' not in text
        assert 'CAD 和 DXF 与 PCB 使用同一个坐标，不在导出时镜像' not in text
    for row in csv.DictReader((ROOT / 'docs/modular/qualification-checklist.csv').open(encoding='utf-8-sig')):
        assert not row['Measured / 实测'] and row['Result / 结论'] == 'PENDING / 待测'
    for file in ['README.md', 'README.zh-CN.md']:
        text = (ROOT / file).read_text()
        assert '299 × 136.6' in text and 'BOM-B1-complete.csv' in text and 'B1.1' in text
    for file in ['docs/case-design', 'docs/battery-options', 'docs/reproduce', 'docs/inventory-review', 'docs/review-fixes']:
        for suffix in ['.md', '.zh-CN.md']:
            assert 'B1.1' in (ROOT / (file + suffix)).read_text().splitlines()[2]
    report = dict(result='PASS', scope='Saved-file integrity and cross-file contracts; no physical certification',
                  audited_files=len(catalog), local_links_checked=links_checked, inventory_counts=counts,
                  native_report_formats_checked=10, native_report_negative_cases=4,
                  pending_physical_measurements=True, files=catalog)
    (ROOT / REPORT).write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(f'PASS: {len(catalog)} files catalogued, {links_checked} local links, exact BOM/guide/native footprint contracts, ERC-sheet regression; physical tests remain pending.')


if __name__ == '__main__':
    main()
