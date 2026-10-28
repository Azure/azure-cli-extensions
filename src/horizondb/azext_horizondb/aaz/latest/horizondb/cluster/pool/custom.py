# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._create import Create as _PoolCreate
from ._show import Show as _PoolShow
from ._update import Update as _PoolUpdate


class PoolCreate(_PoolCreate):
    AZ_HELP = {
        **_PoolCreate.AZ_HELP,
        'examples': [{
            'name': 'Create a provisioned HorizonDB pool',
            'text': 'az horizondb cluster pool create --resource-group example-resource-group '
                    '--cluster-name example-cluster --pool-name example-pool '
                    '--compute-processor Intel --compute-generation 1 --v-cores 2 '
                    '--node-count 1 --high-availability-mode Disabled',
        }],
    }

    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.parameter_group_resource_id._registered = False  # pylint: disable=protected-access
        args_schema.parameter_group_apply_method._registered = False  # pylint: disable=protected-access
        args_schema.scheduled_maintenance._registered = False  # pylint: disable=protected-access
        return args_schema

    class PoolsCreateOrReplace(_PoolCreate.PoolsCreateOrReplace):

        @property
        def content(self):
            content = super().content
            content['properties']['computeModel']['type'] = 'Provisioned'
            if not content['properties']['parameterGroup'].get('parameterGroupResourceId'):
                del content['properties']['parameterGroup']
            return content


class PoolUpdate(_PoolUpdate):
    _arguments_schema = None
    _args_schema = None

    def _output(self, *args, **kwargs):
        command_args = {
            name: getattr(self.ctx.args, name).to_serialized_data()
            for name in ['cluster_name', 'pool_name', 'resource_group']
        }
        command_args['subscription'] = self.ctx.subscription_id
        return _PoolShow(cli_ctx=self.cli_ctx)(command_args=command_args)
