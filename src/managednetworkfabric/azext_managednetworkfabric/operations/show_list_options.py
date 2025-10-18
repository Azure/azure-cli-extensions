# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,no-member,too-few-public-methods,useless-parent-delegation

from abc import ABC


class ShowListOptions(ABC):
    """Helper class for all InternetGateway commands show and list"""

    def pre_operations(self):
        return super().pre_operations()
