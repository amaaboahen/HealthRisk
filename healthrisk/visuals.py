"""Bundled atlas meshes: identical anatomy in both synthetic comparison panels."""
from functools import lru_cache
from pathlib import Path
import gzip
import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ASSET_DIR = Path(__file__).resolve().parents[1] / 'assets' / 'anatomy'
MODEL_KEYS = {'Heart':'heart', 'Lungs':'lungs', 'Kidneys':'kidneys', 'Liver':'liver', 'Whole body':'whole_body'}
CAMERA = dict(eye=dict(x=0, y=-2.1, z=.35), up=dict(x=0,y=0,z=1), center=dict(x=0,y=0,z=0))


@lru_cache(maxsize=5)
def load_model(organ):
    """Load only local, reviewed assets; never accept paths or mesh data from CSVs."""
    with gzip.open(ASSET_DIR / f'{MODEL_KEYS[organ]}.json.gz', 'rt') as source:
        return json.load(source)


@lru_cache(maxsize=10)
def anatomy_figure(organ, comparison=True):
    model = load_model(organ)
    columns = 2 if comparison else 1
    titles = ['Lower simulation label', 'Higher simulation label'] if comparison else [organ]
    fig = make_subplots(rows=1, cols=columns, specs=[[{'type':'scene'}]*columns], subplot_titles=titles, horizontal_spacing=.04)
    # One shared normalization preserves the relative positions of all atlas parts.
    all_vertices = np.concatenate([np.asarray(part['vertices']) for part in model['parts']])
    center = (all_vertices.max(axis=0) + all_vertices.min(axis=0))/2
    scale = np.max(np.ptp(all_vertices, axis=0))/2
    for column in range(1, columns+1):
        for part in model['parts']:
            vertices = ((np.asarray(part['vertices'])-center)/scale).astype(np.float32)
            faces = np.asarray(part['faces'], dtype=np.int32)
            fig.add_trace(go.Mesh3d(x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                i=faces[:,0], j=faces[:,1], k=faces[:,2],
                color=part['color'], name=part['name'], opacity=part.get('opacity',1),
                flatshading=False, lighting=dict(ambient=.45, diffuse=.85, specular=.25, roughness=.65, fresnel=.1),
                lightposition=dict(x=-100,y=-200,z=300), hovertemplate=part['name']+'<extra></extra>', showlegend=False), row=1,col=column)
    axis = dict(visible=False, showbackground=False)
    for col in range(1, columns+1):
        scene = 'scene' if col==1 else f'scene{col}'
        fig.update_layout(**{scene:dict(xaxis=axis,yaxis=axis,zaxis=axis,aspectmode='data',camera=(dict(eye=dict(x=0,y=-3.8,z=.15),up=dict(x=0,y=0,z=1),center=dict(x=0,y=0,z=0)) if organ=='Whole body' else CAMERA),
                                       dragmode='orbit',bgcolor='#102237')})
    fig.update_layout(height=500 if comparison else 650, paper_bgcolor='#102237', plot_bgcolor='#102237',
        margin=dict(l=5,r=5,t=45,b=5), font=dict(color='#E6EEF7'), uirevision=f'anatomy-{organ}',
        meta=dict(organ=organ,identical_comparison=True,source='Z-Anatomy atlas'))
    return fig


def fallback_path(organ):
    return ASSET_DIR / f'{MODEL_KEYS[organ]}.png'
