# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azext_confcom import os_util

# input json values
ACI_FIELD_VERSION = "version"
ACI_FIELD_RESOURCES = "resources"
ACI_FIELD_RESOURCES_NAME = "name"
ACI_FIELD_CONTAINERS = "containers"
ACI_FIELD_CONTAINERS_CONTAINERIMAGE = "containerImage"
ACI_FIELD_CONTAINERS_ENVS = "environmentVariables"
ACI_FIELD_CONTAINERS_ENVS_NAME = "name"
ACI_FIELD_CONTAINERS_ENVS_VALUE = "value"
ACI_FIELD_CONTAINERS_ENVS_STRATEGY = "strategy"
ACI_FIELD_CONTAINERS_ENVS_REQUIRED = "required"
ACI_FIELD_CONTAINERS_COMMAND = "command"
ACI_FIELD_CONTAINERS_WORKINGDIR = "workingDir"
ACI_FIELD_CONTAINERS_MOUNTS = "mounts"
ACI_FIELD_CONTAINERS_MOUNTS_TYPE = "mountType"
ACI_FIELD_CONTAINERS_MOUNTS_PATH = "mountPath"
ACI_FIELD_CONTAINERS_MOUNTS_READONLY = "readonly"
ACI_FIELD_CONTAINERS_WAIT_MOUNT_POINTS = "wait_mount_points"
ACI_FIELD_CONTAINERS_ALLOW_ELEVATED = "allow_elevated"
ACI_FIELD_CONTAINERS_REGO_FRAGMENTS = "fragments"
ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_FEED = "feed"
ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_ISS = "iss"
ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_MINIMUM_SVN = "minimumSvn"
ACI_FIELD_CONTAINERS_REGO_FRAGMENTS_INCLUDES = "includes"
ACI_FIELD_CONTAINERS_ID = "id"

ACI_FIELD_CONTAINERS_ARCHITECTURE_KEY = "Architecture"
ACI_FIELD_CONTAINERS_ARCHITECTURE_VALUE = "amd64"


ACI_FIELD_CONTAINERS_EXEC_PROCESSES = "execProcesses"
ACI_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS = "allowStdioAccess"
ACI_FIELD_CONTAINERS_LIVENESS_PROBE = "livenessProbe"
ACI_FIELD_CONTAINERS_READINESS_PROBE = "readinessProbe"
ACI_FIELD_CONTAINERS_PROBE_ACTION = "exec"
ACI_FIELD_CONTAINERS_PROBE_COMMAND = "command"
ACI_FIELD_CONTAINERS_SIGNAL_CONTAINER_PROCESSES = "signals"

ACI_FIELD_TEMPLATE_PROPERTIES = "properties"
ACI_FIELD_TEMPLATE_PARAMETERS = "parameters"
ACI_FIELD_TEMPLATE_CONTAINERS = "containers"
ACI_FIELD_TEMPLATE_INIT_CONTAINERS = "initContainers"
ACI_FIELD_TEMPLATE_VARIABLES = "variables"
ACI_FIELD_TEMPLATE_VOLUMES = "volumes"
ACI_FIELD_TEMPLATE_IMAGE = "image"
ACI_FIELD_TEMPLATE_RESOURCE_LABEL = "Microsoft.ContainerInstance/containerGroups"
ACI_FIELD_TEMPLATE_COMMAND = "command"
ACI_FIELD_TEMPLATE_ENVS = "environmentVariables"
ACI_FIELD_TEMPLATE_VOLUME_MOUNTS = "volumeMounts"
ACI_FIELD_TEMPLATE_MOUNTS_TYPE = "mountType"
ACI_FIELD_TEMPLATE_MOUNTS_PATH = "mountPath"
ACI_FIELD_TEMPLATE_MOUNTS_READONLY = "readOnly"
ACI_FIELD_TEMPLATE_CONFCOM_PROPERTIES = "confidentialComputeProperties"
ACI_FIELD_TEMPLATE_CCE_POLICY = "ccePolicy"


# output json values
POLICY_FIELD_CONTAINERS = "containers"
POLICY_FIELD_CONTAINERS_ID = "id"
POLICY_FIELD_CONTAINERS_ELEMENTS = "elements"
POLICY_FIELD_CONTAINERS_LENGTH = "length"
POLICY_FIELD_CONTAINERS_ELEMENTS_COMMANDS = "command"
POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS = "env_rules"
POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY = "strategy"
POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE = "pattern"
POLICY_FIELD_CONTAINERS_ELEMENTS_REQUIRED = "required"
POLICY_FIELD_CONTAINERS_ELEMENTS_LAYERS = "layers"
POLICY_FIELD_CONTAINERS_ELEMENTS_WORKINGDIR = "working_dir"
POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS = "mounts"
POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_SOURCE = "source"
POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_DESTINATION = "destination"
POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_TYPE = "type"
POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_TYPE_BIND = "bind"
POLICY_FIELD_CONTAINERS_ELEMENTS_MOUNTS_OPTIONS = "options"
POLICY_FIELD_CONTAINERS_ELEMENTS_WAIT_MOUNT_POINTS = "wait_mount_points"
POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_ELEVATED = "allow_elevated"
POLICY_FIELD_CONTAINER_EXEC_PROCESSES = "exec_processes"
POLICY_FIELD_CONTAINER_SIGNAL_CONTAINER_PROCESSES = "signals"
POLICY_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS = "allow_stdio_access"
POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS = "fragments"
POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED = "feed"
POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISS = "iss"
POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN = "minimum_svn"
POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_INCLUDES = "includes"

CONFIG_FILE = "./data/internal_config.json"

script_directory = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE_PATH = f"{script_directory}/{CONFIG_FILE}"

_config = os_util.load_json_from_file(CONFIG_FILE_PATH)
DEFAULT_WORKING_DIR = _config["containerd"]["defaultWorkingDir"]

MOUNT_SOURCE_TABLE = {}
for entry in _config["mount"]["source_table"]:
    mount_type, mount_source = entry.get("mountType"), entry.get("source")
    MOUNT_SOURCE_TABLE[mount_type] = mount_source

BASELINE_SIDECAR_CONTAINERS = _config["sidecar_base_names"]
# OPENGCS environment variables for customer containers
OPENGCS_ENV_RULES = _config["openGCS"]["environmentVariables"]
# Fabric environment variables for customer containers
FABRIC_ENV_RULES = _config["fabric"]["environmentVariables"]
# Managed Identity environment variables for customer containers
MANAGED_IDENTITY_ENV_RULES = _config["managedIdentity"]["environmentVariables"]
# Enable container restart environment variable for all containers
ENABLE_RESTART_ENV_RULE = _config["enableRestart"]["environmentVariables"]
# default mounts image for customer containers
DEFAULT_MOUNTS_USER = _config["mount"]["default_mounts_user"]
# default mounts policy options for all containers
DEFAULT_MOUNT_POLICY = _config["mount"]["default_policy"]
# default rego policy to be added to all user containers
DEFAULT_REGO_FRAGMENTS = _config["default_rego_fragments"]
# things that need to be set for debug mode
DEBUG_MODE_SETTINGS = _config["debugMode"]
# customer rego file for data to be injected
REGO_FILE = "./data/customer_rego_policy.txt"
script_directory = os.path.dirname(os.path.realpath(__file__))
REGO_FILE_PATH = f"{script_directory}/{REGO_FILE}"
CUSTOMER_REGO_POLICY = os_util.load_str_from_file(REGO_FILE_PATH)
# sidecar rego file
SIDECAR_REGO_FILE = "./data/sidecar_rego_policy.txt"
SIDECAR_REGO_FILE_PATH = f"{script_directory}/{SIDECAR_REGO_FILE}"
SIDECAR_REGO_POLICY = os_util.load_str_from_file(SIDECAR_REGO_FILE_PATH)
# default containers to be added to all container groups
DEFAULT_CONTAINERS = _config["default_containers"]
