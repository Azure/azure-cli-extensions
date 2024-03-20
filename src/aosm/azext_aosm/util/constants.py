# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Constants used across aosm cli extension."""

from enum import Enum

# The types of definition that can be generated
VNF = "vnf"
CNF = "cnf"
NSD = "nsd"


class DeployableResourceTypes(str, Enum):
    VNF = VNF
    CNF = CNF
    NSD = NSD


# Skip steps
BICEP_PUBLISH = "bicep-publish"
ARTIFACT_UPLOAD = "artifact-upload"
IMAGE_UPLOAD = "image-upload"


class SkipSteps(Enum):
    BICEP_PUBLISH = BICEP_PUBLISH
    ARTIFACT_UPLOAD = ARTIFACT_UPLOAD
    IMAGE_UPLOAD = IMAGE_UPLOAD


# Names of files used in the repo
NF_TEMPLATE_JINJA2_SOURCE_TEMPLATE = "nf_template.bicep.j2"
NF_DEFINITION_JSON_FILENAME = "nf_definition.json"
NF_DEFINITION_OUTPUT_BICEP_PREFIX = "nfd-bicep-"
NSD_DEFINITION_JINJA2_SOURCE_TEMPLATE = "nsd_template.bicep.j2"
NSD_BICEP_FILENAME = "nsd_definition.bicep"
NSD_OUTPUT_BICEP_PREFIX = "nsd-bicep-templates"
NSD_ARTIFACT_MANIFEST_BICEP_FILENAME = "artifact_manifest.bicep"
NSD_ARTIFACT_MANIFEST_SOURCE_TEMPLATE_FILENAME = (
    "artifact_manifest_template.bicep"
)

VNF_DEFINITION_BICEP_TEMPLATE_FILENAME = "vnfdefinition.bicep"
VNF_MANIFEST_BICEP_TEMPLATE_FILENAME = "vnfartifactmanifests.bicep"

CNF_DEFINITION_JINJA2_SOURCE_TEMPLATE_FILENAME = "cnfdefinition.bicep.j2"
CNF_MANIFEST_JINJA2_SOURCE_TEMPLATE_FILENAME = "cnfartifactmanifest.bicep.j2"
CNF_DEFINITION_BICEP_TEMPLATE_FILENAME = "cnfdefinition.bicep"
CNF_MANIFEST_BICEP_TEMPLATE_FILENAME = "cnfartifactmanifest.bicep"
CNF_VALUES_SCHEMA_FILENAME = "values.schema.json"


# Names of directories used in the repo
CONFIG_MAPPINGS_DIR_NAME = "configMappings"
SCHEMAS_DIR_NAME = "schemas"
TEMPLATES_DIR_NAME = "templates"
GENERATED_VALUES_MAPPINGS_DIR_NAME = "generatedValuesMappings"

# Items used when building NFDs/NSDs
DEPLOYMENT_PARAMETERS_FILENAME = "deploymentParameters.json"
OPTIONAL_DEPLOYMENT_PARAMETERS_FILENAME = "optionalDeploymentParameters.txt"
TEMPLATE_PARAMETERS_FILENAME = "templateParameters.json"
VHD_PARAMETERS_FILENAME = "vhdParameters.json"
OPTIONAL_DEPLOYMENT_PARAMETERS_HEADING = (
    "# The following parameters are optional as they have default values.\n"
    "# If you do not wish to expose them in the NFD, find and remove them from both\n"
    f"# {DEPLOYMENT_PARAMETERS_FILENAME} and {TEMPLATE_PARAMETERS_FILENAME} (and {VHD_PARAMETERS_FILENAME} if\n"
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

# For VNF NFD Generator
# Additional config fields from VHD artifact config in input.json that are
# converted to camel case and end up within configMappings/vhdParameters.json
# These become part of the vnfdefinition.bicep, namely:
#   deployParametersMappingRuleProfile: {
#     vhdImageMappingRuleProfile: {
#       userConfiguration: string(loadJsonContent('configMappings/vhdParameters.json'))
#     }
# Add new config fields to this list if they should also end up there.
EXTRA_VHD_PARAMETERS = [
    "image_disk_size_GB",
    "image_hyper_v_generation",
    "image_api_version"
]

# For CNF NFD Generator
# To match the image path if image: is present in the yaml file
IMAGE_START_STRING = "image:"
IMAGE_PATH_REGEX = r".Values\.([^\s})]*)"

# To match the image name and version if 'imagePullSecrets:' is present in the yaml file
IMAGE_PULL_SECRETS_START_STRING = "imagePullSecrets:"
IMAGE_NAME_AND_VERSION_REGEX = r"\/(?P<name>[^\s]*):(?P<version>[^\s)\"}]*)"

DEPLOYMENT_PARAMETER_MAPPING_REGEX = r"\{deployParameters.(.+?)\}"

# Assume that the registry id is of the form:
# /subscriptions/<sub_id>/resourceGroups/<rg_name>/providers/
#   Microsoft.ContainerRegistry/registries/<registry_name>
# This returns groups for the resource group name and registry name
SOURCE_ACR_REGEX = (
    r".*\/resourceGroups\/(?P<resource_group>[^\/]*)\/providers\/Microsoft."
    r"ContainerRegistry\/registries\/(?P<registry_name>[^\/]*)"
)

# Required features for AOSM publish aka deploy
AOSM_FEATURE_NAMESPACE = "Microsoft.HybridNetwork"
AOSM_REQUIRED_FEATURES = [
    "Allow-Publisher",
]
