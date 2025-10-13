"""
Input handling and editing logic for Infinity Canvas.
"""

from dyu.canvas.render import screen_to_world
import pygame
from pygame.locals import *
import logging
from typing import Optional, Tuple
from dyu.canvas.base_object import BaseObject
from dyu.canvas.shapes import SUBCLASS_MAP
import tkinter as tk


def get_object_at(canvas, pos: Tuple[int, int]) -> Optional[BaseObject]:
    world_pos = screen_to_world(canvas, pos)
    for obj in reversed(canvas.children):
        bbox = obj.get_bounding_box()
        if isinstance(obj, SUBCLASS_MAP["Arrow"]):  # Assuming Arrow class
            bbox.inflate_ip(10, 10)  # Pad for thin lines
        if bbox.collidepoint(world_pos):
            return obj
    return None


def edit_properties(canvas, obj: BaseObject):
    """Modal: Draw grid of inputs for props."""

    canvas.modal_active = True
    modal_surf = pygame.Surface((400, 300))
    modal_surf.fill((200, 200, 200))
    fields = [
        ("Label", lambda x: setattr(obj, "label", x), obj.label, canvas.font),
        (
            "Color R",
            lambda x: setattr(obj, "color", (int(x), obj.color[1], obj.color[2])),
            str(obj.color[0]),
            canvas.font,
        ),
        (
            "Color G",
            lambda x: setattr(obj, "color", (obj.color[0], int(x), obj.color[2])),
            str(obj.color[1]),
            canvas.font,
        ),
        (
            "Color B",
            lambda x: setattr(obj, "color", (obj.color[0], obj.color[1], int(x))),
            str(obj.color[2]),
            canvas.font,
        ),
        (
            "Description",
            lambda x: setattr(obj, "description", x),
            obj.description,
            canvas.small_font,
        ),
    ]
    active_field = 0
    input_text = fields[active_field][2]
    while canvas.modal_active:
        modal_surf.fill((200, 200, 200))
        y = 20
        for i, (label, _, val, font) in enumerate(fields):
            color = (255, 255, 0) if i == active_field else (0, 0, 0)
            modal_surf.blit(font.render(f"{label}: {val}", True, color), (20, y))
            y += font.get_height() + 10
        canvas.screen.blit(
            modal_surf,
            (
                canvas.screen.get_width() // 2 - 200,
                canvas.screen.get_height() // 2 - 150,
            ),
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                canvas.modal_active = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    try:
                        fields[active_field][1](input_text)
                    except ValueError:
                        logging.debug(
                            f"Invalid input for {fields[active_field][0]}: {input_text}"
                        )
                    active_field = (active_field + 1) % len(fields)
                    input_text = fields[active_field][2]
                elif event.key == K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isprintable():
                    input_text += event.unicode
                elif event.key == K_UP:
                    active_field = (active_field - 1) % len(fields)
                    input_text = fields[active_field][2]
                elif event.key == K_DOWN:
                    active_field = (active_field + 1) % len(fields)
                    input_text = fields[active_field][2]
            fields[active_field] = (
                fields[active_field][0],
                fields[active_field][1],
                input_text,
                fields[active_field][3],
            )
    canvas.modal_active = False


def handle_event(canvas, event):
    """Process input."""

    if canvas.modal_active:
        logging.debug("Modal active, skipping event")
        return True
    logging.debug(f"Handling event: type={event.type}, details={event}")
    if event.type == QUIT:
        logging.debug("Quit event received")
        return False
    if event.type == KEYDOWN:
        logging.debug(f"Key pressed: key={event.key}, unicode='{event.unicode}'")
        if event.key == K_F11:
            canvas.fullscreen = not canvas.fullscreen
            if canvas.fullscreen:
                # Store current size before going fullscreen
                canvas.window_size = canvas.screen.get_size()
                # Set to fullscreen with current desktop resolution
                canvas.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                # Restore the previous window size
                canvas.screen = pygame.display.set_mode(
                    canvas.window_size, pygame.RESIZABLE
                )
        if event.key == K_q:
            logging.debug("Exiting create mode and quitting")
            canvas.create_mode = None
            canvas.create_start = None
            return False
        if event.key == K_ESCAPE:
            logging.debug("Exiting create mode")
            canvas.create_mode = None
            canvas.create_start = None
        elif event.key == K_e and canvas.selected:
            logging.debug(
                f"Editing properties for {canvas.selected.__class__.__name__}"
            )
            edit_properties(canvas, canvas.selected)
        elif event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
            logging.debug("Save triggered")
            from tkinter import filedialog, Tk

            root = Tk()
            root.withdraw()
            path = filedialog.asksaveasfilename(
                defaultextension=f".{canvas.default_format}",
                filetypes=[
                    ("All", "*"),
                    ("JSON", "*.json"),
                    ("Pickle", "*.pkl"),
                    ("SVG", "*.svg"),
                ],
            )
            if path:
                canvas.save_to_file(path)
        elif event.key == K_r:  # Explicit check for 'r'
            canvas.create_mode = "Rectangle"
            canvas.create_start = None
            logging.debug("Entering create mode: Rectangle")
        elif event.key == K_a:  # Explicit check for 'a'
            canvas.create_mode = "Arrow"
            canvas.create_start = None
            logging.debug("Entering create mode: Arrow")

    elif event.type == MOUSEBUTTONDOWN:
        logging.debug(f"Mouse button down: button={event.button}, pos={event.pos}")
        if event.button == 1:  # Left click
            if canvas.create_mode:
                canvas.create_start = screen_to_world(canvas, event.pos)
                logging.debug(
                    f"Mouse down in create mode: {canvas.create_mode}, start={canvas.create_start}"
                )
            else:
                canvas.selected = get_object_at(canvas, event.pos)
                logging.debug(
                    f"Selected object: {canvas.selected.__class__.__name__ if canvas.selected else None}"
                )
        elif event.button == 2:  # Middle click
            canvas.pan_start = event.pos
            logging.debug(f"Starting pan at {canvas.pan_start}")
        elif event.button == 4:  # Wheel up
            canvas.zoom *= canvas.config["zoom_speed"]
            logging.debug(f"Zoom in: {canvas.zoom}")
        elif event.button == 5:  # Wheel down
            canvas.zoom /= canvas.config["zoom_speed"]
            logging.debug(f"Zoom out: {canvas.zoom}")
    elif event.type == MOUSEBUTTONUP:
        logging.debug(f"Mouse button up: button={event.button}, pos={event.pos}")
        if event.button == 1 and canvas.create_mode and canvas.create_start:
            end_pos = screen_to_world(canvas, event.pos)
            logging.debug(
                f"Mouse up: creating {canvas.create_mode}, start={canvas.create_start}, end={end_pos}"
            )
            try:
                new_obj = SUBCLASS_MAP[canvas.create_mode](
                    start=canvas.create_start,
                    end=end_pos,
                    color=canvas.config["default_color"],
                    fill_color=(255, 255, 255)
                    if canvas.create_mode != "Arrow"
                    else None,
                    label="New" if canvas.create_mode == "Text" else "",
                )
                canvas.children.append(new_obj)
                canvas.selected = new_obj
                logging.debug(
                    f"Created object: {new_obj.__class__.__name__}, children count={len(canvas.children)}"
                )
            except Exception as e:
                logging.error(f"Failed to create object: {e}")
            # canvas.create_mode = None
            canvas.create_start = None
    elif event.type == MOUSEMOTION:
        canvas.hovered = get_object_at(canvas, event.pos)
        if pygame.mouse.get_pressed()[1]:
            if hasattr(canvas, "pan_start"):
                delta = (
                    event.pos[0] - canvas.pan_start[0],
                    event.pos[1] - canvas.pan_start[1],
                )
                canvas.pan = (canvas.pan[0] + delta[0], canvas.pan[1] + delta[1])
                canvas.pan_start = event.pos
                logging.debug(f"Panning: delta={delta}, new pan={canvas.pan}")
        if canvas.create_mode and canvas.create_start:
            logging.debug("Mouse motion in create mode, triggering draw")
            canvas.draw()
    return True
