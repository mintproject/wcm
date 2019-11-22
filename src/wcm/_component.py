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

import configparser
import modelcatalog
from modelcatalog.rest import ApiException
from pprint import pprint
import json
import ast


from wcm import _schema, _utils
import requests

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

log = logging.getLogger()
__DEFAULT_MINT_API_CREDENTIALS_FILE__ = "~/.mint_api/credentials"

PREFIX_URI = "https://w3id.org/okn/i/mint/"
WINGS_EXPORT_URI = "https://w3id.org/wings/export/"

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
                log.warning(f"input data-type \"{dtype}\" not defined")

    for _t in spec["outputs"]:
        if not _t["isParam"] and _t["type"] not in _types:
            if dtype not in spec.get("data", {}):
                log.warning(f"output data-type \"{dtype}\" not defined")


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


def component_exists(spec, profile, overwrite, credentials):
    """
    :param spec: Component specification
    :type spec: dict
    :param profile: If we are using the cli, User profile with credentials required
    :type profile: dict
    :param overwrite: Overwrite component
    :type overwrite: bool
    :param credentials: If we are using the API, Credentials required
    :type credentials: dict
    :return: Boolean
    :rtype: bool
    """
    with _cli(profile=profile, **credentials) as wi:
        if spec["version"].isspace() or len(spec["version"]) <= 0:
            name = spec["name"]
        else:
            name = spec["name"] + "-" + spec["version"]

        comps = wi.component.get_component_description(name)
        if comps is not None:
            log.info("Component already exists on server")
            if not overwrite:
                log.error("Publishing this component would overwrite the existing one. To force upload use flag -f")
            return True
        return False


def deploy_component(component_dir, profile=None, creds={}, debug=False, dry_run=False, ignore_data=False, overwrite=None):
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

        name = spec["name"]
        version = spec["version"]

        # _id = f"{name}-v{version}" #removed this line because it would make errors if 'v' was in version name
        if version.isspace() or len(version) <= 0:
            log.warning("No version. Component will be uploaded with no version identifier")
            _id = name
        else:
            _id = name + "-" + version

        if component_exists(spec, profile, overwrite, creds):
            if overwrite:
                log.info("Replacing the component")
            else:
                log.info("Skipping publish")
                return cli.component.get_component_description(_id)
        else:
            log.info("Component does not exist, deploying the component")

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


def make_request(request_uri, data, request_type, access_token):
    if request_type == "POST":
        headers = {"content-type": "application/json", "Authorization": "Bearer " + access_token}
        response = requests.post(request_uri, headers = headers, data = json.dumps(data))
        return response

def upload_to_software_catalog(component_dir, profile=None, apiprofile=None, creds={}, debug=False, dry_run=False, ignore_data=False, overwrite=None, upload_catalog=True):
    component_dir = Path(component_dir)
    if not component_dir.exists():
        raise ValueError("Component directory does not exist.")
    
    logging.info(apiprofile)
    credentials_file = Path(
        os.getenv("WCM_CREDENTIALS_FILE", __DEFAULT_MINT_API_CREDENTIALS_FILE__)
    ).expanduser()
    
    credentials = configparser.ConfigParser()
    credentials.optionxform = str

    if credentials_file.exists():
        credentials.read(credentials_file)
    
    username = credentials[apiprofile]["api_username"]
    password = credentials[apiprofile]["api_password"]

    # Loading the WINGS YAML File data into model_data dict
    model_data = {}
    try:
        spec = load((component_dir / "wings-component.yml").open(), Loader=Loader)
    except FileNotFoundError:
        spec = load((component_dir / "wings-component.yaml").open(), Loader=Loader)
    
    try:
        _schema.check_package_spec(spec)
    except ValueError as err:
        log.error(err)
        exit(1)
    
    model_data = spec

    """
    # Loading the METADATA YAML file data into metadata dict
    metadata = {}
    try:
        spec = load((component_dir / "metadata.yml").open(), Loader=Loader)
    except FileNotFoundError:
        spec = load((component_dir / "metadata.yaml").open(), Loader=Loader)
    
    try:
        _schema.check_package_spec(spec)
    except ValueError as err:
        log.error(err)
        exit(1)
    
    metadata = spec
    """

    input_param = []
    output_param = []
    param = []
    for element in model_data['wings']['inputs']:
        if not element['isParam']:
            element.pop('isParam')
            #element.pop('type')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')
            if 'prefix' in element.keys():
                element['position'] = element.pop('prefix')
            if 'type' in element.keys():
                element['type'] = element.pop('type')
            
            # Ask from where do we get the metadata for the variable presentation
            if "has_presentation" in element.keys():
                element['hasPresentation'] = element.pop('has_presentation')
            
            input_param.append(element)
        else:
            element.pop('isParam')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'paramDefaultValue' in element.keys():
                element['hasDefaultValue'] = str(element.pop('paramDefaultValue'))
            if 'type' in element.keys():
                element['type'] = element.pop('type')
            if "has_presentation" in element.keys():
                element['hasPresentation'] = element.pop('has_presentation')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')

            param.append(element)
    
    for element in model_data['wings']['outputs']:
        if not element['isParam']:
            element.pop('isParam')
            #element.pop('type')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')
            if 'prefix' in element.keys():
                element['position'] = element.pop('prefix')
            if 'type' in element.keys():
                element['type'] = element.pop('type')
            
            # Ask from where do we get the metadata for the variable presentation
            if "has_presentation" in element.keys():
                element['hasPresentation'] = element.pop('has_presentation')
            output_param.append(element)
        else:
            element.pop('isParam')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'paramDefaultValue' in element.keys():
                element['hasDefaultValue'] = str(element.pop('paramDefaultValue'))
            if 'type' in element.keys():
                element['type'] = element.pop('type')
            if "has_presentation" in element.keys():
                element['hasPresentation'] = element.pop('has_presentation')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')
            param.append(element)
    configuration = modelcatalog.Configuration()
    user_api_instance = modelcatalog.DefaultApi()

    # Login the user into the API to get the access token
    if username and password:
        try:
            api_response = user_api_instance.user_login_get(username, password)
            data = json.dumps(ast.literal_eval(api_response))
            access_token = json.loads(data)["access_token"]
            configuration.access_token = access_token
        except ApiException as e:
            print("Exception when calling DefaultApi->user_login_get: %s\n" % e)
    else:
        log.error("There is some issue while getting the username and password")
        exit(1)

    # Create an instance of DatasetSpecificationApi to register the input and output parameters
    # Add input parameter to DatasetSpecification API
    input_param_uri = []
    for each in input_param:
        logging.info(each)

        dataset_specification = {}

        if "hasDimensionality" in each:
            dataset_specification["hasDimensionality"] = [each["hasDimensionality"]]
        
        if "id" in each:
            dataset_specification["id"] = each["id"]

        if "hasFormat" in each:
            dataset_specification["hasFormat"] = [each["hasFormat"]]
        
        if "hasFileStructure" in each:
            dataset_specification["hasFileStructure"] = each["hasFileStructure"]

        if "description" in each:
            dataset_specification["descripition"] = [each["description"]]

        # What does position map to in wings yaml file
        """
        if "position" in each:
            dataset_specification["position"] = [each["position"]]
        """

        if "type" in each:
            dataset_specification["type"] = [each["type"]]
        
        if "hasFixedResource" in each:
            dataset_specification["hasFixedResource"] = each["hasFixedResource"]

        if "hasPresentation" in each:
            
            # Handle the Internal References for hasPresentation like hasStandardVariable and partOfDataset (Doubt regarding how to handle partOfDataset)

            if "hasStandardVariable" in each["hasPresentation"]:
                response = make_request('https://api.models.mint.isi.edu/v1.1.0/standardvariables?user=' + username, each["hasPresentation"]["hasStandardVariable"], "POST", configuration.access_token)
                if response.status_code == 201 or response.status_code == 200:
                    print(response.json())
                    response_data = response.json()
                    each["hasPresentation"]["hasStandardVariable"] = response_data
                else:
                    print("Error creating standard variables for " + dataset_specification["id"])
                    print(response.status_code)
                    exit(1)
            
            response = make_request('https://api.models.mint.isi.edu/v1.1.0/variablepresentations?user=' + username, each["hasPresentation"], "POST", configuration.access_token)
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                dataset_specification["hasPresentation"] = response_data
            else:
                print("Error creating variable presentation for " + dataset_specification["id"])
                print(response.status_code)
                exit(1)
        
        #print(dataset_specification)
        response = make_request('https://api.models.mint.isi.edu/v1.1.0/datasetspecifications?user=' + username, dataset_specification, "POST", configuration.access_token)
        if response.status_code == 201 or response.status_code == 200:
            #print("Created an input parameter " + dataset_specification["id"])
            print(response.json())
            response_data = response.json()
            unique_id = PREFIX_URI + response_data["id"]
            tp = response_data["type"]
            input_param_uri.append({"id": unique_id, "type": [ WINGS_EXPORT_URI +  tp[0], tp[1]]})
        else:
            print("Error creating an input paramater " + dataset_specification["id"])
            print(response.status_code)
            exit(1)

    print(input_param_uri, len(input_param_uri))
    # Add output parameter to DatasetSpecification API
    output_param_uri = []
    for each in output_param:

        dataset_specification = {}

        if "hasDimensionality" in each:
            dataset_specification["hasDimensionality"] = [each["hasDimensionality"]]
        
        if "id" in each:
            dataset_specification["id"] = each["id"]

        if "hasFormat" in each:
            dataset_specification["hasFormat"] = [each["hasFormat"]]
        
        if "hasFileStructure" in each:
            dataset_specification["hasFileStructure"] = each["hasFileStructure"]

        if "description" in each:
            dataset_specification["descripition"] = [each["description"]]

        # What does position map to in wings yaml file
        """
        if "position" in each:
            dataset_specification["position"] = [each["position"]]
        """

        if "type" in each:
            dataset_specification["type"] = [each["type"]]
        
        if "hasFixedResource" in each:
            dataset_specification["hasFixedResource"] = each["hasFixedResource"]

        if "hasPresentation" in each:
            
            # Handle the Internal References for hasPresentation like hasStandardVariable and partOfDataset (Doubt regarding how to handle partOfDataset)

            if "hasStandardVariable" in each["hasPresentation"]:
                response = make_request('https://api.models.mint.isi.edu/v1.1.0/standardvariables?user=' + username, each["hasPresentation"]["hasStandardVariable"], "POST", configuration.access_token)
                if response.status_code == 201 or response.status_code == 200:
                    print(response.json())
                    response_data = response.json()
                    each["hasPresentation"]["hasStandardVariable"] = response_data
                else:
                    print("Error creating standard variables for " + dataset_specification["id"])
                    print(response.status_code)
                    exit(1)
            
            response = make_request('https://api.models.mint.isi.edu/v1.1.0/variablepresentations?user=' + username, each["hasPresentation"], "POST", configuration.access_token)
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                dataset_specification["hasPresentation"] = response_data
            else:
                print("Error creating variable presentation for " + dataset_specification["id"])
                print(response.status_code)
                exit(1)
        
        response = make_request('https://api.models.mint.isi.edu/v1.1.0/datasetspecifications?user=' + username, dataset_specification, "POST", configuration.access_token)
        if response.status_code == 201 or response.status_code == 200:
            #print("Created an output parameter " + dataset_specification["id"])
            print(response.json())
            response_data = response.json()
            unique_id = PREFIX_URI + response_data["id"]
            tp = response_data["type"]
            output_param_uri.append({"id": unique_id, "type": [ WINGS_EXPORT_URI +  tp[0], tp[1]]})
        else:
            print("Error creating an output paramater " + dataset_specification["id"])
            print(response.status_code)
            exit(1)

    print(output_param_uri, len(output_param_uri))

    # Registering the Parameters through the ParameterAPI
    parameter_uri = []
    for each in param:
        parameter = {}
    
        if "has_default_value" in each:
            parameter["hasDefaultValue"] = [each["hasDefaultValue"]]
        
        """
        if "has_maximum_accepted_value" in each:
            parameter["hasMaximumAcceptedValue"] = [each["hasMaximumAcceptedValue"]]
        
        if "description" in each:
            parameter["description"] = [each["description"]]

        if "has_data_type" in each:
            parameter["hasDataType"] = [each["hasDataType"]]

        if "has_fixed_value" in each:
            parameter.has_fixed_value = [each["hasFixedValue"]]
        else:
            parameter.has_fixed_value = []
        """
        
        if "hasPresentation" in each:
            
            # Handle the Internal References for hasPresentation like hasStandardVariable and partOfDataset (Doubt regarding how to handle partOfDataset)

            if "hasStandardVariable" in each["hasPresentation"]:
                response = make_request('https://api.models.mint.isi.edu/v1.1.0/standardvariables?user=' + username, each["hasPresentation"]["hasStandardVariable"], "POST", configuration.access_token)
                if response.status_code == 201 or response.status_code == 200:
                    print(response.json())
                    response_data = response.json()
                    each["hasPresentation"]["hasStandardVariable"] = response_data
                else:
                    print("Error creating standard variables for " + dataset_specification["id"])
                    print(response.status_code)
                    exit(1)
            
            response = make_request('https://api.models.mint.isi.edu/v1.1.0/variablepresentations?user=' + username, each["hasPresentation"], "POST", configuration.access_token)
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                dataset_specification["hasPresentation"] = response_data
            else:
                print("Error creating variable presentation for " + dataset_specification["id"])
                print(response.status_code)
                exit(1)
        
        """
        if "label" in each:
            parameter.label = [each["label"]]
        else:
            parameter.label = []
        """

        if "type" in each:
            parameter["type"] = [each["type"]]
        
        """
        if "has_minimum_accepted_value" in each:
            parameter.has_minimum_accepted_value = [each["hasMinimumAcceptedValue"]]
        else:
            parameter.has_minimum_accepted_value = []
        
        if "adjust_variable" in each:
            parameter.adjusts_variable = [each["adjustVariable"]]
        else:
            parameter.adjusts_variable = []

        if "position" in each:
            parameter.position = [each["position"]]
        else:
            parameter.position = []
        """
        
        if "id" in each:
            parameter["id"] = each["id"]
        
        """
        if "uses_unit" in each:
            parameter.uses_unit = [each["uses_unit"]]
        else:
            parameter.uses_unit = []
        """

        response = make_request('https://api.models.mint.isi.edu/v1.1.0/parameters?user=' + username, parameter, "POST", configuration.access_token)
        if response.status_code == 201 or response.status_code == 200:
            print("Created a parameter " + parameter["id"])
            print(response.json())
            response_data = response.json()
            unique_id = PREFIX_URI + response_data["id"]
            parameter_uri.append({"id": unique_id, "type": response_data["type"]})
        else:
            print("Error creating a parameter " + parameter["id"])
            print(response.status_code)
            exit(1)

    # Create a model configuration
    model_configuration = {}
    if "name" in model_data:
        model_configuration['id'] = model_data['name']
    
    model_configuration['hasInput'] = input_param_uri
    model_configuration['hasOutput'] = output_param_uri
    model_configuration['hasParameter'] = parameter_uri

    if "contributor" in model_data:
        model_configuration["hasContributors"] = model_data["contributors"]
    
    if "author" in model_data:
        model_configuration["author"] = model_data["author"]
    
    if "licence" in model_data:
        model_configuration["licence"] = model_data["licence"]
    
    model_configuration["hasVersion"] = [{'id':model_data['name'] + '_' + model_data['version']}]

    response = make_request('https://api.models.mint.isi.edu/v1.1.0/modelconfigurations?user=' + username, model_configuration, "POST", configuration.access_token)
    if response.status_code == 201 or response.status_code == 200:
        print("Created a Model Configuration " + response.json()["id"])
        print(response.json())
    else:
        print("Error creating Model Configuration")
        print(response.status_code)
        exit(1)



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
