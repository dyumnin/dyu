from .base_object import BaseObject
from typing import Optional, Tuple
import pygame
import math

class Arrow(BaseObject):
    """
    Directed arrow with optional connections to other objects.

    Example:
        arrow = Arrow(start=(0,0), end=(100,100), start_connection="obj1_id")
        arrow.draw(surface)
    """

    start_connection: Optional[str] = None
    end_connection: Optional[str] = None

    def draw(
        self,
        surface: pygame.Surface,
        font: Optional[pygame.font.Font] = None,
        canvas=None,
    ) -> pygame.Rect:
        """
        Draw line from start to end; arrowhead at end, correctly oriented for all directions.
        If connected, snap endpoints to object edges.
        """
        start_pos = self.start
        end_pos = self.end
        screen_start_pos = canvas.world_to_screen(start_pos)
        screen_end_pos = canvas.world_to_screen(end_pos)
        # Resolve connections (stub; canvas passes objects)
        if self.start_connection:
            # Fetch obj = canvas.get_by_id(self.start_connection); snap start_pos
            pass
        if self.end_connection:
            # Similar for end
            pass
        # Draw the main line
        pygame.draw.line(surface, self.color, screen_start_pos, screen_end_pos, 2)

        # Draw arrowhead if not a zero-length line
        if end_pos != start_pos:
            # Compute direction vector and normalize
            dx = screen_end_pos[0] - screen_start_pos[0]
            dy = screen_end_pos[1] - screen_start_pos[1]
            length = math.hypot(dx, dy)
            if length > 0:  # Avoid division by zero
                dx, dy = dx / length, dy / length  # Unit vector
                head_len = 10
                head_angle = math.radians(30)  # ±30° for arrowhead wings
                # Arrowhead points: rotate unit vector by ±30° and scale
                cos_a, sin_a = math.cos(head_angle), math.sin(head_angle)
                # First wing: rotate (dx, dy) by +30°
                p1_x = screen_end_pos[0] - head_len * (dx * cos_a - dy * sin_a)
                p1_y = screen_end_pos[1] - head_len * (dx * sin_a + dy * cos_a)
                # Second wing: rotate (dx, dy) by -30°
                p2_x = screen_end_pos[0] - head_len * (dx * cos_a + dy * sin_a)
                p2_y = screen_end_pos[1] - head_len * (-dx * sin_a + dy * cos_a)
                pygame.draw.line(surface, self.color, screen_end_pos, (p1_x, p1_y), 2)
                pygame.draw.line(surface, self.color, screen_end_pos, (p2_x, p2_y), 2)

        # Compute bounding box
        rect = pygame.Rect(
            min(screen_start_pos[0], screen_end_pos[0]),
            min(screen_start_pos[1], screen_end_pos[1]),
            abs(screen_end_pos[0] - screen_end_pos[0]) + 1,  # +1 to ensure non-zero
            abs(screen_end_pos[1] - screen_start_pos[1]) + 1,
        )
        # Draw label if present
        if self.label and font:
            text = font.render(self.label, True, self.color)
            mid = (
                (screen_start_pos[0] + screen_end_pos[0]) // 2,
                (screen_start_pos[1] + screen_end_pos[1]) // 2,
            )
            surface.blit(text, mid)
            rect.union_ip(text.get_rect(center=mid))
        # Pad bounding box for selection (fixes editability issue)
        rect.inflate_ip(10, 10)  # Add padding for easier clicking
        return rect
