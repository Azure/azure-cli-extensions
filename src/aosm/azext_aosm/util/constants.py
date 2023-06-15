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


# Names of folder used in the repo
CONFIG_MAPPINGS = "configMappings"
SCHEMAS = "schemas"
TEMPLATES = "templates"
GENERATED_VALUES_MAPPINGS = "generatedValuesMappings"

# Names of files when building NFDs/NSDs
DEPLOYMENT_PARAMETERS = "deploymentParameters.json"
OPTIONAL_DEPLOYMENT_PARAMETERS_FILE = "optionalDeploymentParameters.txt"
TEMPLATE_PARAMETERS = "templateParameters.json"
VHD_PARAMETERS = "vhdParameters.json"
OPTIONAL_DEPLOYMENT_PARAMETERS_HEADING = (
    "# The following parameters are optional as they have default values.\n"
    "# If you do not wish to expose them in the NFD, find and remove them from both\n"
    f"# {DEPLOYMENT_PARAMETERS} and {TEMPLATE_PARAMETERS} (and {VHD_PARAMETERS} if\n"
    "they are there)\n"
    "# You can re-run the build command with the --order-params flag to order those\n"
    "# files with the optional parameters at the end of the file, and with the \n"
    "# --interactive flag to interactively choose y/n for each parameter to expose.\n\n"
)

# Deployment Schema

SCHEMA_PREFIX = {
    "$schema": "https://json-schema.org/draft-07/schema#",
    "title": "DeployParametersSchema",
    "type": "object",
    "properties": {},
}

# For CNF NFD Generator
# To match the image path if image: is present in the yaml file
IMAGE_START_STRING = "image:"
IMAGE_PATH_REGEX = r".Values\.([^\s})]*)"

# To match the image name and version if imagePullSecrets: is present in the yaml file
IMAGE_PULL_SECRETS_START_STRING = "imagePullSecrets:"
IMAGE_NAME_AND_VERSION_REGEX = r"\/([^\s]*):([^\s)\"}]*)"

DEPLOYMENT_PARAMETER_MAPPING_REGEX = r"\{deployParameters.(.+?)\}"
