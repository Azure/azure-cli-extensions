# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable= protected-access, too-few-public-methods
# pylint: disable=duplicate-code

"""
This custom code inherits from generate cluster metrics configuration
functions. It is integrated into the generated code via:
  cli-ext/v20221212preview/ext/src/networkcloud/azext_networkcloud/commands.py
"""

from azext_networkcloud.aaz.latest.networkcloud.cluster.metricsconfiguration._create import (
    Create as _Create,
)
from azure.cli.core.aaz import register_callback

from .common import ClusterMetricsConfiguration


class Create(_Create):
    """Custom class for create operation of cluster's metrics configuration"""

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return ClusterMetricsConfiguration._build_arguments_schema(args_schema)

    @register_callback
    def pre_operations(self):
        ClusterMetricsConfiguration.pre_operations(self.ctx.args)
