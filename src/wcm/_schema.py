# -*- coding: utf-8 -*-

import logging

from jsonschema import Draft7Validator

schema = {
    "type": "object",
    "required": ["name", "version"],
    "properties": {
        "name": {
            "description": "The name of the component.",
            "type": "string",
            "maxLength": 214,
            "minLength": 1,
            "pattern": "^(?:@[a-zA-Z0-9-~][a-zA-Z0-9-._~]*/)?[a-zA-Z0-9-~][a-zA-Z0-9-._~]*$",
        },
        "version": {"type": "string"},
        "description": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "homepage": {"type": "string", "oneOf": [{"format": "uri"}, {"enum": ["."]}]},
        "bugs": {
            "type": ["object", "string"],
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The url to your project's issue tracker.",
                    "format": "uri",
                },
                "email": {"type": "string", "format": "email"},
            },
        },
        "license": {"type": "string"},
        "dateCreated": {"type": "string"},
        "author": {"type": "array", "items": {"$ref": "#/definitions/person"}},
        "contributors": {"type": "array", "items": {"$ref": "#/definitions/person"}},
        "maintainers": {"type": "array", "items": {"$ref": "#/definitions/person"}},
        "publisher": {"$ref": "#/definitions/organization"},
        "assumptions": {"type": "string"},
        "citation": {"type": "string"},
        "memoryRequirements": {"type": "string"},
        "operatingSystems": {"type": "array", "items": {"type": "string"}},
        "processorRequirements": {"type": "string"},
        "softwareRequirements": {"type": "string"},
        "repository": {
            "type": ["object", "string"],
            "properties": {
                "type": {"type": "string"},
                "url": {"type": "string"},
                "directory": {"type": "string"},
            },
        },
        "container": {
            "type": ["object", "string"],
            "properties": {
                "dockerPull": {"type": "string"},
                "directory": {"type": "string"},
            },
        },
        "source": {"type": "string"},
        "schemaVersion": {"type": "string"},
        "wings": {
            "type": ["object"],
            "properties": {
                "inputs": {"type": "array", "items": {"$ref": "#/definitions/ioData"}},
                "outputs": {"type": "array", "items": {"$ref": "#/definitions/ioData"}},
                "rules": {"type": ["string","array"]},
                "inheritedRules": {"type": ["string", "array"]},
                "documentation": {"type": "string"},
                "requirement": {"type": "object", "items": {"$ref": "/definitions/requirements"}},
                "componentType": {"type": "string"},
                "files": {"type": "array", "items": {"type": "string"}},
            },
        },
    },

    "definitions": {
        "person": {
            "type": ["object", "string"],
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "url": {"type": "string", "format": "uri"},
                "email": {"type": "string", "format": "email"},
            },
        },
        "ioData": {
            "type": ["object"],
            "required": ["role", "prefix", "isParam", "type", "dimensionality"],
            "properties": {
                "role": {"type": "string"},
                "prefix": {"type": "string"},
                "isParam": {"type": "boolean"},
                "type": {"type": "string"},
                "dimensionality": {"type": "integer"}
            },
        },
        "requirement": {
            "type": ["object"],
            "properties": {
                "storageGB": {"type": "double"},
                "memoryGB": {"type": "double"},
                "need64bit": {"type": "boolean"},
                "softwareIds": {"type": "array", "items": {"type": "string"}},

            },
        },
        "organization": {
            "type": ["object", "string"],
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "url": {"type": "string", "format": "uri"},
            },
        },
    },

}
#Missing extension for variables of each input and variable of each output

v = Draft7Validator(schema)


def _msg(e):
    """Generate a user friendly error message."""
    return e.message


def check_package_spec(spec):
    """Check package specification."""
    err = []
    for e in v.iter_errors(spec):
        err.append(_msg(e))
        logging.error(_msg(e))

    if err:
        raise ValueError("Invalid component specification.")
