# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-nested-blocks,line-too-long
# pylint: disable=protected-access
"""
Provides Kubernetescluster customization
"""

from azext_networkcloud.aaz.latest.networkcloud.kubernetescluster import (
    Update as _Update,
)
from azure.cli.core.aaz import AAZListArg, AAZStrArg, register_callback
from azure.cli.core.aaz._base import has_value
from knack.log import get_logger

from ..common_ssh import CustomSshOptions

logger = get_logger(__name__)


class Update(_Update, CustomSshOptions):

    """
    This custom code inherits from generate kubernetescluster functions. It is
    integrated into the generated code via:
    cli-ext/v*/ext/src/networkcloud/azext_networkcloud/commands.py
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Build Kubernetescluster Authentication args
        args_schema = CustomSshOptions.build_ssh_arg_schema(
            args_schema, True, "AdministratorConfiguration"
        )

        # Build control_plane_node_configuration ssh-key-values
        args_schema.control_plane_node_configuration.ssh_key_values = AAZListArg(
            options=["ssh-key-values"],
            help="The array of comma-separated SSH public keys. If empty array is provided, the top level cluster ssh keys will be used.",
        )
        args_schema.control_plane_node_configuration.ssh_key_values.Element = (
            AAZStrArg()
        )

        # deregister the cli arguments which users should not interact with
        args_schema.ssh_public_keys._registered = False
        args_schema.control_plane_node_configuration.ssh_public_keys._registered = False
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
                    "Empty SSH key value is provided for the cluster administrator configuration. All existing keys will be removed from the Kubernetes cluster nodes."
                )
            args.ssh_public_keys = ssh_keys
        else:
            # no changes will be expected for this update
            args.ssh_public_keys = None

        # only send control plane node ssh keys if they are provided
        has_cp_ssh_config = has_value(
            args.control_plane_node_configuration.ssh_key_values
        )
        if has_cp_ssh_config:
            ssh_keys_control_plane = []
            ssh_keys_control_plane += CustomSshOptions.add_ssh_key_action(
                list(args.control_plane_node_configuration.ssh_key_values)
            )
            if len(ssh_keys_control_plane) == 0:
                logger.warning(
                    "Empty SSH keys array is provided for the control plane. All existing keys will be removed and the top level cluster SSH keys will be used."
                )
            args.control_plane_node_configuration.ssh_public_keys = (
                ssh_keys_control_plane
            )
        else:
            # When control_plane_node_configuration is not provided, empty 'sshPublicKey' array is not sent to the backend
            # as it will erase the existing keys in that level. When control_plane_node_configuration sshPublicKey is not sent,
            # the top level cluster ssh keys will be used
            ssh_keys_control_plane = None

        return args
