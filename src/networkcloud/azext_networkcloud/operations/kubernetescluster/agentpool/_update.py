# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

"""
Provides Agentpool customization
"""

from azext_networkcloud.aaz.latest.networkcloud.kubernetescluster.agentpool import (
    Update as _Update,
)
from azure.cli.core.aaz import register_callback
from knack.log import get_logger

from ...common_ssh import CustomSshOptions

logger = get_logger(__name__)


class Update(_Update, CustomSshOptions):

    """
    This custom code inherits from generate agentpool functions. It is
    integrated into the generated code via:
    cli-ext/v*/ext/src/networkcloud/azext_networkcloud/commands.py
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Build agentpool Authentication args
        args_schema = CustomSshOptions.build_ssh_arg_schema(
            args_schema, True, "AdministratorConfiguration"
        )
        # deregister the cli arguments which users should not interact with
        args_schema.ssh_public_keys._registered = False
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args

        # only send ssh keys if they are provided
        # special case: if the user has provided an empty array, we need to send an empty array to the backend
        # to clear the existing keys
        has_ssh_config = CustomSshOptions.has_ssh_config(args)

        if has_ssh_config:
            ssh_keys = []
            ssh_keys = CustomSshOptions.add_ssh_config(args)
            if len(ssh_keys) == 0:
                logger.warning(
                    "Empty SSH key value is provided. All existing keys will be removed from the agent pool nodes."
                )
            args.ssh_public_keys = ssh_keys
        else:
            logger.warning(
                "No SSH keys are provided for insertion into the agent pool nodes. "
                "The image will need to have keys or credentials "
                "setup in order to access."
            )
            args.ssh_public_keys = None

        return args
