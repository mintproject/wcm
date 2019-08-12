import argparse
import concurrent.futures
import configparser
import yaml
import yamlordereddictloader
import logging
import time
import json
import wings
import os
import zipfile
import shutil
import sys

'''
logging
'''
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def download(component_dir, profile=None, download_path=None):
    comp_id = component_dir

    # sets path, this determines where the component will be downloaded. Default is the current directory of the program
    if download_path is None:
        path = os.getcwd()
    else:
        path = download_path

    wings_instance = wings.init()
    component = wings_instance.component.get_component_description(comp_id)

    if component is None:
        logger.error("Invalid ID: \"" + comp_id + "\"")
        exit(1)

    # Make new folder to put everything in
    path = os.path.join(path, comp_id)
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
    info = info.split("-")  # splits it by the - (ie {"HAND","1"})

    # First part becomes name, other becomes version
    yaml_data["name"] = info[0]
    yaml_data["version"] = info[1] + ".0.0"

    component.pop("location")
    component.pop("id")
    component.pop("type")
    component["documentation"] = component["documentation"].strip()
    component["files"] = ["src\\*"]

    # loops through every input field
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
    except:
        logger.error("something went wrong downloading the code from zip file")
        logger.error(sys.exc_info())

    # copy files into src folder
    comp_files = os.listdir(os.path.join(comp_os_path, comp_id))
    for files in comp_files:
        full_file_name = os.path.join(os.path.join(comp_os_path, comp_id), files)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, os.path.join(path, "src"))

    # remove component folder
    shutil.rmtree(comp_os_path)

    logger.info("Download complete")
