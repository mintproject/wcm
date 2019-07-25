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
            "pattern": "^(?:@[a-z0-9-~][a-z0-9-._~]*/)?[a-z0-9-~][a-z0-9-._~]*$",
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
        "author": {"$ref": "#/definitions/person"},
        "contributors": {"type": "array", "items": {"$ref": "#/definitions/person"}},
        "maintainers": {"type": "array", "items": {"$ref": "#/definitions/person"}},
        "repository": {
            "type": ["object", "string"],
            "properties": {
                "type": {"type": "string"},
                "url": {"type": "string"},
                "directory": {"type": "string"},
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
        }
    },
}

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
