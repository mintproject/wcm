
import logging
import yaml
from jsonschema import Draft7Validator

schemaVersion = "0.0.1"

schema= {   "type": "object",
            "required":["id"],
            "properties": {
               "hasDocumentation": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "keywords": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasGrid": {
                  "items": {
                     "$ref": "#/Grid"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "softwareRequirements": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasImplementationScriptLocation": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasDownloadURL": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasInstallationInstructions": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "compatibleVisualizationSoftware": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasRegion": {
                  "items": {
                     "$ref": "#/Region"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasFAQ": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "logo": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasContactPerson": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "type": "string"
               },
               "identifier": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSampleExecution": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSampleResult": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "author": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasConstraint": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "shortDescription": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasExecutionCommand": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "datePublished": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "license": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSourceCode": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSetup": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasExplanationDiagram": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasExample": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "publisher": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasOutput": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasOutputTimeInterval": {
                  "items": {
                     "$ref": "#/TimeInterval"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasFunding": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasComponentLocation": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasProcess": {
                  "items": {
                     "$ref": "#/Process"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "supportDetails": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasVersion": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasTypicalDataSource": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "referencePublication": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "screenshot": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasModelCategory": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hadPrimarySource": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSoftwareImage": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "dateCreated": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "contributor": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasModelResultTable": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasPurpose": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSampleVisualization": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasCausalDiagram": {
                  "items": {
                     "$ref": "#/CausalDiagram"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "memoryRequirements": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "website": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "citation": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "processorRequirements": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasUsageNotes": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSupportScriptLocation": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasAssumption": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasParameter": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "operatingSystems": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasEquation": {
                  "items": {
                     "$ref": "#/Equation"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "usefulForCalculatingIndex": {
                  "items": {
                     "$ref": "#/NumericalIndex"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasInput": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               }
            }
         ,
         "Grid": {
            "properties": {
               "hasDimensionality": {
                  "items": {
                     "type": "number"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasFormat": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasFileStructure": {
                  "nullable": True,
                  "type": "object"
               },
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasPresentation": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasFixedResource": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasCoordinateSystem": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasSpatialResolution": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasShape": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasDimension": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "position": {
                  "items": {
                     "type": "number"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "nullable": False,
                  "type": "string"
               }
            },
            "type": "object"
         },
         "Region": {
            "properties": {
               "geo": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "country": {
                  "items": {
                     "$ref": "#/components/schemas/Region"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "nullable": False,
                  "type": "string"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               }
            },
            "type": "object"
         },
         "TimeInterval": {
            "properties": {
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "nullable": False,
                  "type": "string"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "intervalValue": {
                  "items": {
                     "type": "number"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "intervalUnit": {
                  "items": {
                     "type": "object"
                  },
                  "nullable": True,
                  "type": "array"
               }
            },
            "type": "object"
         },
         "Process": {
            "properties": {
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "nullable": False,
                  "type": "string"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "influences": {
                  "items": {
                     "$ref": "#/Process"
                  },
                  "nullable": True,
                  "type": "array"
               }
            },
            "type": "object"
         },
         "CausalDiagram": {
            "properties": {
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "nullable": False,
                  "type": "string"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "hasPart": {
                  "items": {
                     "type": ["object","string"]
                  },
                  "nullable": True,
                  "type": "array"
               }
            },
            "type": ["object"]
         },
         "Equation": {
            "properties": {
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "nullable": False,
                  "type": "string"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               }
            },
            "type": "object"
         },
         "NumericalIndex": {
            "properties": {
               "description": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "id": {
                  "nullable": False,
                  "type": "string"
               },
               "label": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               },
               "type": {
                  "items": {
                     "type": "string"
                  },
                  "nullable": True,
                  "type": "array"
               }
            },
            "type": "object"
         }
      }


v = Draft7Validator(schema)


def get_schema():
    return schema


def get_schema_version():
    return schemaVersion


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
    logging.info("Metadata YAML is validated successfully.")
   

def validate_file(metadata_path, wings_path):
   with open(metadata_path, 'r') as metadata_stream, open(wings_path, 'r') as wings_stream:
      metadata_loaded=yaml.safe_load(metadata_stream)
      wings_loaded=yaml.safe_load(wings_stream)
      logging.info(wings_loaded['name'].strip() + '-' + wings_loaded['version'].strip())
      if(metadata_loaded['wingsId'].strip() == wings_loaded['name'].strip() + '-' + wings_loaded['version'].strip()):
         check_package_spec(metadata_loaded)
      else:
         logging.info("Two files are not consistent") 



