# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class AzCommandError(Exception):
    """Raised when az command called and returns error"""


class SkuNotAvailableError(Exception):
    """Raised when unable to find compatible SKU for repair VM"""


class UnmanagedDiskCopyError(Exception):
    """Raised when error occured during unmanaged disk copy"""


class WindowsOsNotAvailableError(Exception):
    """Raised the Windows image not available from gallery."""


class RunScriptNotFoundForIdError(Exception):
    """Raised when the run-id is not found in the repair-script-library"""


class SkuDoesNotSupportHyperV(Exception):
    """Raised when the SKU size does not end with v3"""


class ScriptReturnsError(Exception):
    """Raised when run script returns error"""


class SuseNotAvailableError(Exception):
    """Raised when SUSE image not available"""


class SupportingResourceNotFoundError(Exception):
    """Raised when a supporting resource needed for the command is not found"""


class CommandCanceledByUserError(Exception):
    """Raised when the command is canceled an user input"""
