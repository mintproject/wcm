from wcm import _component
from yaml import load, dump

def iterate_on_recursive_data(root, access_token, BASE_URL, component_dir, PREFIX_URI, username):
    stack, node_list = [], []

    if "influences" in root:
        for child_node in root["influences"][::-1]:
            stack.append(child_node)
    
    while stack:
        last_node = stack[-1]

        # If the last node in the stack has children, 
        # add all children to the stack and mark it
        # as 'already added all children to stack' by
        # setting its visited to true
        
        if "influences" in last_node and not last_node["visited"]:
            for child in last_node["influences"][::-1]:
                stack.append(child)
            last_node["visited"] = True
            continue
        # If not, pop it, and add its value to the result list
        else:
            current_node = stack.pop()

            # Register the Process with the API
            if "id" not in current_node:
                print("Process POST")
                print(current_node)
                response = _component.make_request( BASE_URL + '/processs', current_node, "POST", access_token, {'user': username})
                if response.status_code == 201 or response.status_code == 200:

                    response_data = response.json() 
                    unique_id = PREFIX_URI + response_data["id"]

                    response_data["id"] = unique_id
                    print(response.json())
                    # Adding the unique id to the JSON data
                    current_node["id"] = unique_id

                else:
                    print(response.status_code)
                    exit(1) 
            else:
                print("Process PUT")
                resource_id = current_node["id"].split("/")
                response = _component.make_request( BASE_URL + '/processs/' + resource_id[-1], current_node, "PUT", access_token, {'user': username})
                if response.status_code == 201 or response.status_code == 200:
                    print(response.json())
                    response_data = response.json()                    
                else:
                    print("Error creating a process " + current_node["id"])
                    print(response.status_code)
                    exit(1)

            node_list.append(current_node["id"])
    
    # Append the root node
    if "id" not in root:
        print("Process POST")
        response = _component.make_request( BASE_URL + '/processs', root, "POST", access_token, {'user': username})
        if response.status_code == 201 or response.status_code == 200:
            
            response_data = response.json() 
            unique_id = PREFIX_URI + response_data["id"]
            
            response_data["id"] = unique_id
            print(response.json())
            # Adding the unique id to the JSON data
            root["id"] = unique_id

        else:
            print(response.status_code)
            exit(1) 
    else:
        print("Process PUT")
        resource_id = root["id"].split("/")
        response = _component.make_request( BASE_URL + '/processs/' + resource_id[-1], root, "PUT", access_token, {'user': username})
        if response.status_code == 201 or response.status_code == 200:
            print(response.json())
            response_data = response.json()                    
        else:
            print("Error creating a process " + root["id"])
            print(response.status_code)
            exit(1)
        
    node_list.append(root["id"])
    return root


# Attach a visited field to each Process Object
def attach_visited_to_duplicate_metadata(data):
    stack = []
    stack.append(data)

    while stack:
        root = stack.pop()
        root["visited"] = False

        if "influences" not in root:
            continue

        stack.extend(root["influences"])
    
    return data

# Detach the visited field from each Process Object
def detach_visited_from_duplicate_metadata(data):
    stack = []
    stack.append(data)

    while stack:
        root = stack.pop()

        if "visited" in root:
            del root["visited"]

        if "influences" not in root:
            continue

        stack.extend(root["influences"])
    
    return data

def has_process_handler(metadata, access_token, BASE_URL, component_dir, PREFIX_URI, username):
    processes = metadata["hasProcess"]

    process_uri = []
    for process in processes:
        duplicate_process = attach_visited_to_duplicate_metadata(process)
        changed_metadata = iterate_on_recursive_data(duplicate_process, access_token, BASE_URL, component_dir, PREFIX_URI, username)
        final_metadata = detach_visited_from_duplicate_metadata(changed_metadata)
        process_uri.append(final_metadata)
    

    # Writing the new data to the YAML file
    metadata["hasProcess"] = process_uri
    with open(component_dir / "metadata.yaml", "w") as fp:
        dump(metadata, fp)

    return process_uri
