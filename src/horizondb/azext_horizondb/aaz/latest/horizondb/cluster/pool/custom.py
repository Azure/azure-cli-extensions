# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._create import Create as _PoolCreate
from ._show import Show as _PoolShow
from ._update import Update as _PoolUpdate


class PoolCreate(_PoolCreate):
    class PoolsCreateOrReplace(_PoolCreate.PoolsCreateOrReplace):

        @property
        def content(self):
            content = super().content
            content['properties']['computeModel']['type'] = 'Provisioned'
            return content


class PoolUpdate(_PoolUpdate):
    def _output(self, *args, **kwargs):
        command_args = {
            name: getattr(self.ctx.args, name).to_serialized_data()
            for name in ['cluster_name', 'pool_name', 'resource_group']
        }
        command_args['subscription'] = self.ctx.subscription_id
        return _PoolShow(cli_ctx=self.cli_ctx)(command_args=command_args)
