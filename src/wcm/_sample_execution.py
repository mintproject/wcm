from wcm import _component
from yaml import load, dump

def has_sample_execution_handler(metadata, access_token, BASE_URL, component_dir, PREFIX_URI, username):
    sample_execution = []
    for sample_execution_index, each in enumerate(metadata["hasSampleExecution"]):
        if "id" not in each:
            logging.info("Sample Execution POST")
            response = _component.make_request( BASE_URL + '/sampleexecutions', each, "POST", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                logging.info(response.json())
                response_data = response.json()
                unique_id = PREFIX_URI + response_data["id"]

                # Adding the unique id to the YAML file
                metadata["hasSampleExecution"][sample_execution_index]["id"] = unique_id

                # Writing the new ID to the YAML file
                with open(component_dir / "metadata.yaml", "w") as fp:
                    dump(metadata, fp)

                if "type" in response_data:
                    tp = response_data["type"]
                    sample_execution.append({"id": unique_id, "type": response_data["type"]})
                else:
                    sample_execution.append({"id": unique_id})
            else:
                logging.info("Error creating a Sample Execution for index " + sample_execution_index)
                logging.info(response.status_code)
                exit(1)
        else:
            logging.info("Sample Executions PUT")
            resource_id = each["id"].split("/")
            response = _component.make_request( BASE_URL + '/sampleexecutions/' + resource_id[-1], each, "PUT", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                logging.info(response.json())
                response_data = response.json()
                unique_id = response_data["id"]
                if "type" in response_data:
                    tp = response_data["type"]
                    sample_execution.append({"id": unique_id, "type": response_data["type"]})
                else:
                    sample_execution.append({"id": unique_id})
            else:
                logging.info("Error creating a Sample Executions " + each["id"])
                logging.info(response.status_code)
                exit(1)
    return sample_execution


