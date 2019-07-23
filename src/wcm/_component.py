#!/usr/bin/env python3
"""Component Uploader."""

import argparse
import logging
import os
from pathlib import Path
from shutil import make_archive

from semver import parse_version_info
from yaml import load

from wcm import _utils, _schema

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

log = logging.getLogger()


def check_data_types(spec, data):
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


def create_data_types(spec, component_dir, data):
    for dtype, _file in spec.get("data", {}).items():
        data.new_data_type(dtype, None)
        # Properties
        format = _file.get("format", None)
        metadata_properties = _file.get("metadataProperties", {})
        if metadata_properties or format:
            data.add_type_properties(
                dtype, properties=metadata_properties, format=format
            )

        # Files
        for f in _file.get("files", ()):
            data.upload_data_for_type((component_dir / Path(f)).resolve(), dtype)


def deploy_component(component_dir, wings_config, debug=False, dry_run=False):
    component_dir = Path(component_dir)
    if not component_dir.exists():
        raise ValueError("Component directory does not exist.")

    with _utils.component_cli(wings_config) as (component, data):
        spec = load((component_dir / "wings-component.yml").open(), Loader=Loader)
        _schema.check_package_spec(spec)

        name = spec["name"]
        version = parse_version_info(spec["version"])
        _id = f"{name}-{version.major}"
        wings_component = spec["wings"]

        check_data_types(wings_component, data)
        create_data_types(wings_component, component_dir, data)
        component.new_component_type(wings_component["componentType"], None)
        component.new_component(_id, wings_component["componentType"])
        component.save_component(_id, wings_component)
        try:
            _c = make_archive("_c", "zip", component_dir / "src")
            component.upload_component(_c, _id)
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
