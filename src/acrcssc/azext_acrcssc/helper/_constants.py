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
    # CopaV1 = "CopaV1"
    # TrivyV1 = "TrivyV1"


# General Constants
CSSC_TAGS = "acr-cssc"
ACR_API_VERSION_2023_01_01_PREVIEW = "2023-01-01-preview"
ACR_API_VERSION_2019_06_01_PREVIEW = "2019-06-01-preview"
BEARER_TOKEN_USERNAME = "00000000-0000-0000-0000-000000000000"
RESOURCE_GROUP = "resource_group"
SUBSCRIPTION = "subscription"
TMP_DRY_RUN_FILE_NAME = "tmp_dry_run_template.yaml"


# Continuous Patch Constants
CONTINUOSPATCH_OCI_ARTIFACT_TYPE = "oci-artifact"
CSSC_WORKFLOW_POLICY_REPOSITORY = "csscpolicies"
CONTINUOSPATCH_OCI_ARTIFACT_CONFIG = "patchpolicy"
CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_V1 = "v1"
CONTINUOSPATCH_OCI_ARTIFACT_CONFIG_TAG_DRYRUN = "dryrun"
CONTINUOSPATCH_DEPLOYMENT_NAME = "continuouspatchingdeployment"
CONTINUOSPATCH_DEPLOYMENT_TEMPLATE = "CSSC-AutoImagePatching-encodedtasks.json"
# listing all individual tasks that are requires for Continuous Patching to work
CONTINUOSPATCH_TASK_PATCHIMAGE_NAME = "cssc-patch-image"
CONTINUOUSPATCH_TASK_PATCHIMAGE_DESCRIPTION = "This task will patch the OS vulnerabilities on a given image using Copacetic."
CONTINUOSPATCH_TASK_SCANIMAGE_NAME = "cssc-scan-image"
CONTINUOUSPATCH_TASK_SCANIMAGE_DESCRIPTION = f"This task will perform vulnerability OS scan on a given image using Trivy. If there are any vulnerabilities found, it will trigger the patching task using {CONTINUOSPATCH_TASK_PATCHIMAGE_NAME} task."
CONTINUOSPATCH_TASK_SCANREGISTRY_NAME = "cssc-trigger-workflow"
CONTINUOUSPATCH_TASK_SCANREGISTRY_DESCRIPTION = f"This task will trigger the coninuous patching workflow based on the cadence set during the creation. It will match the filter repositories set with config parameter and schedule vulnerability scan check using {CONTINUOSPATCH_TASK_SCANIMAGE_NAME} task."
CONTINUOUS_PATCHING_WORKFLOW_NAME = "continuouspatchv1"
DESCRIPTION = "Description"
TASK_RUN_STATUS_FAILED = "Failed"
TASK_RUN_STATUS_SUCCESS = "Succeeded"
TASK_RUN_STATUS_RUNNING = "Running"

CONTINUOSPATCH_ALL_TASK_NAMES = [
    CONTINUOSPATCH_TASK_PATCHIMAGE_NAME,
    CONTINUOSPATCH_TASK_SCANIMAGE_NAME,
    CONTINUOSPATCH_TASK_SCANREGISTRY_NAME
]

CONTINUOUS_PATCH_WORKFLOW = {
    CONTINUOSPATCH_TASK_SCANREGISTRY_NAME: {
        DESCRIPTION: CONTINUOUSPATCH_TASK_SCANREGISTRY_DESCRIPTION
    },
    CONTINUOSPATCH_TASK_SCANIMAGE_NAME: {
        DESCRIPTION: CONTINUOUSPATCH_TASK_SCANIMAGE_DESCRIPTION
    },
    CONTINUOSPATCH_TASK_PATCHIMAGE_NAME: {
        DESCRIPTION: CONTINUOUSPATCH_TASK_PATCHIMAGE_DESCRIPTION
    }
}

ERROR_MESSAGE_INVALID_TASK = "Workflow type is invalid"
ERROR_MESSAGE_INVALID_TIMESPAN = "Cadence value is invalid. "
RECOMMENDATION_CADENCE = "Cadence must be in the format of <number><unit> where unit is d for days. Example: 1d"
# this dictionary can be expanded to handle more configuration of the tasks regarding continuous patching
# if this gets out of hand, or more types of tasks are supported, this should be a class on its own
CONTINUOSPATCH_TASK_DEFINITION = {
    CONTINUOSPATCH_TASK_PATCHIMAGE_NAME:
        {
            "parameter_name": "imagePatchingEncodedTask",
            "template_file": "task/cssc_patch_image.yaml"
        },
    CONTINUOSPATCH_TASK_SCANIMAGE_NAME:
        {
            "parameter_name": "imageScanningEncodedTask",
            "template_file": "task/cssc_scan_image.yaml"
        },
    CONTINUOSPATCH_TASK_SCANREGISTRY_NAME:
        {
            "parameter_name": "registryScanningEncodedTask",
            "template_file": "task/cssc_trigger_workflow.yaml"
        },
}
CONTINUOUSPATCH_CONFIG_SCHEMA_SIZE_LIMIT = 1024 * 1024 * 10  # 10MB, we don't want to allow huge files
CONTINUOUSPATCH_CONFIG_SCHEMA_V1 = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
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
            }
        }
    },
    "required": ["repositories", "version"]
}
