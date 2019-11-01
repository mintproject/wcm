# -*- coding: utf-8 -*-
"""
wcm.

:license: Apache 2.0
"""


import logging
import os
import sys
from pathlib import Path

import click

import semver

import wcm
from wcm import _component, _utils, _download, _list, _makeyaml

__DEFAULT_WCM_CREDENTIALS_FILE__ = "~/.wcm/credentials"
__DEFAULT_MINT_API_CREDENTIALS_FILE__ = "~/.mint_api/credentials"


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
        try:
            with Path("wings-component.yml").open("w") as fh:
                fh.write(spec)
                click.secho(f"Success", fg="green")
        except FileNotFoundError:
            with Path("wings-component.yaml").open("w") as fh:
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


@cli.command(help="Configure MINT API credentials")
@click.option(
    "--profile",
    "-p",
    envvar="WCM_PROFILE",
    type=str,
    default="default",
    metavar="<profile-name>",
)
def configure_mint_api(profile="default"):
    api_username = click.prompt("MINT API Username")
    api_password = click.prompt("MINT API Password", hide_input=True)

    credentials_file = Path(
        os.getenv("MINT_API_CREDENTIALS_FILE", __DEFAULT_MINT_API_CREDENTIALS_FILE__)
    ).expanduser()
    os.makedirs(str(credentials_file.parent), exist_ok=True)

    credentials = configparser.ConfigParser()
    credentials.optionxform = str

    if credentials_file.exists():
        credentials.read(credentials_file)

    credentials[profile] = {
        "api_username": api_username,
        "api_password": api_password
    }

    with credentials_file.open("w") as fh:
        credentials_file.parent.chmod(0o700)
        credentials_file.chmod(0o600)
        credentials.write(fh)
        click.secho(f"Success", fg="green")


@cli.command(help="Deploy the package to the wcm.")
@click.option("--debug/--no-debug", "-d/-nd", default=False)
@click.option("--dry-run", "-n", is_flag=True)
@click.option("--ignore-data/--no-ignore-data", "-i/-ni", default=False)
@click.option("--overwrite", "-f", is_flag=True, help="Replace existing components")
@click.option("--upload-catalog", "-sc", is_flag=True, help="Upload component to software catalog")
@click.option(
    "--profile",
    "-p",
    envvar="WCM_PROFILE",
    type=str,
    default="default",
    metavar="<profile-name>",
)
@click.option(
    "--apiprofile",
    "-m",
    envvar="MINT_API_PROFILE",
    type=str,
    default="default",
    metavar="<profile-name>",
)
@click.argument(
    "component",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, exists=True),
    default=".",
)
def publish(component, profile="default", apiprofile="default", debug=False, dry_run=False, ignore_data=False, overwrite=False, upload_catalog=False):
    logging.info("Publishing component")
    if not upload_catalog:
        _component.deploy_component(
            component, profile=profile, debug=debug, dry_run=dry_run, ignore_data=ignore_data, overwrite=overwrite
        )
    else:
        logging.info(component)
        _component.upload_to_software_catalog(
            component, profile=profile, apiprofile=apiprofile, debug=debug, dry_run=dry_run, ignore_data=ignore_data, overwrite=overwrite, upload_catalog=upload_catalog
        )

    click.secho(f"Success", fg="green")


@cli.command(help="Download a component from wings server. Data stored in .yaml file and source code downloaded to "
                  "folder within same directory. file-path can be specified to download into a specific directory")
@click.option(
    "--profile",
    "-p",
    envvar="WCM_PROFILE",
    type=str,
    default="default",
    metavar="<profile-name>",
)
@click.option(
    "--path",
    "-p",
    type=str,
    default=None,
)
@click.option("--force", "-f", is_flag=True, help="Force Download, even if component already exists in local directory")
@click.argument("component_id", default=None, type=str)
def download(component_id, profile="default", path=None, force=False):
    logging.info("Downloading component")
    _download.download(component_id, profile=profile, download_path=path, overwrite=force)
    click.secho(f"Success", fg="green")


@cli.command(help="Lists all the components in the current wings instance")
@click.option(
    "--profile",
    "-p",
    envvar="WCM_PROFILE",
    type=str,
    default="default",
    metavar="<profile-name>",
)
def list(profile="default"):
    _list.list_components(profile=profile)
    click.secho(f"Done", fg="green")


@cli.command(help="Generates a blank YAML from the schema. Useful for creating a new component from scratch. Optional "
                  "parameter --file-path <path> to choose which directory the blank YAML should be created in")
@click.option(
    "--file-path",
    "-f",
    type=str,
    default=None,
)
def make_yaml(file_path=None):
    logging.info("Generating blank YAML")
    _makeyaml.make_yaml(download_path=file_path)
    click.secho(f"Done", fg="green")
