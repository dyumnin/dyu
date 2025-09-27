"""
Arrow subclass: Adds start_connection/end_connection (object IDs).

Latch to objects on drag; resolves on draw/move.
"""
from .base_object import BaseObject
from typing import Optional, Tuple
import pygame


class Arrow(BaseObject):
    """
    Directed arrow with optional connections to other objects.

    Example:
        arrow = Arrow(start=(0,0), end=(100,100), start_connection="obj1_id")
        arrow.draw(surface)
    """
    start_connection: Optional[str] = None
    end_connection: Optional[str] = None

    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None) -> pygame.Rect:
        """
        Draw line from start to end; arrowhead at end.
        If connected, snap endpoints to object edges.
        """
        start_pos = self.start
        end_pos = self.end
        # Resolve connections (stub; canvas passes objects)
        if self.start_connection:
            # Fetch obj = canvas.get_by_id(self.start_connection); snap start_pos
            pass
        if self.end_connection:
            # Similar for end
            pass
        pygame.draw.line(surface, self.color, start_pos, end_pos, 2)
        if end_pos != start_pos:
            vec = pygame.math.Vector2(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
            angle = vec.angle_to((1,0))
            head_len = 10
            p1 = (end_pos[0] - head_len * pygame.math.Vector2(1,0).rotate(angle + 30).x,
                  end_pos[1] - head_len * pygame.math.Vector2(1,0).rotate(angle + 30).y)
            p2 = (end_pos[0] - head_len * pygame.math.Vector2(1,0).rotate(angle - 30).x,
                  end_pos[1] - head_len * pygame.math.Vector2(1,0).rotate(angle - 30).y)
            pygame.draw.line(surface, self.color, end_pos, p1, 2)
            pygame.draw.line(surface, self.color, end_pos, p2, 2)
        rect = pygame.Rect(min(start_pos[0], end_pos[0]), min(start_pos[1], end_pos[1]),
                          abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1]))
        if self.label and font:
            text = font.render(self.label, True, self.color)
            mid = ((start_pos[0] + end_pos[0]) // 2, (start_pos[1] + end_pos[1]) // 2)
            surface.blit(text, mid)
            rect.union_ip(text.get_rect(center=mid))
        return rect
