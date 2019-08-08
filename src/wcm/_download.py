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

def download(component_dir, profile=None,download_path=None):

    comp_id = component_dir
    
    #sets path, this determins where the component will be downloaded. Default is the current directory of the program
    if download_path == None:
        path = os.getcwd()
    else:
        path = download_path
    
    wings_instance = wings.init() #server=serverWings,export_url=exportWingsURL,username=userWings,domain=domainWings
   
    component = wings_instance.component.get_component_description(comp_id)
    
    if(component == None):
        logger.error("Invalid ID: \""+comp_id+"\"")
        exit(1)


    file_path = wings_instance.component.download_component(comp_id,os.path.join(path,"components"))  
    
    yamlData = {}    
    data ={}
    dataTypes = {}   
    
    
    yamlData["name"] = ""
    yamlData["version"] = ""
    #yamlData["#description"] = None
    #yamlData["#keywords"] = None
    #yamlData["homepage"] = None
    #amlData["license"] = None
    #yamlData["author"] = None
    #yamlData["container"] = None
    #yamlData["repository"] = None
    
    yamlData["wings"] = component
    

    component = yamlData["wings"]

    #takes the id and splits it by the # (id example: http://localhost:8080/export/users/mint/api-test/components/library.owl#HAND-1)
    info = component["id"].split("#")
    info = info[len(info) - 1] #gets the last index of the split (ie: HAND-1)
    info = info.split("-") #splits it by the - (ie {"HAND","1"})
    
    #First part becomes name, other becomes version
    yamlData["name"] = info[0]
    yamlData["version"] = info[1] + ".0.0"
    
    component.pop("location")
    component.pop("id")
    component.pop("type")
    component["documentation"] = component["documentation"].strip()   
    component["files"] = ["src\\*"]

    #loops through every input field
    for i in component["inputs"]:
        files = {}
        i.pop("id")
        try:
            if "XMLSchema" not in i["type"]:
                
                typeName = i["type"].split("#")
                typeName = typeName[len(typeName)-1]
                
                i["type"] = "dcdom:" + typeName

                files["files"] = ["data/placeholder.tif"]
                dataTypes[typeName] = files
        except:
            logger.warning("no type in " + str(i))
            
    component["data"] = dataTypes;  

    for o in component["outputs"]:
        files = {}
        o.pop("id")
        try:
            if "XMLSchema" not in o["type"]:
                typeName = o["type"].split("#")
                typeName = typeName[len(typeName)-1]
                
                o["type"] = "dcdom:" + typeName


                files["files"] = ["data/placeholder.tif"]
                dataTypes[typeName] = files
        except:
            logger.warning("no type in " + str(o))
       
    #makes the YAML file 
    json_data = (yamlData)
    stream = open(os.path.join(path,"wings-component.yaml"), 'w+')
    yaml.dump(json_data,stream,sort_keys=False)

   
    #makes the src folder in the directory
    try:
        os.mkdir(os.path.join(path,"src"))
    except FileExistsError:
        logger.warning("src folder already exists")

    data_path = os.path.join(path,"data")

    try:
        os.mkdir(data_path)
    except:
        logger.warning("data folder already exists")

    open(os.path.join(data_path,"placeholder.tif"),'w+')

    #unzip components
    try:
        comp_os_path = os.path.join(path,"components")
        zip_path = os.path.join(comp_os_path,comp_id + ".zip")
        with zipfile.ZipFile(zip_path,"r") as zip_ref:
            zip_ref.extractall(comp_os_path)
    except:
        logger.error("something went wrong downloading the code from zip file")
        logger.error(sys.exc_info())

    #copy files into src folder
    comp_files = os.listdir(os.path.join(comp_os_path,comp_id))
    for files in comp_files:
        full_file_name = os.path.join(os.path.join(comp_os_path,comp_id), files)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, os.path.join(path,"src"))

    #remove component folder
    shutil.rmtree(comp_os_path)

    logger.info("Download complete")



    

    