# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.commands.command_operation import WaitCommandOperation

from ._create import Create as _ClusterCreate
from ._show import Show as _ClusterShow


logger = get_logger(__name__)


class ClusterCreate(_ClusterCreate):
    AZ_HELP = {
        'type': 'command',
        'short-summary': 'Create a HorizonDB cluster.',
        'long-summary': 'Waits for cluster provisioning and retrieves the cluster to return its current state.',
        'examples': [{
            'name': 'Create a HorizonDB cluster',
            'text': 'az horizondb cluster create --resource-group example-resource-group '
                    '--cluster-name example-cluster --location eastus2 --version 17 '
                    '--geo-redundancy Enabled',
        }],
    }

    def _output(self, *args, **kwargs):
        command_args = {
            name: getattr(self.ctx.args, name).to_serialized_data()
            for name in ['cluster_name', 'resource_group']
        }
        command_args['subscription'] = self.ctx.subscription_id
        return _ClusterShow(cli_ctx=self.cli_ctx)(command_args=command_args)

    def post_operations(self):
        args = self.ctx.args
        cluster_args = {
            'cluster_name': args.cluster_name.to_serialized_data(),
            'resource_group': args.resource_group.to_serialized_data(),
            'subscription': self.ctx.subscription_id,
        }

        def get_cluster(**command_args):
            return _ClusterShow(cli_ctx=self.cli_ctx)(command_args=command_args)

        logger.warning("Waiting for cluster '%s' provisioning to complete...", cluster_args['cluster_name'])
        wait_result = WaitCommandOperation.wait(
            command_args={
                **cluster_args,
                'created': True,
                'updated': False,
                'deleted': False,
                'exists': False,
                'custom': None,
                'interval': 30,
                'timeout': 3600,
            },
            cli_ctx=self.cli_ctx,
            getter=get_cluster,
        )
        # The standard wait helper returns a CLIError on timeout instead of raising it.
        if isinstance(wait_result, CLIError):
            raise wait_result
