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
    Create as _Create,
)
from azure.cli.core.aaz import AAZListArg, AAZStrArg, register_callback
from azure.cli.core.aaz._base import has_value
from knack.log import get_logger

from ..common_ssh import CustomSshOptions

logger = get_logger(__name__)


class Create(_Create, CustomSshOptions):

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
            args_schema, "AdministratorConfiguration"
        )
        # Build initial_agent_pool_configurations admin configuration(admin-username and ssh-key-values)
        _element = cls._args_schema.initial_agent_pool_configurations.Element

        _element.ssh_key_values = AAZListArg(
            options=["ssh-key-values"],
            help="The array of comma-separated SSH public keys.",
        )
        _element.ssh_key_values.Element = AAZStrArg()
        # Build control_plane_node_configuration admin configuration(admin-username and ssh-key-values)
        args_schema.control_plane_node_configuration.ssh_key_values = AAZListArg(
            options=["ssh-key-values"],
            help="The array of comma-separated SSH public keys.",
        )
        args_schema.control_plane_node_configuration.ssh_key_values.Element = (
            AAZStrArg()
        )

        # deregister the cli arguments which users should not interact with
        args_schema.ssh_public_keys._registered = False
        args_schema.initial_agent_pool_configurations.Element.ssh_public_keys._registered = (
            False
        )
        args_schema.control_plane_node_configuration.ssh_public_keys._registered = False
        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args
        ssh_keys = []
        ssh_keys = CustomSshOptions.add_ssh_config(args)
        if len(ssh_keys) == 0:
            logger.warning(
                "No keys are selected for insertion into the Kubernetes cluster node. "
                "The image will need to have keys or credentials "
                "setup in order to access."
            )
        if len(ssh_keys) > 0:
            args.ssh_public_keys = ssh_keys

        # control plane node configuration
        ssh_keys_control_plane = []
        ssh_keys_control_plane += CustomSshOptions.add_ssh_key_action(
            list(args.control_plane_node_configuration.ssh_key_values)
        )

        # When control_plane_node_configuration contains no ssh keys in the input, empty 'sshPublicKey' array is not sent to the backend
        # as it will erase the existing keys in that level. When control_plane_node_configuration sshPublicKey is not sent,
        # the top level cluster ssh keys will be used
        # Check if added here to avoid sending empty sshPublicKeys
        if len(ssh_keys_control_plane) > 0:
            args.control_plane_node_configuration.ssh_public_keys = (
                ssh_keys_control_plane
            )

        # initial agent pool configuration
        for x in args.initial_agent_pool_configurations:
            ssh_keys_initial_pool = []
            if has_value(x.ssh_key_values) and x.ssh_key_values.to_serialized_data():
                ssh_keys_initial_pool += CustomSshOptions.add_ssh_key_action(
                    (x.ssh_key_values.to_serialized_data())
                )
            # When initial_agent_pool_configurations contains no ssh keys in the input, empty 'sshPublicKey' array is not sent to the backend
            # as it will erase the existing keys in that level. When initial_agent_pool_configurations sshPublicKey is not sent,
            # the top level cluster ssh keys will be used
            # Check if added here to avoid sending empty sshPublicKeys
            if len(ssh_keys_initial_pool) > 0:
                x.ssh_public_keys = ssh_keys_initial_pool
        return args
