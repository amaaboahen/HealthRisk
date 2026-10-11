"""Original source-informed mechanism diagrams. No atlas mesh is deformed.

Run with development CairoSVG: .venv/bin/python -m tools.build_education
See assets/education/ATTRIBUTION.md for factual references and artwork licenses.
"""
from pathlib import Path
import cairosvg

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'education'


def label(text,y=400):
    return f'<text x="300" y="{y}" text-anchor="middle" fill="#e6eef7" font-size="20">{text}</text>'


def wrap(content,title,subtitle):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="460" viewBox="0 0 600 460">
<defs><radialGradient id="tissue"><stop stop-color="#e5aaa0"/><stop offset="1" stop-color="#98554f"/></radialGradient>
<radialGradient id="air"><stop stop-color="#eef0e9"/><stop offset="1" stop-color="#cdb0a8"/></radialGradient></defs>
<rect width="600" height="460" rx="18" fill="#102237"/>
<text x="300" y="38" text-anchor="middle" fill="#2dd4bf" font-family="sans-serif" font-size="23" font-weight="bold">{title}</text>
<g font-family="sans-serif">{content}{label(subtitle,420)}
<text x="300" y="448" text-anchor="middle" fill="#9fb3c8" font-size="12">Educational mechanism schematic · not to scale · no patient inference</text></g></svg>'''


for key in ['cad','emphysema','ckd','cirrhosis']:
    for affected in [False,True]:
        if key=='cad':
            content='<circle cx="300" cy="220" r="140" fill="url(#tissue)" stroke="#e8b3a4" stroke-width="5"/>'
            if affected:
                content+='<circle cx="300" cy="220" r="105" fill="#dbbd71"/><path d="M325 134 C410 145 390 280 318 302 C272 307 254 282 273 249 C299 213 264 166 325 134Z" fill="#712f3e" stroke="#ecb7a7" stroke-width="5"/>'
                content+=label('Plaque in wall → narrower lumen',390)
            else:
                content+='<circle cx="300" cy="220" r="105" fill="#712f3e" stroke="#ecb7a7" stroke-width="5"/>'+label('Patent lumen inside artery wall',390)
            title='Coronary artery disease' if affected else 'Reference artery'
            subtitle='Artery cross-section · illustrative plaque' if affected else 'Artery cross-section · no plaque shown'
        elif key=='emphysema':
            content='<rect x="100" y="85" width="400" height="270" rx="60" fill="url(#tissue)"/>'
            if affected:
                content+='<path d="M160 120 Q215 82 256 136 Q330 84 375 128 Q465 111 455 205 Q494 263 424 297 Q360 361 310 298 Q237 360 204 302 Q126 313 140 243 Q105 170 160 120Z" fill="url(#air)" stroke="#8a5358" stroke-width="7"/>'
                content+=label('Lost septa → enlarged connected spaces',390)
            else:
                for x,y in [(170,150),(270,150),(370,150),(220,245),(320,245),(420,245)]:
                    content+=f'<ellipse cx="{x}" cy="{y}" rx="50" ry="52" fill="url(#air)" stroke="#8a5358" stroke-width="8"/>'
                content+=label('Many airspaces separated by septa',390)
            title='Emphysema mechanism' if affected else 'Reference alveolar tissue'
            subtitle='Alveolar walls and airspaces'
        elif key=='ckd':
            content='<rect x="100" y="85" width="400" height="270" rx="35" fill="url(#tissue)"/>'
            for i,(x,y) in enumerate([(175,155),(285,155),(395,155),(175,265),(285,265),(395,265)]):
                scarred=affected and i in [0,2,3,4]
                if scarred:
                    content+=f'<path d="M{x-35} {y-30} l70 60 m-70 0 l70 -60 m-70 30 h70" stroke="#ead6b6" stroke-width="11"/>'
                else:
                    content+=f'<circle cx="{x}" cy="{y}" r="29" fill="#bd5662" stroke="#f5b2a7" stroke-width="6"/><path d="M{x+30} {y} q32 20 12 38 q-28 18 -2 34" fill="none" stroke="#edc689" stroke-width="10"/>'
            title='Advanced CKD: fibrosis concept' if affected else 'Reference nephron units'
            content+=label('Fibrosis and loss of functioning units' if affected else 'Glomeruli and tubules: simplified units',390)
            subtitle='Tissue-level concept · no stage or size inferred'
        else:
            content='<rect x="100" y="85" width="400" height="270" rx="40" fill="url(#tissue)"/>'
            if affected:
                for x,y,r in [(173,157,48),(295,163,54),(416,151,46),(224,274,53),(373,270,56)]:
                    content+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="#b77665" stroke="#ead1a6" stroke-width="12"/>'
                content+='<path d="M100 225 Q270 220 310 85 M305 227 Q410 225 500 225 M305 228 L305 355" fill="none" stroke="#ead1a6" stroke-width="12"/>'
            else:
                for x,y in [(175,153),(300,153),(425,153),(240,267),(365,267)]:
                    content+=f'<polygon points="{x-50},{y-25} {x},{y-55} {x+50},{y-25} {x+50},{y+25} {x},{y+55} {x-50},{y+25}" fill="#b77665" stroke="#ce9b87" stroke-width="3"/><circle cx="{x}" cy="{y}" r="8" fill="#783d51"/>'
            title='Cirrhosis tissue pattern' if affected else 'Reference liver architecture'
            content+=label('Fibrous bands separate regenerative nodules' if affected else 'Regular lobular organization: simplified',390)
            subtitle='Conceptual tissue architecture'
        svg=wrap(content,title,subtitle)
        name=f"{key}_{'condition' if affected else 'reference'}"
        (ROOT/f'{name}.svg').write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(ROOT/f'{name}.png'),output_width=1200,output_height=920)
