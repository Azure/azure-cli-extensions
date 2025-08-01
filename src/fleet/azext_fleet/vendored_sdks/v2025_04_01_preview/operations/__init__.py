# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
# pylint: disable=wrong-import-position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._patch import *  # pylint: disable=unused-wildcard-import

from ._operations import Operations  # type: ignore
from ._fleets_operations import FleetsOperations  # type: ignore
from ._auto_upgrade_profiles_operations import AutoUpgradeProfilesOperations  # type: ignore
from ._auto_upgrade_profile_operations_operations import AutoUpgradeProfileOperationsOperations  # type: ignore
from ._gates_operations import GatesOperations  # type: ignore
from ._fleet_members_operations import FleetMembersOperations  # type: ignore
from ._update_runs_operations import UpdateRunsOperations  # type: ignore
from ._fleet_update_strategies_operations import FleetUpdateStrategiesOperations  # type: ignore

from ._patch import __all__ as _patch_all
from ._patch import *
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "Operations",
    "FleetsOperations",
    "AutoUpgradeProfilesOperations",
    "AutoUpgradeProfileOperationsOperations",
    "GatesOperations",
    "FleetMembersOperations",
    "UpdateRunsOperations",
    "FleetUpdateStrategiesOperations",
]
__all__.extend([p for p in _patch_all if p not in __all__])  # pyright: ignore
_patch_sdk()
