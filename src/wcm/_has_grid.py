from wcm import _component
from yaml import load, dump

def has_grid_handler(metadata, access_token, BASE_URL, component_dir, PREFIX_URI, username):
    grid_uri = []
    for grid_index, each in enumerate(metadata["hasGrid"]):
        if "id" not in each:
            print("Grid POST")
            response = _component.make_request( BASE_URL + '/grids', each, "POST", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json() 
                unique_id = PREFIX_URI + response_data["id"]

                response_data["id"] = unique_id

                # Adding the unique id to the YAML file
                metadata["hasGrid"][grid_index]["id"] = unique_id

                # Writing the new ID to the YAML file
                with open(component_dir / "metadata.yaml", "w") as fp:
                    dump(metadata, fp)
                
                grid_uri.append(response_data)
                
            else:
                print("Error creating a region for index " + region_index)
                print(response.status_code)
                exit(1)
        else:
            print("Grid PUT")
            resource_id = each["id"].split("/")
            response = _component.make_request( BASE_URL + '/grids/' + resource_id[-1], each, "PUT", access_token, {'user': username})
            if response.status_code == 201 or response.status_code == 200:
                print(response.json())
                response_data = response.json()
                grid_uri.append(response_data)
            else:
                print("Error creating a region " + each["id"])
                print(response.status_code)
                exit(1)
    return grid_uri


