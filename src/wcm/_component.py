#!/usr/bin/env python3
"""Component Uploader."""

import argparse
import logging
import os
from contextlib import contextmanager
from pathlib import Path
from shutil import make_archive

import wings
from semver import parse_version_info
from yaml import load
import click

from wcm import _schema, _utils

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

log = logging.getLogger()


@contextmanager
def _cli(**kw):
    i = None
    try:
        log.debug("Initializing WINGS API Client")
        i = wings.init(**kw)
        yield i
    finally:
        if i:
            i.close()


def check_data_types(spec):
    _types = set()
    for _t in spec["inputs"]:
        if not _t["isParam"] and _t["type"] not in _types:
            dtype = _t["type"][6:]
            if dtype not in spec.get("data", {}):
                raise ValueError(f"data-type {dtype} not defined")

    for _t in spec["outputs"]:
        if not _t["isParam"] and _t["type"] not in _types:
            if dtype not in spec.get("data", {}):
                raise ValueError(f"data-type {dtype} not defined")


def create_data_types(spec, component_dir, cli, ignore_data):
    for dtype, _file in spec.get("data", {}).items():
        cli.data.new_data_type(dtype, None)
        if ignore_data:
            continue

        if _file:
            # Properties
            format = _file.get("format", None)
            metadata_properties = _file.get("metadataProperties", {})
            if metadata_properties or format:
                cli.data.add_type_properties(
                    dtype, properties=metadata_properties, format=format
                )

            # Files
            for f in _file.get("files", ()):
                cli.data.upload_data_for_type(
                    (component_dir / Path(f)).resolve(), dtype
                )


def check_if_component_exists(spec, profile, force, creds):
    with _cli(profile=profile, **creds) as wi:
        if spec["version"].isspace() or len(spec["version"]) <= 0:
            name = spec["name"]
        else:
            name = spec["name"] + "-" + spec["version"]

        comps = wi.component.get_component_description(name)
        if not comps is None and not force:
            click.echo("publishing this will override an existing component. Continue anyway? [y/n]")
            ans = input()
            if ans == "n" or ans == "no":
                log.info("Aborting publish")
                exit(0)


def deploy_component(component_dir, profile=None, creds={}, debug=False, dry_run=False, ignore_data=False, force=False):
    component_dir = Path(component_dir)
    if not component_dir.exists():
        raise ValueError("Component directory does not exist.")

    with _cli(profile=profile, **creds) as cli:
        try:
            spec = load((component_dir / "wings-component.yml").open(), Loader=Loader)
        except FileNotFoundError:
            spec = load((component_dir / "wings-component.yaml").open(), Loader=Loader)

        try:
            _schema.check_package_spec(spec)
        except ValueError as err:
            log.error(err)
            exit(1)

        check_if_component_exists(spec, profile, force, creds)

        name = spec["name"]
        version = spec["version"]

        # _id = f"{name}-v{version}" #removed this line because it would make errors if 'v' was in version name
        if version.isspace() or len(version) <= 0:
            log.warning("No version. Component will be uploaded with no version identifier")
            _id = name
        else:
            _id = name + "-" + version

        if ignore_data:
            log.info("Upload data and metadata skipped")

        wings_component = spec["wings"]
        log.debug("Check component's data-types")
        check_data_types(wings_component)
        log.debug("Create component's data-types")
        create_data_types(wings_component, component_dir, cli, ignore_data)

        log.debug("Create component's type")
        cli.component.new_component_type(wings_component["componentType"], None)

        log.debug("Create the component")
        cli.component.new_component(_id, wings_component["componentType"])

        log.debug("Create component's I/O, Documentation, etc.")
        cli.component.save_component(_id, wings_component)

        try:
            _c = make_archive("_c", "zip", component_dir / "src")
            log.debug("Upload component code")
            cli.component.upload_component(_c, _id)
            return cli.component.get_component_description(_id)
        finally:
            os.remove(_c)



def _main():
    parser = argparse.ArgumentParser(
        description="Run WINGS template based on simulation matrix."
    )
    parser.add_argument(
        "-w",
        "--wings-config",
        dest="wings_config",
        required=True,
        help="WINGS Configuration File",
    )
    parser.add_argument(
        "-d", "--debug", dest="debug", default=False, action="store_true", help="Debug"
    )
    parser.add_argument(
        "--dry-run", dest="dry_run", default=False, action="store_true", help="Dry run"
    )
    parser.add_argument("component_dir", help="Component Directory")
    args = parser.parse_args()

    if args.debug:
        os.environ["WINGS_DEBUG"] = "1"
    _utils.init_logger()

    deploy_component(**vars(args))


if __name__ == "__main__":
    try:
        _main()
        log.info("Done")
    except Exception as e:
        log.exception(e)
