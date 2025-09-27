"""
Save/load and SVG export for Infinity Canvas.
"""
import json
import pickle
import logging
from pathlib import Path
from dyu.canvas.shapes import SUBCLASS_MAP

def save(canvas, path: str):
    """Save to path in default_format."""
    fmt = Path(path).suffix.lstrip('.') or canvas.default_format
    logging.debug(f"Saving to {path} with format {fmt}")
    if fmt == 'pickle':
        with open(path, 'wb') as f:
            pickle.dump(canvas.children, f)
    elif fmt == 'json':
        data = {'objects': [o.to_dict() for o in canvas.children]}
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    elif fmt == 'svg':
        svg = export_svg(canvas)
        with open(path, 'w') as f:
            f.write(svg)
    logging.debug(f"Saved {len(canvas.children)} objects to {path}")

def load(canvas, path: str):
    """Load from path (detect fmt)."""
    from dyu.canvas.base_object import BaseObject
    fmt = Path(path).suffix.lstrip('.')
    logging.debug(f"Loading from {path} with format {fmt}")
    if fmt == 'pickle':
        with open(path, 'rb') as f:
            canvas.children = pickle.load(f)
    elif fmt == 'json':
        with open(path) as f:
            data = json.load(f)
        canvas.children = [SUBCLASS_MAP.get(o.get('__type__', 'BaseObject'), BaseObject).from_dict(o, SUBCLASS_MAP) for o in data['objects']]
    logging.debug(f"Loaded {len(canvas.children)} objects: {[obj.__class__.__name__ for obj in canvas.children]}")

def export_svg(canvas) -> str:
    """Generate basic SVG string."""
    w, h = 1200, 800
    svg = f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">\n'
    for obj in canvas.children:
        if isinstance(obj, canvas.SUBCLASS_MAP['Rectangle']):
            x, y, w_, h_ = obj.start[0], obj.start[1], obj.end[0]-obj.start[0], obj.end[1]-obj.start[1]
            svg += f'<rect x="{x}" y="{y}" width="{w_}" height="{h_}" fill="rgb{obj.fill_color}" stroke="rgb{obj.color}" stroke-width="2"/>\n'
            if obj.label:
                svg += f'<text x="{x+5}" y="{y+20}" fill="rgb{obj.color}">{obj.label}</text>\n'
        elif isinstance(obj, canvas.SUBCLASS_MAP['Arrow']):
            svg += f'<line x1="{obj.start[0]}" y1="{obj.start[1]}" x2="{obj.end[0]}" y2="{obj.end[1]}" stroke="rgb{obj.color}" stroke-width="2"/>\n'
        elif isinstance(obj, canvas.SUBCLASS_MAP['Text']):
            svg += f'<text x="{obj.start[0]}" y="{obj.start[1]}" fill="rgb{obj.color}">{obj.label}</text>\n'
        elif isinstance(obj, canvas.SUBCLASS_MAP['Circle']):
            cx, cy = (obj.start[0] + obj.end[0]) // 2, (obj.start[1] + obj.end[1]) // 2
            r = min(abs(obj.end[0] - obj.start[0]), abs(obj.end[1] - obj.start[1])) // 2
            svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="rgb{obj.fill_color}" stroke="rgb{obj.color}" stroke-width="2"/>\n'
    svg += '</svg>'
    return svg
