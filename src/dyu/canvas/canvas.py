"""
Infinity Canvas: Main app logic.

Coordinates submodules for config, rendering, input, shapes, and I/O.

Usage:
    from dyu.canvas import Canvas
    c = Canvas()
    c.run()  # Starts Pygame loop
"""
import pygame
from pygame.locals import *
import logging
import os
from typing import Optional, List, Tuple
from dyu.canvas.base_object import BaseObject
from dyu.canvas.config import load_config, save_config
from dyu.canvas.render import draw, screen_to_world, world_to_screen, draw_tooltip
from dyu.canvas.input import handle_event
from dyu.canvas.io import save, load, export_svg
from dyu.canvas.shapes import SUBCLASS_MAP

# Ensure log file is writable
log_file = 'infinitycanvas.log'
try:
    with open(log_file, 'w') as f:
        f.write("")
    os.chmod(log_file, 0o666)
except Exception as e:
    print(f"Failed to initialize log file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)
logging.debug("Logging initialized in canvas.py")
print("Logging initialized in canvas.py")  # Debug print

class Canvas:
    """
    Manages top-level objects, rendering, input.

    zoom: float = 1.0
    pan: (x,y) offset
    selected: Optional[BaseObject]
    """
    def __init__(self, filename: Optional[str] = None, default_format: str = 'json'):
        logging.debug("Initializing Canvas")
        print("Initializing Canvas")
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800),pygame.RESIZABLE)
        pygame.display.set_caption("Infinity Canvas")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        self.fullscreen = False
        self.window_size = (1200,800)
        self.zoom = 1.0
        self.pan = (0, 0)
        self.children: List[BaseObject] = []
        self.selected: Optional[BaseObject] = None
        self.hovered: Optional[BaseObject] = None
        self.modal_active = False
        self.default_format = default_format
        self.config = load_config()
        self.hotkeys = self.config.get('hotkeys', {
            'rectangle': 'r', 'arrow': 'a', 'text': 't', 'circle': 'c',
            'edit': 'e', 'delete': 'DEL', 'group': 'g', 'save': 'ctrl+s',
            'undo': 'ctrl+z', 'quit': 'ESC'
        })
        self.create_mode: Optional[str] = None
        self.create_start: Optional[Tuple[float, float]] = None
        # Add test rectangle
        if 'Rectangle' in SUBCLASS_MAP:
            test_rect = SUBCLASS_MAP['Rectangle'](
                start=(100, 100),
                end=(300, 200),
                color=(0, 0, 0),
                fill_color=(255, 255, 255),
                label="Test Rectangle"
            )
            self.children.append(test_rect)
            logging.debug("Added test rectangle to children")
            print("Added test rectangle")
        logging.debug(f"SUBCLASS_MAP: {list(SUBCLASS_MAP.keys())}")
        if filename:
            self.load_from_file(filename)
        logging.debug(f"Initialized Canvas with {len(self.children)} objects: {[obj.__class__.__name__ for obj in self.children]}")

    def draw(self):
        logging.debug(f"Calling draw with {len(self.children)} children")
        draw(self)

    def draw_tooltip(self, md_text: str):
        draw_tooltip(self, md_text)

    def screen_to_world(self, pos):
        return screen_to_world(self, pos)

    def world_to_screen(self, pos):
        return world_to_screen(self, pos)

    def handle_event(self, event):
        return handle_event(self, event)

    def save_to_file(self, path: str):
        logging.debug(f"Calling save_to_file: {path}")
        save(self, path)

    def load_from_file(self, path: str):
        logging.debug(f"Calling load_from_file: {path}")
        load(self, path)

    def export_svg(self) -> str:
        return export_svg(self)

    def save_config(self):
        save_config(self)

    def run(self):
        """Main loop."""
        import platform
        import asyncio
        logging.debug("Starting main loop")
        print("Starting main loop")
        async def main():
            running = True
            while running:
                for event in pygame.event.get():
                    logging.debug(f"Processing event: {event}")
                    print(f"Processing event: {event}")
                    running = self.handle_event(event)
                self.draw()
                self.clock.tick(60)
                await asyncio.sleep(1.0 / 60)
            pygame.quit()

        if platform.system() == "Emscripten":
            asyncio.ensure_future(main())
        else:
            asyncio.run(main())

def run_canvas(filename: Optional[str] = None, default_format: str = 'json'):
    """CLI entry: Init and run."""
    print("Starting run_canvas")
    logging.debug(f"Running canvas with filename={filename}, default_format={default_format}")
    app = Canvas(filename, default_format)
    app.run()
