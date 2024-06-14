# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Constants used across the extension."""

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
CONTINUOSPATCH_TASK_SCANIMAGE_NAME = "cssc-scan-image-schedule-patch"
CONTINUOSPATCH_TASK_SCANREPO_NAME = "cssc-scan-repository-schedule-patch"
CONTINUOSPATCH_TASK_SCANREGISTRY_NAME = "cssc-trigger-scan"
CONTINUOUS_PATCHING_WORKFLOW_NAME = "continuouspatchv1"

CONTINUOSPATCH_ALL_TASK_NAMES = [
    CONTINUOSPATCH_TASK_PATCHIMAGE_NAME,
    CONTINUOSPATCH_TASK_SCANIMAGE_NAME,
    CONTINUOSPATCH_TASK_SCANREGISTRY_NAME
]

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
            "template_file": "task/cssc_scan_image_schedule_patch.yaml"
        },
    CONTINUOSPATCH_TASK_SCANREGISTRY_NAME:
        {
            "parameter_name": "registryScanningEncodedTask",
            "template_file": "task/cssc-trigger-scan.yaml"
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
