# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import deepcopy

from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.command_operation import WaitCommandOperation

from ._create import Create as _ClusterCreate
from ._show import Show as _ClusterShow
from .pool._create import Create as _PoolCreate
from .pool.custom import PoolCreate


logger = get_logger(__name__)


_POOL_ARGUMENTS = {
    'compute_generation': ['--pool-compute-generation', '--pool-compute-gen'],
    'compute_processor': ['--pool-compute-processor', '--pool-compute-proc'],
    'v_cores': ['--pool-v-cores'],
    'high_availability_mode': ['--pool-high-availability-mode', '--pool-ha-mode'],
    'node_count': ['--pool-node-count'],
}


class ClusterCreate(_ClusterCreate):
    AZ_HELP = {
        'type': 'command',
        'short-summary': 'Create a HorizonDB cluster and its default pool.',
        'long-summary': 'Waits for cluster provisioning before creating defaultpool, '
                        'then waits for pool provisioning and retrieves the cluster to return its current state. '
                        'If pool creation fails, the cluster is not deleted.',
        'examples': [{
            'name': 'Create a HorizonDB cluster with a single-node default pool',
            'text': 'az horizondb cluster create --resource-group example-resource-group '
                    '--cluster-name example-cluster --location eastus2 --version 17 '
                    '--geo-redundancy Enabled --pool-compute-processor AMD --pool-compute-generation 3 '
                    '--pool-v-cores 2 --pool-node-count 1 --pool-high-availability-mode Disabled',
        }],
    }

    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        pool_schema = _PoolCreate.get_arguments_schema()
        for name, options in _POOL_ARGUMENTS.items():
            argument = deepcopy(getattr(pool_schema, name))
            argument._options = list(options)  # pylint: disable=protected-access
            argument._help['name'] = ' '.join(options)  # pylint: disable=protected-access
            argument._required = True  # pylint: disable=protected-access
            setattr(args_schema, name, argument)
        args_schema.v_cores._help['short-summary'] = (  # pylint: disable=protected-access
            'The number of vCores for the default pool. Allowed values are 2 through 192.'
        )
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        node_count = args.node_count.to_serialized_data()
        mode = args.high_availability_mode.to_serialized_data()
        if node_count == 1 and mode != 'Disabled':
            raise InvalidArgumentValueError(
                '--pool-high-availability-mode must be Disabled when --pool-node-count is 1.'
            )
        if node_count > 1 and mode == 'Disabled':
            raise InvalidArgumentValueError(
                '--pool-high-availability-mode must be AnyZone or ZoneRedundant '
                'when --pool-node-count is greater than 1.'
            )

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

        pool_args = {
            name: getattr(args, name).to_serialized_data()
            for name in _POOL_ARGUMENTS
        }
        pool_args.update(cluster_args, pool_name='defaultpool')
        logger.warning(
            "Creating default pool 'defaultpool' for cluster '%s'...", cluster_args['cluster_name']
        )
        poller = PoolCreate(cli_ctx=self.cli_ctx)(command_args=pool_args)
        LongRunningOperation(self.cli_ctx)(poller)
