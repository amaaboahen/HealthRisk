"""Independent educational comparison views with no anatomy-module dependency."""
import base64
from functools import lru_cache
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .education import illustration_path


@lru_cache(maxsize=8)
def condition_figure(condition):
    """Independent pan/zoom of honest 2D mechanism illustrations, never fake 3D."""
    fig = make_subplots(rows=1,cols=2,subplot_titles=['Healthy / reference structure','Selected condition · schematic'],horizontal_spacing=.04)
    for column, affected in [(1,False),(2,True)]:
        image = base64.b64encode(illustration_path(condition,affected).read_bytes()).decode()
        axis = '' if column==1 else '2'
        # Invisible bounds establish the view, with images anchored in data coordinates.
        fig.add_trace(go.Scatter(x=[0,600],y=[0,460],mode='markers',marker=dict(opacity=0),hoverinfo='skip',showlegend=False),row=1,col=column)
        fig.add_layout_image(dict(source='data:image/png;base64,'+image,xref='x'+axis,yref='y'+axis,
            x=0,y=0,sizex=600,sizey=460,xanchor='left',yanchor='top',sizing='stretch',layer='below'))
        fig.update_xaxes(range=[0,600],visible=False,constrain='domain',row=1,col=column)
        fig.update_yaxes(range=[460,0],visible=False,scaleanchor='x'+axis,scaleratio=1,row=1,col=column)
    fig.update_layout(height=540,dragmode='pan',paper_bgcolor='#102237',plot_bgcolor='#102237',
        margin=dict(l=5,r=5,t=45,b=5),font=dict(color='#E6EEF7'),uirevision='education-'+condition,
        meta=dict(condition=condition,medium='2D educational mechanism schematic',population_independent=True))
    return fig
