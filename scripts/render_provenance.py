"""Record input/output hashes; reject edits made during rendering."""
import hashlib
import json
from common import ROOT


def hashes(paths):
    return {str(path): hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in paths}


def record(path, sources, images, renderer):
    assert hashes(sources) == sources, 'Render inputs changed during rendering'
    (ROOT/path).write_text(json.dumps(dict(renderer=renderer, sources=sources, images=hashes(images)), indent=2)+'\n')
