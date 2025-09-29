"""
CLI entry point for Infinity Canvas.
"""
import typer
from typing import Optional
from .canvas import run_canvas

app = typer.Typer()

@app.command()
def canvas(filename: Optional[str] = None, default_format: str = "json"):
    """Run the Infinity Canvas app."""
    run_canvas(filename, default_format)

if __name__ == "__main__":
    app()
