"""Simplify bundled meshes once; preserve shared parts across all views."""
from pathlib import Path
import gzip
import json
import numpy as np
import fast_simplification

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'anatomy'
cache = {}
for key in ['heart','lungs','liver','whole_body']:
    path = ROOT / f'{key}.json.gz'
    with gzip.open(path,'rt') as f:
        model = json.load(f)
    for part in model['parts']:
        name = part['name']
        if name not in cache:
            maximum = 40000 if name == 'Reference skeleton' else 7000
            if len(part['faces']) > maximum:
                vertices, faces = fast_simplification.simplify(np.array(part['vertices'], dtype=np.float64), np.array(part['faces'], dtype=np.int32), target_count=maximum)
                part['vertices'] = vertices.round(5).tolist()
                part['faces'] = faces.tolist()
            cache[name] = part
    model['parts'] = [cache[p['name']] for p in model['parts']]
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:
        f.write(json.dumps(model,separators=(',',':')).encode())
    print(key, sum(len(p['faces']) for p in model['parts']))
