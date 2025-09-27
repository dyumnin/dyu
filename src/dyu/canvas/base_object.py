"""
Base class for all placable objects.

Properties: id, startpoint (x,y), endpoint (x,y), label, color (RGB tuple),
fill_color (RGB tuple), description (Markdown str), children (list of BaseObject).

Each subclass implements draw(surface: pygame.Surface) -> pygame.Rect (bounding box).
Supports serialization for JSON/pickle.
"""
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional
import pygame


@dataclass
class BaseObject:
    """
    Base for all canvas objects. Derived classes add specific draw logic.

    Example:
        obj = Rectangle(start=(0,0), end=(100,100), label="Box")
        rect = obj.draw(surface)
        # rect is the bounding Rect for positioning
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start: Tuple[int, int] = (0, 0)
    end: Tuple[int, int] = (100, 100)
    label: str = ""
    color: Tuple[int, int, int] = (0, 0, 0)
    fill_color: Tuple[int, int, int] = (255, 255, 255)
    description: str = ""
    children: List['BaseObject'] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None) -> pygame.Rect:
        """
        Draw self and children recursively. Returns bounding Rect.

        Subclasses override for specific rendering (e.g., line, rect).
        """
        rect = pygame.Rect(self.start[0], self.start[1], 0, 0)
        # Draw children first (background)
        for child in self.children:
            child_rect = child.draw(surface, font)
            rect.union_ip(child_rect)
        # Draw self (stub; override in subclass)
        if self.label and font:
            text_surf = font.render(self.label, True, self.color)
            surface.blit(text_surf, self.start)
            rect.union_ip(text_surf.get_rect(topleft=self.start))
        return rect

    def get_bounding_box(self) -> pygame.Rect:
        """Compute full bounding box including children."""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        points = [(self.start, self.end)]
        for child in self.children:
            c_box = child.get_bounding_box()
            points.append((c_box.topleft, c_box.bottomright))
        for start, end in points:
            min_x = min(min_x, start[0], end[0])
            min_y = min(min_y, start[1], end[1])
            max_x = max(max_x, start[0], end[0])
            max_y = max(max_y, start[1], end[1])
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def to_dict(self) -> dict:
        """For JSON serialization (recursive)."""
        data = asdict(self)
        data['children'] = [c.to_dict() for c in self.children]
        return data

    @classmethod
    def from_dict(cls, data: dict, subclass_map: dict = None):
        """Factory from dict (use subclass_map for type dispatch)."""
        # Stub; implement in canvas for type resolution
        obj = cls(**{k: v for k, v in data.items() if k != 'children'})
        obj.children = [BaseObject.from_dict(c, subclass_map) for c in data.get('children', [])]
        return obj

    def has_description(self) -> bool:
        """True if description is nonempty."""
        return bool(self.description.strip())
