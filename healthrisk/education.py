"""Curated condition education, independent of simulated scores and filters."""
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'education'
CONDITIONS = {
    'Coronary artery disease': {
        'organ':'Heart', 'key':'cad',
        'visible':'Plaque within an artery wall narrows its lumen. The comparison focuses on an artery cross-section: coronary disease may not visibly change the outside of the heart.',
        'function':'Narrowing can restrict oxygen delivery to heart muscle. Plaque rupture and clot formation can cause an acute blockage; these complications are not shown or predicted here.',
        'factors':'Tobacco exposure, hypertension, abnormal blood lipids, diabetes, age, and family history are established risk factors. They do not establish a diagnosis in an individual.',
        'limits':'The cross-section is a mechanism diagram, not a scan, measurement of stenosis, or disease-specific 3D heart model.',
        'sources':[('OpenStax §20.2 Blood Flow, Blood Pressure, and Resistance','https://openstax.org/books/anatomy-and-physiology-2e/pages/20-2-blood-flow-blood-pressure-and-resistance'),('NHLBI: Coronary heart disease','https://www.nhlbi.nih.gov/health/coronary-heart-disease')],
    },
    'Emphysema': {
        'organ':'Lungs', 'key':'emphysema',
        'visible':'Loss of alveolar walls produces larger, connected airspaces and less gas-exchange surface. The drawing compares microscopic airspaces, not patient lung shape.',
        'function':'Reduced elastic recoil and surface area can impair gas exchange and make exhalation difficult. Air trapping may occur; severity cannot be read from this illustration.',
        'factors':'Tobacco smoke and other inhaled exposures are risk factors. Alpha-1 antitrypsin deficiency can also contribute. Emphysema can occur without a smoking history.',
        'limits':'The alveolar arrangement is schematic and not to scale. This is not a histology image or reconstructed diseased lung.',
        'sources':[('OpenStax §22.2 The Lungs','https://openstax.org/books/anatomy-and-physiology-2e/pages/22-2-the-lungs'),('NHLBI: COPD','https://www.nhlbi.nih.gov/health/copd')],
    },
    'Advanced CKD-related changes': {
        'organ':'Kidneys', 'key':'ckd',
        'visible':'The mechanism diagram contrasts functioning nephron units with scarred, nonfunctioning units. Fibrosis and nephron loss can occur in advanced chronic kidney disease. Some causes lead to small kidneys, but size may be normal or enlarged in others; no universal kidney shape is depicted.',
        'function':'Loss of filtration capacity can disrupt waste removal, fluid/electrolyte balance, and hormone production. These functions are not measured in the synthetic dataset.',
        'factors':'Diabetes, hypertension, inherited kidney disorders, and other kidney diseases can contribute. Smoking is a risk factor, but a smoking category cannot identify kidney damage.',
        'limits':'This is a conceptual tissue-level diagram, not a depiction of a particular CKD cause, stage, or patient scan. BMI, cholesterol and blood pressure alone cannot diagnose CKD.',
        'sources':[('OpenStax §25.3 Gross Anatomy of the Kidney','https://openstax.org/books/anatomy-and-physiology-2e/pages/25-3-gross-anatomy-of-the-kidney'),('NIDDK: Chronic kidney disease','https://www.niddk.nih.gov/health-information/kidney-disease/chronic-kidney-disease-ckd')],
    },
    'Cirrhosis': {
        'organ':'Liver', 'key':'cirrhosis',
        'visible':'Fibrous bands and regenerative nodules alter the architecture of liver tissue. The comparison is a tissue-pattern diagram, not a deformed healthy liver mesh.',
        'function':'Scarring can disrupt blood flow through the liver and impair liver functions. Portal hypertension can develop. Clinical severity varies and is not represented by these drawings.',
        'factors':'Chronic viral hepatitis, alcohol-associated liver disease, and metabolic dysfunction-associated steatotic liver disease are among the causes. Cirrhosis has multiple causes; smoking status is not a diagnosis.',
        'limits':'Nodule arrangement and band thickness are illustrative, not a validated staging scale. The dataset contains no liver enzymes, imaging, or fibrosis measurements.',
        'sources':[('OpenStax §23.6 Accessory Organs in Digestion','https://openstax.org/books/anatomy-and-physiology-2e/pages/23-6-accessory-organs-in-digestion-the-liver-pancreas-and-gallbladder'),('NIDDK: Cirrhosis','https://www.niddk.nih.gov/health-information/liver-disease/cirrhosis')],
    },
}


def condition_options(organ):
    return [name for name, details in CONDITIONS.items() if organ=='Whole body' or details['organ']==organ]


def illustration_path(condition, affected=False):
    return ASSETS / f"{CONDITIONS[condition]['key']}_{'condition' if affected else 'reference'}.png"


def cohort_context(df, condition):
    """Descriptive context never decides which educational illustration to display."""
    if df.empty:
        return f'No synthetic records match these filters. {condition} remains an independently selected educational topic; the illustrations are unchanged.'
    parts = [f'{len(df):,} synthetic records', f'mean age {df.age.mean():.1f}', f'mean BMI {df.bmi.mean():.1f}']
    counts = df.smoking_status.value_counts()
    parts += [f'{status}: {int(counts.get(status,0)):,}' for status in ['Never','Former','Current']]
    return '; '.join(parts) + f'. Topic: {condition}. These counts describe the selected data, not condition prevalence or inferred organ damage.'
