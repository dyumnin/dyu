"""
Configuration loading/saving for Infinity Canvas.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load/create XDG config."""
    xdg = os.environ.get('XDG_CONFIG_HOME', Path('~').expanduser() / '.config')
    config_dir = Path(xdg) / 'infinitycanvas'
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / 'settings.json'
    defaults = {
        'default_color': (0, 0, 0),
        'zoom_speed': 1.1,
        'hotkeys': {
            'rectangle': 'r', 'arrow': 'a', 'text': 't', 'circle': 'c',
            'edit': 'e', 'delete': 'DEL', 'group': 'g', 'save': 'ctrl+s',
            'undo': 'ctrl+z', 'quit': 'ESC'
        }
    }
    logging.debug(f"Loading config from: {config_path}")
    try:
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                logging.debug(f"Loaded config: {config}")
                return config
        else:
            logging.debug(f"Config file not found, creating with defaults: {defaults}")
            with open(config_path, 'w') as f:
                json.dump(defaults, f, indent=2)
            return defaults
    except json.JSONDecodeError as e:
        logging.debug(f"Error decoding config file: {e}, using defaults: {defaults}")
        with open(config_path, 'w') as f:
            json.dump(defaults, f, indent=2)
        return defaults
    except Exception as e:
        logging.debug(f"Error loading config: {e}, using defaults: {defaults}")
        return defaults

def save_config(canvas):
    """Save config updates."""
    xdg = os.environ.get('XDG_CONFIG_HOME', Path('~').expanduser() / '.config')
    config_dir = Path(xdg) / 'infinitycanvas'
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / 'settings.json'
    logging.debug(f"Saving config to: {config_path}")
    try:
        with open(config_path, 'w') as f:
            json.dump(canvas.config, f, indent=2)
    except Exception as e:
        logging.debug(f"Error saving config: {e}")
