import logging
import json
import wings
import os
from wcm import _schema, _utils

logger = logging.getLogger()


def list_components(profile="default"):
    wings_instance = wings.init()
    component = wings_instance.component.get_all_items()
    component = component["children"]
    for i in component:
        comp_class = ((i["cls"])["component"])["id"]
        comp_class = comp_class.split('#')
        print("Class: " + comp_class[-1])

        length = len(i["children"])
        count = 1
        print("   └────┐")
        for j in i["children"]:
            comp_id = ((j["cls"])["component"])["id"]
            comp_id = comp_id.split('#')

            if length == 1 or count == length:
                print("\t└─ " + comp_id[-1])
            else:
                print("\t├─ " + comp_id[-1])

            count += 1


def _main():
    list_components()


if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        logger.exception(e)
