# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, useless-parent-delegation

from azure.cli.command_modules.containerapp.containerapp_auth_decorator import ContainerAppAuthDecorator


# decorator for preview auth show/update
class ContainerAppPreviewAuthDecorator(ContainerAppAuthDecorator):
    def construct_payload(self):
        super().construct_payload()
