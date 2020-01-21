from wcm import _component
from yaml import load, dump

def equation_handler(metadata, access_token, BASE_URL, component_dir, PREFIX_URI, username):
    equation_uri = []
    for equation_index, each in enumerate(metadata["hasEquation"]):
        if "id" not in each:
            logging.info("Equation POST")
            response = _component.make_request( BASE_URL + '/equations', each, "POST", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                logging.info(response.json())
                response_data = response.json()
                unique_id = PREFIX_URI + response_data["id"]

                # Adding the unique id to the YAML file

                metadata["hasEquation"][equation_index]["id"] = unique_id

                # Writing the new ID to the YAML file
                with open(component_dir / "metadata.yaml", "w") as fp:
                    dump(metadata, fp)

                if "type" in response_data:
                    tp = response_data["type"]
                    equation_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    equation_uri.append({"id": unique_id})
            else:
                logging.info("Error creating a equation for index " + equation_index)
                logging.info(response.status_code)
                exit(1)
        else:
            logging.info("Equation PUT")
            resource_id = each["id"].split("/")
            response = _component.make_request( BASE_URL + '/equations/' + resource_id[-1], each, "PUT", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                logging.info(response.json())
                response_data = response.json()
                unique_id = response_data["id"]
                if "type" in response_data:
                    tp = response_data["type"]
                    equation_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    equation_uri.append({"id": unique_id})
            else:
                logging.info("Error creating a equation " + each["id"])
                logging.info(response.status_code)
                exit(1)
    return equation_uri


