# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Constants used across the extension."""
# pylint: disable=line-too-long
from enum import Enum


# This enum is used to define the task types for the CLI, in case new types are added this is the place to start
class CSSCTaskTypes(Enum):
    """Enum for the task type."""
    ContinuousPatchV1 = 'continuouspatchv1'


class TaskRunStatus(Enum):
    """Enum for the task status. ACR.Build.Contracts"""
    Unknown = 'Unknown'
    Queued = 'Queued'
    Started = 'Started'
    Running = 'Running'
    Succeeded = 'Succeeded'
    Failed = 'Failed'
    Canceled = 'Canceled'
    Error = 'Error'
    Timeout = 'Timeout'


# General Constants
CSSC_TAGS = "acr-cssc"
ACR_API_VERSION_2023_01_01_PREVIEW = "2023-01-01-preview"
ACR_API_VERSION_2019_06_01_PREVIEW = "2019-06-01-preview"
BEARER_TOKEN_USERNAME = "00000000-0000-0000-0000-000000000000"
RESOURCE_GROUP = "resource_group"
SUBSCRIPTION = "subscription"
TMP_DRY_RUN_FILE_NAME = "tmp_dry_run_template.yaml"


# Continuous Patch Constants
CONTINUOUSPATCH_IMAGE_LIMIT = 100
CONTINUOUSPATCH_OCI_ARTIFACT_TYPE = "oci-artifact"
CSSC_WORKFLOW_POLICY_REPOSITORY = "csscpolicies"
CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG = "patchpolicy"
CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1 = "v1"
CONTINUOUSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN = "dryrun"
CONTINUOUSPATCH_DEPLOYMENT_NAME = "continuouspatchingdeployment"
CONTINUOUSPATCH_DEPLOYMENT_TEMPLATE = "CSSC-AutoImagePatching-encodedtasks.json"
# listing all individual tasks that are required for Continuous Patching to work
CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME = "cssc-patch-image"
CONTINUOUSPATCH_TASK_PATCHIMAGE_DESCRIPTION = "This task will patch the OS vulnerabilities on a given image using Copacetic."
CONTINUOUSPATCH_TASK_SCANIMAGE_NAME = "cssc-scan-image"
CONTINUOUSPATCH_TASK_SCANIMAGE_DESCRIPTION = f"This task will perform vulnerability OS scan on a given image using Trivy. If there are any vulnerabilities found, it will trigger the patching task using {CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME} task."
CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME = "cssc-trigger-workflow"
CONTINUOUSPATCH_TASK_SCANREGISTRY_DESCRIPTION = f"This task will trigger the continuous patching workflow based on the schedule set during the creation. It will match the filter repositories set with config parameter and schedule vulnerability scan check using {CONTINUOUSPATCH_TASK_SCANIMAGE_NAME} task."
CONTINUOUS_PATCHING_WORKFLOW_NAME = CSSCTaskTypes.ContinuousPatchV1.value
DESCRIPTION = "Description"
CONTINUOUSPATCH_SCHEDULE_MIN_DAYS = 1
CONTINUOUSPATCH_SCHEDULE_MAX_DAYS = 30


CONTINUOUSPATCH_ALL_TASK_NAMES = [
    CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME,
    CONTINUOUSPATCH_TASK_SCANIMAGE_NAME,
    CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME
]

WORKFLOW_STATUS_NOT_AVAILABLE = "---Not Available---"
WORKFLOW_STATUS_PATCH_NOT_AVAILABLE = "---No patch image available---"
WORKFLOW_VALIDATION_MESSAGE = "Validating configuration"

ERROR_MESSAGE_WORKFLOW_TASKS_DOES_NOT_EXIST = f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow tasks does not exist. Run 'az acr supply-chain workflow create' command to create workflow tasks."
ERROR_MESSAGE_WORKFLOW_TASKS_ALREADY_EXISTS = f"{CONTINUOUS_PATCHING_WORKFLOW_NAME} workflow tasks already exists. Use 'az acr supply-chain workflow update' command to perform updates."
ERROR_MESSAGE_INVALID_TASK = "Workflow type %s is invalid"
ERROR_MESSAGE_INVALID_TIMESPAN_VALUE = "Schedule value is invalid. "
ERROR_MESSAGE_INVALID_TIMESPAN_FORMAT = "Schedule format is invalid. "
ERROR_MESSAGE_INVALID_JSON_PARSE = "File used for --config cannot be parsed as a JSON file. Use --help to see the schema of the config file."
ERROR_MESSAGE_INVALID_JSON_SCHEMA = "File used for --config is not a valid config JSON file. Use --help to see the schema of the config file."
RECOMMENDATION_SCHEDULE = f"Schedule must be in the format of <number><unit> where unit is d for days. Example: {CONTINUOUSPATCH_SCHEDULE_MIN_DAYS}d. Max value for d is {CONTINUOUSPATCH_SCHEDULE_MAX_DAYS}d."

# this dictionary can be expanded to handle more configuration of the tasks regarding continuous patching
# if this gets out of hand, or more types of tasks are supported, this should be a class on its own
CONTINUOUSPATCH_TASK_DEFINITION = {
    CONTINUOUSPATCH_TASK_PATCHIMAGE_NAME:
        {
            "parameter_name": "imagePatchingEncodedTask",
            "template_file": "task/cssc_patch_image.yaml",
            DESCRIPTION: CONTINUOUSPATCH_TASK_PATCHIMAGE_DESCRIPTION
        },
    CONTINUOUSPATCH_TASK_SCANIMAGE_NAME:
        {
            "parameter_name": "imageScanningEncodedTask",
            "template_file": "task/cssc_scan_image.yaml",
            DESCRIPTION: CONTINUOUSPATCH_TASK_SCANIMAGE_DESCRIPTION
        },
    CONTINUOUSPATCH_TASK_SCANREGISTRY_NAME:
        {
            "parameter_name": "registryScanningEncodedTask",
            "template_file": "task/cssc_trigger_workflow.yaml",
            DESCRIPTION: CONTINUOUSPATCH_TASK_SCANREGISTRY_DESCRIPTION
        },
}
CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT = 1024 * 1024 * 10  # 10MB, we don't want to allow huge files
CONTINUOUSPATCH_CONFIG_SCHEMA_V1 = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^(v1)$"
        },
        "tag-convention": {
            "type": "string",
            "pattern": "^(floating|incremental)$"
        },
        "repositories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string"
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "uniqueItems": True,
                        "minItems": 1
                    },
                    "enabled": {
                        "type": "boolean"
                    }
                },
                "required": ["repository", "tags"]
            },
            "uniqueItems": True,
            "minItems": 1
        }
    },
    "required": ["repositories", "version"]
}
