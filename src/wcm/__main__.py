# -*- coding: utf-8 -*-
"""
wcm.

:license: Apache 2.0
"""

import configparser
import logging
import os
import sys
from pathlib import Path

import click

import semver

import wcm
from wcm import _component, _utils

__DEFAULT_WCM_CREDENTIALS_FILE__ = "~/.wcm/credentials"


@click.group()
@click.option("--verbose", "-v", default=0, count=True)
def cli(verbose):
    _utils.init_logger()
    lv = ".".join(_utils.get_latest_version().split(".")[:3])
    cv = ".".join(wcm.__version__.split(".")[:3])

    if semver.compare(lv, cv) > 0:
        click.secho(
            f"""WARNING: You are using wcm version {wcm.__version__}, however version {lv} is available.
You should consider upgrading via the 'pip install --upgrade wcm' command.""",
            fg="yellow",
        )


@cli.command(help="Show wcm version.")
def version(debug=False):
    click.echo(f"{Path(sys.argv[0]).name} v{wcm.__version__}")


@cli.command(help="Initialize a directory for a new component.")
@click.option("--yes", "-y", is_flag=True)
@click.argument(
    "component",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, exists=True),
    default=".",
)
def init(component, yes=False):
    component_name = Path(".").resolve().name
    version = "0.0.0"
    description = ""
    author = ""
    license = "Apache"

    if not yes:
        component_name = click.prompt("Component Name", default=component_name)
        version = click.prompt("Version", default=version)
        description = click.prompt("Description", default=description)
        author = click.prompt("Author", default=author)
        license = click.prompt("License", default=license)
    spec = f"""name: {component_name}
version: {version}
description: {description}
author: {author}
license: {license}
"""

    click.echo(spec)
    if yes or click.confirm("Do you want to continue?"):
        with Path("wings-component.yml").open("w") as fh:
            fh.write(spec)
            click.secho(f"Success", fg="green")
    else:
        click.secho(f"Aborted!", fg="red")


@cli.command(help="Configure credentials")
@click.option(
    "--profile",
    "-p",
    envvar="WCM_PROFILE",
    type=str,
    default="default",
    metavar="<profile-name>",
)
def configure(profile="default"):
    server_wings = click.prompt("WINGS Server URL")
    export_wings_url = click.prompt("WINGS Export URL")
    user_wings = click.prompt("WINGS User")
    password_wings = click.prompt("WINGS Password", hide_input=True)
    domain_wings = click.prompt("WINGS Domain")

    credentials_file = Path(
        os.getenv("WCM_CREDENTIALS_FILE", __DEFAULT_WCM_CREDENTIALS_FILE__)
    ).expanduser()
    os.makedirs(str(credentials_file.parent), exist_ok=True)

    credentials = configparser.ConfigParser()
    credentials.optionxform = str

    if credentials_file.exists():
        credentials.read(credentials_file)

    credentials[profile] = {
        "serverWings": server_wings,
        "exportWingsURL": export_wings_url,
        "userWings": user_wings,
        "passwordWings": password_wings,
        "domainWings": domain_wings,
    }

    with credentials_file.open("w") as fh:
        credentials_file.parent.chmod(0o700)
        credentials_file.chmod(0o600)
        credentials.write(fh)
        click.secho(f"Success", fg="green")


@cli.command(help="Deploy the pacakge to the wcm.")
@click.option("--debug/--no-debug", "-d/-nd", default=False)
@click.option("--dry-run", "-n", is_flag=True)
@click.option(
    "--profile",
    "-p",
    envvar="WCM_PROFILE",
    type=str,
    default="default",
    metavar="<profile-name>",
)
@click.argument(
    "component",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, exists=True),
    default=".",
)
def publish(component, profile="default", debug=False, dry_run=False):
    logging.info("Publishing component")
    _component.deploy_component(
        component, profile=profile, debug=debug, dry_run=dry_run
    )
    click.secho(f"Success", fg="green")
