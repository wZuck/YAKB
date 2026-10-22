"""YAKB dimensions: PCB top is z=0; x right, y towards the typist."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "design/yakb.json").read_text())

def keys():
    result = []
    for row in SPEC["rows"]:
        for x, width, label in row["keys"]:
            # Physical 1u bin. This avoids folding widely separated bottom-row
            # keys onto the leftmost five sensing columns.
            col = int(x + width/2)
            result.append(dict(ref=f"EC{len(result)+1}", row=row["y"], col=col,
                               u=x, width=width, label=label,
                               x=SPEC["pcb"]["first_center"][0] + (x + width/2 - .5)*SPEC["pitch"],
                               y=SPEC["pcb"]["first_center"][1] + row["y"]*SPEC["pitch"]))
    return result

def case_screws():
    a=SPEC['case']['fastening']['axis_outside_pcb_mm']
    return [(x,y) for y in [-a, SPEC['pcb']['height']+a] for x in [40,142.5,245]] + [(-a,47.3),(SPEC['pcb']['width']+a,47.3)]


def normalize_text(path):
    """Canonical LF / no trailing whitespace for generated text artifacts."""
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
