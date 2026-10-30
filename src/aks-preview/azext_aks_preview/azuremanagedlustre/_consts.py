# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

CONST_AMLFS_EXT_INSTALLATION_NAME = "azurelustre"
CONST_AMLFS_K8S_EXTENSION_NAME = "microsoft.azuremanagedlustre"
CONST_AMLFS_RELEASE_TRAIN = "stable"
CONST_AMLFS_SUPPORTED_OS_ARCHITECTURES = {
    "ubuntu2004": frozenset(("x64",)),
    "ubuntu2204": frozenset(("x64",)),
    "ubuntu2404": frozenset(("x64", "arm64")),
    "azurelinux3": frozenset(("x64",)),
}
