"""Command Line Interface."""

#import pkg_resources
import subprocess
import copier
import typer
import os
import yaml
from xdg_base_dirs import xdg_config_home
from .beancounter import app as bean

app = typer.Typer()
app.add_typer(bean,name="bean")


@app.command()
def run() -> None:
    """Run command."""
    print("Hello World")


@app.command()
def venv() -> None:
    """Creates a virtual env file."""
    subprocess.run(["python3", "-m", "venv", "venv"])


@app.command()
def ip(name: str, org: str = "dyu.yaml") -> None:
    """Creates an IP folder layout."""
    data=read_config(org)
    print(f"DATA={data}")
    copier.run_copy("gh:dyu-copier/hdl_unit", name, data=data)


@app.command()
def cocotbext(name: str, org: str = "dyu.yaml") -> None:
    """Creates an cocotbext plugin folder layout."""
    copier.run_copy("gh:dyu-copier/cocotbext", name, data=read_config())


@app.command()
def peakrdl(name: str, org: str = "dyu.yaml") -> None:
    """Creates an peakrdl plugin folder layout."""
    copier.run_copy("gh:dyu-copier/peakrdl", name, data=read_config())


@app.command()
def plan(configfile: str, org: str = "dyu.yaml") -> None:
    """
    Creates a plan using taskJuggler
    """
    # template = pkg_resources.resource_filename("dyu", "template/plan.tji")
    raise NotImplementedError("This feature is not implemented")


def read_config(file="config.yml"):
    """
    Reads config file at ~/.config/dyu/config.yml and returns the value
    """
    cfg_path = os.path.join(xdg_config_home(), "dyu")
    cfg_file = os.path.join(cfg_path, file)
    if not os.path.exists(cfg_path):
        os.mkdir(cfg_path)
    if not os.path.exists(cfg_file):
        with open(cfg_file, "w") as cfg:
            print(
                "This is a one time setup of your configuration data for all projects"
            )
            name = typer.prompt("Your Name")
            org = typer.prompt("Your Org")
            email = typer.prompt("Your Email ID")
            yaml.dump({"author": name, "org": org, "email": email}, cfg)
    with open(cfg_file, "r") as cfg:
        data = yaml.safe_load(cfg)
    print(data)
    return data


@app.callback(no_args_is_help=True)
def main() -> None:
    """CLI for Dyumnin supertool."""


typer_click_object = typer.main.get_command(app)
