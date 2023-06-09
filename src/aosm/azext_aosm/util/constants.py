# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Constants used across aosm cli extension."""

# The types of definition that can be generated
VNF = "vnf"
CNF = "cnf"
NSD = "nsd"
SCHEMA = "schema"

# TODO pk5: clean up these names

# Names of files used in the repo
NSD_DEFINITION_BICEP_SOURCE_TEMPLATE = "nsd_template.bicep"
NSD_DEFINITION_BICEP_FILE = "nsd_definition.bicep"
NF_TEMPLATE_BICEP_FILE = "nf_template.bicep"
NF_DEFINITION_BICEP_FILE = "nf_definition.bicep"
NF_DEFINITION_JSON_FILE = "nf_definition.json"
NSD_DEFINITION_OUTPUT_BICEP_PREFIX = "nsd-bicep-templates"
NSD_ARTIFACT_MANIFEST_BICEP_FILE = "artifact_manifest.bicep"
NSD_ARTIFACT_MANIFEST_JSON_FILE = "artifact_manifest.json"
DEFINITION_OUTPUT_BICEP_PREFIX = "nfd-bicep-"
NSD_CONFIG_MAPPING_FILE = "configMappings.json"
NSD_ARTIFACT_MANIFEST_SOURCE_TEMPLATE = "artifact_manifest_template.bicep"

VNF_DEFINITION_BICEP_TEMPLATE = "vnfdefinition.bicep"
VNF_MANIFEST_BICEP_TEMPLATE = "vnfartifactmanifests.bicep"

CNF_DEFINITION_JINJA2_SOURCE_TEMPLATE = "cnfdefinition.bicep.j2"
CNF_MANIFEST_JINJA2_SOURCE_TEMPLATE = "cnfartifactmanifest.bicep.j2"
CNF_DEFINITION_BICEP_TEMPLATE = "cnfdefinition.bicep"
CNF_MANIFEST_BICEP_TEMPLATE = "cnfartifactmanifest.bicep"

DEPLOYMENT_PARAMETERS = "deploymentParameters.json"
# Names of folder used in the repo
CONFIG_MAPPINGS = "configMappings"
SCHEMAS = "schemas"
TEMPLATES = "templates"

# Deployment Schema

SCHEMA_PREFIX = {
    "$schema": "https://json-schema.org/draft-07/schema#",
    "title": "DeployParametersSchema",
    "type": "object",
    "properties": {},
}
# IMAGE_LINE_REGEX = (
#     r"image: \{\{ .Values.(.+?) \}\}/(.+?):(\d+\.\d+\.\d+(-\w+)?(\.\d+)?)"
# )
IMAGE_LINE_REGEX = r".Values\.([^\s})]*)"
# IMAGE_PULL_SECRET_LINE_REGEX = r"imagePullSecrets: \[name: \{\{ .Values.(.+?) \}\}\]"
IMAGE_PULL_SECRET_LINE_REGEX = r".Values\.([^\s})]*)"

DEPLOYMENT_PARAMETER_MAPPING_REGEX = r"\{deployParameters.(.+?)\}"
