"""
Shape classes for Infinity Canvas.
"""
import pygame
from dyu.canvas.base_object import BaseObject
from dyu.canvas.arrow import Arrow
import logging

class Rectangle(BaseObject):
    def draw(self, surface, font=None):
        # Skip zero-sized rectangles
        if self.start == self.end:
            logging.debug(f"Skipping draw for zero-sized Rectangle: start={self.start}, end={self.end}")
            return pygame.Rect(0, 0, 0, 0)
        rect = pygame.Rect(self.start[0], self.start[1], self.end[0]-self.start[0], self.end[1]-self.start[1])
        pygame.draw.rect(surface, self.fill_color, rect)
        pygame.draw.rect(surface, self.color, rect, 2)
        if self.label and font:
            text = font.render(self.label, True, self.color)
            surface.blit(text, (self.start[0] + 5, self.start[1] + 5))
        return rect

class Text(BaseObject):
    def draw(self, surface, font=None):
        y = self.start[1]
        if font and self.label:
            lines = self.label.split('\n')
            for line in lines:
                surf = font.render(line, True, self.color)
                surface.blit(surf, (self.start[0], y))
                y += font.get_height()
        return pygame.Rect(self.start[0], self.start[1], 0, y - self.start[1])

class Circle(BaseObject):
    def draw(self, surface, font=None):
        center = ((self.start[0] + self.end[0]) // 2, (self.start[1] + self.end[1]) // 2)
        radius = min(abs(self.end[0] - self.start[0]), abs(self.end[1] - self.start[1])) // 2
        if radius == 0:
            logging.debug(f"Skipping draw for zero-sized Circle: start={self.start}, end={self.end}")
            return pygame.Rect(0, 0, 0, 0)
        pygame.draw.circle(surface, self.fill_color, center, radius)
        pygame.draw.circle(surface, self.color, center, radius, 2)
        return pygame.Rect(center[0] - radius, center[1] - radius, radius*2, radius*2)

SUBCLASS_MAP = {'Rectangle': Rectangle, 'Arrow': Arrow, 'Text': Text, 'Circle': Circle}
