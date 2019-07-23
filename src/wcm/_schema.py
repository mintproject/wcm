# -*- coding: utf-8 -*-

from jsonschema import Draft7Validator

schema = {
    "type": "object",
    "required": ["name", "version"],
    "properties": {
        "name": {"type": "string", "minLength": 3},
        "version": {"type": "string"},
        "description": {"type": "string"},
        "keywords": {"type": "array"},
        "homepage": {"type": "string", "format": "iri"},
    },
}

v = Draft7Validator(schema)


def check_package_spec(spec):
    """Check package specification."""
    for e in v.iter_errors(spec):
        print(e)
        raise e
