"""
Shape classes for Infinity Canvas.
"""

import pygame
from dyu.canvas.base_object import BaseObject
from dyu.canvas.arrow import Arrow
import logging


class Rectangle(BaseObject):
    def draw(self, surface, font=None, canvas=None):
        # Skip zero-sized rectangles
        if self.start == self.end or not canvas:
            logging.debug(
                f"Skipping draw for zero-sized Rectangle: start={self.start}, end={self.end}"
            )
            return pygame.Rect(0, 0, 0, 0)
        screen_pos, screen_width, screen_height = self.get_coords(canvas)
        # world_x = min(self.start[0],self.end[0])
        # world_y = min(self.start[1],self.end[1])
        # world_width = abs(self.end[0] - self.start[0])
        # world_height = abs(self.end[1] - self.start[1])
        # screen_pos = canvas.world_to_screen((world_x, world_y))
        # screen_width= world_width * canvas.zoon
        # screen_height= world_height * canvas.zoon
        if screen_width < 1 or screen_height < 1:
            return pygame.Rect(screen_pos[0], screen_pos[1], 0, 0)
        screen_rect = pygame.Rect(
            screen_pos[0], screen_pos[1], screen_width, screen_height
        )
        pygame.draw.rect(surface, self.fill_color, screen_rect)
        pygame.draw.rect(surface, self.color, screen_rect, 2)
        if self.label and font:
            text = font.render(self.label, True, self.color)
            surface.blit(text, (screen_rect.x + 5, screen_rect.y + 5))
        return screen_rect


class Text(BaseObject):
    def draw(self, surface, font=None, canvas=None):
        screen_pos, screen_width, screen_height = self.get_coords(canvas)
        y = screen_pos[1]
        x = screen_pos[0]
        if font and self.label:
            lines = self.label.split("\n")
            for line in lines:
                surf = font.render(line, True, self.color)
                surface.blit(surf, (x, y))
                y += font.get_height()
        return pygame.Rect(x, y, 0, font.get_height)


class Circle(BaseObject):
    def draw(self, surface, font=None, canvas=None):
        center = (
            (self.start[0] + self.end[0]) // 2,
            (self.start[1] + self.end[1]) // 2,
        )
        radius = (
            min(abs(self.end[0] - self.start[0]), abs(self.end[1] - self.start[1])) // 2
        )
        if radius == 0:
            logging.debug(
                f"Skipping draw for zero-sized Circle: start={self.start}, end={self.end}"
            )
            return pygame.Rect(0, 0, 0, 0)
        screen_center = canvas.world_to_screen(center)
        screen_radiut = canvas.world_to_screen(raidus)
        pygame.draw.circle(surface, self.fill_color, screen_center, screen_radius)
        pygame.draw.circle(surface, self.color, screen_center, screen_radius, 2)
        return pygame.Rect(
            center[0] - screen_radius,
            screen_center[1] - screen_radius,
            screen_radius * 2,
            screen_radius * 2,
        )


SUBCLASS_MAP = {"Rectangle": Rectangle, "Arrow": Arrow, "Text": Text, "Circle": Circle}
