"""
Rendering and transformation logic for Infinity Canvas.
"""
import pygame
from pygame.locals import *
import logging
from typing import Tuple
from dyu.canvas.shapes import SUBCLASS_MAP

def screen_to_world(canvas, pos: Tuple[int, int]) -> Tuple[float, float]:
    """Transform screen pos to world coords."""
    x = (pos[0] - canvas.screen.get_width() / 2 - canvas.pan[0]) / canvas.zoom
    y = (pos[1] - canvas.screen.get_height() / 2 - canvas.pan[1]) / canvas.zoom
    logging.debug(f"screen_to_world: screen={pos}, world=({x}, {y})")
    return (x, y)

def world_to_screen(canvas, pos: Tuple[float, float]) -> Tuple[int, int]:
    """Inverse transform."""
    x = int(canvas.pan[0] + pos[0] * canvas.zoom + canvas.screen.get_width() / 2)
    y = int(canvas.pan[1] + pos[1] * canvas.zoom + canvas.screen.get_height() / 2)
    logging.debug(f"world_to_screen: world={pos}, screen=({x}, {y})")
    return (x, y)

def draw(canvas):
    """Clear, transform/draw objects, UI."""
    canvas.screen.fill((255, 255, 255))
    temp_surf = pygame.Surface(canvas.screen.get_size(), pygame.SRCALPHA)
    temp_surf.fill((255, 255, 255, 0))  # Transparent background
    logging.debug(f"Drawing {len(canvas.children)} objects")

    # Draw debug rectangle to ensure rendering works
    pygame.draw.rect(temp_surf, (255, 0, 0), (50, 50, 100, 100), 2)
    logging.debug("Drew debug rectangle at (50, 50, 100, 100)")

    # Draw all persistent objects
    for obj in canvas.children:
        logging.debug(f"Drawing object: {obj.__class__.__name__}, start={obj.start}, end={obj.end}")
        obj.draw(temp_surf, canvas.font)

    # Draw preview for create mode
    if canvas.create_mode and canvas.create_start:
        mouse_pos = screen_to_world(canvas, pygame.mouse.get_pos())
        logging.debug(f"Preview: mode={canvas.create_mode}, start={canvas.create_start}, end={mouse_pos}")
        preview_obj = SUBCLASS_MAP[canvas.create_mode](
            start=canvas.create_start,
            end=mouse_pos,
            color=(100, 100, 100),  # Gray for preview
            fill_color=(200, 200, 200, 128) if canvas.create_mode != 'Arrow' else None,  # Semi-transparent
            label="Preview" if canvas.create_mode == 'Text' else ""
        )
        preview_obj.draw(temp_surf, canvas.font)

    # Simplified scaling to avoid off-screen issues
    canvas.screen.blit(temp_surf, (0, 0))
    if canvas.hovered and canvas.hovered.has_description():
        draw_tooltip(canvas, canvas.hovered.description)
    if canvas.selected:
        box = canvas.selected.get_bounding_box()
        s_box = pygame.Rect(world_to_screen(canvas, box.topleft), (box.width * canvas.zoom, box.height * canvas.zoom))
        pygame.draw.rect(canvas.screen, (0, 0, 255), s_box, 2)
    pygame.display.flip()

def draw_tooltip(canvas, md_text: str):
    """Parse basic MD to Pygame text, draw as hover box."""
    lines = []
    for line in md_text.split('\n'):
        if line.startswith('- '):
            surf = canvas.small_font.render('• ' + line[2:], True, (0,0,0))
        elif '**' in line:
            bold_font = pygame.font.Font(None, 16, bold=True)
            surf = bold_font.render(line.replace('**', ''), True, (0,0,0))
        elif '*' in line:
            surf = canvas.small_font.render(line.replace('*', ''), True, (0,0,0))
        else:
            surf = canvas.small_font.render(line, True, (0,0,0))
        lines.append(surf)
    mouse = pygame.mouse.get_pos()
    height = sum(s.get_height() for s in lines) + len(lines) * 5
    tooltip_rect = pygame.Rect(mouse[0] + 10, mouse[1] + 10, 200, height)
    pygame.draw.rect(canvas.screen, (255,255,200), tooltip_rect)
    pygame.draw.rect(canvas.screen, (0,0,0), tooltip_rect, 1)
    y = tooltip_rect.y
    for surf in lines:
        canvas.screen.blit(surf, (tooltip_rect.x + 5, y))
        y += surf.get_height() + 5
