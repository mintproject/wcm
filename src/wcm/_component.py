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

    logging.info(model_data)

    input_param = []
    output_param = []
    param = []
    for element in model_data['wings']['inputs']:
        if not element['isParam']:
            element.pop('isParam')
            element.pop('type')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')
            if 'prefix' in element.keys():
                element['hasPrefix'] = element.pop('prefix')
            if 'testValue' in element.keys():
                element['hasTestValue'] = element.pop('testValue')
            input_param.append(element)
        else:
            element.pop('isParam')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'paramDefaultValue' in element.keys():
                element['hasDefaultValue'] = str(element.pop('paramDefaultValue'))
            if 'type' in element.keys():
                element['hasDataType'] = element.pop('type')
            if 'prefix' in element.keys():
                element['hasPrefix'] = element.pop('prefix')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')
            param.append(element)
    
    for element in model_data['wings']['outputs']:
        if not element['isParam']:
            element.pop('isParam')
            element.pop('type')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')
            if 'prefix' in element.keys():
                element['hasPrefix'] = element.pop('prefix')
            if 'testValue' in element.keys():
                element['hasTestValue'] = element.pop('testValue')
            output_param.append(element)
        else:
            element.pop('isParam')
            if 'role' in element.keys():
                element['id'] = element.pop('role')
            if 'paramDefaultValue' in element.keys():
                element['hasDefaultValue'] = str(element.pop('paramDefaultValue'))
            if 'type' in element.keys():
                element['hasDataType'] = element.pop('type')
            if 'prefix' in element.keys():
                element['hasPrefix'] = element.pop('prefix')
            if 'dimensionality' in element.keys():
                element['hasDimensionality'] = element.pop('dimensionality')
            param.append(element)
    configuration = modelcatalog.Configuration()
    user_api_instance = modelcatalog.DefaultApi()

    # Login the user into the API to get the access token
    if username and password:
        try:
            print("hekll")
            api_response = user_api_instance.user_login_get(username, password)
            print("hekl")
            data = json.dumps(ast.literal_eval(api_response))
            access_token = json.loads(data)["access_token"]
            configuration.access_token = access_token
        except ApiException as e:
            print("Exception when calling DefaultApi->user_login_get: %s\n" % e)
    else:
        log.error("There is some issue while getting the username and password")
        exit(1)

    # Create an instance of DatasetSpecificationApi to register the input and output parameters
    api_instance = modelcatalog.DatasetSpecificationApi(modelcatalog.ApiClient(configuration))
    # Add input parameter to DatasetSpecification API
    for each in input_param:
        logging.info(each)
        dataset_specification = modelcatalog.DatasetSpecification()

        if "hasDimensionality" in each:
            dataset_specification.has_dimensionality = [each["hasDimensionality"]]
        else:
            dataset_specification.has_dimensionality = []
        
        if "id" in each:
            dataset_specification.id = each["id"]
        else:
            dataset_specification.id = []

        if "has_format" in each:
            dataset_specification.has_format = each["has_format"]
        else:
            dataset_specification.has_format = []
        
        if "has_file_structure" in each:
            dataset_specification.has_file_structure = each["has_file_structure"]
        else:
            dataset_specification.has_file_structure = {}

        if "description" in each:
            dataset_specification.description = each["description"]
        else:
            dataset_specification.description = []
        
        if "position" in each:
            dataset_specification.position = each["position"]
        else:
            dataset_specification.position = []

        if "type" in each:
            dataset_specification.type = each["type"]
        else:
            dataset_specification.type = []

        if "role" in each:
            dataset_specification.label = [each["role"]]
        else:
            dataset_specification.label = []
        
        if "has_fixed_resource" in each:
            dataset_specification.has_fixed_resource = each["has_fixed_resource"]
        else:
            dataset_specification.has_fixed_resource = []
        
        if "has_presentation" in each:
            dataset_specification.has_presentation = each["has_presentation"]
        else:
            dataset_specification.has_presentation = []

        try:
            api_instance.datasetspecifications_post(dataset_specification=dataset_specification, user=username)
            pprint("Created Input Dataset Specification")
        except ApiException as e:
            pprint("Exception when calling DatasetspecificationApi->create_data_set: %s\n" % e)

    # Add output parameter to DatasetSpecification API
    for each in output_param:
        dataset_specification = modelcatalog.DatasetSpecification()

        if "hasDimensionality" in each:
            dataset_specification.has_dimensionality = [each["hasDimensionality"]]
        else:
            dataset_specification.has_dimensionality = []
        
        if "id" in each:
            dataset_specification.id = each["id"]
        else:
            dataset_specification.id = []

        if "has_format" in each:
            dataset_specification.has_format = each["has_format"]
        else:
            dataset_specification.has_format = []
        
        if "has_file_structure" in each:
            dataset_specification.has_file_structure = each["has_file_structure"]
        else:
            dataset_specification.has_file_structure = {}
        
        if "description" in each:
            dataset_specification.description = each["description"]
        else:
            dataset_specification.description = []
        
        if "position" in each:
            dataset_specification.position = each["position"]
        else:
            dataset_specification.position = []

        if "type" in each:
            dataset_specification.type = each["type"]
        else:
            dataset_specification.type = []

        if "role" in each:
            dataset_specification.label = [each["role"]]
        else:
            dataset_specification.label = []
        
        if "has_fixed_resource" in each:
            dataset_specification.has_fixed_resource = each["has_fixed_resource"]
        else:
            dataset_specification.has_fixed_resource = []
        
        if "has_presentation" in each:
            dataset_specification.has_presentation = each["has_presentation"]
        else:
            dataset_specification.has_presentation = []
        try:
            api_instance.datasetspecifications_post(dataset_specification=dataset_specification, user=username)
            pprint("Created Output Dataset Specification")
        except ApiException as e:
            pprint("Exception when calling DatasetspecificationApi->create_data_set: %s\n" % e)
        
    
    logging.info(param)

    for each in param:
        parameter = modelcatalog.Parameter()

        if "has_default_value" in each:
            parameter.has_default_value = [each["hasDefaultValue"]]
        else:
            parameter.has_default_value = []
        
        if "has_maximum_accepted_value" in each:
            parameter.has_maximum_accepted_value = [each["hasMaximumAcceptedValue"]]
        else:
            parameter.has_maximum_accepted_value = []
        
        if "description" in each:
            parameter.description = [each["description"]]
        else:
            parameter.description = []
        
        if "has_data_type" in each:
            parameter.has_data_type = [each["hasDataType"]]
        else:
            parameter.has_data_type = []
    
        if "has_fixed_value" in each:
            parameter.has_fixed_value = [each["hasFixedValue"]]
        else:
            parameter.has_fixed_value = []
        
        if "has_presentation" in each:
            parameter.has_presentation = [each["hasPresentation"]]
        else:
            parameter.has_presentation = []
        
        if "label" in each:
            parameter.label = [each["label"]]
        else:
            parameter.label = []
        
        if "type" in each:
            parameter.type = each["type"]
        else:
            parameter.type = []
        
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
        
        if "id" in each:
            parameter.id = each["id"]
        else:
            parameter.id = []

        if "uses_unit" in each:
            parameter.uses_unit = [each["uses_unit"]]
        else:
            parameter.uses_unit = []

        api_instance = modelcatalog.ParameterApi(modelcatalog.ApiClient(configuration))
        try:
            # Create a Parameter
            api_response = api_instance.parameters_post(user=username, parameter=parameter)
            pprint("Created Parameters")
        except ApiException as e:
            print("Exception when calling ParameterApi->parameters_post: %s\n" % e)
        
    
    headers = {"content-type": "application/json", "Authorization": "Bearer " + configuration.access_token}

    # Create a model configuration
    api_instance = modelcatalog.ModelConfigurationApi(modelcatalog.ApiClient(configuration))
    model_configuration = modelcatalog.ModelConfiguration()

    model_configuration={}
    model_configuration['id'] = model_data['name']
    model_configuration['hasInput'] = input_param
    model_configuration['hasOutput'] = output_param
    model_configuration['hasParameter'] = param
    model_configuration['hasContainer'] = []
    model_configuration['hasRepository'] = []
    model_configuration['hasContributors'] = []

    r = requests.post('https://api.models.mint.isi.edu/v1.1.0/modelconfigurations?user=dhruvrpa@usc.edu', headers = headers, data=json.dumps(model_configuration))
    print(r.status_code)
    print("Created the Model Configurations")

    model_version = {}
    model_version['id']=model_data['name']+'_'+model_data['version']
    model_version['has_version_id'] = [model_data['version']]
    model_version['has_configuration'] = []
    model_version['has_configuration'].append({'id':model_data['name']})

    print(model_version)

    r = requests.post('https://api.models.mint.isi.edu/v1.1.0/softwareversions?user=dhruvrpa@usc.edu', headers = headers, data=json.dumps(model_version))
    print(r.status_code)
    print("Created the Model Versions")

    model = {}
    model['id'] = model_data['name']+'_model'
    model['label'] = [model_data['name']]
#model['description']=data['description']
    model['has_documentation'] = []
    #model['hasDocumentation'].append(model_data['wings']['documentation'])
    model['has_version'] = []
    model['has_version'].append({'id':model_data['name']+'_'+model_data['version']})
#model['author']=data['author']
#model['hasLicense']=data['license']
    model['has_bugs'] = []
#model['hasBugs'].append([{'url':element['url']},{'email':element['email']}])
#model['hasHomepage']=data['homepage']
    model['keywords'] = []

    print(model)
    r = requests.post('https://api.models.mint.isi.edu/v1.1.0/models?user=dhruvrpa@usc.edu', headers = headers, data=json.dumps(model))
    print(r.status_code)

    print("Created the Model")



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
