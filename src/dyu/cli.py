"""Command Line Interface."""

import subprocess

import copier
import typer

app = typer.Typer()


@app.command()
def run() -> None:
    """Run command."""
    print("Hello World")


@app.command()
def venv() -> None:
    """Creates a virtual env file."""
    subprocess.run(["python3", "-m", "venv", "venv"])


@app.command()
def ip(name: str) -> None:
    """Creates an IP folder layout."""
    copier.run_copy("gh:dyu-copier/hdl_unit", name)


@app.command()
def cocotbext(name: str) -> None:
    """Creates an cocotbext plugin folder layout."""
    copier.run_copy("gh:dyu-copier/cocotbext", name)


@app.command()
def peakrdl(name: str) -> None:
    """Creates an peakrdl plugin folder layout."""
    copier.run_copy("gh:dyu-copier/cocotbext", name)


# NOTE(huxuan): callback is required for single command as a subcommand in typer.
# And it is a convenient way to document the cli here.
# Reference: https://typer.tiangolo.com/tutorial/commands/one-or-multiple/#one-command-and-one-callback
@app.callback(no_args_is_help=True)
def main() -> None:
    """CLI for Dyumnin supertool."""


# NOTE(huxuan): click object is used for document generation.
# Reference: https://github.com/tiangolo/typer/issues/200#issuecomment-796485787
typer_click_object = typer.main.get_command(app)
