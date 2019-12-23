from wcm import _component
from yaml import load, dump

def person_handler(metadata, access_token, BASE_URL, component_dir, PREFIX_URI, username, field_name):
    person_uri = []
    for person_index, each in enumerate(metadata[field_name]):
        if "id" not in each:
            print("Person POST")
            response = _component.make_request( BASE_URL + '/persons', each, "POST", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                unique_id = PREFIX_URI + response_data["id"]

                # Adding the unique id to the YAML file
                metadata[field_name][person_index]["id"] = unique_id

                # Writing the new ID to the YAML file
                with open(component_dir / "metadata.yaml", "w") as fp:
                    dump(metadata, fp)

                if "type" in response_data:
                    tp = response_data["type"]
                    person_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    person_uri.append({"id": unique_id})
            else:
                print("Error creating a person for index " + person_index)
                print(response.status_code)
                exit(1)
        else:
            print("Persons PUT")
            resource_id = each["id"].split("/")
            response = _component.make_request( BASE_URL + '/persons/' + resource_id[-1], each, "PUT", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                unique_id = response_data["id"]
                if "type" in response_data:
                    tp = response_data["type"]
                    person_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    person_uri.append({"id": unique_id})
            else:
                print("Error creating a person " + each["id"])
                print(response.status_code)
                exit(1)
    return person_uri


