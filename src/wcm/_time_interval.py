from wcm import _component
from yaml import load, dump

def time_interval_handler(metadata, access_token, BASE_URL, component_dir, PREFIX_URI, username, field_name):
    time_interval_uri = []
    for time_interval_index, each in enumerate(metadata[field_name]):
        if "id" not in each:
            print("Time Interval POST")
            response = _component.make_request( BASE_URL + '/timeintervals', each, "POST", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                unique_id = PREFIX_URI + response_data["id"]

                # Adding the unique id to the YAML file
                metadata[field_name][time_interval_index]["id"] = unique_id

                # Writing the new ID to the YAML file
                with open(component_dir / "metadata.yaml", "w") as fp:
                    dump(metadata, fp)

                if "type" in response_data:
                    tp = response_data["type"]
                    time_interval_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    time_interval_uri.append({"id": unique_id})
            else:
                print("Error creating a Time Interval for index " + time_interval_index)
                print(response.status_code)
                exit(1)
        else:
            print("Time Interval PUT")
            resource_id = each["id"].split("/")
            response = _component.make_request( BASE_URL + '/timeintervals/' + resource_id[-1], each, "PUT", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                unique_id = response_data["id"]
                if "type" in response_data:
                    tp = response_data["type"]
                    time_interval_uri.append({"id": unique_id, "type": response_data["type"]})
                else:
                    time_interval_uri.append({"id": unique_id})
            else:
                print("Error creating a Time Intervals " + each["id"])
                print(response.status_code)
                exit(1)
    return time_interval_uri


