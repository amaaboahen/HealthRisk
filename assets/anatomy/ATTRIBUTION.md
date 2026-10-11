# Anatomical asset attribution and licensing

These meshes and the PNG renderings are **third-party anatomical artwork**, not
MIT-licensed application code. Preserve this notice, the upstream notices, and
applicable attribution/share-alike terms when redistributing them.

## Source (all five views)

**Z-Anatomy — The libre 3D atlas of anatomy**, by Gauthier Kervyn (design, 3D,
anatomy), Marcin Zielinski (Blender scripting), and contributors, derived in part
from **BodyParts3D — The Database Center for Life Science**, original model by
Kousaku Okubo.

- Repository: https://github.com/Z-Anatomy/Models-of-human-anatomy
- Pinned commit: `9de5d6912a1b0df9cab739d57f00e036b0496ddc`
- Archive: `Z-Anatomy.zip`, embedded `Z-Anatomy/Startup.blend`
- Upstream atlas license: **Creative Commons Attribution-ShareAlike 4.0 International**
  https://creativecommons.org/licenses/by-sa/4.0/
- BodyParts3D original attribution: **CC BY-SA 2.1 Japan**
  https://creativecommons.org/licenses/by-sa/2.1/jp/
- Original database: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/
- Full upstream statements are retained in `UPSTREAM-LICENSE.txt` and
  `UPSTREAM-README.md`, including references not exported here.

## Kidney reference restriction

The upstream atlas explicitly credits **“Kidney — by Lissie Cowley — CC BY-NC
4.0”**, https://creativecommons.org/licenses/by-nc/4.0/.
It does not supply per-object provenance distinguishing the kidney references.
We retain this attribution and conservatively treat `kidneys.json.gz`, the
kidney geometry included in `whole_body.json.gz`, and their corresponding PNGs
as carrying this **noncommercial** restriction in addition to applicable upstream
attribution. This is an educational, noncommercial deployment; do not assume these
assets are cleared for commercial use. Obtain clarification or replace the kidney
meshes before a commercial deployment. No claim is made that the atlas's blanket
CC BY-SA statement removes the reference's restriction.

## Included geometry

| File | Atlas object names / anatomy |
|---|---|
| `heart.json.gz` | Left atrium, Right atrium, Left ventricle, Right ventricle, Pulmonary trunk |
| `lungs.json.gz` | Superior/inferior lobes of left lung, superior/middle/inferior lobes of right lung, Trachea |
| `kidneys.json.gz` | Kidney.l, Kidney.r, Renal pelvis.l, Renal pelvis.r |
| `liver.json.gz` | Liver |
| `whole_body.json.gz` | Reference skeleton (selected skull, spine, ribs, sternum, limb, hand/foot and pelvic bones), plus the four organ groups above |

## Changes from the source

Extracted selected meshes into world coordinates with Blender, triangulated and
subdivided organ surfaces once, simplified triangles for browser performance,
rounded coordinates to five decimals, and stored compressed JSON. Skeleton
parts are merged into one render layer. Full extraction rules are in
`tools/export_anatomy.py`; reduction rules are in `tools/optimize_anatomy.py`.
PNG fallbacks are rendered from these same meshes by `tools/render_anatomy.py`.
Display normalization centers/scales each view; relative positions within a view
are retained. Materials are replaced with consistent naturalistic tissue/bone
colors and lighting. These are surface atlas representations, not scans,
patient-specific anatomy, complete dissection models, or clinical illustrations
validated for diagnosis. Mesh simplification removes fine detail.

**The same asset, geometry, material, and starting camera are used in Lower and
Higher simulation panels. No risk score or patient record affects the anatomy.**
