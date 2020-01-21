from wcm import _component
from yaml import load, dump

def has_source_code_handler(metadata, access_token, BASE_URL, component_dir, PREFIX_URI, username):
    source_code_uri = []
    for source_index, each in enumerate(metadata["hasSourceCode"]):
        if "id" not in each:
            logging.info("Source Codes POST")
            response = _component.make_request( BASE_URL + '/sourcecodes', each, "POST", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                logging.info(response.json())
                response_data = response.json() 
                unique_id = PREFIX_URI + response_data["id"]

                # Adding the unique id to the YAML file
                metadata["hasSourceCode"][source_index]["id"] = unique_id

                # Writing the new ID to the YAML file
                with open(component_dir / "metadata.yaml", "w") as fp:
                    dump(metadata, fp)
                
                if "type" in response_data:
                    tp = response_data["type"]
                    source_code_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    source_code_uri.append({"id": unique_id})
            else:
                logging.info("Error creating a source code for index " + source_index)
                logging.info(response.status_code)
                exit(1)
        else:
            logging.info("Source Codes PUT")
            resource_id = each["id"].split("/")
            response = _component.make_request( BASE_URL + '/sourcecodes/' + resource_id[-1], each, "PUT", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                logging.info(response.json())
                response_data = response.json()
                unique_id = response_data["id"]
                if "type" in response_data:
                    tp = response_data["type"]
                    source_code_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    source_code_uri.append({"id": unique_id})
            else:
                logging.info("Error creating a source code " + each["id"])
                logging.info(response.status_code)
                exit(1)
    return source_code_uri


