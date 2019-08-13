import argparse
import concurrent.futures
import configparser
from contextlib import contextmanager
import yaml
import yamlordereddictloader
import logging
import json
import wings
import click
import os
import zipfile
import shutil
from wcm import _schema, _utils

logger = logging.getLogger()


@contextmanager
def _cli(**kw):
    i = None
    try:
        logger.debug("Initializing WINGS API Client")
        i = wings.init(**kw)
        yield i
    finally:
        if i:
            i.close()


def download(component_dir, profile=None, download_path=None):

    comp_id = component_dir

    # sets path, this determines where the component will be downloaded. Default is the current directory of the program
    if download_path is None:
        path = os.getcwd()
    else:
        path = download_path

    with _cli(profile=profile) as wings_instance:
        component = wings_instance.component.get_component_description(comp_id)

        if component is None:
            logger.error("Invalid ID: \"" + comp_id + "\"")
            exit(1)

        # Make new folder to put everything in
        path = os.path.join(path, comp_id)

        if os.path.exists(path):
            click.echo("\"" + path + "\" already exists. Do you want to overwrite it? [y/n]")
            ans = input()
            if ans == 'y' or ans == "yes":
                shutil.rmtree(path)
            else:
                logger.info("Aborting Download")
                exit(0)

        os.mkdir(path)

        wings_instance.component.download_component(comp_id, os.path.join(path, "components"))

        yaml_data = {}
        data_types = {}

        yaml_data["name"] = ""
        yaml_data["version"] = ""
        # yaml_data["#description"] = None
        # yaml_data["#keywords"] = None
        # yaml_data["homepage"] = None
        # amlData["license"] = None
        # yaml_data["author"] = None
        # yaml_data["container"] = None
        # yaml_data["repository"] = None

        yaml_data["wings"] = component
        component = yaml_data["wings"]

        # takes the id and splits it by the '#' sign
        # (id example: http://localhost:8080/export/users/mint/api-test/components/library.owl#HAND-1)
        info = component["id"].split("#")
        info = info[len(info) - 1]  # gets the last index of the split (ie: HAND-1)
        info = info.split("-")  # splits it by the '-' (ie {"HAND","1"})

        # First part becomes name, other becomes version
        yaml_data["name"] = info[0]
        if len(info) > 1:
            yaml_data["version"] = info[-1]
        else:
            logger.warning("No version could be ascertained from the name")

        try:
            component.pop("location")
            component.pop("id")
            component.pop("type")
            component["documentation"] = component["documentation"].strip()
            component["files"] = ["src\\*"]
        except KeyError:
            logger.warning("Component seems to be missing metadata")

        # loops through every input field
        if len(component["inputs"]) <= 0:
            logger.warning("Component has no inputs")
        for i in (component["inputs"]):
            files = {}
            i.pop("id")
            try:
                if "XMLSchema" not in (i["type"]):
                    type_name = i["type"].split("#")
                    type_name = type_name[len(type_name) - 1]

                    i["type"] = "dcdom:" + type_name

                    files["files"] = ["data/placeholder.tif"]
                    data_types[type_name] = files
            except:
                logger.warning("no type in " + str(i))

        component["data"] = data_types

        if len(component["outputs"]) <= 0:
            logger.warning("Component has no outputs")
        for o in (component["outputs"]):
            files = {}
            o.pop("id")
            try:
                if "XMLSchema" not in o["type"]:
                    type_name = o["type"].split("#")
                    type_name = type_name[len(type_name) - 1]

                    o["type"] = "dcdom:" + type_name

                    files["files"] = ["data/placeholder.tif"]
                    data_types[type_name] = files
            except:
                logger.warning("no type in " + str(o))

        # makes the YAML file
        stream = open(os.path.join(path, "wings-component.yaml"), 'w+')
        yaml.dump(yaml_data, stream, sort_keys=False)

        logger.info("Generated YAML")

        # makes the src folder in the directory
        try:
            os.mkdir(os.path.join(path, "src"))
        except FileExistsError:
            logger.warning("src folder already exists")

        data_path = os.path.join(path, "data")

        try:
            os.mkdir(data_path)
        except:
            logger.warning("data folder already exists")

        open(os.path.join(data_path, "placeholder.tif"), 'w+')

        # unzip components
        comp_os_path = ""
        try:
            comp_os_path = os.path.join(path, "components")
            zip_path = os.path.join(comp_os_path, comp_id + ".zip")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(comp_os_path)
        except zipfile.BadZipFile:
            logger.error("Downloaded zip file seems to be corrupt")
            exit(1)

        # copy files into src folder
        comp_files = os.listdir(os.path.join(comp_os_path, comp_id))
        for files in comp_files:
            full_file_name = os.path.join(os.path.join(comp_os_path, comp_id), files)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, os.path.join(path, "src"))

        # remove component folder
        shutil.rmtree(comp_os_path)

        logger.info("Download complete")


def _main():
    parser = argparse.ArgumentParser(
        description="Download wings components given the component id."
    )
    parser.add_argument(
        "--file-path",
        "-f",
        type=str,
        default=None,
    )
    parser.add_argument("-c", "--component", required=True, help="Component name to download")
    parser.add_argument(
        "-d", "--debug", dest="debug", default=False, action="store_true", help="Debug"
    )
    parser.add_argument(
        "--dry-run", dest="dry_run", default=False, action="store_true", help="Dry run"
    )
    args = parser.parse_args()

    if args.debug:
        os.environ["WINGS_DEBUG"] = "1"
    _utils.init_logger()
    component_dir = args.component
    file_path = args.file_path
    download(component_dir, file_path)


if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        logger.exception(e)
