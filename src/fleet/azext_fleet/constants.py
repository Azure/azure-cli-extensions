# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

UPGRADE_TYPE_CONTROLPLANEONLY = "ControlPlaneOnly"
UPGRADE_TYPE_FULL = "Full"
UPGRADE_TYPE_NODEIMAGEONLY = "NodeImageOnly"

UPGRADE_TYPE_ERROR_MESSAGES = {
    UPGRADE_TYPE_CONTROLPLANEONLY: f"Please set kubernetes version when upgrade type is '{UPGRADE_TYPE_CONTROLPLANEONLY}'.",  # pylint: disable=line-too-long
    UPGRADE_TYPE_FULL: f"Please set kubernetes version when upgrade type is '{UPGRADE_TYPE_FULL}'.",
    UPGRADE_TYPE_NODEIMAGEONLY: f"Cannot set kubernetes version when upgrade type is '{UPGRADE_TYPE_NODEIMAGEONLY}'."
}
