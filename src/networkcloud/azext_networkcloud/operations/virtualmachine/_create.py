# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-nested-blocks
# pylint: disable=protected-access,too-few-public-methods

"""
Provides VirtualMachineCreate customization
"""

from azext_networkcloud.aaz.latest.networkcloud.virtualmachine import Create as _Create
from azure.cli.core.aaz import register_callback
from knack.log import get_logger

from ..common_ssh import CustomSshOptions

logger = get_logger(__name__)


class Create(_Create, CustomSshOptions):

    """
    This custom code inherits from generate virtual machine functions. It is
    integrated into the generated code via:
    cli-ext/v*/ext/src/networkcloud/azext_networkcloud/commands.py
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Build VM Authentication args
        args_schema = cls.build_ssh_arg_schema(args_schema, "Authentication")

        # deregister the VM cli arguments which users should not interact with
        args_schema.ssh_public_keys._registered = False
        args_schema.cloud_services_network_attachment.ip_allocation_method._required = (
            False
        )
        args_schema.cloud_services_network_attachment.ip_allocation_method._registered = (
            False
        )

        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args

        # Dynamic is the default allocation method for the cloud services network attachment
        args.cloud_services_network_attachment.ip_allocation_method = "Dynamic"

        ssh_keys = []
        ssh_keys = CustomSshOptions.add_ssh_config(args)
        if len(ssh_keys) == 0:
            logger.warning(
                "No keys are selected for insertion into the vm. The image will need to have keys or credentials "
                "setup in order to access."
            )
        args.ssh_public_keys = ssh_keys
        return args
