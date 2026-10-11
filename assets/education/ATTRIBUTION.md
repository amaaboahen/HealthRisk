# Education artwork: sources, licenses, and limitations

## Original mechanism diagrams

`cad_*`, `emphysema_*`, `ckd_*`, and `cirrhosis_*` SVG/PNG pairs are **original
HealthRisk mechanism schematics**, distributed under this repository's MIT
license. They communicate standard medical concepts; they do not copy source
illustration artwork or deform atlas meshes. `tools/build_education.py` contains
the complete drawing instructions. SVGs are editable masters; PNGs are rendered
at 1200×920 for deployment without CairoSVG.

- Coronary artery disease: plaque in the arterial wall reduces lumen space;
  OpenStax Anatomy and Physiology 2e, Blood Flow, Blood Pressure, and Resistance,
  “Disorders of the Cardiovascular System: Arteriosclerosis” (`m46635`), and
  Heart Physiology (`m46676`).
- Emphysema: schematic loss of alveolar septa and enlargement of airspaces;
  OpenStax The Lungs (`m46548`) supplies normal gas-exchange anatomy; NHLBI COPD
  patient education supplies disease context: https://www.nhlbi.nih.gov/health/copd.
- Advanced CKD: conceptual nephron loss/fibrosis, **not a universal shrunken kidney**;
  OpenStax Gross Anatomy of the Kidney (`m46429`), renal physiology and renal
  failure discussions, with NIDDK CKD education:
  https://www.niddk.nih.gov/health-information/kidney-disease/chronic-kidney-disease-ckd.
- Cirrhosis: schematic fibrous bands and regenerative nodules; OpenStax Accessory
  Organs in Digestion (`m46496`) supplies normal liver anatomy/function;
  NIDDK cirrhosis education supplies disease context:
  https://www.niddk.nih.gov/health-information/liver-disease/cirrhosis.

OpenStax source modules were inspected from the pinned edition below. NIH links
are supplied as authoritative further reading; direct NIH page retrieval was
blocked by the build environment. The drawings are educational summaries of
standard mechanisms, **not independently clinically reviewed or validated medical
illustrations**, diagnostic images, quantitative pathology, histology, or 3D disease
models. Septal arrangements, nephron icons, and liver patterns are deliberately
schematic and not to scale. Whole-body topics reuse the corresponding tissue-level
insets; they do not create a disease-specific body mesh.

## Reused OpenStax illustrations (commercial reuse permitted under CC BY 4.0)

OpenStax, **Anatomy and Physiology 2e**, Rice University and contributing authors.
Source repository: https://github.com/openstax/osbooks-anatomy-physiology
Pinned historical commit: `b0058a743bdd2cc08196abaaa7d5469970c0d80c`.
This specific edition has **Creative Commons Attribution 4.0 International**:
https://creativecommons.org/licenses/by/4.0/.
The edition's full legal notice is retained in `OPENSTAX-LICENSE.txt`.

The source repository changed its license on 2026-03-19 in commit `fdfa6e2`.
**These files come from the earlier, explicitly CC BY 4.0 licensed edition**;
no later noncommercial artwork is imported. CC BY permissions already granted
are irrevocable when their terms are followed. Preserve this attribution and
pin when redistributing these assets.

| Bundled file | Original | Changes |
|---|---|---|
| `kidney_reference.jpg` | `media/2610_The_Kidney.jpg`, module `m46429` | None |
| `atherosclerosis_panel_a.jpg` | `media/2113ab_Atherosclerosis.jpg`, module `m46635` | Cropped to panel (a) only; excluded the separately credited University of Michigan micrograph in panel (b) |

Artwork color and anatomy are never generated from demographic characteristics,
smoking history, or simulated scores. The condition must be selected manually.
