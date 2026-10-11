"""One-time Blender asset preparation; not needed by Streamlit deployments.

Run: blender -b -t 2 --python tools/export_anatomy.py -- /path/Startup.blend
See assets/anatomy/ATTRIBUTION.md for the pinned upstream archive and licenses.
"""
import sys
import json
import gzip
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
source = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.open_mainfile(filepath=source)
GROUPS = {
    'heart': ['Left atrium', 'Right atrium', 'Left ventricle', 'Right ventricle', 'Pulmonary trunk'],
    'lungs': ['Superior lobe of left lung', 'Inferior lobe of left lung', 'Superior lobe of right lung', 'Middle lobe of right lung', 'Inferior lobe of right lung', 'Trachea'],
    'liver': ['Liver'],
}
COLORS = {'heart':'#B85B62','lungs':'#CC9395','kidneys':'#A95F57','liver':'#985B4D'}


def mesh_part(names, color, subdivide=False):
    vertices, faces = [], []
    for name in names:
        obj = bpy.data.objects[name]
        mesh = obj.data.copy()
        if subdivide:
            # Use a clean temporary object, avoiding the atlas's UI/cross-section modifiers.
            temp = bpy.data.objects.new('export-temp', mesh)
            bpy.context.collection.objects.link(temp)
            modifier = temp.modifiers.new('Surface refinement','SUBSURF')
            modifier.levels = 1
            mesh = bpy.data.meshes.new_from_object(temp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        mesh.calc_loop_triangles()
        offset = len(vertices)
        vertices.extend([[round(v,5) for v in (obj.matrix_world @ vertex.co)] for vertex in mesh.vertices])
        faces.extend([[i+offset for i in triangle.vertices] for triangle in mesh.loop_triangles])
        if subdivide:
            bpy.data.objects.remove(temp, do_unlink=True)
    return dict(name=' / '.join(names), vertices=vertices, faces=faces, color=color)

models = {}
for key, names in GROUPS.items():
    # Separate lung lobes and heart chambers allow named anatomical hover labels.
    models[key] = {'parts':[mesh_part([name], '#DAC6AD' if name=='Trachea' else ('#D4B884' if name.startswith('Renal pelvis') else COLORS[key]), True) for name in names]}

bone_names = []
for obj in bpy.data.objects:
    name = obj.name
    if obj.type != 'MESH' or len(obj.data.vertices) < 10:
        continue
    if (name.startswith(('Vertebra ', 'Femur.', 'Tibia.', 'Fibula.', 'Humerus.', 'Radius.', 'Ulna.', 'Clavicle.', 'Scapula.', 'Hip bone.', 'Parietal bone.', 'Temporal bone.'))
        or name in ['Frontal bone','Occipital bone','Mandible','Sacrum','Atlas','Axis','Body of sternum','Manubrium of sternum']
        or name.lower().split('.')[0].endswith('rib')
        or ((' bone' in name.lower() or name.startswith(('Calcaneus.','Talus.'))) and any(s in name.lower() for s in ['metacarp','metatars','phalan','scaphoid','lunate','triquetr','pisiform','trapez','capitate','hamate','navicular','cuboid','cuneiform','calcaneus','talus']))):
        bone_names.append(name)
body_parts = [mesh_part(sorted(bone_names),'#D7C7AF')]
body_parts[0]['name'] = 'Reference skeleton'
for model in models.values():
    body_parts.extend(model['parts'])
models['whole_body'] = {'parts':body_parts}
for key, model in models.items():
    model['source_commit'] = '9de5d6912a1b0df9cab739d57f00e036b0496ddc'
    with gzip.GzipFile(filename=str(ROOT/'assets'/'anatomy'/f'{key}.json.gz'), mode='wb', mtime=0) as f:
        f.write(json.dumps(model,separators=(',',':')).encode())
    print('EXPORTED',key,sum(len(p['vertices']) for p in model['parts']),sum(len(p['faces']) for p in model['parts']),flush=True)
