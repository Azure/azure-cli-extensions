# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Constants used across aosm cli extension."""

from enum import Enum
from typing import Any, Dict

# The types of definition that can be generated
VNF = "vnf"
CNF = "cnf"
NSD = "nsd"
VNF_NEXUS = "vnf-nexus"


class DeployableResourceTypes(str, Enum):
    VNF = VNF
    CNF = CNF
    NSD = NSD


# Skip steps
BICEP_PUBLISH = "bicep-publish"
ARTIFACT_UPLOAD = "artifact-upload"
IMAGE_UPLOAD = "image-upload"
HELM_TEMPLATE = "helm-template"


class SkipSteps(Enum):
    BICEP_PUBLISH = BICEP_PUBLISH
    ARTIFACT_UPLOAD = ARTIFACT_UPLOAD
    IMAGE_UPLOAD = IMAGE_UPLOAD
    HELM_TEMPLATE = HELM_TEMPLATE


class ManifestsExist(str, Enum):
    ALL = "all"
    NONE = "none"
    SOME = "some"


CNF_TYPE = "ContainerizedNetworkFunction"
VNF_TYPE = "VirtualNetworkFunction"

# Names of files used in the repo
# TODO: remove unused constants
BASE_FOLDER_NAME = "base"
ARTIFACT_LIST_FILENAME = "artifacts"
MANIFEST_FOLDER_NAME = "artifactManifest"
NF_DEFINITION_FOLDER_NAME = "nfDefinition"
ALL_PARAMETERS_FILE_NAME = "all_deploy.parameters.json"
CGS_FILENAME = "config-group-schema.json"
CGS_NAME = "ConfigGroupSchema"
DEPLOY_PARAMETERS_FILENAME = "deployParameters.json"
TEMPLATE_PARAMETERS_FILENAME = "templateParameters.json"
VHD_PARAMETERS_FILENAME = "vhdParameters.json"
NEXUS_IMAGE_PARAMETERS_FILENAME = "imageParameters.json"

NSD_OUTPUT_FOLDER_FILENAME = "nsd-cli-output"
NSD_INPUT_FILENAME = "nsd-input.jsonc"
NSD_DEFINITION_TEMPLATE_FILENAME = "nsddefinition.bicep.j2"
NSD_MANIFEST_TEMPLATE_FILENAME = "nsdartifactmanifest.bicep.j2"
NSD_BASE_TEMPLATE_FILENAME = "nsdbase.bicep"
NSD_TEMPLATE_FOLDER_NAME = "nsd"
NSD_DEFINITION_FOLDER_NAME = "nsdDefinition"
NSD_NF_TEMPLATE_FILENAME = "nf_template.bicep.j2"

VNF_OUTPUT_FOLDER_FILENAME = "vnf-cli-output"
VNF_INPUT_FILENAME = "vnf-input.jsonc"
VNF_DEFINITION_TEMPLATE_FILENAME = "vnfdefinition.bicep.j2"
VNF_MANIFEST_TEMPLATE_FILENAME = "vnfartifactmanifest.bicep.j2"
VNF_CORE_BASE_TEMPLATE_FILENAME = "vnfbase.bicep"
VNF_NEXUS_BASE_TEMPLATE_FILENAME = "vnfnexusbase.bicep"
VNF_TEMPLATE_FOLDER_NAME = "vnf"

CNF_OUTPUT_FOLDER_FILENAME = "cnf-cli-output"
CNF_INPUT_FILENAME = "cnf-input.jsonc"
CNF_DEFINITION_TEMPLATE_FILENAME = "cnfdefinition.bicep.j2"
CNF_MANIFEST_TEMPLATE_FILENAME = "cnfartifactmanifest.bicep.j2"
CNF_HELM_VALIDATION_ERRORS_TEMPLATE_FILENAME = "cnfhelmtemplateerrors.txt.j2"
CNF_BASE_TEMPLATE_FILENAME = "cnfbase.bicep"
CNF_VALUES_SCHEMA_FILENAME = "values.schema.json"
CNF_TEMPLATE_FOLDER_NAME = "cnf"

NEXUS_IMAGE_REGEX = r"^[\~]?(\d+)\.(\d+)\.(\d+)$"

#################
# OLD CONSTANTS #
#################

# Names of directories used in the repo
# CONFIG_MAPPINGS_DIR_NAME = "configMappings"
# SCHEMAS_DIR_NAME = "schemas"
# TEMPLATES_DIR_NAME = "templates"
GENERATED_VALUES_MAPPINGS_DIR_NAME = "generatedValuesMappings"

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
    "image_api_version",
]

# For CNF NFD Generator
# To match the image path if image: is present in the yaml file
IMAGE_START_STRING = "image:"
IMAGE_PATH_REGEX = r".Values\.([^\s})]*)"

# To match the image name and version if 'imagePullSecrets:' is present in the yaml file
IMAGE_PULL_SECRETS_START_STRING = "imagePullSecrets:"
IMAGE_NAME_AND_VERSION_REGEX = r"\/(?P<name>[^\s]*):(?P<version>[^\s)\"}]*)"

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

BASE_SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {},
    "required": [],
}
