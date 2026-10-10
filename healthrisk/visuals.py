"""Original vector schematics drawn from simple geometric primitives."""
import re
import plotly.graph_objects as go

PATHS = {
    "Heart": 'M100 140 C20 95 40 35 75 55 Q100 20 125 55 C160 35 180 95 100 140Z',
    "Lungs": 'M90 45 C45 25 25 110 45 135 Q75 150 90 110Z M110 45 C155 25 175 110 155 135 Q125 150 110 110Z',
    "Kidneys": 'M75 40 C20 35 20 140 75 135 Q100 120 75 95 Q50 85 80 65Z M125 40 C180 35 180 140 125 135 Q100 120 125 95 Q150 85 120 65Z',
    "Liver": 'M30 65 Q90 25 170 60 L150 100 Q110 100 85 135 L30 120Z',
    "Whole body": 'M85 55 L115 55 L145 100 L130 110 L115 85 L115 120 L130 155 L110 160 L100 130 L90 160 L70 155 L85 120 L85 85 L70 110 L55 100Z',
}


def schematic(organ):
    fig = go.Figure()
    for offset, color, label in [(0, "#2DD4BF", "LOWER SIMULATION LABEL"), (220, "#FB923C", "HIGHER SIMULATION LABEL")]:
        # Every pair in these original paths is an absolute x/y coordinate.
        coordinates = iter(re.findall(r"-?\d+(?:\.\d+)?", PATHS[organ]))
        axis = [0]
        def translate(match):
            value = float(next(coordinates)) + (offset if axis[0] % 2 == 0 else 25)
            axis[0] += 1
            return str(value)
        path = re.sub(r"-?\d+(?:\.\d+)?", translate, PATHS[organ])
        fig.add_shape(type="path", path=path, xref="x", yref="y", fillcolor=color, opacity=.65,
                      line=dict(color=color, width=3))
        if organ == "Whole body":
            fig.add_shape(type="circle", x0=offset+85, x1=offset+115, y0=190, y1=220, fillcolor=color, line_color=color)
        fig.add_annotation(x=offset+100, y=5, text=label, showarrow=False, font=dict(size=11, color=color))
    fig.update_layout(height=260, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      xaxis=dict(range=[0,420], visible=False), yaxis=dict(range=[0,220], visible=False), showlegend=False)
    return fig
